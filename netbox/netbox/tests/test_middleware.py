import json
import sys
from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.contrib.messages import get_messages
from django.core.cache import cache
from django.core.signals import got_request_exception
from django.db import connection
from django.db.utils import InterfaceError, InternalError
from django.test import RequestFactory, TransactionTestCase, override_settings
from django.urls import reverse
from rest_framework import status

from core.events import OBJECT_CREATED
from core.models import ConfigRevision, ObjectType
from dcim.models import Site
from extras.models import ConfigContext, Dashboard, Notification, TableConfig
from netbox.config import clear_config
from netbox.middleware import CoreMiddleware, MaintenanceModeMiddleware
from users.constants import TOKEN_PREFIX
from users.models import Token, User
from utilities.testing import TestCase, disable_warnings


class CoreMiddlewareTestCase(TestCase):

    def setUp(self):
        super().setUp()

        self.factory = RequestFactory()
        self.middleware = CoreMiddleware(lambda request: None)
        self.maintenance_mode_middleware = MaintenanceModeMiddleware(lambda request: None)

    @contextmanager
    def capture_request_exception_signal(self):
        captured_requests = []

        def receiver(sender, request, **kwargs):
            captured_requests.append(request)

        got_request_exception.connect(receiver, sender=CoreMiddleware, weak=False)

        try:
            yield captured_requests
        finally:
            got_request_exception.disconnect(receiver, sender=CoreMiddleware)

    def process_runtime_error(self, request, message='Test exception'):
        """
        Call CoreMiddleware.process_exception() from inside an active exception
        handler. handle_rest_api_exception() uses sys.exc_info(), so calling this
        inside an except block is important for the JSON response body.
        """
        try:
            raise RuntimeError(message)
        except RuntimeError as exc:
            return self.middleware.process_exception(request, exc)

    def process_internal_error(self, request, message='Test database error'):
        """
        Call MaintenanceModeMiddleware.process_exception() from inside an active
        exception handler with an InternalError (the maintenance-mode trigger).
        """
        try:
            raise InternalError(message)
        except InternalError as exc:
            return self.maintenance_mode_middleware.process_exception(request, exc)

    def assert_json_500_response(self, response, *, error=None, exception=None):
        self.assertIsNotNone(response)
        self.assertHttpStatus(response, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.headers['Content-Type'], 'application/json')

        data = json.loads(response.content)

        self.assertIn('error', data)
        self.assertIn('exception', data)
        self.assertIn('netbox_version', data)
        self.assertIn('python_version', data)

        if error is not None:
            self.assertEqual(data['error'], error)

        if exception is not None:
            self.assertEqual(data['exception'], exception)

    @override_settings(DEBUG=False)
    def test_process_exception_handles_rest_api_request(self):
        request = self.factory.get(reverse('api-root'))

        with self.capture_request_exception_signal() as captured_requests:
            response = self.process_runtime_error(request, 'Simulated REST API error')

        self.assert_json_500_response(response, error='Simulated REST API error', exception='RuntimeError')
        self.assertEqual(captured_requests, [request])

    @override_settings(DEBUG=False)
    def test_process_exception_handles_graphql_json_request(self):
        request = self.factory.post(
            reverse('graphql'),
            data='{"query": "{ __typename }"}',
            content_type='application/json',
        )

        with self.capture_request_exception_signal() as captured_requests:
            response = self.process_runtime_error(request, 'Simulated GraphQL error')

        self.assert_json_500_response(response, error='Simulated GraphQL error', exception='RuntimeError')
        self.assertEqual(captured_requests, [request])

    @override_settings(DEBUG=False)
    def test_process_exception_does_not_handle_graphql_request_without_json_content_type(self):
        request = self.factory.get(reverse('graphql'))

        response = self.process_runtime_error(request, 'Simulated GraphiQL error')

        self.assertIsNone(response)

    @override_settings(DEBUG=False)
    def test_process_exception_does_not_handle_non_api_request(self):
        request = self.factory.get('/login/')

        response = self.process_runtime_error(request, 'Simulated UI error')

        self.assertIsNone(response)

    @override_settings(DEBUG=True)
    def test_process_exception_does_not_handle_api_requests_in_debug_mode(self):
        requests = (
            self.factory.get(reverse('api-root')),
            self.factory.post(
                reverse('graphql'),
                data='{"query": "{ __typename }"}',
                content_type='application/json',
            ),
        )

        for request in requests:
            with self.subTest(path=request.path_info):
                response = self.process_runtime_error(request, 'Debug exception')

                self.assertIsNone(response)

    def test_maintenance_mode_handles_rest_api_request(self):
        request = self.factory.get(reverse('api-root'))

        with patch('netbox.middleware.get_config', return_value=SimpleNamespace(MAINTENANCE_MODE=True)):
            response = self.process_internal_error(request, 'Simulated maintenance mode REST API error')

        self.assert_json_500_response(response)

    def test_maintenance_mode_handles_ui_post_request(self):
        request = self.factory.post('/dcim/sites/add/')
        request._messages = Mock()

        with patch('netbox.middleware.get_config', return_value=SimpleNamespace(MAINTENANCE_MODE=True)):
            response = self.process_internal_error(request, 'Simulated maintenance mode UI error')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/dcim/sites/add/')

    def test_maintenance_mode_handles_ui_get_request(self):
        """
        A failed write during a GET request must not redirect back to the same URL, which would fail again.
        """
        request = self.factory.get('/')

        with patch('netbox.middleware.get_config', return_value=SimpleNamespace(MAINTENANCE_MODE=True)):
            response = self.process_internal_error(request, 'Simulated maintenance mode UI error')

        self.assertEqual(response.status_code, 503)
        self.assertIn('maintenance mode', response.content.decode())
        self.assertNotIn('Server Error', response.content.decode())

    def test_maintenance_mode_handles_graphql_json_request(self):
        request = self.factory.post(
            reverse('graphql'),
            data='{"query": "{ __typename }"}',
            content_type='application/json',
        )

        # With the fix, is_graphql_request short-circuits to the JSON handler before the
        # messages/redirect path. Mock message storage so that if the fix regresses, the
        # test fails on response shape instead of erroring on absent message middleware.
        request._messages = Mock()

        with patch('netbox.middleware.get_config', return_value=SimpleNamespace(MAINTENANCE_MODE=True)):
            response = self.process_internal_error(request, 'Simulated maintenance mode GraphQL error')

        self.assert_json_500_response(response)


def is_read_only():
    with connection.cursor() as cursor:
        cursor.execute('SHOW transaction_read_only')
        return cursor.fetchone()[0] == 'on'


@override_settings(MAINTENANCE_MODE=True)
class MaintenanceModeTestCase(TransactionTestCase):
    """
    Maintenance mode is enforced on the database session, which has no effect on writes within the transaction that
    wraps each TestCase test, so these tests run against a real connection.
    """

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword', is_superuser=True)

    def tearDown(self):
        # Don't leave a read-only connection behind for other tests
        with connection.cursor() as cursor:
            cursor.execute('SET SESSION CHARACTERISTICS AS TRANSACTION READ WRITE')

    def get_read_only_during_request(self, path):
        """
        Return whether the database connection was read-only while handling a request for the given path.
        """
        read_only = []

        def get_response(request):
            read_only.append(is_read_only())

        MaintenanceModeMiddleware(get_response)(RequestFactory().get(path))
        return read_only[0]

    def test_exempt_paths(self):
        exempt_paths = (
            reverse('login'),
            reverse('logout'),
            reverse('social:begin', kwargs={'backend': 'github'}),
            reverse('social:complete', kwargs={'backend': 'github'}),
            reverse('core:configrevision_list'),
            reverse('core:configrevision_add'),
            reverse('users-api:token_provision'),
        )
        for path in exempt_paths:
            with self.subTest(path=path):
                self.assertFalse(self.get_read_only_during_request(path))
                self.assertFalse(is_read_only())

    def test_restricted_paths(self):
        restricted_paths = (
            reverse('home'),
            reverse('dcim:site_add'),
            reverse('account:preferences'),
            reverse('api-root'),
            reverse('graphql'),
        )
        for path in restricted_paths:
            with self.subTest(path=path):
                self.assertTrue(self.get_read_only_during_request(path))
                self.assertFalse(is_read_only(), "Connection was left read-only after the request")

    def test_maintenance_mode_disabled(self):
        with override_settings(MAINTENANCE_MODE=False):
            self.assertFalse(self.get_read_only_during_request(reverse('dcim:site_add')))

    def test_ui_write_refused(self):
        self.client.force_login(self.user)
        url = reverse('dcim:site_add')

        response = self.client.post(url, {'name': 'Site 1', 'slug': 'site-1', 'status': 'active'})

        self.assertRedirects(response, url, fetch_redirect_response=False)
        self.assertIn('maintenance mode', str(list(get_messages(response.wsgi_request))[0]))
        self.assertFalse(Site.objects.exists())

    def test_api_write_refused(self):
        token = Token.objects.create(user=self.user)
        header = {'HTTP_AUTHORIZATION': f'Bearer {TOKEN_PREFIX}{token.key}.{token.token}'}

        response = self.client.post(
            reverse('dcim-api:site-list'),
            {'name': 'Site 1', 'slug': 'site-1', 'status': 'active'},
            content_type='application/json',
            **header,
        )

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn('maintenance mode', response.json()['error'])
        self.assertFalse(Site.objects.exists())

    def test_api_user_config_write_refused(self):
        """
        Explicitly saving a user's preferences is refused, unlike the incidental changes made while viewing a page.
        """
        token = Token.objects.create(user=self.user)
        header = {'HTTP_AUTHORIZATION': f'Bearer {TOKEN_PREFIX}{token.key}.{token.token}'}

        response = self.client.patch(
            reverse('users-api:userconfig-list'),
            {'data_format': 'yaml'},
            content_type='application/json',
            **header,
        )

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn('maintenance mode', response.json()['error'])
        self.user.config.refresh_from_db()
        self.assertIsNone(self.user.config.get('data_format'))

    def test_writes_resume_when_maintenance_mode_disabled(self):
        self.client.force_login(self.user)
        data = {'name': 'Site 1', 'slug': 'site-1', 'status': 'active'}
        self.client.post(reverse('dcim:site_add'), data)

        with override_settings(MAINTENANCE_MODE=False):
            response = self.client.post(reverse('dcim:site_add'), data)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Site.objects.filter(slug='site-1').exists())

    @override_settings(SESSION_SAVE_EVERY_REQUEST=True)
    def test_session_saved_on_every_request(self):
        """
        LOGIN_PERSISTENCE saves the session on every request.
        """
        self.client.force_login(self.user)

        response = self.client.get(reverse('dcim:site_list'))

        self.assertEqual(response.status_code, 200)

    def test_login_and_logout(self):
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'testpassword'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(int(self.client.session['_auth_user_id']), self.user.pk)

        # The login time isn't recorded in maintenance mode
        self.user.refresh_from_db()
        self.assertIsNone(self.user.last_login)

        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertNotIn('_auth_user_id', self.client.session)

        # The login time is recorded once maintenance mode is disabled
        with override_settings(MAINTENANCE_MODE=False):
            self.client.post(reverse('login'), {'username': 'testuser', 'password': 'testpassword'})
        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.last_login)

    @override_settings(REMOTE_AUTH_ENABLED=True, LOGIN_REQUIRED=True)
    def test_remote_auth_login(self):
        User.objects.create(username='remoteuser1')

        # A refused write must not leave the connection read-only for the next request
        self.client.force_login(self.user)
        self.client.post(reverse('dcim:site_add'), {'name': 'Site 1', 'slug': 'site-1', 'status': 'active'})
        self.client.logout()

        response = self.client.get(reverse('home'), follow=True, HTTP_REMOTE_USER='remoteuser1')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.session['_auth_user_id'], str(User.objects.get(username='remoteuser1').pk))

    # Use a per-process cache, so that activating the new revision doesn't affect other tests
    @override_settings(CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'netbox-maintenance-mode-tests',
        },
    })
    def test_modify_configuration(self):
        self.addCleanup(cache.clear)
        self.addCleanup(clear_config)
        self.client.force_login(self.user)

        response = self.client.post(reverse('core:configrevision_add'), {'comment': 'Disable maintenance mode'})

        self.assertEqual(response.status_code, 302)
        self.assertTrue(ConfigRevision.objects.filter(comment='Disable maintenance mode').exists())

    def test_connection_closed_if_restore_fails(self):
        middleware = MaintenanceModeMiddleware(lambda request: None)

        # Simulate losing the connection before read/write access is restored
        with (
            patch.object(MaintenanceModeMiddleware, '_set_session_type', side_effect=[None, InterfaceError]),
            patch('netbox.middleware.connection') as mock_connection,
        ):
            middleware(RequestFactory().get(reverse('home')))

        mock_connection.close.assert_called_once()

    def test_table_ordering_not_saved(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse('dcim:site_list'), {'sort': 'name'})

        self.assertEqual(response.status_code, 200)
        self.user.config.refresh_from_db()
        self.assertIsNone(self.user.config.get('tables.SiteTable.ordering'))

    def test_table_config_not_saved(self):
        tableconfig = TableConfig.objects.create(
            name='Table Config 1',
            object_type=ObjectType.objects.get_for_model(Site),
            table='SiteTable',
            user=self.user,
            columns=['name', 'status'],
            ordering=['name'],
        )
        self.client.force_login(self.user)

        response = self.client.get(reverse('dcim:site_list'), {'tableconfig_id': tableconfig.pk})

        self.assertEqual(response.status_code, 200)
        self.user.config.refresh_from_db()
        self.assertIsNone(self.user.config.get('tables.SiteTable.columns'))

    def test_data_format_not_saved(self):
        configcontext = ConfigContext.objects.create(name='Config Context 1', data={'foo': 'bar'})
        self.client.force_login(self.user)

        response = self.client.get(configcontext.get_absolute_url(), {'format': 'yaml'})

        self.assertEqual(response.status_code, 200)
        self.user.config.refresh_from_db()
        self.assertIsNone(self.user.config.get('data_format'))

    def test_default_dashboard_not_saved(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(get_messages(response.wsgi_request)), [])
        self.assertFalse(Dashboard.objects.filter(user=self.user).exists())

    def test_notification_not_marked_read(self):
        site = Site.objects.create(name='Site 1', slug='site-1')
        notification = Notification.objects.create(user=self.user, object=site, event_type=OBJECT_CREATED)
        self.client.force_login(self.user)

        response = self.client.get(reverse('extras:notification_read', kwargs={'pk': notification.pk}))

        self.assertRedirects(response, site.get_absolute_url(), fetch_redirect_response=False)
        notification.refresh_from_db()
        self.assertIsNone(notification.read)

    @override_settings(REMOTE_AUTH_BACKEND=['netbox.authentication.LDAPBackend'])
    def test_api_ldap_user_not_updated(self):
        token = Token.objects.create(user=self.user)
        header = {'HTTP_AUTHORIZATION': f'Bearer {TOKEN_PREFIX}{token.key}.{token.token}'}

        with patch('netbox.authentication.LDAPBackend') as mock_backend:
            response = self.client.get(reverse('dcim-api:site-list'), **header)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_backend.return_value.populate_user.assert_not_called()


@override_settings(SENTRY_ENABLED=True)
class SentryNotFoundReportingTestCase(TestCase):

    def setUp(self):
        super().setUp()
        self.sentry_sdk = Mock()
        patcher = patch.dict(sys.modules, {'sentry_sdk': self.sentry_sdk})
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_404_reported_to_sentry(self):
        with disable_warnings('django.request'):
            response = self.client.get('/nonexistent-path/')

        self.assertEqual(response.status_code, 404)
        self.sentry_sdk.capture_message.assert_called_once_with('Page not found', level='error')

    def test_append_slash_redirect_not_reported_to_sentry(self):
        url = reverse('api-status')

        for method in ('get', 'head'):
            with self.subTest(method=method):
                response = getattr(self.client, method)(url.rstrip('/'))

                self.assertEqual(response.status_code, 301)
                self.assertEqual(response.headers['Location'], url)
                self.sentry_sdk.capture_message.assert_not_called()

    def test_unsafe_api_request_without_slash_reported_to_sentry(self):
        with disable_warnings('django.request'):
            response = self.client.post(
                reverse('api-status').rstrip('/'), data={}, content_type='application/json'
            )

        self.assertEqual(response.status_code, 404)
        self.sentry_sdk.capture_message.assert_called_once_with('Page not found', level='error')

    @override_settings(SENTRY_ENABLED=False)
    def test_404_not_reported_when_sentry_disabled(self):
        with disable_warnings('django.request'):
            response = self.client.get('/nonexistent-path/')

        self.assertEqual(response.status_code, 404)
        self.sentry_sdk.capture_message.assert_not_called()
