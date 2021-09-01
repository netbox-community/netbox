import uuid
from urllib import parse

from django.conf import settings
from django.contrib.auth.middleware import RemoteUserMiddleware as RemoteUserMiddleware_
from django.db import ProgrammingError
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse

from extras.context_managers import change_logging
from netbox.views import server_error
from utilities.api import is_api_request, rest_api_server_error


class LoginRequiredMiddleware(object):
    """
    If LOGIN_REQUIRED is True, redirect all non-authenticated users to the login page.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Redirect unauthenticated requests (except those exempted) to the login page if LOGIN_REQUIRED is true
        if settings.LOGIN_REQUIRED and not request.user.is_authenticated:
            # Determine exempt paths
            exempt_paths = [
                reverse('api-root'),
                reverse('graphql'),
            ]
            if settings.METRICS_ENABLED:
                exempt_paths.append(reverse('prometheus-django-metrics'))

            # Redirect unauthenticated requests
            if not request.path_info.startswith(tuple(exempt_paths)) and request.path_info != settings.LOGIN_URL:
                login_url = f'{settings.LOGIN_URL}?next={parse.quote(request.get_full_path_info())}'
                return HttpResponseRedirect(login_url)

        return self.get_response(request)


class RemoteUserMiddleware(RemoteUserMiddleware_):
    """
    Custom implementation of Django's RemoteUserMiddleware which allows for a user-configurable HTTP header name.
    """
    force_logout_if_no_header = False

    @property
    def header(self):
        return settings.REMOTE_AUTH_HEADER

    def process_request(self, request):

        # Bypass middleware if remote authentication is not enabled
        if not settings.REMOTE_AUTH_ENABLED:
            return

        return super().process_request(request)


class ObjectChangeMiddleware(object):
    """
    This middleware performs three functions in response to an object being created, updated, or deleted:

        1. Create an ObjectChange to reflect the modification to the object in the changelog.
        2. Enqueue any relevant webhooks.
        3. Increment the metric counter for the event type.

    The post_save and post_delete signals are employed to catch object modifications, however changes are recorded a bit
    differently for each. Objects being saved are cached into thread-local storage for action *after* the response has
    completed. This ensures that serialization of the object is performed only after any related objects (e.g. tags)
    have been created. Conversely, deletions are acted upon immediately, so that the serialized representation of the
    object is recorded before it (and any related objects) are actually deleted from the database.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Assign a random unique ID to the request. This will be used to associate multiple object changes made during
        # the same request.
        request.id = uuid.uuid4()

        # Process the request with change logging enabled
        with change_logging(request):
            response = self.get_response(request)

        return response


class APIVersionMiddleware(object):
    """
    If the request is for an API endpoint, include the API version as a response header.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if is_api_request(request):
            response['API-Version'] = settings.REST_FRAMEWORK_VERSION
        return response


class ExceptionHandlingMiddleware(object):
    """
    Intercept certain exceptions which are likely indicative of installation issues and provide helpful instructions
    to the user.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):

        # Handle exceptions that occur from REST API requests
        if is_api_request(request):
            return rest_api_server_error(request)

        # Don't catch exceptions when in debug mode
        if settings.DEBUG:
            return

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
            return server_error(request, template_name=custom_template)
