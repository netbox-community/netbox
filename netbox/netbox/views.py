import sys

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.reverse import reverse

from django.shortcuts import render

from circuits.models import Provider, Circuit
from dcim.models import Site, Rack, Device, ConsolePort, PowerPort, InterfaceConnection
from extras.models import UserAction
from ipam.models import Aggregate, Prefix, IPAddress, VLAN, VRF
from secrets.models import Secret
from tenancy.models import Tenant


def home(request):

    stats = {

        # Organization
        'site_count': Site.objects.count(),
        'tenant_count': Tenant.objects.count(),

        # DCIM
        'rack_count': Rack.objects.count(),
        'device_count': Device.objects.count(),
        'interface_connections_count': InterfaceConnection.objects.count(),
        'console_connections_count': ConsolePort.objects.filter(cs_port__isnull=False).count(),
        'power_connections_count': PowerPort.objects.filter(power_outlet__isnull=False).count(),

        # IPAM
        'vrf_count': VRF.objects.count(),
        'aggregate_count': Aggregate.objects.count(),
        'prefix_count': Prefix.objects.count(),
        'ipaddress_count': IPAddress.objects.count(),
        'vlan_count': VLAN.objects.count(),

        # Circuits
        'provider_count': Provider.objects.count(),
        'circuit_count': Circuit.objects.count(),

        # Secrets
        'secret_count': Secret.objects.count(),

    }

    return render(request, 'home.html', {
        'stats': stats,
        'recent_activity': UserAction.objects.select_related('user')[:50]
    })


class APIRootView(APIView):
    _ignore_model_permissions = True
    exclude_from_schema = True

    def get_view_name(self):
        return u"API Root"

    def get(self, request, format=None):

        return Response({
            'circuits': reverse('circuits-api:api-root', request=request, format=format),
            'dcim': reverse('dcim-api:api-root', request=request, format=format),
            'extras': reverse('extras-api:api-root', request=request, format=format),
            'ipam': reverse('ipam-api:api-root', request=request, format=format),
            'secrets': reverse('secrets-api:api-root', request=request, format=format),
            'tenancy': reverse('tenancy-api:api-root', request=request, format=format),
        })


def handle_500(request):
    """
    Custom server error handler
    """
    type_, error, traceback = sys.exc_info()
    return render(request, '500.html', {
        'exception': str(type_),
        'error': error,
    }, status=500)


def trigger_500(request):
    """
    Hot-wired method of triggering a server error to test reporting
    """
    raise Exception("Congratulations, you've triggered an exception! Go tell all your friends what an exceptional "
                    "person you are.")
