import json
import re
from contextlib import contextmanager
from types import SimpleNamespace
from unittest import skipIf
from unittest.mock import Mock, patch

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.core.signals import got_request_exception
from django.db.utils import InternalError
from django.test import Client, RequestFactory, override_settings
from django.urls import ResolverMatch, reverse
from django.utils.csp import CSP
from django.views.generic import View
from rest_framework import status
from rest_framework.views import APIView

from netbox.middleware import CoreMiddleware, LoginRequiredMiddleware, MaintenanceModeMiddleware
from utilities.testing import TestCase

CSP_POLICY = {
    'default-src': [CSP.SELF],
    'script-src': [CSP.SELF, CSP.NONCE],
}


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


class LoginRequiredMiddlewareTestCase(TestCase):

    def setUp(self):
        super().setUp()

        self.anonymous_client = Client()

    @override_settings(LOGIN_REQUIRED=True)
    def test_anonymous_request_redirected_to_login(self):
        for url in (reverse('home'), reverse('dcim:site_list')):
            with self.subTest(url=url):
                response = self.anonymous_client.get(url)
                self.assertHttpStatus(response, 302)
                self.assertEqual(response['Location'], f"{reverse('login')}?next={url}")

    @override_settings(LOGIN_REQUIRED=False)
    def test_anonymous_request_permitted_when_login_not_required(self):
        response = self.anonymous_client.get(reverse('home'))
        self.assertHttpStatus(response, 200)

    @override_settings(LOGIN_REQUIRED=True)
    def test_exempt_views(self):
        """
        Views which must be reachable without a session respond themselves rather than redirecting to the login page.
        """
        login_url = reverse('login')
        requests = (
            ('get', reverse('login'), 200),
            ('get', reverse('logout'), 302),
            ('post', reverse('social_auth_begin', args=['invalid']), 404),
            ('get', reverse('social:complete', args=['invalid']), 404),
            ('get', reverse('media_failure'), 200),
            ('get', reverse('api-root'), 403),
        )
        for method, url, status_code in requests:
            with self.subTest(url=url):
                response = getattr(self.anonymous_client, method)(url)
                self.assertHttpStatus(response, status_code)
                self.assertFalse(response.get('Location', '').startswith(login_url))

        # The GraphQL API enforces LOGIN_REQUIRED itself
        response = self.anonymous_client.post(
            reverse('graphql'),
            data='{"query": "{ __typename }"}',
            content_type='application/json',
            HTTP_ACCEPT='application/json',
        )
        self.assertHttpStatus(response, 403)
        self.assertEqual(response.content, b'No credentials provided.')

    @override_settings(LOGIN_REQUIRED=True)
    def test_process_view_exemptions(self):
        """
        DRF views and exempt URL names do not require login. Any other view does, even under the REST API path.
        """
        middleware = LoginRequiredMiddleware(lambda request: None)
        view = View.as_view()
        request = RequestFactory().get(f"{reverse('api-root')}non-drf-view/")
        request.user = AnonymousUser()

        self.assertIsNone(middleware.process_view(request, APIView.as_view(), (), {}))
        self.assertHttpStatus(middleware.process_view(request, view, (), {}), 302)

        request.resolver_match = ResolverMatch(view, (), {}, url_name='prometheus-django-metrics')
        self.assertIsNone(middleware.process_view(request, view, (), {}))

    @skipIf('netbox.tests.dummy_plugin' not in settings.PLUGINS, "dummy_plugin not in settings.PLUGINS")
    @override_settings(LOGIN_REQUIRED=True)
    def test_plugin_views(self):
        """
        Plugin views which do not enforce authentication themselves require login. Plugin REST API views do not.
        """
        url = reverse('plugins:dummy_plugin:dummy_model_list')
        response = self.anonymous_client.get(url)
        self.assertHttpStatus(response, 302)
        self.assertEqual(response['Location'], f"{reverse('login')}?next={url}")
        self.assertHttpStatus(self.client.get(url), 200)

        response = self.anonymous_client.get(reverse('plugins-api:dummy_plugin-api:dummymodel-list'))
        self.assertHttpStatus(response, 403)

    @skipIf('netbox.tests.dummy_plugin' not in settings.PLUGINS, "dummy_plugin not in settings.PLUGINS")
    @override_settings(LOGIN_REQUIRED=False)
    def test_plugin_views_login_not_required(self):
        response = self.anonymous_client.get(reverse('plugins:dummy_plugin:dummy_model_list'))
        self.assertHttpStatus(response, 200)


class ContentSecurityPolicyTestCase(TestCase):
    """
    SECURE_CSP and SECURE_CSP_REPORT_ONLY are passed through to Django's CSP middleware.

    Django adds the nonce to the header only when the rendered page reads csp_nonce. The nonce
    tests set DEBUG=True because {% django_htmx_script %} in base.html then does.
    """

    def setUp(self):
        super().setUp()

        self.anonymous_client = Client()

    def get_nonce(self, response, header='Content-Security-Policy'):
        match = re.search(r"'nonce-([^']+)'", response[header])
        self.assertIsNotNone(match, f'No nonce in {header}: {response[header]}')
        return match.group(1)

    @override_settings(SECURE_CSP=CSP_POLICY, DEBUG=True)
    def test_policy_sends_header_with_nonce(self):
        response = self.anonymous_client.get(reverse('login'))
        self.assertHttpStatus(response, 200)
        self.assertIn("default-src 'self'", response['Content-Security-Policy'])
        nonce = self.get_nonce(response)
        self.assertIn(f'nonce="{nonce}"', response.content.decode())

    @override_settings(SECURE_CSP=CSP_POLICY, DEBUG=True)
    def test_nonce_differs_between_requests(self):
        nonce1 = self.get_nonce(self.anonymous_client.get(reverse('login')))
        nonce2 = self.get_nonce(self.anonymous_client.get(reverse('login')))
        self.assertNotEqual(nonce1, nonce2)

    @override_settings(SECURE_CSP_REPORT_ONLY=CSP_POLICY, DEBUG=True)
    def test_report_only_policy(self):
        response = self.anonymous_client.get(reverse('login'))
        self.assertHttpStatus(response, 200)
        self.assertNotIn('Content-Security-Policy', response)
        nonce = self.get_nonce(response, header='Content-Security-Policy-Report-Only')
        self.assertIn(f'nonce="{nonce}"', response.content.decode())

    def test_no_header_by_default(self):
        response = self.anonymous_client.get(reverse('login'))
        self.assertHttpStatus(response, 200)
        self.assertNotIn('Content-Security-Policy', response)
        self.assertNotIn('Content-Security-Policy-Report-Only', response)

    @override_settings(SECURE_CSP=CSP_POLICY, LOGIN_REQUIRED=True, DEBUG=False)
    def test_header_on_non_html_responses(self):
        requests = (
            (reverse('home'), 302),
            (reverse('api-root'), 403),
            ('/no-such-page/', 404),
        )
        for url, status_code in requests:
            with self.subTest(url=url):
                response = self.anonymous_client.get(url)
                self.assertHttpStatus(response, status_code)
                self.assertIn("default-src 'self'", response['Content-Security-Policy'])
