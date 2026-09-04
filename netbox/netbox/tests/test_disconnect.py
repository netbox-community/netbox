import errno
import fcntl
import os
import select
import socket
import struct
import sys
import threading
import time
from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.test import SimpleTestCase

from netbox.disconnect import (
    CANCEL_TIMEOUT,
    CancelTarget,
    ClientDisconnectWatchdog,
    RegistrationState,
    get_client_fd,
    server_exposes_client_socket,
)


class FakePgConn:
    """
    Stand-in for a psycopg connection. Only the attributes the watchdog actually touches are
    implemented: it reads `closed` and calls `cancel_safe()`, and does nothing else.
    """
    def __init__(self, fail=False, gate=None):
        self.closed = False
        self.fail = fail
        self.gate = gate
        self.in_cancel = threading.Event()
        self.closed_during_cancel = False
        self.cancelled = threading.Event()
        self.cancel_timeouts = []
        self.info = SimpleNamespace(backend_pid=12345)
        self.pgconn = SimpleNamespace(finish=self._finish)

    def _finish(self):
        if self.in_cancel.is_set():
            self.closed_during_cancel = True
        self.closed = True

    def cancel_safe(self, *, timeout=None):
        self.in_cancel.set()
        try:
            if self.gate is not None:
                # Hold the cancellation in flight until the test lets it complete.
                self.gate.wait(5.0)
            self.cancel_timeouts.append(timeout)
            self.cancelled.set()
            if self.fail:
                raise RuntimeError("simulated cancellation failure")
        finally:
            self.in_cancel.clear()


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

    def make_targets(self, *aliases, fail_on=(), gate=None):
        targets = []
        for alias in (aliases or ('default',)):
            wrapper = FakeWrapper(alias=alias, pgconn=FakePgConn(fail=alias in fail_on, gate=gate))
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

    def test_buffered_data_does_not_spin(self):
        """
        poll() is level-triggered, so an fd with unread data reports POLLIN on every pass. The
        watchdog must stop asking for it once data is seen, or its thread busy-loops for the rest of
        the request.
        """
        server_sock, client_sock = self.make_socketpair()
        targets = self.make_targets()
        self.watchdog.register(make_request(), server_sock.fileno(), targets)

        with patch.object(self.watchdog, '_handle', wraps=self.watchdog._handle) as handle:
            client_sock.sendall(b'GET /api/ HTTP/1.1\r\n')
            time.sleep(0.3)

        self.assertGreaterEqual(handle.call_count, 1)
        self.assertLessEqual(handle.call_count, 2)
        self.assert_not_cancelled(targets, settle=0)

    def test_claimed_registration_does_not_spin(self):
        """
        A disconnected fd reports POLLHUP or POLLIN on every pass, whatever events are requested. Once
        the watchdog has claimed the registration it must stop polling the fd, or its thread busy-loops
        until the request thread gets around to releasing it.
        """
        server_sock, client_sock = self.make_socketpair()
        targets = self.make_targets()
        registration = self.watchdog.register(make_request(), server_sock.fileno(), targets)

        client_sock.close()
        self.assertTrue(self.wait_for(lambda: registration.state is RegistrationState.CANCELLED))

        with patch.object(self.watchdog, '_handle', wraps=self.watchdog._handle) as handle:
            time.sleep(0.3)

        self.assertEqual(handle.call_count, 0)

    def test_poll_failure_backs_off(self):
        """A persistent poll() failure must not turn the loop into a tight retry that floods the log."""
        failing_poll = Mock()
        failing_poll.poll.side_effect = OSError(errno.ENOMEM, "Cannot allocate memory")

        with self.assertLogs('netbox.disconnect', 'WARNING'):
            self.watchdog._poll = failing_poll
            # Interrupt the poll() already in progress on the real object.
            self.watchdog._wake()
            time.sleep(0.3)

        self.assertEqual(failing_poll.poll.call_count, 1)

    def test_detects_half_close_after_buffered_data(self):
        server_sock, client_sock = self.make_socketpair()
        targets = self.make_targets()
        registration = self.watchdog.register(make_request(), server_sock.fileno(), targets)

        client_sock.sendall(b'GET /api/ HTTP/1.1\r\n')
        self.assertTrue(self.wait_for(lambda: registration.saw_buffered_data))
        client_sock.shutdown(socket.SHUT_WR)

        self.assertTrue(targets[0].pgconn.cancelled.wait(5.0))

    def test_detects_close_queued_behind_data(self):
        """
        A clean TLS shutdown sends a close_notify record immediately followed by FIN, so both may be
        queued by the time the watchdog first looks. The data must not mask the disconnect.
        """
        server_sock, client_sock = self.make_socketpair()
        targets = self.make_targets()
        client_sock.sendall(b'\x15\x03\x03\x00\x02\x01\x00')
        client_sock.shutdown(socket.SHUT_WR)

        self.watchdog.register(make_request(), server_sock.fileno(), targets)

        self.assertTrue(targets[0].pgconn.cancelled.wait(5.0))

    def test_detects_reset_after_buffered_data(self):
        server_sock, client_sock = self.make_socketpair()
        targets = self.make_targets()
        registration = self.watchdog.register(make_request(), server_sock.fileno(), targets)

        client_sock.sendall(b'GET /api/ HTTP/1.1\r\n')
        self.assertTrue(self.wait_for(lambda: registration.saw_buffered_data))
        client_sock.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack('ii', 1, 0))
        client_sock.close()

        self.assertTrue(targets[0].pgconn.cancelled.wait(5.0))

    def test_stale_pollnval_is_ignored(self):
        """
        poll() can report POLLNVAL for a descriptor released while it was running, which is then
        reissued to a new registration before the event is handled. That stale event must not evict
        the new registration.
        """
        server_sock, client_sock = self.make_socketpair()
        targets = self.make_targets()
        registration = self.watchdog.register(make_request(), server_sock.fileno(), targets)

        self.watchdog._handle(registration.peek_sock.fileno(), select.POLLNVAL)

        self.assertIn(registration.token, self.watchdog._by_token)
        client_sock.close()
        self.assertTrue(targets[0].pgconn.cancelled.wait(5.0))

    def test_genuine_pollnval_releases_without_cancelling(self):
        server_sock, client_sock = self.make_socketpair()
        targets = self.make_targets()
        registration = self.watchdog.register(make_request(), server_sock.fileno(), targets)

        # Break the ownership invariant behind the watchdog's back.
        with self.assertLogs('netbox.disconnect', 'WARNING'):
            os.close(registration.peek_sock.fileno())
            self.assertTrue(self.wait_for(lambda: registration.token not in self.watchdog._by_token))

        self.assert_not_cancelled(targets, settle=0)

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

    def test_default_timeout_does_not_alter_socket_flags(self):
        """
        Adopting an fd into a socket object sets O_NONBLOCK on it when a process-wide default timeout
        is in effect. The server's blocking mode must be left exactly as found, whichever it was.
        """
        previous = socket.getdefaulttimeout()
        self.addCleanup(socket.setdefaulttimeout, previous)

        for blocking in (True, False):
            with self.subTest(blocking=blocking):
                server_sock, client_sock = self.make_socketpair()
                server_sock.setblocking(blocking)
                targets = self.make_targets()
                socket.setdefaulttimeout(10)
                try:
                    self.watchdog.register(make_request(), server_sock.fileno(), targets)
                finally:
                    socket.setdefaulttimeout(previous)

                self.assertEqual(os.get_blocking(server_sock.fileno()), blocking)

                # The adopted socket must still peek without waiting.
                client_sock.close()
                self.assertTrue(targets[0].pgconn.cancelled.wait(5.0))

    #
    # Cancellation behaviour
    #

    def test_restart_shuts_down_previous_executor(self):
        """Restarting after the thread died must not orphan the previous cancellation workers."""
        old_executor = self.watchdog._executor
        self.watchdog._stopping.set()
        self.watchdog._wake()
        self.watchdog._thread.join(5.0)
        self.assertFalse(self.watchdog.is_alive())

        self.watchdog.start()

        self.assertTrue(self.watchdog.is_alive())
        self.assertIsNot(self.watchdog._executor, old_executor)
        with self.assertRaises(RuntimeError):
            old_executor.submit(lambda: None)

    def test_abandon_after_fork_closes_inherited_descriptors(self):
        server_sock, client_sock = self.make_socketpair()
        watchdog = ClientDisconnectWatchdog()
        registration = watchdog.register(make_request(), server_sock.fileno(), self.make_targets())
        fds = (watchdog._wake_r, watchdog._wake_w, registration.peek_sock.fileno())

        watchdog.abandon_after_fork()

        for fd in fds:
            with self.assertRaises(OSError):
                os.fstat(fd)
        self.assertEqual(watchdog._by_token, {})
        # The server's own socket is untouched.
        os.fstat(server_sock.fileno())

    def test_abandon_after_fork_ignores_inherited_lock(self):
        """
        A lock held by a parent thread at the moment of forking is never released in the child, so
        abandoning the inherited watchdog must not wait for it.
        """
        watchdog = ClientDisconnectWatchdog()
        held = threading.Event()
        done = threading.Event()
        self.addCleanup(done.set)

        def hold_lock():
            with watchdog._lock:
                held.set()
                done.wait(5.0)

        threading.Thread(target=hold_lock, daemon=True).start()
        self.assertTrue(held.wait(5.0))

        abandoner = threading.Thread(target=watchdog.abandon_after_fork, daemon=True)
        abandoner.start()
        abandoner.join(2.0)
        self.assertFalse(abandoner.is_alive())

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

    def test_cancelled_alias_recorded_before_cancellation_returns(self):
        """
        The request thread can receive QueryCanceled, and log the abort, before cancel_safe() has
        returned on the worker. The alias must already be recorded by then.
        """
        server_sock, client_sock = self.make_socketpair()
        gate = threading.Event()
        self.addCleanup(gate.set)
        targets = self.make_targets('default', gate=gate)
        registration = self.watchdog.register(make_request(), server_sock.fileno(), targets)

        client_sock.close()

        self.assertTrue(targets[0].pgconn.in_cancel.wait(5.0))
        self.assertEqual(registration.cancelled_aliases, ('default',))

    #
    # Connection disposal
    #

    def test_hand_off_defers_disposal_until_cancellation_finishes(self):
        """
        Closing a connection while its cancellation is in flight races libpq, and with pooling would
        hand the backend to another request before the cancellation lands. Connections handed off
        mid-cancellation must be terminated by the cancellation worker, and only once it has finished.
        """
        server_sock, client_sock = self.make_socketpair()
        gate = threading.Event()
        self.addCleanup(gate.set)
        targets = self.make_targets('default', gate=gate)
        pgconn = targets[0].pgconn
        pgconn._pool = Mock()
        registration = self.watchdog.register(make_request(), server_sock.fileno(), targets)

        client_sock.close()
        self.assertTrue(pgconn.in_cancel.wait(5.0))
        self.assertIs(self.watchdog.release(registration), RegistrationState.CANCELLING)
        self.assertTrue(self.watchdog.hand_off(registration, targets))

        time.sleep(0.1)
        self.assertFalse(pgconn.closed)
        pgconn._pool.putconn.assert_not_called()

        gate.set()

        self.assertTrue(self.wait_for(lambda: pgconn._pool.putconn.called))
        self.assertTrue(pgconn.closed)
        self.assertFalse(pgconn.closed_during_cancel)
        # The pool must get the connection back, already terminated, so it can replace it.
        pgconn._pool.putconn.assert_called_once_with(pgconn)

    def test_hand_off_refused_once_cancellation_finished(self):
        server_sock, client_sock = self.make_socketpair()
        targets = self.make_targets()
        registration = self.watchdog.register(make_request(), server_sock.fileno(), targets)

        client_sock.close()
        self.assertTrue(self.wait_for(lambda: registration.state is RegistrationState.CANCELLED))

        self.assertFalse(self.watchdog.hand_off(registration, targets))
        self.assertFalse(targets[0].pgconn.closed)

    def test_hand_off_refused_when_not_cancelled(self):
        server_sock, client_sock = self.make_socketpair()
        targets = self.make_targets()
        registration = self.watchdog.register(make_request(), server_sock.fileno(), targets)

        self.assertIs(self.watchdog.release(registration), RegistrationState.ARMED)
        self.assertFalse(self.watchdog.hand_off(registration, targets))

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
            # The server is still supported: only this request's socket is unusable.
            self.assertTrue(server_exposes_client_socket(request))

    def test_server_exposes_client_socket(self):
        with patch.dict(sys.modules, {'uwsgi': None}):
            self.assertFalse(server_exposes_client_socket(SimpleNamespace(META={})))
        with patch.dict(sys.modules, {'uwsgi': SimpleNamespace()}):
            self.assertTrue(server_exposes_client_socket(SimpleNamespace(META={})))
