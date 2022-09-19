import dcim.filtersets
import dcim.tables
from django.db import models
from ipam.models import ASN, VLAN, VRF, Aggregate, IPAddress, Prefix, Service
from search.models import SearchMixin


class VRFIndex(SearchMixin):
    def __init__(self):
        self.model = VRF
        self.queryset = VRF.objects.prefetch_related('tenant', 'tenant__group')
        self.filterset = ipam.filtersets.VRFFilterSet
        self.table = ipam.tables.VRFTable
        self.url = 'ipam:vrf_list'


class AggregateIndex(SearchMixin):
    def __init__(self):
        self.model = Aggregate
        self.queryset = Aggregate.objects.prefetch_related('rir')
        self.filterset = ipam.filtersets.AggregateFilterSet
        self.table = ipam.tables.AggregateTable
        self.url = 'ipam:aggregate_list'


class PrefixIndex(SearchMixin):
    def __init__(self):
        self.model = Prefix
        self.queryset = Prefix.objects.prefetch_related(
            'site', 'vrf__tenant', 'tenant', 'tenant__group', 'vlan', 'role'
        )
        self.filterset = ipam.filtersets.PrefixFilterSet
        self.table = ipam.tables.PrefixTable
        self.url = 'ipam:prefix_list'


class IPAddressIndex(SearchMixin):
    def __init__(self):
        self.model = IPAddress
        self.queryset = IPAddress.objects.prefetch_related('vrf__tenant', 'tenant', 'tenant__group')
        self.filterset = ipam.filtersets.IPAddressFilterSet
        self.table = ipam.tables.IPAddressTable
        self.url = 'ipam:ipaddress_list'


class VLANIndex(SearchMixin):
    def __init__(self):
        self.model = VLAN
        self.queryset = VLAN.objects.prefetch_related('site', 'group', 'tenant', 'tenant__group', 'role')
        self.filterset = ipam.filtersets.VLANFilterSet
        self.table = ipam.tables.VLANTable
        self.url = 'ipam:vlan_list'


class ASNIndex(SearchMixin):
    def __init__(self):
        self.model = ASN
        self.queryset = ASN.objects.prefetch_related('rir', 'tenant', 'tenant__group')
        self.filterset = ipam.filtersets.ASNFilterSet
        self.table = ipam.tables.ASNTable
        self.url = 'ipam:asn_list'


class ServiceIndex(SearchMixin):
    def __init__(self):
        self.model = Service
        self.queryset = Service.objects.prefetch_related('device', 'virtual_machine')
        self.filterset = ipam.filtersets.ServiceFilterSet
        self.table = ipam.tables.ServiceTable
        self.url = 'ipam:service_list'


IPAM_SEARCH_TYPES = {
    'vrf': VRFIndex(),
    'aggregate': AggregateIndex(),
    'prefix': PrefixIndex(),
    'ipaddress': IPAddressIndex(),
    'vlan': VLANIndex(),
    'asn': ASNIndex(),
    'service': ServiceIndex(),
}
