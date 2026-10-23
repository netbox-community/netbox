import platform
import sys

from django.conf import settings
from django.http import HttpResponseServerError
from django.shortcuts import render
from django.template import loader
from django.template.exceptions import TemplateDoesNotExist
from django.views.decorators.csrf import requires_csrf_token
from django.views.defaults import ERROR_500_TEMPLATE_NAME, page_not_found
from django.views.generic import View

from netbox.plugins.utils import get_installed_plugins

__all__ = (
    'StaticMediaFailureView',
    'handler_404',
    'handler_500',
)


class StaticMediaFailureView(View):
    """
    Display a user-friendly error message with troubleshooting tips when a static media file fails to load.
    """
    def get(self, request):
        return render(request, 'media_failure.html', {
            'filename': request.GET.get('filename')
        })


def handler_404(request, exception):
    """
    Mark the request for Sentry, then return Django's default 404 response.

    SentryNotFoundMiddleware reports the event only if the response is still a
    404 after CommonMiddleware applies APPEND_SLASH.
    """
    request._sentry_report_404 = True
    return page_not_found(request, exception)


@requires_csrf_token
def handler_500(request, template_name=ERROR_500_TEMPLATE_NAME):
    """
    Custom 500 handler to provide additional context when rendering 500.html.
    """
    try:
        template = loader.get_template(template_name)
    except TemplateDoesNotExist:
        return HttpResponseServerError('<h1>Server Error (500)</h1>', content_type='text/html')
    type_, error = sys.exc_info()[:2]

    return HttpResponseServerError(template.render({
        'request': request,
        'error': error,
        'exception': str(type_),
        'netbox_version': settings.RELEASE.full_version,
        'python_version': platform.python_version(),
        'plugins': get_installed_plugins(),
    }))
