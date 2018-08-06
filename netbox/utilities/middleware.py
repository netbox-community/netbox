from __future__ import unicode_literals

import sys

from django.conf import settings
from django.db import ProgrammingError
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse

from .views import server_error

BASE_PATH = getattr(settings, 'BASE_PATH', False)
LOGIN_REQUIRED = getattr(settings, 'LOGIN_REQUIRED', False)


class LoginRequiredMiddleware(object):
    """
    If LOGIN_REQUIRED is True, redirect all non-authenticated users to the login page.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if LOGIN_REQUIRED and not request.user.is_authenticated:
            # Redirect unauthenticated requests to the login page. API requests are exempt from redirection as the API
            # performs its own authentication.
            api_path = reverse('api-root')
            if not request.path_info.startswith(api_path) and request.path_info != settings.LOGIN_URL:
                return HttpResponseRedirect('{}?next={}'.format(settings.LOGIN_URL, request.path_info))
        return self.get_response(request)


class APIVersionMiddleware(object):
    """
    If the request is for an API endpoint, include the API version as a response header.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        api_path = reverse('api-root')
        response = self.get_response(request)
        if request.path_info.startswith(api_path):
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
        elif (
            sys.version_info[0] >= 3 and isinstance(exception, PermissionError)
        ) or (
            isinstance(exception, OSError) and exception.errno == 13
        ):
            custom_template = 'exceptions/permission_error.html'

        # Return a custom error message, or fall back to Django's default 500 error handling
        if custom_template:
            return server_error(request, template_name=custom_template)
