import ipam.filtersets
import ipam.tables
from django.db import models
from ipam.models import ASN, VLAN, VRF, Aggregate, IPAddress, Prefix, Service
from search.models import SearchMixin
from utilities.utils import count_related


class VRFIndex(SearchMixin):
    model = VRF
    queryset = VRF.objects.prefetch_related('tenant', 'tenant__group')
    filterset = ipam.filtersets.VRFFilterSet
    table = ipam.tables.VRFTable
    url = 'ipam:vrf_list'


class AggregateIndex(SearchMixin):
    model = Aggregate
    queryset = Aggregate.objects.prefetch_related('rir')
    filterset = ipam.filtersets.AggregateFilterSet
    table = ipam.tables.AggregateTable
    url = 'ipam:aggregate_list'


class PrefixIndex(SearchMixin):
    model = Prefix
    queryset = Prefix.objects.prefetch_related(
        'site', 'vrf__tenant', 'tenant', 'tenant__group', 'vlan', 'role'
    )
    filterset = ipam.filtersets.PrefixFilterSet
    table = ipam.tables.PrefixTable
    url = 'ipam:prefix_list'


class IPAddressIndex(SearchMixin):
    model = IPAddress
    queryset = IPAddress.objects.prefetch_related('vrf__tenant', 'tenant', 'tenant__group')
    filterset = ipam.filtersets.IPAddressFilterSet
    table = ipam.tables.IPAddressTable
    url = 'ipam:ipaddress_list'


class VLANIndex(SearchMixin):
    model = VLAN
    queryset = VLAN.objects.prefetch_related('site', 'group', 'tenant', 'tenant__group', 'role')
    filterset = ipam.filtersets.VLANFilterSet
    table = ipam.tables.VLANTable
    url = 'ipam:vlan_list'


class ASNIndex(SearchMixin):
    model = ASN
    queryset = ASN.objects.prefetch_related('rir', 'tenant', 'tenant__group')
    filterset = ipam.filtersets.ASNFilterSet
    table = ipam.tables.ASNTable
    url = 'ipam:asn_list'


class ServiceIndex(SearchMixin):
    model = Service
    queryset = Service.objects.prefetch_related('device', 'virtual_machine')
    filterset = ipam.filtersets.ServiceFilterSet
    table = ipam.tables.ServiceTable
    url = 'ipam:service_list'


IPAM_SEARCH_TYPES = {
    'vrf': VRFIndex(),
    'aggregate': AggregateIndex(),
    'prefix': PrefixIndex(),
    'ipaddress': IPAddressIndex(),
    'vlan': VLANIndex(),
    'asn': ASNIndex(),
    'service': ServiceIndex(),
}
