import platform

from django import __version__ as DJANGO_VERSION
from django.apps import apps
from django.conf import settings
from django_rq.queues import get_connection
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from rq.worker import Worker

from netbox.api.authentication import IsAuthenticatedOrLoginNotRequired


class APIRootView(APIView):
    """
    This is the root of NetBox's REST API. API endpoints are arranged by app and model name; e.g. `/api/dcim/sites/`.
    """
    _ignore_model_permissions = True
    exclude_from_schema = True
    swagger_schema = None

    def get_view_name(self):
        return "API Root"

    def get(self, request, format=None):

        return Response({
            'circuits': reverse('circuits-api:api-root', request=request, format=format),
            'dcim': reverse('dcim-api:api-root', request=request, format=format),
            'extras': reverse('extras-api:api-root', request=request, format=format),
            'ipam': reverse('ipam-api:api-root', request=request, format=format),
            'plugins': reverse('plugins-api:api-root', request=request, format=format),
            'status': reverse('api-status', request=request, format=format),
            'tenancy': reverse('tenancy-api:api-root', request=request, format=format),
            'users': reverse('users-api:api-root', request=request, format=format),
            'virtualization': reverse('virtualization-api:api-root', request=request, format=format),
            'wireless': reverse('wireless-api:api-root', request=request, format=format),
        })


class StatusView(APIView):
    """
    A lightweight read-only endpoint for conveying NetBox's current operational status.
    """
    permission_classes = [IsAuthenticatedOrLoginNotRequired]

    def get(self, request):
        # Gather the version numbers from all installed Django apps
        installed_apps = {}
        for app_config in apps.get_app_configs():
            app = app_config.module
            version = getattr(app, 'VERSION', getattr(app, '__version__', None))
            if version:
                if type(version) is tuple:
                    version = '.'.join(str(n) for n in version)
                installed_apps[app_config.name] = version
        installed_apps = {k: v for k, v in sorted(installed_apps.items())}

        # Gather installed plugins
        plugins = {}
        for plugin_name in settings.PLUGINS:
            plugin_name = plugin_name.rsplit('.', 1)[-1]
            plugin_config = apps.get_app_config(plugin_name)
            plugins[plugin_name] = getattr(plugin_config, 'version', None)
        plugins = {k: v for k, v in sorted(plugins.items())}

        return Response({
            'django-version': DJANGO_VERSION,
            'installed-apps': installed_apps,
            'netbox-version': settings.VERSION,
            'plugins': plugins,
            'python-version': platform.python_version(),
            'rq-workers-running': Worker.count(get_connection('default')),
        })
