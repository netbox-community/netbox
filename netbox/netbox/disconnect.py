import dataclasses
import enum
import errno
import itertools
import logging
import os
import select
import socket
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from django.db import DEFAULT_DB_ALIAS
from django.db.backends.base.base import BaseDatabaseWrapper

__all__ = (
    'ARMED_METHODS',
    'HTTP_499_CLIENT_CLOSED_REQUEST',
    'SQLSTATE_QUERY_CANCELED',
    'CancelTarget',
    'ClientDisconnectWatchdog',
    'Registration',
    'RegistrationState',
    'get_client_fd',
    'get_watchdog',
    'server_exposes_client_socket',
)

logger = logging.getLogger('netbox.disconnect')

# HTTP methods for which the watchdog is armed. Cancelling an unsafe method which the client has
# abandoned would silently roll back a write the client may believe has landed, so only safe methods
# are watched. This is a tuning constant, not a policy knob: it is deliberately not user-configurable.
ARMED_METHODS = frozenset(('GET', 'HEAD', 'OPTIONS'))

# Seconds between poll() wakeups. Shutdown latency does not depend on this value; a self-pipe is used
# to interrupt the loop immediately.
POLL_INTERVAL = 1.0

# Per-connection budget passed to cancel_safe(). psycopg's default of 30 seconds is far too long to
# tie up a cancellation worker, and a timeout of zero means "no deadline at all".
CANCEL_TIMEOUT = 2.0

# Total budget for cancelling every connection registered to a single request.
CANCEL_BUDGET = 6.0

# Size of the pool used to dispatch cancellations off the poll loop. Bounded so that a disconnect
# storm (e.g. a load balancer dropping every connection at once) cannot spawn unbounded threads.
CANCEL_WORKERS = 4

# Backstop TTL for a registration. The middleware releases in a finally block, so this should be
# unreachable; it exists because a silently leaked registration holds a file descriptor open.
REGISTRATION_MAX_AGE = 3600

# PostgreSQL SQLSTATE raised when a query is cancelled (psycopg.errors.QueryCanceled).
SQLSTATE_QUERY_CANCELED = '57014'

# Django provides no class for 499, and it is absent from http.HTTPStatus, so the reason phrase must
# be supplied explicitly or Django reports "Unknown Status Code".
HTTP_499_CLIENT_CLOSED_REQUEST = 499

# MSG_DONTWAIT keeps the peek non-blocking without setting O_NONBLOCK on the socket. That distinction
# is critical: O_NONBLOCK lives in the open file description, which dup() shares, so setting it would
# also flip the WSGI server's own client socket to non-blocking. MSG_DONTWAIT is absent on some
# platforms; those reach this module only via runserver, where it is already disabled.
PEEK_FLAGS = socket.MSG_PEEK | getattr(socket, 'MSG_DONTWAIT', 0)

# poll() events which report that the peer has gone, independently of any data still queued for
# reading. POLLRDHUP (the peer sent FIN) is Linux-specific; elsewhere only POLLHUP and POLLERR, which
# poll() reports whether or not they are requested, are available.
POLLRDHUP = getattr(select, 'POLLRDHUP', 0)
HANGUP_EVENTS = select.POLLHUP | select.POLLERR | POLLRDHUP

# errno values from a peek which indicate the peer is gone.
DISCONNECT_ERRNOS = frozenset((
    errno.ECONNRESET,
    errno.ENOTCONN,
    errno.EPIPE,
    errno.ETIMEDOUT,
))


class RegistrationState(enum.IntEnum):
    """
    Lifecycle of a single watched request. Every transition is performed under the watchdog's lock,
    and both ARMED -> CANCELLING (claimed by the watchdog) and ARMED -> RELEASED (reclaimed by the
    request thread) require the state to still be ARMED, so exactly one of them can win.
    """
    ARMED = 0        # The watchdog owns this registration and may still cancel it
    CANCELLING = 1   # The watchdog has claimed it; cancellation is in flight
    CANCELLED = 2    # The cancellation attempt has finished (successfully or not)
    RELEASED = 3     # The request thread reclaimed it; the watchdog must not touch it


class CancelTarget:
    """
    A single database connection which may need to be cancelled on behalf of a request.

    The psycopg connection object is captured at registration time and compared by identity before
    cancelling. Without that check, a wrapper which has since reconnected (connections persist for
    CONN_MAX_AGE) would have its *new* backend cancelled instead.
    """
    __slots__ = ('alias', 'backend_pid', 'pgconn', 'wrapper')

    def __init__(self, alias: str, wrapper: BaseDatabaseWrapper, pgconn: Any, backend_pid: int | None = None):
        self.alias = alias
        self.wrapper = wrapper
        self.pgconn = pgconn
        self.backend_pid = backend_pid

    def __repr__(self):
        return f'<CancelTarget {self.alias} pid={self.backend_pid}>'

    def terminate(self):
        """
        End this connection's database session, so that no cancellation, however late, can land on a
        query issued over it afterwards. Connection.close() is deliberately not used: a pool
        configured with close_returns would take the connection back with its session still open.
        """
        if not self.pgconn.closed:
            self.pgconn.pgconn.finish()


@dataclasses.dataclass
class Registration:
    """
    One in-flight request being watched. This object is handed back to the caller by register() and
    passed to release() verbatim, so the watchdog never needs to key anything on the request ID and
    there is no per-request bookkeeping to leak: the registration dies with the request.
    """
    token: int
    request_id: str
    method: str
    path: str
    started: float
    peek_sock: socket.socket
    targets: tuple
    watchdog: Any = dataclasses.field(repr=False, default=None)
    state: RegistrationState = RegistrationState.ARMED
    # Aliases to which a cancellation is being or has been sent, less any whose cancellation failed
    cancelled_aliases: tuple = ()
    saw_buffered_data: bool = False
    handed_off: tuple = ()

    def elapsed(self):
        return time.monotonic() - self.started


def get_client_fd(request):
    """
    Return the file descriptor of the client connection for this request, or None if it cannot be
    determined. Resolving the socket is WSGI server-specific, so each supported server is tried in
    turn.

    A None return is the expected outcome under the development server, under an unrecognised WSGI
    server, and in tests. Callers must treat it as "disable silently", never as an error.
    """
    # gunicorn places the live client socket object in the WSGI environ. Django's WSGIRequest aliases
    # request.META to that environ, so it is reachable here.
    sock = request.META.get('gunicorn.socket')
    if sock is not None:
        try:
            fd = sock.fileno()
        except OSError:
            logger.debug("gunicorn.socket present but its fd could not be read", exc_info=True)
        else:
            if fd >= 0:
                return fd

    # uWSGI exposes the connection fd through its extension module, which exists only when actually
    # running under uWSGI. Import it lazily and tolerate its absence.
    try:
        import uwsgi
        fd = uwsgi.connection_fd()
    except Exception:
        pass
    else:
        if isinstance(fd, int) and fd >= 0:
            return fd

    return None


def server_exposes_client_socket(request):
    """
    Report whether the WSGI server is one which get_client_fd() supports, regardless of whether this
    particular request's socket was usable. A supported server can still yield no fd for a single
    request (e.g. the client socket was closed before the request reached us), and that must not be
    mistaken for an unsupported server.
    """
    if 'gunicorn.socket' in request.META:
        return True
    try:
        import uwsgi  # noqa: F401
    except ImportError:
        return False
    return True


class ClientDisconnectWatchdog:
    """
    A single thread per worker process which watches the client sockets of all in-flight requests and
    cancels their database queries when a client goes away.

    One thread is used rather than one per request because NetBox's own gunicorn configuration runs
    multiple request threads per worker; a thread per request would double the concurrency footprint
    for no benefit.
    """

    def __init__(self):
        self._lock = threading.RLock()
        self._by_token = {}    # token -> Registration
        self._by_fd = {}       # our duplicated fd -> token
        self._tokens = itertools.count(1)
        self._poll = select.poll()
        self._stopping = threading.Event()
        self._thread = None
        self._executor = None
        self._last_reap = time.monotonic()

        # Self-pipe, so that shutdown and new registrations interrupt poll() immediately rather than
        # waiting out POLL_INTERVAL.
        self._wake_r, self._wake_w = os.pipe()
        os.set_blocking(self._wake_r, False)
        os.set_blocking(self._wake_w, False)
        self._poll.register(self._wake_r, select.POLLIN)

    #
    # Request-thread API
    #

    def register(self, request, fd, targets):
        """
        Begin watching the given client fd on behalf of a request. Returns a Registration to be
        passed to release(), or None if the registration could not be made.
        """
        if not targets or self._stopping.is_set():
            return None

        # Duplicate the descriptor and take ownership of the copy. The original belongs to the WSGI
        # server, which may close it at any time; once closed, the kernel is free to reissue that
        # integer to an unrelated connection, and polling it would then be both a use-after-close and
        # a route to cancelling the wrong request. Our duplicate cannot be reissued while we hold it.
        try:
            dup_fd = os.dup(fd)
        except OSError:
            logger.debug("Unable to duplicate client fd %s", fd, exc_info=True)
            return None
        try:
            blocking = os.get_blocking(dup_fd)
            peek_sock = socket.socket(fileno=dup_fd)
        except OSError:
            os.close(dup_fd)
            logger.debug("Unable to adopt duplicated fd %s", dup_fd, exc_info=True)
            return None

        # If anything in the process has called socket.setdefaulttimeout(), adopting the fd above set
        # O_NONBLOCK on it, and so on the WSGI server's own socket (see PEEK_FLAGS). Clear the timeout
        # so that recv() does not wait for readability, then restore the server's blocking mode
        # exactly as found: some servers (e.g. gevent workers) run their sockets non-blocking.
        try:
            peek_sock.settimeout(None)
            os.set_blocking(dup_fd, blocking)
        except OSError:
            peek_sock.close()
            logger.debug("Unable to restore blocking mode of fd %s", dup_fd, exc_info=True)
            return None

        # Cancel the default database first, so that a slow secondary cannot exhaust the budget
        # before the connection the request is most likely blocked on has been dealt with.
        targets = tuple(sorted(targets, key=lambda target: target.alias != DEFAULT_DB_ALIAS))

        registration = Registration(
            token=next(self._tokens),
            request_id=str(getattr(request, 'id', '')),
            method=request.method,
            path=request.path,
            started=time.monotonic(),
            peek_sock=peek_sock,
            targets=targets,
            watchdog=self,
        )

        with self._lock:
            self._by_token[registration.token] = registration
            self._by_fd[peek_sock.fileno()] = registration.token
            self._poll.register(peek_sock.fileno(), select.POLLIN)

        self._wake()
        return registration

    def release(self, registration):
        """
        Reclaim a registration and return the state observed at the moment it was reclaimed.

        The return value is the entire cancel/release race protocol. If it is ARMED, the watchdog
        never touched this request. Anything else means a cancellation was claimed and may still be
        in flight, and the caller must treat every target connection as unusable.
        """
        with self._lock:
            observed = registration.state
            if observed is RegistrationState.ARMED:
                registration.state = RegistrationState.RELEASED
            # A claimed registration keeps its state: the watchdog still owns the in-flight
            # cancellation, and the caller needs to see that it lost the race.
            self._discard(registration)

        # Closing the socket releases our duplicated fd. It happens outside the lock, and only the
        # side which removed the entry from the registry performs it, so it happens exactly once.
        self._close(registration)
        return observed

    def hand_off(self, registration, targets):
        """
        Pass the given targets to a cancellation still in flight for this registration, which will
        terminate them once it has finished. Returns False if no cancellation is in flight, in which
        case the targets remain the caller's to dispose of.

        Neither thread may dispose of a connection while the other is still using it: closing one
        mid-cancellation races libpq, and with connection pooling it would hand the backend to another
        request just before the cancellation lands on it. So whichever finishes last disposes of it.
        """
        with self._lock:
            if registration.state is not RegistrationState.CANCELLING:
                return False
            registration.handed_off = tuple(targets)
            return True

    #
    # Thread lifecycle
    #

    def start(self):
        with self._lock:
            if self._thread is not None and self._thread.is_alive():
                return
            self._stopping.clear()
            if self._executor is not None:
                # Restarting after the thread died. Queued cancellations still run; the old workers
                # exit once they have drained.
                self._executor.shutdown(wait=False)
            self._executor = ThreadPoolExecutor(
                max_workers=CANCEL_WORKERS,
                thread_name_prefix='netbox-cancel',
            )
            self._thread = threading.Thread(
                target=self._run,
                name='netbox-disconnect-watchdog',
                daemon=True,
            )
            self._thread.start()

    def is_alive(self):
        thread = self._thread
        return thread is not None and thread.is_alive()

    def shutdown(self, timeout=5.0):
        self._stopping.set()
        self._wake()
        thread = self._thread
        if thread is not None:
            thread.join(timeout)
        executor = self._executor
        if executor is not None:
            executor.shutdown(wait=False)
        with self._lock:
            registrations = list(self._by_token.values())
            for registration in registrations:
                self._discard(registration)
        for registration in registrations:
            self._close(registration)

    def abandon_after_fork(self):
        """
        Drop state inherited from a parent process. The watchdog thread does not survive fork, so the
        registry describes requests this process never served; the descriptors in it belong to
        sockets owned by the parent and must be released without being shut down.

        The lock is deliberately not taken. Only the calling thread survives a fork, and if another
        thread in the parent held the lock at the moment of forking, it would never be released here.
        """
        registrations = list(self._by_token.values())
        self._by_token.clear()
        self._by_fd.clear()
        self._thread = None
        self._executor = None
        for registration in registrations:
            self._close(registration)
        # The self-pipe was inherited too; closing this process's copies leaves the parent's intact.
        for fd in (self._wake_r, self._wake_w):
            try:
                os.close(fd)
            except OSError:
                pass

    #
    # Internals
    #

    def _discard(self, registration):
        """Remove a registration from the registry. Must be called with the lock held."""
        self._by_token.pop(registration.token, None)
        fd = self._fileno(registration)
        if fd >= 0:
            self._by_fd.pop(fd, None)
            self._unpoll(fd)

    def _unpoll(self, fd):
        """Stop polling a descriptor. Must be called with the lock held."""
        try:
            self._poll.unregister(fd)
        except (KeyError, OSError):
            pass

    @staticmethod
    def _fileno(registration):
        try:
            return registration.peek_sock.fileno()
        except OSError:
            return -1

    @staticmethod
    def _close(registration):
        try:
            registration.peek_sock.close()
        except OSError:
            pass

    def _wake(self):
        try:
            os.write(self._wake_w, b'\x00')
        except (BlockingIOError, OSError):
            # A full pipe already carries a pending wakeup, which is all we need.
            pass

    def _drain_wake(self):
        while True:
            try:
                if not os.read(self._wake_r, 4096):
                    return
            except (BlockingIOError, OSError):
                return

    def _run(self):
        timeout_ms = max(int(POLL_INTERVAL * 1000), 1)
        while not self._stopping.is_set():
            try:
                events = self._poll.poll(timeout_ms)
            except OSError as exc:
                logger.warning("poll() failed: %s", exc)
                # Back off rather than retrying at once: a persistent failure (e.g. ENOMEM) would
                # otherwise spin this thread and flood the log. Shutdown still interrupts the wait.
                self._stopping.wait(POLL_INTERVAL)
                continue
            for fd, mask in events:
                if fd == self._wake_r:
                    self._drain_wake()
                    continue
                try:
                    self._handle(fd, mask)
                except Exception:
                    # The watchdog must outlive any single bad registration.
                    logger.exception("Error handling watched fd %s", fd)
            self._reap_stale()

    def _handle(self, fd, mask):
        with self._lock:
            token = self._by_fd.get(fd)
            registration = self._by_token.get(token) if token is not None else None
            if registration is None or registration.state is not RegistrationState.ARMED:
                return
            # Guard against acting on an event which was queued before this fd was recycled into a
            # different registration.
            try:
                if registration.peek_sock.fileno() != fd:
                    return
            except OSError:
                return

        if mask & select.POLLNVAL:
            if not self._poll_now(fd) & select.POLLNVAL:
                # Stale: the event belonged to a registration released while poll() was running, and
                # its descriptor number has since been reissued to this one, which is valid.
                return
            # We own this descriptor for the lifetime of the registration, so this should be
            # unreachable. It means the invariant is broken and the fd may already have been reused,
            # so the one thing we must not do is cancel anything.
            logger.warning("POLLNVAL on owned fd %s (request %s)", fd, registration.request_id)
            self._force_release(registration)
            return

        if registration.saw_buffered_data:
            # Data is queued ahead of any end-of-stream, so a peek can no longer detect it. Rely on
            # the hangup events instead, re-polled now rather than read from the mask, which may be
            # stale.
            if self._is_hung_up(fd):
                self._claim_and_cancel(registration)
            return

        # Always confirm with a peek, including for POLLHUP and POLLERR. Those flags are treated as a
        # hint rather than a verdict so that a stale event cannot cancel a request which happens to
        # have inherited the same descriptor number.
        try:
            data = registration.peek_sock.recv(1, PEEK_FLAGS)
        except (BlockingIOError, InterruptedError):
            # Spurious wakeup; nothing to conclude.
            return
        except ConnectionResetError:
            self._claim_and_cancel(registration)
            return
        except OSError as exc:
            if exc.errno in DISCONNECT_ERRNOS:
                self._claim_and_cancel(registration)
            elif exc.errno == errno.EBADF:
                logger.warning("EBADF on owned fd %s (request %s)", fd, registration.request_id)
                self._force_release(registration)
            else:
                logger.warning("Failed to peek at fd %s: %s", fd, exc)
                self._force_release(registration)
            return

        if data == b'':
            self._claim_and_cancel(registration)
            return

        # Data is queued which the request has not read: a pipelined request, an unread body, or a TLS
        # record such as close_notify. poll() is level-triggered, so the fd would now report POLLIN on
        # every pass and spin this thread. Stop watching for it and rely on the hangup events, which
        # FIN and RST raise regardless of what is queued ahead of them. The peer may already have gone
        # (e.g. close_notify followed by FIN), so check immediately as well.
        registration.saw_buffered_data = True
        with self._lock:
            if self._by_fd.get(fd) == registration.token:
                try:
                    self._poll.modify(fd, POLLRDHUP)
                except (KeyError, OSError):
                    pass
        if self._is_hung_up(fd):
            self._claim_and_cancel(registration)

    @staticmethod
    def _poll_now(fd):
        """Return the fd's poll() events as of now, rather than as of an event already queued."""
        probe = select.poll()
        probe.register(fd, POLLRDHUP)
        try:
            events = probe.poll(0)
        except OSError:
            return 0
        return events[0][1] if events else 0

    @classmethod
    def _is_hung_up(cls, fd):
        """Report whether the peer has closed or reset the connection, regardless of queued data."""
        mask = cls._poll_now(fd)
        return bool(mask & HANGUP_EVENTS) and not mask & select.POLLNVAL

    def _force_release(self, registration):
        """Evict a registration from the watchdog side, without cancelling anything."""
        with self._lock:
            self._discard(registration)
        self._close(registration)

    def _claim_and_cancel(self, registration):
        with self._lock:
            if registration.state is not RegistrationState.ARMED:
                return
            registration.state = RegistrationState.CANCELLING
            # A disconnected fd reports POLLHUP or POLLIN on every pass, and POLLHUP and POLLERR
            # cannot be masked out, so leaving it in the poll set would spin this thread until the
            # request thread releases the registration. The fd itself stays open, and registered,
            # until then.
            fd = self._fileno(registration)
            if fd >= 0:
                self._unpoll(fd)
        logger.debug(
            "Client disconnected during request %s (%s %s)",
            registration.request_id, registration.method, registration.path,
        )
        executor = self._executor
        if executor is None:
            self._cancel_all(registration)
        else:
            # Cancellation opens a fresh authenticated connection to PostgreSQL, which may take
            # hundreds of milliseconds and can block past its own deadline while libpq resolves the
            # host. It must not run on the poll loop, where it would stall every other watched request.
            executor.submit(self._cancel_all, registration)

    def _cancel_all(self, registration):
        deadline = time.monotonic() + CANCEL_BUDGET
        try:
            for target in registration.targets:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    logger.warning(
                        "Cancellation budget exhausted for request %s; %s not cancelled",
                        registration.request_id, target.alias,
                    )
                    break
                try:
                    # Only ever read an attribute of the wrapper. Its methods call
                    # validate_thread_sharing() and would raise if called from this thread.
                    pgconn = target.wrapper.connection
                    if pgconn is None or pgconn is not target.pgconn or pgconn.closed:
                        # The wrapper has reconnected or closed since registration, so whatever it
                        # holds now is not the query we set out to cancel.
                        continue
                    # Record the alias before sending: the request thread may receive the resulting
                    # error, and log the abort, before cancel_safe() has returned here.
                    registration.cancelled_aliases += (target.alias,)
                    pgconn.cancel_safe(timeout=min(CANCEL_TIMEOUT, remaining))
                except Exception as exc:
                    # One connection failing to cancel must not prevent the others from being tried.
                    registration.cancelled_aliases = tuple(
                        alias for alias in registration.cancelled_aliases if alias != target.alias
                    )
                    logger.warning(
                        "Failed to cancel query for request %s on database '%s': %s",
                        registration.request_id, target.alias, exc,
                    )
        finally:
            with self._lock:
                if registration.state is RegistrationState.CANCELLING:
                    registration.state = RegistrationState.CANCELLED
                handed_off = registration.handed_off
            for target in handed_off:
                self._dispose(registration, target)

    @staticmethod
    def _dispose(registration, target):
        """Terminate a connection handed off by the request thread, which has already detached it."""
        try:
            target.terminate()
            # Return a pooled connection even though it is now dead: abandoning it would permanently
            # cost the pool a slot. The pool discards it and opens a replacement.
            pool = getattr(target.pgconn, '_pool', None)
            if pool is not None:
                pool.putconn(target.pgconn)
        except Exception as exc:
            logger.warning(
                "Failed to dispose of connection for request %s on database '%s': %s",
                registration.request_id, target.alias, exc,
            )

    def _reap_stale(self):
        now = time.monotonic()
        if now - self._last_reap < 1.0:
            return
        self._last_reap = now
        with self._lock:
            stale = [
                registration for registration in self._by_token.values()
                if now - registration.started > REGISTRATION_MAX_AGE
            ]
            for registration in stale:
                self._discard(registration)
        for registration in stale:
            logger.error(
                "Reaped a stale client disconnect registration for request %s after %.0fs; "
                "this indicates a leaked registration",
                registration.request_id, registration.elapsed(),
            )
            self._close(registration)


_watchdog = None
_watchdog_pid = None
_watchdog_lock = threading.Lock()


def get_watchdog():
    """
    Return this process's watchdog, starting it if necessary.

    The thread is created lazily on first use rather than at import or application-ready time. Under
    uWSGI's default (non-lazy-apps) configuration the WSGI application is loaded in the master process
    and then forked; a thread started there would live only in the master and would be absent from
    every process which actually serves requests. Creating it on the first watched request guarantees
    it is created post-fork, in the worker that needs it.
    """
    global _watchdog, _watchdog_pid

    pid = os.getpid()
    watchdog = _watchdog
    if watchdog is not None and _watchdog_pid == pid and watchdog.is_alive():
        return watchdog

    with _watchdog_lock:
        watchdog = _watchdog
        if watchdog is None or _watchdog_pid != pid or not watchdog.is_alive():
            if watchdog is not None and _watchdog_pid != pid:
                # Inherited across a fork: the registry describes the parent's requests and the
                # thread does not exist here.
                watchdog.abandon_after_fork()
                watchdog = None
            elif watchdog is not None:
                # Restart in place, so that requests already registered remain watched.
                logger.error("Client disconnect watchdog thread died unexpectedly; restarting it")
            if watchdog is None:
                watchdog = ClientDisconnectWatchdog()
            watchdog.start()
            _watchdog = watchdog
            _watchdog_pid = pid
        return _watchdog
