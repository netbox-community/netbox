import json
import sys
from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.conf import settings
from django.core.signals import got_request_exception
from django.db.utils import InternalError
from django.test import RequestFactory, override_settings
from django.urls import reverse
from rest_framework import status

from netbox.middleware import CoreMiddleware, MaintenanceModeMiddleware
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


class SentryNotFoundMiddlewareTestCase(TestCase):
    """
    Sentry must see the status CommonMiddleware left behind.

    GET and HEAD without a trailing slash are APPEND_SLASH redirects and are not
    reported. A path that is still missing, including an unsafe API method, is.
    """

    def setUp(self):
        super().setUp()

        self.capture_message = Mock()
        sentry_sdk = Mock()
        sentry_sdk.capture_message = self.capture_message
        patcher = patch.dict(sys.modules, {'sentry_sdk': sentry_sdk})
        patcher.start()
        self.addCleanup(patcher.stop)

    @override_settings(SENTRY_ENABLED=True)
    def test_get_and_head_slash_redirect_is_not_reported(self):
        url = reverse('api-status').rstrip('/')

        for method in ('get', 'head'):
            with self.subTest(method=method):
                self.capture_message.reset_mock()
                response = getattr(self.client, method)(url)

                self.assertIn(response.status_code, (status.HTTP_301_MOVED_PERMANENTLY, status.HTTP_302_FOUND))
                self.assertTrue(response['Location'].endswith('/'))
                self.capture_message.assert_not_called()

    @override_settings(SENTRY_ENABLED=True)
    def test_unresolved_path_is_reported(self):
        url = reverse('api-status') + 'missing'

        with disable_warnings('django.request'):
            response = self.client.get(url)

        self.assertHttpStatus(response, status.HTTP_404_NOT_FOUND)
        self.capture_message.assert_called_once_with("Page not found", level="error")

    @override_settings(SENTRY_ENABLED=True)
    def test_post_without_trailing_slash_is_reported(self):
        url = reverse('api-status').rstrip('/')

        with disable_warnings('django.request'):
            response = self.client.post(url)

        self.assertHttpStatus(response, status.HTTP_404_NOT_FOUND)
        self.capture_message.assert_called_once_with("Page not found", level="error")

    @override_settings(SENTRY_ENABLED=False)
    def test_disabled_sentry_does_not_report_or_import_sdk(self):
        import netbox.middleware as middleware

        # sentry_sdk is optional and must not be imported when the middleware module loads.
        self.assertNotIn('sentry_sdk', vars(middleware))

        url = reverse('api-status') + 'missing'
        with disable_warnings('django.request'):
            response = self.client.get(url)

        self.assertHttpStatus(response, status.HTTP_404_NOT_FOUND)
        self.capture_message.assert_not_called()

    def test_registered_outside_common_middleware(self):
        # Debug, metrics, and dummy-plugin middleware may surround this entry.
        sentry_index = settings.MIDDLEWARE.index('netbox.middleware.SentryNotFoundMiddleware')
        common_index = settings.MIDDLEWARE.index('netbox.middleware.CommonMiddleware')
        self.assertLess(sentry_index, common_index)
