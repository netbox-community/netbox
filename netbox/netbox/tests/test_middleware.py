import json
import time
import uuid
from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import MagicMock, Mock, patch

from django.core.exceptions import MiddlewareNotUsed
from django.core.signals import got_request_exception
from django.db.utils import InternalError, OperationalError
from django.test import RequestFactory, override_settings
from django.urls import reverse
from prometheus_client import REGISTRY
from psycopg import errors as psycopg_errors
from rest_framework import status

from netbox.disconnect import CancelTarget, Registration, RegistrationState
from netbox.middleware import ClientDisconnectMiddleware, CoreMiddleware, MaintenanceModeMiddleware
from utilities.testing import TestCase


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


class FakePgConn:
    def __init__(self):
        self.closed = False
        self.info = SimpleNamespace(backend_pid=4242)

    def cancel_safe(self, *, timeout=None):
        pass


class FakeWrapper:
    def __init__(self, alias='default', in_atomic_block=False):
        self.alias = alias
        self.vendor = 'postgresql'
        self.connection = FakePgConn()
        self.in_atomic_block = in_atomic_block
        self.closed = False
        self.rollback_set = None

    def ensure_connection(self):
        pass

    def set_rollback(self, value):
        self.rollback_set = value

    def close(self):
        self.closed = True


@override_settings(ABORT_ON_CLIENT_DISCONNECT=True)
class ClientDisconnectMiddlewareTestCase(TestCase):
    """
    The watchdog itself is covered by netbox.tests.test_disconnect; these tests cover the middleware's
    arming, response handling, and connection hygiene, with the watchdog and the client socket faked.
    """

    def setUp(self):
        super().setUp()

        self.factory = RequestFactory()

    def build_request(self, method='get', path='/dcim/devices/'):
        request = getattr(self.factory, method)(path)
        request.id = uuid.uuid4()
        return request

    def build_registration(self, state=RegistrationState.ARMED, targets=None, release_state=None):
        if targets is None:
            targets = self.build_targets(FakeWrapper('default'))
        registration = Registration(
            token=1,
            request_id='test-request',
            method='GET',
            path='/dcim/devices/',
            started=time.monotonic(),
            peek_sock=Mock(),
            targets=tuple(targets),
            watchdog=Mock(),
        )
        registration.state = state
        registration.watchdog.release.return_value = release_state if release_state is not None else state
        return registration

    def build_targets(self, *wrappers):
        return [CancelTarget(w.alias, w, w.connection) for w in wrappers]

    @contextmanager
    def armed(self, registration, fd=7):
        """Run the middleware with a resolvable client socket and a faked watchdog."""
        watchdog = Mock()
        watchdog.register.return_value = registration
        targets = list(registration.targets)
        with patch('netbox.middleware.get_client_fd', return_value=fd), \
                patch('netbox.middleware.get_watchdog', return_value=watchdog), \
                patch.object(ClientDisconnectMiddleware, '_get_cancel_targets', return_value=targets):
            yield watchdog

    @staticmethod
    def cancellation_error(sqlstate='57014'):
        """Build the OperationalError Django raises when a query is cancelled."""
        cause = psycopg_errors.lookup(sqlstate)('canceling statement due to user request')
        error = OperationalError('canceling statement due to user request')
        error.__cause__ = cause
        return error

    #
    # Gating
    #

    def test_middleware_not_used_when_disabled(self):
        """
        Disabled is the default, so it must cost nothing: MiddlewareNotUsed removes the middleware
        from the chain outright rather than leaving an inert one in it.
        """
        with override_settings(ABORT_ON_CLIENT_DISCONNECT=False):
            with self.assertRaises(MiddlewareNotUsed):
                ClientDisconnectMiddleware(lambda request: None)

    def test_disabled_without_socket(self):
        """
        A WSGI server which does not expose the client socket is a supported configuration, not an
        error: the middleware must pass the request through and say so exactly once.
        """
        response = SimpleNamespace()
        middleware = ClientDisconnectMiddleware(lambda request: response)

        with patch('netbox.middleware.get_client_fd', return_value=None), \
                patch('netbox.middleware.get_watchdog') as get_watchdog:
            with self.assertLogs('netbox.disconnect', 'INFO') as logs:
                self.assertIs(middleware(self.build_request()), response)
            # A second request must not repeat the message: the disable is latched.
            self.assertIs(middleware(self.build_request()), response)

        self.assertEqual(len(logs.records), 1)
        get_watchdog.assert_not_called()

    #
    # Arming
    #

    def test_safe_methods_are_armed(self):
        for method in ('get', 'head', 'options'):
            with self.subTest(method=method):
                registration = self.build_registration()
                with self.armed(registration) as watchdog:
                    ClientDisconnectMiddleware(lambda request: SimpleNamespace())(self.build_request(method))
                watchdog.register.assert_called_once()
                registration.watchdog.release.assert_called_once_with(registration)

    def test_unsafe_methods_not_armed(self):
        """
        Cancelling an abandoned write would silently roll back a change the client may believe has
        landed, so unsafe methods always run to completion.
        """
        for method in ('post', 'put', 'patch', 'delete'):
            with self.subTest(method=method):
                registration = self.build_registration()
                with self.armed(registration) as watchdog:
                    request = self.build_request(method)
                    middleware = ClientDisconnectMiddleware(lambda request: SimpleNamespace())
                    middleware(request)
                    watchdog.register.assert_not_called()

                    # Even if something else cancelled the query, an unsafe method must not be
                    # converted into a 499.
                    self.assertIsNone(middleware.process_exception(request, self.cancellation_error()))

    def test_all_open_connections_are_registered(self):
        """Every PostgreSQL connection open for the request is cancelled, not only the default."""
        default = FakeWrapper('default')
        replica = FakeWrapper('replica')
        other = FakeWrapper('mysql_thing')
        other.vendor = 'mysql'

        connections = MagicMock()
        connections.__getitem__.return_value = default
        connections.all.return_value = [replica, default, other]

        with patch('netbox.middleware.connections', connections):
            targets = ClientDisconnectMiddleware._get_cancel_targets()

        connections.all.assert_called_once_with(initialized_only=True)
        self.assertEqual({target.alias for target in targets}, {'default', 'replica'})

    #
    # Response handling
    #

    def test_disconnect_returns_499(self):
        registration = self.build_registration(state=RegistrationState.CANCELLED)
        registration.cancelled_aliases = ('default',)
        request = self.build_request()
        request._client_disconnect = registration
        middleware = ClientDisconnectMiddleware(lambda request: None)

        with self.assertLogs('netbox.disconnect', 'INFO'):
            response = middleware.process_exception(request, self.cancellation_error())

        self.assertEqual(response.status_code, 499)
        self.assertEqual(response.reason_phrase, 'Client Closed Request')

    def test_cancellation_without_our_flag_propagates(self):
        """
        An operator's statement_timeout produces the same SQLSTATE, so the SQLSTATE alone must not be
        enough to claim the cancellation as ours.
        """
        registration = self.build_registration(state=RegistrationState.ARMED)
        request = self.build_request()
        request._client_disconnect = registration
        middleware = ClientDisconnectMiddleware(lambda request: None)

        self.assertIsNone(middleware.process_exception(request, self.cancellation_error()))

    def test_cancellation_without_registration_propagates(self):
        request = self.build_request()
        middleware = ClientDisconnectMiddleware(lambda request: None)

        self.assertIsNone(middleware.process_exception(request, self.cancellation_error()))

    def test_other_operational_error_propagates(self):
        registration = self.build_registration(state=RegistrationState.CANCELLED)
        request = self.build_request()
        request._client_disconnect = registration
        middleware = ClientDisconnectMiddleware(lambda request: None)

        self.assertIsNone(middleware.process_exception(request, self.cancellation_error('40001')))
        self.assertIsNone(middleware.process_exception(request, InternalError('unrelated')))

    def test_cancellation_does_not_fire_got_request_exception(self):
        """
        Returning a response here is what keeps the exception out of CoreMiddleware.process_exception
        (which does fire the signal) and out of handler_500. This asserts the mechanism: nothing
        escapes, and we send nothing ourselves.
        """
        registration = self.build_registration(state=RegistrationState.CANCELLED)
        request = self.build_request()
        request._client_disconnect = registration
        middleware = ClientDisconnectMiddleware(lambda request: None)

        captured = []
        got_request_exception.connect(lambda sender, request, **kwargs: captured.append(request), weak=False)
        receiver = got_request_exception.receivers[-1][1]
        self.addCleanup(got_request_exception.disconnect, receiver)

        with self.assertLogs('netbox.disconnect', 'INFO'):
            response = middleware.process_exception(request, self.cancellation_error())

        self.assertEqual(response.status_code, 499)
        self.assertEqual(captured, [])

    def test_view_label_falls_back_when_url_unresolved(self):
        registration = self.build_registration(state=RegistrationState.CANCELLED)
        request = self.build_request()
        request._client_disconnect = registration
        request.resolver_match = None
        middleware = ClientDisconnectMiddleware(lambda request: None)

        with patch('netbox.middleware.increment_client_disconnects') as increment:
            with self.assertLogs('netbox.disconnect', 'INFO'):
                middleware.process_exception(request, self.cancellation_error())

        increment.assert_called_once_with(method='GET', view='<unnamed view>')

    #
    # Connection hygiene
    #

    def test_cleanup_closes_connections_when_cancelled(self):
        wrappers = [FakeWrapper('default'), FakeWrapper('replica')]
        registration = self.build_registration(
            state=RegistrationState.CANCELLED,
            targets=self.build_targets(*wrappers),
            release_state=RegistrationState.CANCELLED,
        )

        with self.armed(registration):
            ClientDisconnectMiddleware(lambda request: SimpleNamespace())(self.build_request())

        for wrapper in wrappers:
            self.assertTrue(wrapper.closed, f"{wrapper.alias} was not closed")

    def test_no_cleanup_when_not_cancelled(self):
        """The happy path must not close connections, or CONN_MAX_AGE reuse is defeated."""
        wrapper = FakeWrapper('default')
        registration = self.build_registration(
            state=RegistrationState.ARMED,
            targets=self.build_targets(wrapper),
            release_state=RegistrationState.ARMED,
        )

        with self.armed(registration):
            ClientDisconnectMiddleware(lambda request: SimpleNamespace())(self.build_request())

        self.assertFalse(wrapper.closed)
        self.assertIsNone(wrapper.rollback_set)

    def test_set_rollback_only_inside_atomic_block(self):
        """set_rollback() raises outside an atomic block, which would turn the 499 into a 500."""
        for in_atomic_block in (False, True):
            with self.subTest(in_atomic_block=in_atomic_block):
                wrapper = FakeWrapper('default', in_atomic_block=in_atomic_block)
                registration = self.build_registration(
                    state=RegistrationState.CANCELLED,
                    targets=self.build_targets(wrapper),
                    release_state=RegistrationState.CANCELLED,
                )

                with self.armed(registration):
                    ClientDisconnectMiddleware(lambda request: SimpleNamespace())(self.build_request())

                self.assertEqual(wrapper.rollback_set, True if in_atomic_block else None)
                self.assertTrue(wrapper.closed)

    def test_reconnected_wrapper_is_not_closed(self):
        wrapper = FakeWrapper('default')
        targets = self.build_targets(wrapper)
        wrapper.connection = FakePgConn()  # reconnected since registration
        registration = self.build_registration(
            state=RegistrationState.CANCELLED,
            targets=targets,
            release_state=RegistrationState.CANCELLED,
        )

        with self.armed(registration):
            ClientDisconnectMiddleware(lambda request: SimpleNamespace())(self.build_request())

        self.assertFalse(wrapper.closed)

    def test_registration_released_when_view_raises(self):
        """Release lives in a finally: a leaked registration would poison the next request."""
        registration = self.build_registration()

        def get_response(request):
            raise RuntimeError('boom')

        with self.armed(registration):
            with self.assertRaises(RuntimeError):
                ClientDisconnectMiddleware(get_response)(self.build_request())

        registration.watchdog.release.assert_called_once_with(registration)

    #
    # Metrics
    #

    @override_settings(METRICS_ENABLED=True)
    def test_metric_incremented_on_disconnect(self):
        registration = self.build_registration(state=RegistrationState.CANCELLED)
        request = self.build_request()
        request._client_disconnect = registration
        request.resolver_match = SimpleNamespace(view_name='dcim:device_list')
        middleware = ClientDisconnectMiddleware(lambda request: None)

        labels = {'method': 'GET', 'view': 'dcim:device_list'}
        # Counters live in a process-global registry, so only the delta is meaningful.
        before = REGISTRY.get_sample_value('netbox_client_disconnects_total', labels) or 0

        with self.assertLogs('netbox.disconnect', 'INFO'):
            middleware.process_exception(request, self.cancellation_error())

        after = REGISTRY.get_sample_value('netbox_client_disconnects_total', labels) or 0
        self.assertEqual(after - before, 1)

    def test_metric_not_incremented_when_metrics_disabled(self):
        """
        Touching the singleton would register the whole django_prometheus metric set on installations
        which never expose /metrics.
        """
        registration = self.build_registration(state=RegistrationState.CANCELLED)
        request = self.build_request()
        request._client_disconnect = registration
        middleware = ClientDisconnectMiddleware(lambda request: None)

        with patch('netbox.metrics.Metrics.get_instance') as get_instance:
            with self.assertLogs('netbox.disconnect', 'INFO'):
                middleware.process_exception(request, self.cancellation_error())

        get_instance.assert_not_called()
