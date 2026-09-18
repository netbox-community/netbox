import fcntl
import os
import socket
import struct
import sys
import threading
import time
from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase

from netbox.disconnect import (
    CANCEL_TIMEOUT,
    CancelTarget,
    ClientDisconnectWatchdog,
    RegistrationState,
    get_client_fd,
)


class FakePgConn:
    """
    Stand-in for a psycopg connection. Only the attributes the watchdog actually touches are
    implemented: it reads `closed` and calls `cancel_safe()`, and does nothing else.
    """
    def __init__(self, fail=False):
        self.closed = False
        self.fail = fail
        self.cancelled = threading.Event()
        self.cancel_timeouts = []
        self.info = SimpleNamespace(backend_pid=12345)

    def cancel_safe(self, *, timeout=None):
        self.cancel_timeouts.append(timeout)
        self.cancelled.set()
        if self.fail:
            raise RuntimeError("simulated cancellation failure")


class FakeWrapper:
    """Stand-in for a Django BaseDatabaseWrapper."""
    def __init__(self, alias='default', pgconn=None):
        self.alias = alias
        self.vendor = 'postgresql'
        self.connection = pgconn if pgconn is not None else FakePgConn()
        self.in_atomic_block = False
        self.closed = False
        self.rollback_set = None

    def set_rollback(self, value):
        self.rollback_set = value

    def close(self):
        self.closed = True


def make_request(method='GET', path='/dcim/devices/'):
    return SimpleNamespace(id='11111111-1111-1111-1111-111111111111', method=method, path=path)


class ClientDisconnectWatchdogTestCase(SimpleTestCase):
    """
    Exercises the watchdog against real socket pairs. socketpair() gives a genuine pollable,
    closeable, resettable descriptor pair, so none of this needs a WSGI server or a database.
    """

    def setUp(self):
        super().setUp()
        self.watchdog = ClientDisconnectWatchdog()
        self.watchdog.start()
        self.addCleanup(self.watchdog.shutdown)

    def make_socketpair(self):
        server_sock, client_sock = socket.socketpair()
        self.addCleanup(server_sock.close)
        self.addCleanup(client_sock.close)
        return server_sock, client_sock

    def make_targets(self, *aliases, fail_on=()):
        targets = []
        for alias in (aliases or ('default',)):
            wrapper = FakeWrapper(alias=alias, pgconn=FakePgConn(fail=alias in fail_on))
            targets.append(CancelTarget(alias, wrapper, wrapper.connection))
        return targets

    def wait_for(self, predicate, timeout=5.0):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if predicate():
                return True
            time.sleep(0.005)
        return False

    def assert_not_cancelled(self, targets, settle=0.2):
        # Give the watchdog several poll cycles to (incorrectly) act before concluding it did not.
        time.sleep(settle)
        for target in targets:
            self.assertFalse(target.pgconn.cancelled.is_set(), f"{target.alias} was cancelled")

    #
    # Disconnect detection
    #

    def test_detects_half_close(self):
        server_sock, client_sock = self.make_socketpair()
        targets = self.make_targets()
        self.watchdog.register(make_request(), server_sock.fileno(), targets)

        client_sock.shutdown(socket.SHUT_WR)

        self.assertTrue(targets[0].pgconn.cancelled.wait(5.0))

    def test_detects_full_close(self):
        server_sock, client_sock = self.make_socketpair()
        targets = self.make_targets()
        self.watchdog.register(make_request(), server_sock.fileno(), targets)

        client_sock.close()

        self.assertTrue(targets[0].pgconn.cancelled.wait(5.0))

    def test_detects_reset(self):
        server_sock, client_sock = self.make_socketpair()
        targets = self.make_targets()
        self.watchdog.register(make_request(), server_sock.fileno(), targets)

        # SO_LINGER with a zero timeout forces an RST rather than an orderly shutdown.
        client_sock.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack('ii', 1, 0))
        client_sock.close()

        self.assertTrue(targets[0].pgconn.cancelled.wait(5.0))

    def test_pipelined_data_is_not_a_disconnect(self):
        server_sock, client_sock = self.make_socketpair()
        targets = self.make_targets()
        self.watchdog.register(make_request(), server_sock.fileno(), targets)

        client_sock.sendall(b'GET /api/ HTTP/1.1\r\n')

        self.assert_not_cancelled(targets)

    def test_peek_does_not_alter_socket_flags(self):
        """
        O_NONBLOCK lives in the open file description, which dup() shares. Setting it on our
        duplicate would silently flip the WSGI server's own socket to non-blocking, so the peek must
        use MSG_DONTWAIT instead.
        """
        server_sock, client_sock = self.make_socketpair()
        before = fcntl.fcntl(server_sock.fileno(), fcntl.F_GETFL)
        targets = self.make_targets()
        self.watchdog.register(make_request(), server_sock.fileno(), targets)

        client_sock.sendall(b'x')
        time.sleep(0.2)

        after = fcntl.fcntl(server_sock.fileno(), fcntl.F_GETFL)
        self.assertEqual(before & os.O_NONBLOCK, after & os.O_NONBLOCK)
        self.assertEqual(before, after)

    #
    # Cancellation behaviour
    #

    def test_cancel_timeout_is_short(self):
        """psycopg's 30-second default would tie up a cancellation worker far too long."""
        server_sock, client_sock = self.make_socketpair()
        targets = self.make_targets()
        self.watchdog.register(make_request(), server_sock.fileno(), targets)

        client_sock.close()

        self.assertTrue(targets[0].pgconn.cancelled.wait(5.0))
        self.assertTrue(self.wait_for(lambda: targets[0].pgconn.cancel_timeouts))
        self.assertLessEqual(targets[0].pgconn.cancel_timeouts[0], CANCEL_TIMEOUT)

    def test_cancels_all_registered_connections(self):
        server_sock, client_sock = self.make_socketpair()
        targets = self.make_targets('replica', 'default', 'archive')
        registration = self.watchdog.register(make_request(), server_sock.fileno(), targets)

        client_sock.close()

        for target in targets:
            self.assertTrue(target.pgconn.cancelled.wait(5.0), f"{target.alias} not cancelled")
        self.assertTrue(self.wait_for(lambda: len(registration.cancelled_aliases) == 3))
        # The default alias is cancelled first, so a slow secondary cannot exhaust the budget before
        # the connection the request is most likely blocked on has been dealt with.
        self.assertEqual(registration.cancelled_aliases[0], 'default')

    def test_reconnected_wrapper_is_skipped(self):
        """
        A wrapper which reconnected since registration holds a different backend, so cancelling it
        would interrupt an unrelated query. Its siblings must still be cancelled.
        """
        server_sock, client_sock = self.make_socketpair()
        targets = self.make_targets('default', 'replica')
        stale = targets[0]
        replacement = FakePgConn()
        stale.wrapper.connection = replacement
        registration = self.watchdog.register(make_request(), server_sock.fileno(), targets)

        client_sock.close()

        self.assertTrue(targets[1].pgconn.cancelled.wait(5.0))
        self.assertTrue(self.wait_for(lambda: registration.state is RegistrationState.CANCELLED))
        self.assertFalse(stale.pgconn.cancelled.is_set())
        self.assertFalse(replacement.cancelled.is_set())
        self.assertEqual(registration.cancelled_aliases, ('replica',))

    def test_one_failing_cancel_does_not_block_siblings(self):
        server_sock, client_sock = self.make_socketpair()
        targets = self.make_targets('default', 'replica', fail_on=('default',))
        registration = self.watchdog.register(make_request(), server_sock.fileno(), targets)

        client_sock.close()

        self.assertTrue(targets[1].pgconn.cancelled.wait(5.0))
        self.assertTrue(self.wait_for(lambda: registration.state is RegistrationState.CANCELLED))
        self.assertEqual(registration.cancelled_aliases, ('replica',))

    def test_closed_connection_is_skipped(self):
        server_sock, client_sock = self.make_socketpair()
        targets = self.make_targets()
        targets[0].pgconn.closed = True
        registration = self.watchdog.register(make_request(), server_sock.fileno(), targets)

        client_sock.close()

        self.assertTrue(self.wait_for(lambda: registration.state is RegistrationState.CANCELLED))
        self.assertFalse(targets[0].pgconn.cancelled.is_set())

    #
    # Registration lifecycle
    #

    def test_release_before_disconnect_prevents_cancel(self):
        server_sock, client_sock = self.make_socketpair()
        targets = self.make_targets()
        registration = self.watchdog.register(make_request(), server_sock.fileno(), targets)

        observed = self.watchdog.release(registration)
        client_sock.close()

        self.assertIs(observed, RegistrationState.ARMED)
        self.assertIs(registration.state, RegistrationState.RELEASED)
        self.assert_not_cancelled(targets)

    def test_release_reports_lost_race(self):
        """
        When the watchdog claims a registration at the same moment the request finishes, release()
        must report that it lost, so the caller knows the connections may still be cancelled.
        """
        server_sock, client_sock = self.make_socketpair()
        targets = self.make_targets()
        proceed = threading.Event()
        self.addCleanup(proceed.set)

        original = self.watchdog._cancel_all

        def blocking_cancel(registration):
            proceed.wait(5.0)
            original(registration)

        with patch.object(self.watchdog, '_cancel_all', blocking_cancel):
            registration = self.watchdog.register(make_request(), server_sock.fileno(), targets)
            client_sock.close()
            self.assertTrue(self.wait_for(lambda: registration.state is RegistrationState.CANCELLING))

            observed = self.watchdog.release(registration)

        self.assertIs(observed, RegistrationState.CANCELLING)

    def test_fd_reuse_does_not_cancel_stale_registration(self):
        """
        Descriptors are recycled integers. A released registration must never be reachable through a
        descriptor number which has since been reissued to a different request.
        """
        first_server, first_client = self.make_socketpair()
        second_server, second_client = self.make_socketpair()

        first_targets = self.make_targets('default')
        first = self.watchdog.register(make_request(), first_server.fileno(), first_targets)
        first_dup_fd = first.peek_sock.fileno()

        # Release the first registration, then immediately register the second, so that the second
        # duplicate is allocated the descriptor number the first just gave up.
        self.watchdog.release(first)
        second_targets = self.make_targets('default')
        second = self.watchdog.register(make_request(), second_server.fileno(), second_targets)
        if second.peek_sock.fileno() != first_dup_fd:
            self.skipTest("the kernel did not reissue the released descriptor")

        second_client.close()

        self.assertTrue(second_targets[0].pgconn.cancelled.wait(5.0))
        self.assertFalse(first_targets[0].pgconn.cancelled.is_set())

    def test_release_is_idempotent(self):
        server_sock, _ = self.make_socketpair()
        targets = self.make_targets()
        registration = self.watchdog.register(make_request(), server_sock.fileno(), targets)

        self.assertIs(self.watchdog.release(registration), RegistrationState.ARMED)
        self.assertIs(self.watchdog.release(registration), RegistrationState.RELEASED)

    def test_register_returns_none_without_targets(self):
        server_sock, _ = self.make_socketpair()
        self.assertIsNone(self.watchdog.register(make_request(), server_sock.fileno(), []))

    def test_shutdown_is_prompt(self):
        """The self-pipe must interrupt poll() rather than letting it wait out POLL_INTERVAL."""
        started = time.monotonic()
        self.watchdog.shutdown()
        elapsed = time.monotonic() - started

        self.assertLess(elapsed, 0.5)
        self.assertFalse(self.watchdog.is_alive())

    def test_no_fd_leak(self):
        if not os.path.isdir('/proc/self/fd'):
            self.skipTest("requires /proc")

        def open_fds():
            return len(os.listdir('/proc/self/fd'))

        server_sock, _ = self.make_socketpair()
        # Prime the loop so that one-off allocations are not counted as a leak.
        self.watchdog.release(self.watchdog.register(make_request(), server_sock.fileno(), self.make_targets()))

        before = open_fds()
        for _ in range(100):
            registration = self.watchdog.register(make_request(), server_sock.fileno(), self.make_targets())
            self.watchdog.release(registration)

        self.assertEqual(open_fds(), before)


class GetClientFDTestCase(SimpleTestCase):

    def test_gunicorn_socket(self):
        server_sock, _ = socket.socketpair()
        self.addCleanup(server_sock.close)
        request = SimpleNamespace(META={'gunicorn.socket': server_sock})

        self.assertEqual(get_client_fd(request), server_sock.fileno())

    def test_uwsgi_connection_fd(self):
        server_sock, _ = socket.socketpair()
        self.addCleanup(server_sock.close)
        request = SimpleNamespace(META={})
        fake_uwsgi = SimpleNamespace(connection_fd=lambda: server_sock.fileno())

        with patch.dict(sys.modules, {'uwsgi': fake_uwsgi}):
            self.assertEqual(get_client_fd(request), server_sock.fileno())

    def test_no_adapter_returns_none(self):
        request = SimpleNamespace(META={})

        # Ensure a real uwsgi module (if somehow importable) cannot influence the result.
        with patch.dict(sys.modules, {'uwsgi': None}):
            self.assertIsNone(get_client_fd(request))

    def test_closed_gunicorn_socket_returns_none(self):
        server_sock, _ = socket.socketpair()
        server_sock.close()
        request = SimpleNamespace(META={'gunicorn.socket': server_sock})

        with patch.dict(sys.modules, {'uwsgi': None}):
            self.assertIsNone(get_client_fd(request))
