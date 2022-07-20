import circuits.filtersets
import circuits.tables
import dcim.filtersets
import dcim.tables
import ipam.filtersets
import ipam.tables
import tenancy.filtersets
import tenancy.tables
import virtualization.filtersets
import wireless.tables
import wireless.filtersets
import virtualization.tables
from circuits.models import Circuit, ProviderNetwork, Provider
from dcim.models import (
    Cable, Device, DeviceType, Interface, Location, Module, ModuleType, PowerFeed, Rack, RackReservation, Site,
    VirtualChassis,
)
from ipam.models import Aggregate, ASN, IPAddress, Prefix, Service, VLAN, VRF
from tenancy.models import Contact, Tenant, ContactAssignment
from utilities.utils import count_related
from wireless.models import WirelessLAN, WirelessLink
from virtualization.models import Cluster, VirtualMachine

CIRCUIT_TYPES = {
    'provider': {
        'queryset': Provider.objects.annotate(
            count_circuits=count_related(Circuit, 'provider')
        ),
        'filterset': circuits.filtersets.ProviderFilterSet,
        'table': circuits.tables.ProviderTable,
        'url': 'circuits:provider_list',
    },
    'circuit': {
        'queryset': Circuit.objects.prefetch_related(
            'type', 'provider', 'tenant', 'tenant__group', 'terminations__site'
        ),
        'filterset': circuits.filtersets.CircuitFilterSet,
        'table': circuits.tables.CircuitTable,
        'url': 'circuits:circuit_list',
    },
    'providernetwork': {
        'queryset': ProviderNetwork.objects.prefetch_related('provider'),
        'filterset': circuits.filtersets.ProviderNetworkFilterSet,
        'table': circuits.tables.ProviderNetworkTable,
        'url': 'circuits:providernetwork_list',
    },
}

DCIM_TYPES = {
    'site': {
        'queryset': Site.objects.prefetch_related('region', 'tenant', 'tenant__group'),
        'filterset': dcim.filtersets.SiteFilterSet,
        'table': dcim.tables.SiteTable,
        'url': 'dcim:site_list',
    },
    'rack': {
        'queryset': Rack.objects.prefetch_related('site', 'location', 'tenant', 'tenant__group', 'role').annotate(
            device_count=count_related(Device, 'rack')
        ),
        'filterset': dcim.filtersets.RackFilterSet,
        'table': dcim.tables.RackTable,
        'url': 'dcim:rack_list',
    },
    'rackreservation': {
        'queryset': RackReservation.objects.prefetch_related('site', 'rack', 'user'),
        'filterset': dcim.filtersets.RackReservationFilterSet,
        'table': dcim.tables.RackReservationTable,
        'url': 'dcim:rackreservation_list',
    },
    'location': {
        'queryset': Location.objects.add_related_count(
            Location.objects.add_related_count(
                Location.objects.all(),
                Device,
                'location',
                'device_count',
                cumulative=True
            ),
            Rack,
            'location',
            'rack_count',
            cumulative=True
        ).prefetch_related('site'),
        'filterset': dcim.filtersets.LocationFilterSet,
        'table': dcim.tables.LocationTable,
        'url': 'dcim:location_list',
    },
    'devicetype': {
        'queryset': DeviceType.objects.prefetch_related('manufacturer').annotate(
            instance_count=count_related(Device, 'device_type')
        ),
        'filterset': dcim.filtersets.DeviceTypeFilterSet,
        'table': dcim.tables.DeviceTypeTable,
        'url': 'dcim:devicetype_list',
    },
    'device': {
        'queryset': Device.objects.prefetch_related(
            'device_type__manufacturer', 'device_role', 'tenant', 'tenant__group', 'site', 'rack', 'primary_ip4',
            'primary_ip6',
        ),
        'filterset': dcim.filtersets.DeviceFilterSet,
        'table': dcim.tables.DeviceTable,
        'url': 'dcim:device_list',
    },
    'moduletype': {
        'queryset': ModuleType.objects.prefetch_related('manufacturer').annotate(
            instance_count=count_related(Module, 'module_type')
        ),
        'filterset': dcim.filtersets.ModuleTypeFilterSet,
        'table': dcim.tables.ModuleTypeTable,
        'url': 'dcim:moduletype_list',
    },
    'module': {
        'queryset': Module.objects.prefetch_related(
            'module_type__manufacturer', 'device', 'module_bay',
        ),
        'filterset': dcim.filtersets.ModuleFilterSet,
        'table': dcim.tables.ModuleTable,
        'url': 'dcim:module_list',
    },
    'virtualchassis': {
        'queryset': VirtualChassis.objects.prefetch_related('master').annotate(
            member_count=count_related(Device, 'virtual_chassis')
        ),
        'filterset': dcim.filtersets.VirtualChassisFilterSet,
        'table': dcim.tables.VirtualChassisTable,
        'url': 'dcim:virtualchassis_list',
    },
    'cable': {
        'queryset': Cable.objects.all(),
        'filterset': dcim.filtersets.CableFilterSet,
        'table': dcim.tables.CableTable,
        'url': 'dcim:cable_list',
    },
    'powerfeed': {
        'queryset': PowerFeed.objects.all(),
        'filterset': dcim.filtersets.PowerFeedFilterSet,
        'table': dcim.tables.PowerFeedTable,
        'url': 'dcim:powerfeed_list',
    },
}

IPAM_TYPES = {
    'vrf': {
        'queryset': VRF.objects.prefetch_related('tenant', 'tenant__group'),
        'filterset': ipam.filtersets.VRFFilterSet,
        'table': ipam.tables.VRFTable,
        'url': 'ipam:vrf_list',
    },
    'aggregate': {
        'queryset': Aggregate.objects.prefetch_related('rir'),
        'filterset': ipam.filtersets.AggregateFilterSet,
        'table': ipam.tables.AggregateTable,
        'url': 'ipam:aggregate_list',
    },
    'prefix': {
        'queryset': Prefix.objects.prefetch_related('site', 'vrf__tenant', 'tenant', 'tenant__group', 'vlan', 'role'),
        'filterset': ipam.filtersets.PrefixFilterSet,
        'table': ipam.tables.PrefixTable,
        'url': 'ipam:prefix_list',
    },
    'ipaddress': {
        'queryset': IPAddress.objects.prefetch_related('vrf__tenant', 'tenant', 'tenant__group'),
        'filterset': ipam.filtersets.IPAddressFilterSet,
        'table': ipam.tables.IPAddressTable,
        'url': 'ipam:ipaddress_list',
    },
    'vlan': {
        'queryset': VLAN.objects.prefetch_related('site', 'group', 'tenant', 'tenant__group', 'role'),
        'filterset': ipam.filtersets.VLANFilterSet,
        'table': ipam.tables.VLANTable,
        'url': 'ipam:vlan_list',
    },
    'asn': {
        'queryset': ASN.objects.prefetch_related('rir', 'tenant', 'tenant__group'),
        'filterset': ipam.filtersets.ASNFilterSet,
        'table': ipam.tables.ASNTable,
        'url': 'ipam:asn_list',
    },
    'service': {
        'queryset': Service.objects.prefetch_related('device', 'virtual_machine'),
        'filterset': ipam.filtersets.ServiceFilterSet,
        'table': ipam.tables.ServiceTable,
        'url': 'ipam:service_list',
    },
}

TENANCY_TYPES = {
    'tenant': {
        'queryset': Tenant.objects.prefetch_related('group'),
        'filterset': tenancy.filtersets.TenantFilterSet,
        'table': tenancy.tables.TenantTable,
        'url': 'tenancy:tenant_list',
    },
    'contact': {
        'queryset': Contact.objects.prefetch_related('group', 'assignments').annotate(
            assignment_count=count_related(ContactAssignment, 'contact')),
        'filterset': tenancy.filtersets.ContactFilterSet,
        'table': tenancy.tables.ContactTable,
        'url': 'tenancy:contact_list',
    },
}

VIRTUALIZATION_TYPES = {
    'cluster': {
        'queryset': Cluster.objects.prefetch_related('type', 'group').annotate(
            device_count=count_related(Device, 'cluster'),
            vm_count=count_related(VirtualMachine, 'cluster')
        ),
        'filterset': virtualization.filtersets.ClusterFilterSet,
        'table': virtualization.tables.ClusterTable,
        'url': 'virtualization:cluster_list',
    },
    'virtualmachine': {
        'queryset': VirtualMachine.objects.prefetch_related(
            'cluster', 'tenant', 'tenant__group', 'platform', 'primary_ip4', 'primary_ip6',
        ),
        'filterset': virtualization.filtersets.VirtualMachineFilterSet,
        'table': virtualization.tables.VirtualMachineTable,
        'url': 'virtualization:virtualmachine_list',
    },
}

WIRELESS_TYPES = {
    'wirelesslan': {
        'queryset': WirelessLAN.objects.prefetch_related('group', 'vlan').annotate(
            interface_count=count_related(Interface, 'wireless_lans')
        ),
        'filterset': wireless.filtersets.WirelessLANFilterSet,
        'table': wireless.tables.WirelessLANTable,
        'url': 'wireless:wirelesslan_list',
    },
    'wirelesslink': {
        'queryset': WirelessLink.objects.prefetch_related('interface_a__device', 'interface_b__device'),
        'filterset': wireless.filtersets.WirelessLinkFilterSet,
        'table': wireless.tables.WirelessLinkTable,
        'url': 'wireless:wirelesslink_list',
    },
}

SEARCH_TYPE_HIERARCHY = {
    'Circuits': CIRCUIT_TYPES,
    'DCIM': DCIM_TYPES,
    'IPAM': IPAM_TYPES,
    'Tenancy': TENANCY_TYPES,
    'Virtualization': VIRTUALIZATION_TYPES,
    'Wireless': WIRELESS_TYPES,
}


def build_search_types():
    result = dict()

    for app_types in SEARCH_TYPE_HIERARCHY.values():
        for name, items in app_types.items():
            result[name] = items

    return result


SEARCH_TYPES = build_search_types()
