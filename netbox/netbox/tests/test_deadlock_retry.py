from unittest.mock import MagicMock, patch

import psycopg.errors
from django.db import OperationalError
from django.test import RequestFactory, TestCase

from netbox.middleware import CoreMiddleware


class DeadlockRetryTests(TestCase):
    """Tests for the deadlock retry logic in CoreMiddleware."""

    def setUp(self):
        self.factory = RequestFactory()
        self.success_response = MagicMock(status_code=200)

    def _make_deadlock_error(self):
        """Create an OperationalError wrapping a psycopg DeadlockDetected."""
        pg_exc = psycopg.errors.DeadlockDetected("deadlock detected")
        exc = OperationalError("deadlock detected")
        exc.__cause__ = pg_exc
        return exc

    def _make_lock_timeout_error(self):
        """Create an OperationalError wrapping a psycopg LockNotAvailable."""
        pg_exc = psycopg.errors.LockNotAvailable("lock timeout")
        exc = OperationalError("lock timeout")
        exc.__cause__ = pg_exc
        return exc

    def _make_other_operational_error(self):
        """Create an OperationalError that is NOT retriable."""
        pg_exc = psycopg.errors.ConnectionException("connection lost")
        exc = OperationalError("connection lost")
        exc.__cause__ = pg_exc
        return exc

    @patch('netbox.middleware.connection')
    @patch('netbox.middleware.apply_request_processors')
    def test_retry_on_deadlock(self, mock_processors, mock_connection):
        """Middleware retries once on deadlock and returns the successful response."""
        request = self.factory.patch('/api/dcim/devices/1/')
        request.user = MagicMock()

        call_count = 0

        def get_response(req):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise self._make_deadlock_error()
            return self.success_response

        mock_processors.return_value.__enter__ = MagicMock()
        mock_processors.return_value.__exit__ = MagicMock(return_value=False)

        mw = CoreMiddleware(get_response)
        response = mw(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(call_count, 2)
        self.assertTrue(request._deadlock_retried)
        mock_connection.close.assert_called_once()

    @patch('netbox.middleware.connection')
    @patch('netbox.middleware.apply_request_processors')
    def test_retry_on_lock_timeout(self, mock_processors, mock_connection):
        """Middleware retries once on lock timeout."""
        request = self.factory.patch('/api/dcim/devices/1/')
        request.user = MagicMock()

        call_count = 0

        def get_response(req):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise self._make_lock_timeout_error()
            return self.success_response

        mock_processors.return_value.__enter__ = MagicMock()
        mock_processors.return_value.__exit__ = MagicMock(return_value=False)

        mw = CoreMiddleware(get_response)
        response = mw(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(call_count, 2)

    @patch('netbox.middleware.connection')
    @patch('netbox.middleware.apply_request_processors')
    def test_single_retry_limit(self, mock_processors, mock_connection):
        """Middleware retries only once, then re-raises on second deadlock."""
        request = self.factory.patch('/api/dcim/devices/1/')
        request.user = MagicMock()

        def get_response(req):
            raise self._make_deadlock_error()

        mock_processors.return_value.__enter__ = MagicMock()
        mock_processors.return_value.__exit__ = MagicMock(return_value=False)

        mw = CoreMiddleware(get_response)

        with self.assertRaises(OperationalError):
            mw(request)

    @patch('netbox.middleware.apply_request_processors')
    def test_non_retriable_error_not_caught(self, mock_processors):
        """Non-deadlock OperationalErrors are not retried."""
        request = self.factory.patch('/api/dcim/devices/1/')
        request.user = MagicMock()

        def get_response(req):
            raise self._make_other_operational_error()

        mock_processors.return_value.__enter__ = MagicMock()
        mock_processors.return_value.__exit__ = MagicMock(return_value=False)

        mw = CoreMiddleware(get_response)

        with self.assertRaises(OperationalError):
            mw(request)

    @patch('netbox.middleware.connection')
    @patch('netbox.middleware.apply_request_processors')
    def test_fresh_request_id_on_retry(self, mock_processors, mock_connection):
        """Request gets a fresh UUID on retry for changelog accuracy."""
        request = self.factory.patch('/api/dcim/devices/1/')
        request.user = MagicMock()

        request_ids = []

        call_count = 0

        def get_response(req):
            nonlocal call_count
            request_ids.append(req.id)
            call_count += 1
            if call_count == 1:
                raise self._make_deadlock_error()
            return self.success_response

        mock_processors.return_value.__enter__ = MagicMock()
        mock_processors.return_value.__exit__ = MagicMock(return_value=False)

        mw = CoreMiddleware(get_response)
        mw(request)

        self.assertEqual(len(request_ids), 2)
        self.assertNotEqual(request_ids[0], request_ids[1])

    @patch('netbox.middleware.apply_request_processors')
    def test_operational_error_without_cause(self, mock_processors):
        """OperationalError without __cause__ is not retried."""
        request = self.factory.patch('/api/dcim/devices/1/')
        request.user = MagicMock()

        def get_response(req):
            raise OperationalError("some error")

        mock_processors.return_value.__enter__ = MagicMock()
        mock_processors.return_value.__exit__ = MagicMock(return_value=False)

        mw = CoreMiddleware(get_response)

        with self.assertRaises(OperationalError):
            mw(request)
