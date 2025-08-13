import platform

from django import __version__ as DJANGO_VERSION
from django.conf import settings
from django_rq.queues import get_connection
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from rq.worker import Worker

from netbox.api.authentication import IsAuthenticatedOrLoginNotRequired
from netbox.plugins.utils import get_installed_plugins
from utilities.apps import get_installed_apps


class APIRootView(APIView):
    """
    This is the root of NetBox's REST API. API endpoints are arranged by app and model name; e.g. `/api/dcim/sites/`.
    """
    _ignore_model_permissions = True
    # schema = None

    def get_view_name(self):
        return "API Root"

    @extend_schema(exclude=True)
    def get(self, request, format=None):

        return Response({
            'circuits': reverse('circuits-api:api-root', request=request, format=format),
            'core': reverse('core-api:api-root', request=request, format=format),
            'dcim': reverse('dcim-api:api-root', request=request, format=format),
            'extras': reverse('extras-api:api-root', request=request, format=format),
            'ipam': reverse('ipam-api:api-root', request=request, format=format),
            'plugins': reverse('plugins-api:api-root', request=request, format=format),
            'status': reverse('api-status', request=request, format=format),
            'tenancy': reverse('tenancy-api:api-root', request=request, format=format),
            'users': reverse('users-api:api-root', request=request, format=format),
            'virtualization': reverse('virtualization-api:api-root', request=request, format=format),
            'vpn': reverse('vpn-api:api-root', request=request, format=format),
            'wireless': reverse('wireless-api:api-root', request=request, format=format),
        })


class StatusView(APIView):
    """
    A lightweight read-only endpoint for conveying NetBox's current operational status.
    """
    permission_classes = [IsAuthenticatedOrLoginNotRequired]

    @extend_schema(responses={200: OpenApiTypes.OBJECT})
    def get(self, request):
        return Response({
            'django-version': DJANGO_VERSION,
            'hostname': settings.HOSTNAME,
            'installed_apps': get_installed_apps(),
            'netbox-version': settings.RELEASE.version,
            'netbox-full-version': settings.RELEASE.full_version,
            'plugins': get_installed_plugins(),
            'python-version': platform.python_version(),
            'rq-workers-running': Worker.count(get_connection('default')),
        })
