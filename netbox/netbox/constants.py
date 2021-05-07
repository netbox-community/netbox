from collections import OrderedDict

from circuits.filtersets import CircuitFilterSet, ProviderFilterSet, ProviderNetworkFilterSet
from circuits.models import Circuit, ProviderNetwork, Provider
from circuits.tables import CircuitTable, ProviderNetworkTable, ProviderTable
from dcim.filtersets import (
    CableFilterSet, DeviceFilterSet, DeviceTypeFilterSet, PowerFeedFilterSet, RackFilterSet, LocationFilterSet,
    SiteFilterSet, VirtualChassisFilterSet,
)
from dcim.models import Cable, Device, DeviceType, PowerFeed, Rack, Location, Site, VirtualChassis
from dcim.tables import (
    CableTable, DeviceTable, DeviceTypeTable, PowerFeedTable, RackTable, LocationTable, SiteTable,
    VirtualChassisTable,
)
from ipam.filtersets import AggregateFilterSet, IPAddressFilterSet, PrefixFilterSet, VLANFilterSet, VRFFilterSet
from ipam.models import Aggregate, IPAddress, Prefix, VLAN, VRF
from ipam.tables import AggregateTable, IPAddressTable, PrefixTable, VLANTable, VRFTable
from secrets.filtersets import SecretFilterSet
from secrets.models import Secret
from secrets.tables import SecretTable
from tenancy.filtersets import TenantFilterSet
from tenancy.models import Tenant
from tenancy.tables import TenantTable
from utilities.utils import count_related
from virtualization.filtersets import ClusterFilterSet, VirtualMachineFilterSet
from virtualization.models import Cluster, VirtualMachine
from virtualization.tables import ClusterTable, VirtualMachineDetailTable

SEARCH_MAX_RESULTS = 15
SEARCH_TYPES = OrderedDict((
    # Circuits
    ('provider', {
        'queryset': Provider.objects.annotate(
            count_circuits=count_related(Circuit, 'provider')
        ),
        'filterset': ProviderFilterSet,
        'table': ProviderTable,
        'url': 'circuits:provider_list',
    }),
    ('circuit', {
        'queryset': Circuit.objects.prefetch_related(
            'type', 'provider', 'tenant', 'terminations__site'
        ),
        'filterset': CircuitFilterSet,
        'table': CircuitTable,
        'url': 'circuits:circuit_list',
    }),
    ('providernetwork', {
        'queryset': ProviderNetwork.objects.prefetch_related('provider'),
        'filterset': ProviderNetworkFilterSet,
        'table': ProviderNetworkTable,
        'url': 'circuits:providernetwork_list',
    }),
    # DCIM
    ('site', {
        'queryset': Site.objects.prefetch_related('region', 'tenant'),
        'filterset': SiteFilterSet,
        'table': SiteTable,
        'url': 'dcim:site_list',
    }),
    ('rack', {
        'queryset': Rack.objects.prefetch_related('site', 'location', 'tenant', 'role'),
        'filterset': RackFilterSet,
        'table': RackTable,
        'url': 'dcim:rack_list',
    }),
    ('location', {
        'queryset': Location.objects.add_related_count(
            Location.objects.all(),
            Rack,
            'location',
            'rack_count',
            cumulative=True
        ).prefetch_related('site'),
        'filterset': LocationFilterSet,
        'table': LocationTable,
        'url': 'dcim:location_list',
    }),
    ('devicetype', {
        'queryset': DeviceType.objects.prefetch_related('manufacturer').annotate(
            instance_count=count_related(Device, 'device_type')
        ),
        'filterset': DeviceTypeFilterSet,
        'table': DeviceTypeTable,
        'url': 'dcim:devicetype_list',
    }),
    ('device', {
        'queryset': Device.objects.prefetch_related(
            'device_type__manufacturer', 'device_role', 'tenant', 'site', 'rack', 'primary_ip4', 'primary_ip6',
        ),
        'filterset': DeviceFilterSet,
        'table': DeviceTable,
        'url': 'dcim:device_list',
    }),
    ('virtualchassis', {
        'queryset': VirtualChassis.objects.prefetch_related('master').annotate(
            member_count=count_related(Device, 'virtual_chassis')
        ),
        'filterset': VirtualChassisFilterSet,
        'table': VirtualChassisTable,
        'url': 'dcim:virtualchassis_list',
    }),
    ('cable', {
        'queryset': Cable.objects.all(),
        'filterset': CableFilterSet,
        'table': CableTable,
        'url': 'dcim:cable_list',
    }),
    ('powerfeed', {
        'queryset': PowerFeed.objects.all(),
        'filterset': PowerFeedFilterSet,
        'table': PowerFeedTable,
        'url': 'dcim:powerfeed_list',
    }),
    # Virtualization
    ('cluster', {
        'queryset': Cluster.objects.prefetch_related('type', 'group').annotate(
            device_count=count_related(Device, 'cluster'),
            vm_count=count_related(VirtualMachine, 'cluster')
        ),
        'filterset': ClusterFilterSet,
        'table': ClusterTable,
        'url': 'virtualization:cluster_list',
    }),
    ('virtualmachine', {
        'queryset': VirtualMachine.objects.prefetch_related(
            'cluster', 'tenant', 'platform', 'primary_ip4', 'primary_ip6',
        ),
        'filterset': VirtualMachineFilterSet,
        'table': VirtualMachineDetailTable,
        'url': 'virtualization:virtualmachine_list',
    }),
    # IPAM
    ('vrf', {
        'queryset': VRF.objects.prefetch_related('tenant'),
        'filterset': VRFFilterSet,
        'table': VRFTable,
        'url': 'ipam:vrf_list',
    }),
    ('aggregate', {
        'queryset': Aggregate.objects.prefetch_related('rir'),
        'filterset': AggregateFilterSet,
        'table': AggregateTable,
        'url': 'ipam:aggregate_list',
    }),
    ('prefix', {
        'queryset': Prefix.objects.prefetch_related('site', 'vrf__tenant', 'tenant', 'vlan', 'role'),
        'filterset': PrefixFilterSet,
        'table': PrefixTable,
        'url': 'ipam:prefix_list',
    }),
    ('ipaddress', {
        'queryset': IPAddress.objects.prefetch_related('vrf__tenant', 'tenant'),
        'filterset': IPAddressFilterSet,
        'table': IPAddressTable,
        'url': 'ipam:ipaddress_list',
    }),
    ('vlan', {
        'queryset': VLAN.objects.prefetch_related('site', 'group', 'tenant', 'role'),
        'filterset': VLANFilterSet,
        'table': VLANTable,
        'url': 'ipam:vlan_list',
    }),
    # Secrets
    ('secret', {
        'queryset': Secret.objects.prefetch_related('role', 'device'),
        'filterset': SecretFilterSet,
        'table': SecretTable,
        'url': 'secrets:secret_list',
    }),
    # Tenancy
    ('tenant', {
        'queryset': Tenant.objects.prefetch_related('group'),
        'filterset': TenantFilterSet,
        'table': TenantTable,
        'url': 'tenancy:tenant_list',
    }),
))
