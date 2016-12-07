from django.http import HttpResponseRedirect
from django.conf import settings


BASE_PATH = getattr(settings, 'BASE_PATH', False)
LOGIN_REQUIRED = getattr(settings, 'LOGIN_REQUIRED', False)


class LoginRequiredMiddleware:
    """
    If LOGIN_REQUIRED is True, redirect all non-authenticated users to the login page.
    """
    def process_request(self, request):
        if LOGIN_REQUIRED and not request.user.is_authenticated():
            # Redirect unauthenticated requests to the login page. API requests are exempt from redirection as the API
            # performs its own authentication.
            api_path = '/{}api/'.format(BASE_PATH)
            if not request.path_info.startswith(api_path) and request.path_info != settings.LOGIN_URL:
                return HttpResponseRedirect('{}?next={}'.format(settings.LOGIN_URL, request.path_info))
