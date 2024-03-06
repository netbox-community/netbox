import logging
import uuid
from urllib import parse

from django.conf import settings
from django.contrib import auth, messages
from django.contrib.auth.middleware import RemoteUserMiddleware as RemoteUserMiddleware_
from django.core.exceptions import ImproperlyConfigured
from django.db import connection, ProgrammingError
from django.db.utils import InternalError
from django.http import Http404, HttpResponseRedirect

from extras.context_managers import event_tracking
from netbox.config import clear_config, get_config
from netbox.views import handler_500
from utilities.api import is_api_request, rest_api_server_error

__all__ = (
    'CoreMiddleware',
    'MaintenanceModeMiddleware',
    'RemoteUserMiddleware',
)


class CoreMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # Assign a random unique ID to the request. This will be used for change logging.
        request.id = uuid.uuid4()

        # Enforce the LOGIN_REQUIRED config parameter. If true, redirect all non-exempt unauthenticated requests
        # to the login page.
        if (
            settings.LOGIN_REQUIRED and
            not request.user.is_authenticated and
            not request.path_info.startswith(settings.AUTH_EXEMPT_PATHS)
        ):
            login_url = f'{settings.LOGIN_URL}?next={parse.quote(request.get_full_path_info())}'
            return HttpResponseRedirect(login_url)

        # Enable the event_tracking context manager and process the request.
        with event_tracking(request):
            response = self.get_response(request)

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
            return

        # Cleanly handle exceptions that occur from REST API requests
        if is_api_request(request):
            return rest_api_server_error(request)

        # Ignore Http404s (defer to Django's built-in 404 handling)
        if isinstance(exception, Http404):
            return

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
            return handler_500(request, template_name=custom_template)


class RemoteUserMiddleware(RemoteUserMiddleware_):
    """
    Custom implementation of Django's RemoteUserMiddleware which allows for a user-configurable HTTP header name.
    """
    force_logout_if_no_header = False

    @property
    def header(self):
        return settings.REMOTE_AUTH_HEADER

    def process_request(self, request):
        logger = logging.getLogger(
            'netbox.authentication.RemoteUserMiddleware')
        # Bypass middleware if remote authentication is not enabled
        if not settings.REMOTE_AUTH_ENABLED:
            return
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
            return
        # If the user is already authenticated and that user is the user we are
        # getting passed in the headers, then the correct user is already
        # persisted in the session and we don't need to continue.
        if request.user.is_authenticated:
            if request.user.get_username() == self.clean_username(username, request):
                return
            else:
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

            if is_api_request(request):
                return rest_api_server_error(request, error=error_message)

            messages.error(request, error_message)
            return HttpResponseRedirect(request.path_info)
