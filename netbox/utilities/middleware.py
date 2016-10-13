from django.http import HttpResponseRedirect
from django.conf import settings


LOGIN_REQUIRED = getattr(settings, 'LOGIN_REQUIRED', False)


class LoginRequiredMiddleware:
    """
    If LOGIN_REQUIRED is True, redirect all non-authenticated users to the login page.
    """
    def process_request(self, request):
        if LOGIN_REQUIRED and not request.user.is_authenticated():
            if request.path_info != settings.LOGIN_URL:
                return HttpResponseRedirect('{}?next={}'.format(settings.LOGIN_URL, request.path_info))
