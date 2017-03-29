import sys

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.reverse import reverse

from django.shortcuts import render
from django.views.generic import View

from circuits.filters import CircuitFilter, ProviderFilter
from circuits.models import Circuit, Provider
from circuits.tables import CircuitSearchTable, ProviderSearchTable
from dcim.filters import DeviceFilter, DeviceTypeFilter, RackFilter, SiteFilter
from dcim.models import ConsolePort, Device, DeviceType, InterfaceConnection, PowerPort, Rack, Site
from dcim.tables import DeviceSearchTable, DeviceTypeSearchTable, RackSearchTable, SiteSearchTable
from extras.models import UserAction
from ipam.filters import AggregateFilter, IPAddressFilter, PrefixFilter, VLANFilter, VRFFilter
from ipam.models import Aggregate, IPAddress, Prefix, VLAN, VRF
from ipam.tables import AggregateSearchTable, IPAddressSearchTable, PrefixSearchTable, VLANSearchTable, VRFSearchTable
from secrets.filters import SecretFilter
from secrets.models import Secret
from secrets.tables import SecretSearchTable
from tenancy.filters import TenantFilter
from tenancy.models import Tenant
from tenancy.tables import TenantSearchTable
from .forms import SearchForm


SEARCH_MAX_RESULTS = 15
SEARCH_TYPES = {
    # Circuits
    'provider': {
        'queryset': Provider.objects.all(),
        'filter': ProviderFilter,
        'table': ProviderSearchTable,
        'url': 'circuits:provider_list',
    },
    'circuit': {
        'queryset': Circuit.objects.select_related('type', 'provider', 'tenant'),
        'filter': CircuitFilter,
        'table': CircuitSearchTable,
        'url': 'circuits:circuit_list',
    },
    # DCIM
    'site': {
        'queryset': Site.objects.select_related('region', 'tenant'),
        'filter': SiteFilter,
        'table': SiteSearchTable,
        'url': 'dcim:site_list',
    },
    'rack': {
        'queryset': Rack.objects.select_related('site', 'group', 'tenant', 'role'),
        'filter': RackFilter,
        'table': RackSearchTable,
        'url': 'dcim:rack_list',
    },
    'devicetype': {
        'queryset': DeviceType.objects.select_related('manufacturer'),
        'filter': DeviceTypeFilter,
        'table': DeviceTypeSearchTable,
        'url': 'dcim:devicetype_list',
    },
    'device': {
        'queryset': Device.objects.select_related('device_type__manufacturer', 'device_role', 'tenant', 'site', 'rack'),
        'filter': DeviceFilter,
        'table': DeviceSearchTable,
        'url': 'dcim:device_list',
    },
    # IPAM
    'vrf': {
        'queryset': VRF.objects.select_related('tenant'),
        'filter': VRFFilter,
        'table': VRFSearchTable,
        'url': 'ipam:vrf_list',
    },
    'aggregate': {
        'queryset': Aggregate.objects.select_related('rir'),
        'filter': AggregateFilter,
        'table': AggregateSearchTable,
        'url': 'ipam:aggregate_list',
    },
    'prefix': {
        'queryset': Prefix.objects.select_related('site', 'vrf__tenant', 'tenant', 'vlan', 'role'),
        'filter': PrefixFilter,
        'table': PrefixSearchTable,
        'url': 'ipam:prefix_list',
    },
    'ipaddress': {
        'queryset': IPAddress.objects.select_related('vrf__tenant', 'tenant', 'interface__device'),
        'filter': IPAddressFilter,
        'table': IPAddressSearchTable,
        'url': 'ipam:ipaddress_list',
    },
    'vlan': {
        'queryset': VLAN.objects.select_related('site', 'group', 'tenant', 'role'),
        'filter': VLANFilter,
        'table': VLANSearchTable,
        'url': 'ipam:vlan_list',
    },
    # Secrets
    'secret': {
        'queryset': Secret.objects.select_related('role', 'device'),
        'filter': SecretFilter,
        'table': SecretSearchTable,
        'url': 'secrets:secret_list',
    },
    # Tenancy
    'tenant': {
        'queryset': Tenant.objects.select_related('group'),
        'filter': TenantFilter,
        'table': TenantSearchTable,
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
                filter_cls = SEARCH_TYPES[obj_type]['filter']
                table = SEARCH_TYPES[obj_type]['table']
                url = SEARCH_TYPES[obj_type]['url']

                # Construct the results table for this object type
                filtered_queryset = filter_cls({'q': form.cleaned_data['q']}, queryset=queryset).qs
                table = table(filtered_queryset)
                table.paginate(per_page=SEARCH_MAX_RESULTS)

                if table.page:
                    results.append({
                        'name': queryset.model._meta.verbose_name_plural,
                        'table': table,
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
