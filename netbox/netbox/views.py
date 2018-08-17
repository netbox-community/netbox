from __future__ import unicode_literals

from collections import OrderedDict

from django.db.models import Count
from django.shortcuts import render
from django.views.generic import View
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

from circuits.filters import CircuitFilter, ProviderFilter
from circuits.models import Circuit, Provider
from circuits.tables import CircuitTable, ProviderTable
from dcim.filters import (
    DeviceFilter, DeviceTypeFilter, RackFilter, RackGroupFilter, SiteFilter, VirtualChassisFilter
)
from dcim.models import (
    ConsolePort, Device, DeviceType, InterfaceConnection, PowerPort, Rack, RackGroup, Site,
    VirtualChassis
)
from dcim.tables import (
    DeviceDetailTable, DeviceTypeTable, RackTable, RackGroupTable, SiteTable, VirtualChassisTable
)
from extras.models import ObjectChange, ReportResult, TopologyMap
from ipam.filters import AggregateFilter, IPAddressFilter, PrefixFilter, VLANFilter, VRFFilter
from ipam.models import Aggregate, IPAddress, Prefix, VLAN, VRF
from ipam.tables import AggregateTable, IPAddressTable, PrefixTable, VLANTable, VRFTable
from secrets.filters import SecretFilter
from secrets.models import Secret
from secrets.tables import SecretTable
from tenancy.filters import TenantFilter
from tenancy.models import Tenant
from tenancy.tables import TenantTable
from virtualization.filters import ClusterFilter, VirtualMachineFilter
from virtualization.models import Cluster, VirtualMachine
from virtualization.tables import ClusterTable, VirtualMachineDetailTable
from .forms import SearchForm

SEARCH_MAX_RESULTS = 15
SEARCH_TYPES = OrderedDict((
    # Circuits
    ('provider', {
        'queryset': Provider.objects.all(),
        'filter': ProviderFilter,
        'table': ProviderTable,
        'url': 'circuits:provider_list',
    }),
    ('circuit', {
        'queryset': Circuit.objects.select_related('type', 'provider', 'tenant').prefetch_related('terminations__site'),
        'filter': CircuitFilter,
        'table': CircuitTable,
        'url': 'circuits:circuit_list',
    }),
    # DCIM
    ('site', {
        'queryset': Site.objects.select_related('region', 'tenant'),
        'filter': SiteFilter,
        'table': SiteTable,
        'url': 'dcim:site_list',
    }),
    ('rack', {
        'queryset': Rack.objects.select_related('site', 'group', 'tenant', 'role'),
        'filter': RackFilter,
        'table': RackTable,
        'url': 'dcim:rack_list',
    }),
    ('rackgroup', {
        'queryset': RackGroup.objects.select_related('site').annotate(rack_count=Count('racks')),
        'filter': RackGroupFilter,
        'table': RackGroupTable,
        'url': 'dcim:rackgroup_list',
    }),
    ('devicetype', {
        'queryset': DeviceType.objects.select_related('manufacturer').annotate(instance_count=Count('instances')),
        'filter': DeviceTypeFilter,
        'table': DeviceTypeTable,
        'url': 'dcim:devicetype_list',
    }),
    ('device', {
        'queryset': Device.objects.select_related(
            'device_type__manufacturer', 'device_role', 'tenant', 'site', 'rack', 'primary_ip4', 'primary_ip6',
        ),
        'filter': DeviceFilter,
        'table': DeviceDetailTable,
        'url': 'dcim:device_list',
    }),
    ('virtualchassis', {
        'queryset': VirtualChassis.objects.select_related('master').annotate(member_count=Count('members')),
        'filter': VirtualChassisFilter,
        'table': VirtualChassisTable,
        'url': 'dcim:virtualchassis_list',
    }),
    # IPAM
    ('vrf', {
        'queryset': VRF.objects.select_related('tenant'),
        'filter': VRFFilter,
        'table': VRFTable,
        'url': 'ipam:vrf_list',
    }),
    ('aggregate', {
        'queryset': Aggregate.objects.select_related('rir'),
        'filter': AggregateFilter,
        'table': AggregateTable,
        'url': 'ipam:aggregate_list',
    }),
    ('prefix', {
        'queryset': Prefix.objects.select_related('site', 'vrf__tenant', 'tenant', 'vlan', 'role'),
        'filter': PrefixFilter,
        'table': PrefixTable,
        'url': 'ipam:prefix_list',
    }),
    ('ipaddress', {
        'queryset': IPAddress.objects.select_related('vrf__tenant', 'tenant'),
        'filter': IPAddressFilter,
        'table': IPAddressTable,
        'url': 'ipam:ipaddress_list',
    }),
    ('vlan', {
        'queryset': VLAN.objects.select_related('site', 'group', 'tenant', 'role'),
        'filter': VLANFilter,
        'table': VLANTable,
        'url': 'ipam:vlan_list',
    }),
    # Secrets
    ('secret', {
        'queryset': Secret.objects.select_related('role', 'device'),
        'filter': SecretFilter,
        'table': SecretTable,
        'url': 'secrets:secret_list',
    }),
    # Tenancy
    ('tenant', {
        'queryset': Tenant.objects.select_related('group'),
        'filter': TenantFilter,
        'table': TenantTable,
        'url': 'tenancy:tenant_list',
    }),
    # Virtualization
    ('cluster', {
        'queryset': Cluster.objects.select_related('type', 'group'),
        'filter': ClusterFilter,
        'table': ClusterTable,
        'url': 'virtualization:cluster_list',
    }),
    ('virtualmachine', {
        'queryset': VirtualMachine.objects.select_related(
            'cluster', 'tenant', 'platform', 'primary_ip4', 'primary_ip6',
        ),
        'filter': VirtualMachineFilter,
        'table': VirtualMachineDetailTable,
        'url': 'virtualization:virtualmachine_list',
    }),
))


class HomeView(View):
    template_name = 'home.html'

    def get(self, request):

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

            # Virtualization
            'cluster_count': Cluster.objects.count(),
            'virtualmachine_count': VirtualMachine.objects.count(),

        }

        return render(request, self.template_name, {
            'search_form': SearchForm(),
            'stats': stats,
            'topology_maps': TopologyMap.objects.filter(site__isnull=True),
            'report_results': ReportResult.objects.order_by('-created')[:10],
            'changelog': ObjectChange.objects.select_related('user')[:50]
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
                table = table(filtered_queryset, orderable=False)
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
        return "API Root"

    def get(self, request, format=None):

        return Response(OrderedDict((
            ('circuits', reverse('circuits-api:api-root', request=request, format=format)),
            ('dcim', reverse('dcim-api:api-root', request=request, format=format)),
            ('extras', reverse('extras-api:api-root', request=request, format=format)),
            ('ipam', reverse('ipam-api:api-root', request=request, format=format)),
            ('secrets', reverse('secrets-api:api-root', request=request, format=format)),
            ('tenancy', reverse('tenancy-api:api-root', request=request, format=format)),
            ('virtualization', reverse('virtualization-api:api-root', request=request, format=format)),
        )))
