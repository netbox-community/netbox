import ipam.filtersets
import ipam.tables
from ipam.models import ASN, VLAN, VRF, Aggregate, IPAddress, Prefix, Service
from netbox.search import SearchIndex, register_search


@register_search()
class VRFIndex(SearchIndex):
    model = VRF
    queryset = VRF.objects.prefetch_related('tenant', 'tenant__group')
    filterset = ipam.filtersets.VRFFilterSet
    table = ipam.tables.VRFTable
    url = 'ipam:vrf_list'


@register_search()
class AggregateIndex(SearchIndex):
    model = Aggregate
    queryset = Aggregate.objects.prefetch_related('rir')
    filterset = ipam.filtersets.AggregateFilterSet
    table = ipam.tables.AggregateTable
    url = 'ipam:aggregate_list'


@register_search()
class PrefixIndex(SearchIndex):
    model = Prefix
    queryset = Prefix.objects.prefetch_related(
        'site', 'vrf__tenant', 'tenant', 'tenant__group', 'vlan', 'role'
    )
    filterset = ipam.filtersets.PrefixFilterSet
    table = ipam.tables.PrefixTable
    url = 'ipam:prefix_list'


@register_search()
class IPAddressIndex(SearchIndex):
    model = IPAddress
    queryset = IPAddress.objects.prefetch_related('vrf__tenant', 'tenant', 'tenant__group')
    filterset = ipam.filtersets.IPAddressFilterSet
    table = ipam.tables.IPAddressTable
    url = 'ipam:ipaddress_list'


@register_search()
class VLANIndex(SearchIndex):
    model = VLAN
    queryset = VLAN.objects.prefetch_related('site', 'group', 'tenant', 'tenant__group', 'role')
    filterset = ipam.filtersets.VLANFilterSet
    table = ipam.tables.VLANTable
    url = 'ipam:vlan_list'


@register_search()
class ASNIndex(SearchIndex):
    model = ASN
    queryset = ASN.objects.prefetch_related('rir', 'tenant', 'tenant__group')
    filterset = ipam.filtersets.ASNFilterSet
    table = ipam.tables.ASNTable
    url = 'ipam:asn_list'


@register_search()
class ServiceIndex(SearchIndex):
    model = Service
    queryset = Service.objects.prefetch_related('device', 'virtual_machine')
    filterset = ipam.filtersets.ServiceFilterSet
    table = ipam.tables.ServiceTable
    url = 'ipam:service_list'
