import logging
import uuid

from django.conf import settings
from django.contrib import auth, messages
from django.contrib.auth.middleware import RemoteUserMiddleware as RemoteUserMiddleware_
from django.core.exceptions import ImproperlyConfigured, MiddlewareNotUsed
from django.core.signals import got_request_exception
from django.db import DEFAULT_DB_ALIAS, ProgrammingError, connection, connections
from django.db.utils import InternalError, OperationalError
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.middleware.common import CommonMiddleware as DjangoCommonMiddleware
from django.utils.translation import gettext_lazy as _
from django_prometheus import middleware
from social_django.middleware import SocialAuthExceptionMiddleware as SocialAuthExceptionMiddleware_

from netbox.config import clear_config, get_config
from netbox.disconnect import (
    ARMED_METHODS,
    HTTP_499_CLIENT_CLOSED_REQUEST,
    SQLSTATE_QUERY_CANCELED,
    CancelTarget,
    RegistrationState,
    get_client_fd,
    get_watchdog,
)
from netbox.metrics import Metrics, increment_client_disconnects
from netbox.views import handler_500
from utilities.api import is_api_request, is_graphql_request
from utilities.error_handlers import handle_rest_api_exception
from utilities.request import apply_request_processors, get_client_ip

__all__ = (
    'ClientDisconnectMiddleware',
    'CommonMiddleware',
    'CoreMiddleware',
    'MaintenanceModeMiddleware',
    'PrometheusAfterMiddleware',
    'PrometheusBeforeMiddleware',
    'RemoteUserMiddleware',
    'SocialAuthExceptionMiddleware',
)

disconnect_logger = logging.getLogger('netbox.disconnect')


class CommonMiddleware(DjangoCommonMiddleware):
    """
    Subclass of Django's CommonMiddleware that suppresses the APPEND_SLASH
    redirect for REST API requests using an unsafe HTTP method. Redirecting a
    POST/PUT/PATCH/DELETE to a trailing-slash URL would either drop the request
    body (clients downgrade to GET on a 302) or raise a RuntimeError when
    DEBUG is enabled. Letting the original 404 propagate gives the caller a
    clear, actionable error instead.
    """
    UNSAFE_METHODS = frozenset(('DELETE', 'PATCH', 'POST', 'PUT'))

    def should_redirect_with_slash(self, request):
        if request.method in self.UNSAFE_METHODS and is_api_request(request):
            return False
        return super().should_redirect_with_slash(request)


class CoreMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # Assign a random unique ID to the request. This will be used for change logging.
        request.id = uuid.uuid4()

        # Apply all registered request processors
        with apply_request_processors(request):
            response = self.get_response(request)

        # Set or renew the language cookie based on the user's preference. This handles two cases:
        # 1. The user just logged in (via any auth backend): the user_logged_in signal stores the preferred language on
        #    the request so we set the cookie here on the login response.
        # 2. SESSION_SAVE_EVERY_REQUEST is enabled: renew the language cookie on every request to keep it in sync with
        #    the session expiry.
        if hasattr(request, '_language_cookie'):
            language = request._language_cookie
        elif request.user.is_authenticated and settings.SESSION_SAVE_EVERY_REQUEST:
            language = request.user.config.get('locale.language')
        else:
            language = None
        if language:
            response.set_cookie(
                key=settings.LANGUAGE_COOKIE_NAME,
                value=language,
                max_age=request.session.get_expiry_age(),
                secure=settings.SESSION_COOKIE_SECURE,
            )

        # Attach the unique request ID as an HTTP header.
        response['X-Request-ID'] = request.id

        # Enable the Vary header to help with caching of HTMX responses
        response['Vary'] = 'HX-Request'

        # If this is an API request, attach an HTTP header annotating the API version (e.g. '3.5').
        if is_api_request(request):
            response['API-Version'] = settings.REST_FRAMEWORK_VERSION

        # Clear any cached dynamic config parameters after each request.
        clear_config()

        return response

    def process_exception(self, request, exception):
        """
        Implement custom error handling logic for production deployments.
        """
        # Don't catch exceptions when in debug mode
        if settings.DEBUG:
            return None

        # Cleanly handle exceptions that occur from REST or GraphQL API requests
        if is_api_request(request) or is_graphql_request(request):
            # Fire Django's got_request_exception signal so error-tracking
            # integrations (e.g. Sentry) capture the exception.
            got_request_exception.send(sender=self.__class__, request=request)
            return handle_rest_api_exception(request)

        # Ignore Http404s (defer to Django's built-in 404 handling)
        if isinstance(exception, Http404):
            return None

        # Determine the type of exception. If it's a common issue, return a custom error page with instructions.
        custom_template = None
        if isinstance(exception, ProgrammingError):
            custom_template = 'exceptions/programming_error.html'
        elif isinstance(exception, ImportError):
            custom_template = 'exceptions/import_error.html'
        elif isinstance(exception, PermissionError):
            custom_template = 'exceptions/permission_error.html'

        # Return a custom error message, or fall back to Django's default 500 error handling
        if custom_template:
            # Fire Django's got_request_exception signal so error-tracking
            # integrations (e.g. Sentry) capture the exception.
            got_request_exception.send(sender=self.__class__, request=request)
            return handler_500(request, template_name=custom_template)
        return None


class ClientDisconnectMiddleware:
    """
    Cancel a request's in-flight database queries when the HTTP client disconnects before the
    response has been sent.

    WSGI provides no cancellation mechanism, so a worker ordinarily runs an abandoned request to
    completion and discovers the disconnect only when it attempts to write the response. A client
    which times out aggressively and retries therefore adds a further orphaned request on each
    attempt, and can saturate every worker and database backend on its own.

    This middleware hands the client socket and the request's database connections to a per-process
    watchdog, which cancels those queries as soon as the client goes away. It disables itself
    silently when the WSGI server does not expose the client socket, which is the expected outcome
    under the development server and in tests.
    """

    def __init__(self, get_response):
        # Removing the middleware from the chain outright is considerably cheaper than leaving an
        # inert one in it, and this is disabled by default.
        if not settings.ABORT_ON_CLIENT_DISCONNECT:
            raise MiddlewareNotUsed()
        self.get_response = get_response
        self._unsupported = False

    def __call__(self, request):
        registration = self._arm(request)
        if registration is None:
            return self.get_response(request)

        request._client_disconnect = registration
        try:
            return self.get_response(request)
        finally:
            # Releasing must happen whatever the outcome: a registration left behind would let the
            # watchdog cancel queries belonging to whichever request next uses this worker thread.
            observed = registration.watchdog.release(registration)
            self._cleanup(registration, observed)
            request._client_disconnect = None

    def _arm(self, request):
        """
        Register this request with the watchdog, returning the Registration or None if the request
        is not being watched.
        """
        if self._unsupported or request.method not in ARMED_METHODS:
            return None

        fd = get_client_fd(request)
        if fd is None:
            # Latch off for the lifetime of this middleware instance, and say so exactly once. This
            # is a supported configuration, not an error.
            self._unsupported = True
            disconnect_logger.info(
                "Client disconnect detection is unavailable: this WSGI server does not expose the "
                "client socket. Requests will not be aborted when clients disconnect."
            )
            return None

        targets = self._get_cancel_targets()
        if not targets:
            return None

        return get_watchdog().register(request, fd, targets)

    @staticmethod
    def _get_cancel_targets():
        """
        Capture the database connections to cancel on disconnect.

        This must happen on the request thread: django.db.connections is thread-local, so the
        watchdog cannot look these up for itself. Connections already open in this thread are used
        as-is; opening every configured alias here would force a handshake per alias on each cold
        request, for aliases the request may never touch.
        """
        targets = []
        try:
            connections[DEFAULT_DB_ALIAS].ensure_connection()
        except Exception:
            disconnect_logger.debug("Unable to establish the default database connection", exc_info=True)

        for wrapper in connections.all(initialized_only=True):
            if wrapper.vendor != 'postgresql':
                continue
            try:
                pgconn = wrapper.connection
                if pgconn is None or not hasattr(pgconn, 'cancel_safe'):
                    continue
                targets.append(CancelTarget(
                    alias=wrapper.alias,
                    wrapper=wrapper,
                    pgconn=pgconn,
                    backend_pid=getattr(getattr(pgconn, 'info', None), 'backend_pid', None),
                ))
            except Exception:
                disconnect_logger.debug("Skipping database '%s'", wrapper.alias, exc_info=True)

        return targets

    @staticmethod
    def _cleanup(registration, observed):
        """
        Discard any connection which may have been cancelled.

        Driven by the state observed when the registration was reclaimed rather than by whether an
        exception was seen, because a cancellation which lost the race may still be in flight even
        though the request completed normally.
        """
        if observed is RegistrationState.ARMED:
            # The watchdog never touched this request, so leave connection reuse alone.
            return

        for target in registration.targets:
            try:
                pgconn = target.wrapper.connection
                if pgconn is None or pgconn is not target.pgconn:
                    # Already closed, or replaced by a reconnect; not ours to discard.
                    continue
                # set_rollback() is only meaningful inside an atomic block, and raises otherwise.
                # Django has normally unwound every atomic block by this point, so this covers only
                # those paths which swallowed the exception.
                if target.wrapper.in_atomic_block:
                    target.wrapper.set_rollback(True)
                # Close unconditionally rather than deferring to close_if_unusable_or_obsolete(): a
                # cancellation which found nothing to cancel leaves a perfectly usable connection,
                # but we cannot distinguish that from one which is about to land. Closing terminates
                # the backend, so any late cancellation becomes a no-op instead of interrupting an
                # unrelated query on a connection reused via CONN_MAX_AGE.
                target.wrapper.close()
            except Exception:
                disconnect_logger.exception(
                    "Error discarding database connection '%s' after cancellation", target.alias
                )

    def process_exception(self, request, exception):
        """
        Convert a query cancellation caused by a client disconnect into a synthetic 499.

        This runs before CoreMiddleware.process_exception(), so returning a response here keeps the
        exception out of handler_500() and out of got_request_exception, and error-tracking
        integrations are not flooded with self-inflicted HTTP 500 reports. The response itself is
        never delivered: the client has already gone.
        """
        if not isinstance(exception, OperationalError):
            return None
        if getattr(exception.__cause__, 'sqlstate', None) != SQLSTATE_QUERY_CANCELED:
            return None

        # The SQLSTATE alone is ambiguous: an operator's statement_timeout produces the same code.
        # Only a registration which the watchdog actually claimed identifies this as our doing.
        registration = getattr(request, '_client_disconnect', None)
        if registration is None or registration.state is RegistrationState.ARMED:
            return None

        try:
            client_ip = get_client_ip(request)
        except ValueError:
            client_ip = None

        disconnect_logger.info(
            "Aborted request %s after client disconnected: %s %s (%.3fs, client %s, databases: %s)",
            registration.request_id,
            request.method,
            request.path,
            registration.elapsed(),
            client_ip or 'unknown',
            ', '.join(registration.cancelled_aliases) or 'none',
        )

        resolver_match = getattr(request, 'resolver_match', None)
        view_name = (resolver_match.view_name if resolver_match is not None else None) or '<unnamed view>'
        increment_client_disconnects(method=request.method, view=view_name)

        return HttpResponse(status=HTTP_499_CLIENT_CLOSED_REQUEST, reason='Client Closed Request')


class RemoteUserMiddleware(RemoteUserMiddleware_):
    """
    Custom implementation of Django's RemoteUserMiddleware which allows for a user-configurable HTTP header name.
    """
    async_capable = False
    force_logout_if_no_header = False

    def __init__(self, get_response):
        if get_response is None:
            raise ValueError("get_response must be provided.")
        self.get_response = get_response

    @property
    def header(self):
        return settings.REMOTE_AUTH_HEADER

    def __call__(self, request):
        logger = logging.getLogger('netbox.authentication.RemoteUserMiddleware')
        # Bypass middleware if remote authentication is not enabled
        if not settings.REMOTE_AUTH_ENABLED:
            return self.get_response(request)
        # AuthenticationMiddleware is required so that request.user exists.
        if not hasattr(request, 'user'):
            raise ImproperlyConfigured(
                "The Django remote user auth middleware requires the"
                " authentication middleware to be installed.  Edit your"
                " MIDDLEWARE setting to insert"
                " 'django.contrib.auth.middleware.AuthenticationMiddleware'"
                " before the RemoteUserMiddleware class.")
        try:
            username = request.META[self.header]
        except KeyError:
            # If specified header doesn't exist then remove any existing
            # authenticated remote-user, or return (leaving request.user set to
            # AnonymousUser by the AuthenticationMiddleware).
            if self.force_logout_if_no_header and request.user.is_authenticated:
                self._remove_invalid_user(request)
            return self.get_response(request)
        # If the user is already authenticated and that user is the user we are
        # getting passed in the headers, then the correct user is already
        # persisted in the session and we don't need to continue.
        if request.user.is_authenticated:
            if request.user.get_username() == self.clean_username(username, request):
                return self.get_response(request)
            # An authenticated user is associated with the request, but
            # it does not match the authorized user in the header.
            self._remove_invalid_user(request)

        # We are seeing this user for the first time in this session, attempt
        # to authenticate the user.
        if settings.REMOTE_AUTH_GROUP_SYNC_ENABLED:
            logger.debug("Trying to sync Groups")
            user = auth.authenticate(
                request, remote_user=username, remote_groups=self._get_groups(request))
        else:
            user = auth.authenticate(request, remote_user=username)
        if user:
            # User is valid.
            # Update the User's Profile if set by request headers
            if settings.REMOTE_AUTH_USER_FIRST_NAME in request.META:
                user.first_name = request.META[settings.REMOTE_AUTH_USER_FIRST_NAME]
            if settings.REMOTE_AUTH_USER_LAST_NAME in request.META:
                user.last_name = request.META[settings.REMOTE_AUTH_USER_LAST_NAME]
            if settings.REMOTE_AUTH_USER_EMAIL in request.META:
                user.email = request.META[settings.REMOTE_AUTH_USER_EMAIL]
            user.save()

            # Set request.user and persist user in the session
            # by logging the user in.
            request.user = user
            auth.login(request, user)

        return self.get_response(request)

    def _get_groups(self, request):
        logger = logging.getLogger(
            'netbox.authentication.RemoteUserMiddleware')

        groups_string = request.META.get(
            settings.REMOTE_AUTH_GROUP_HEADER, None)
        if groups_string:
            groups = groups_string.split(settings.REMOTE_AUTH_GROUP_SEPARATOR)
        else:
            groups = []
        logger.debug(f"Groups are {groups}")
        return groups


class PrometheusBeforeMiddleware(middleware.PrometheusBeforeMiddleware):
    metrics_cls = Metrics


class PrometheusAfterMiddleware(middleware.PrometheusAfterMiddleware):
    metrics_cls = Metrics

    def process_response(self, request, response):
        response = super().process_response(request, response)

        # Increment REST API request counters
        if is_api_request(request):
            method = self._method(request)
            name = self._get_view_name(request)
            self.label_metric(self.metrics.rest_api_requests, request, method=method).inc()
            self.label_metric(self.metrics.rest_api_requests_by_view_method, request, method=method, view=name).inc()

        # Increment GraphQL API request counters
        elif is_graphql_request(request):
            self.metrics.graphql_api_requests.inc()

        return response


class MaintenanceModeMiddleware:
    """
    Middleware that checks if the application is in maintenance mode
    and restricts write-related operations to the database.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if get_config().MAINTENANCE_MODE:
            self._set_session_type(
                allow_write=request.path_info.startswith(settings.MAINTENANCE_EXEMPT_PATHS)
            )

        return self.get_response(request)

    @staticmethod
    def _set_session_type(allow_write):
        """
        Prevent any write-related database operations.

        Args:
            allow_write (bool): If True, write operations will be permitted.
        """
        with connection.cursor() as cursor:
            mode = 'READ WRITE' if allow_write else 'READ ONLY'
            cursor.execute(f'SET SESSION CHARACTERISTICS AS TRANSACTION {mode};')

    def process_exception(self, request, exception):
        """
        Prevent any write-related database operations if an exception is raised.
        """
        if get_config().MAINTENANCE_MODE and isinstance(exception, InternalError):
            error_message = 'NetBox is currently operating in maintenance mode and is unable to perform write ' \
                            'operations. Please try again later.'

            if is_api_request(request) or is_graphql_request(request):
                return handle_rest_api_exception(request, error=error_message)

            messages.error(request, error_message)
            return HttpResponseRedirect(request.path_info)
        return None


class SocialAuthExceptionMiddleware(SocialAuthExceptionMiddleware_):
    """
    Subclass of python-social-auth's exception middleware which surfaces a generic, user-friendly
    message rather than exposing the raw social_core exception text to (typically unauthenticated)
    users when an SSO/SAML login fails.
    """
    def get_message(self, request, exception):
        return _("Single sign-on failed. Please try again or contact your administrator.")
