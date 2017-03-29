import sys

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.reverse import reverse

from django.db.models import Count
from django.shortcuts import render
from django.views.generic import View

from circuits.filters import CircuitFilter, ProviderFilter
from circuits.models import Circuit, Provider
from circuits.tables import CircuitTable, ProviderTable
from dcim.filters import DeviceFilter, DeviceTypeFilter, RackFilter, SiteFilter
from dcim.models import ConsolePort, Device, DeviceType, InterfaceConnection, PowerPort, Rack, Site
from dcim.tables import DeviceTable, DeviceTypeTable, RackTable, SiteTable
from extras.models import UserAction
from ipam.filters import AggregateFilter, IPAddressFilter, PrefixFilter, VLANFilter, VRFFilter
from ipam.models import Aggregate, IPAddress, Prefix, VLAN, VRF
from ipam.tables import AggregateTable, IPAddressTable, PrefixTable, VLANTable, VRFTable
from secrets.filters import SecretFilter
from secrets.models import Secret
from secrets.tables import SecretTable
from tenancy.filters import TenantFilter
from tenancy.models import Tenant
from tenancy.tables import TenantTable
from .forms import SearchForm


SEARCH_MAX_RESULTS = 15
SEARCH_TYPES = {
    # Circuits
    'provider': {
        'queryset': Provider.objects.annotate(count_circuits=Count('circuits')),
        'filter': ProviderFilter,
        'table': ProviderTable,
        'url': 'circuits:provider_list',
    },
    'circuit': {
        'queryset': Circuit.objects.select_related('provider', 'type', 'tenant').prefetch_related(
            'terminations__site'
        ),
        'filter': CircuitFilter,
        'table': CircuitTable,
        'url': 'circuits:circuit_list',
    },
    # DCIM
    'site': {
        'queryset': Site.objects.select_related('region', 'tenant'),
        'filter': SiteFilter,
        'table': SiteTable,
        'url': 'dcim:site_list',
    },
    'rack': {
        'queryset': Rack.objects.select_related('site', 'group', 'tenant', 'role').prefetch_related('devices__device_type').annotate(device_count=Count('devices', distinct=True)),
        'filter': RackFilter,
        'table': RackTable,
        'url': 'dcim:rack_list',
    },
    'devicetype': {
        'queryset': DeviceType.objects.select_related('manufacturer').annotate(instance_count=Count('instances')),
        'filter': DeviceTypeFilter,
        'table': DeviceTypeTable,
        'url': 'dcim:devicetype_list',
    },
    'device': {
        'queryset': Device.objects.select_related(
            'device_type__manufacturer', 'device_role', 'tenant', 'site', 'rack', 'primary_ip4', 'primary_ip6'
        ),
        'filter': DeviceFilter,
        'table': DeviceTable,
        'url': 'dcim:device_list',
    },
    # IPAM
    'vrf': {
        'queryset': VRF.objects.select_related('tenant'),
        'filter': VRFFilter,
        'table': VRFTable,
        'url': 'ipam:vrf_list',
    },
    'aggregate': {
        'queryset': Aggregate.objects.select_related('rir'),
        'filter': AggregateFilter,
        'table': AggregateTable,
        'url': 'ipam:aggregate_list',
    },
    'prefix': {
        'queryset': Prefix.objects.select_related('site', 'vrf__tenant', 'tenant', 'vlan', 'role'),
        'filter': PrefixFilter,
        'table': PrefixTable,
        'url': 'ipam:prefix_list',
    },
    'ipaddress': {
        'queryset': IPAddress.objects.select_related('vrf__tenant', 'tenant', 'interface__device'),
        'filter': IPAddressFilter,
        'table': IPAddressTable,
        'url': 'ipam:ipaddress_list',
    },
    'vlan': {
        'queryset': VLAN.objects.select_related('site', 'group', 'tenant', 'role').prefetch_related('prefixes'),
        'filter': VLANFilter,
        'table': VLANTable,
        'url': 'ipam:vlan_list',
    },
    # Secrets
    'secret': {
        'queryset': Secret.objects.select_related('role', 'device'),
        'filter': SecretFilter,
        'table': SecretTable,
        'url': 'secrets:secret_list',
    },
    # Tenancy
    'tenant': {
        'queryset': Tenant.objects.select_related('group'),
        'filter': TenantFilter,
        'table': TenantTable,
        'url': 'tenancy:tenant_list',
    },
}


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
        'search_form': SearchForm(),
        'stats': stats,
        'recent_activity': UserAction.objects.select_related('user')[:50]
    })


class SearchView(View):

    def get(self, request):

        # No query
        if 'q' not in request.GET:
            return render(request, 'search.html', {
                'form': SearchForm(),
            })

        form = SearchForm(request.GET)
        results = []

        if form.is_valid():

            # Searching for a single type of object
            if form.cleaned_data['obj_type']:
                obj_types = [form.cleaned_data['obj_type']]
            # Searching all object types
            else:
                obj_types = SEARCH_TYPES.keys()

            for obj_type in obj_types:
                queryset = SEARCH_TYPES[obj_type]['queryset']
                filter = SEARCH_TYPES[obj_type]['filter']
                table = SEARCH_TYPES[obj_type]['table']
                url = SEARCH_TYPES[obj_type]['url']
                filtered_queryset = filter({'q': form.cleaned_data['q']}, queryset=queryset).qs
                total_count = filtered_queryset.count()
                if total_count:
                    results.append({
                        'name': queryset.model._meta.verbose_name_plural,
                        'table': table(filtered_queryset[:SEARCH_MAX_RESULTS]),
                        'total': total_count,
                        'url': '{}?q={}'.format(reverse(url), form.cleaned_data['q'])
                    })

        return render(request, 'search.html', {
            'form': form,
            'results': results,
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
