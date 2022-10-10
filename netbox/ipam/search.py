import ipam.filtersets
import ipam.tables
from ipam.models import ASN, VLAN, VRF, Aggregate, IPAddress, Prefix, Service
from netbox.search import SearchIndex, register_search


@register_search()
class AggregateIndex(SearchIndex):
    model = Aggregate
    fields = (
        ('prefix', 100),
        ('description', 500),
        ('date_added', 2000),
    )
    queryset = Aggregate.objects.prefetch_related('rir')
    filterset = ipam.filtersets.AggregateFilterSet


@register_search()
class ASNIndex(SearchIndex):
    model = ASN
    fields = (
        ('asn', 100),
        ('description', 500),
    )
    queryset = ASN.objects.prefetch_related('rir', 'tenant', 'tenant__group')
    filterset = ipam.filtersets.ASNFilterSet


@register_search()
class IPAddressIndex(SearchIndex):
    model = IPAddress
    fields = (
        ('address', 100),
        ('dns_name', 300),
        ('description', 500),
    )
    queryset = IPAddress.objects.prefetch_related('vrf__tenant', 'tenant', 'tenant__group')
    filterset = ipam.filtersets.IPAddressFilterSet


@register_search()
class PrefixIndex(SearchIndex):
    model = Prefix
    fields = (
        ('prefix', 100),
        ('description', 500),
    )
    queryset = Prefix.objects.prefetch_related(
        'site', 'vrf__tenant', 'tenant', 'tenant__group', 'vlan', 'role'
    )
    filterset = ipam.filtersets.PrefixFilterSet


@register_search()
class ServiceIndex(SearchIndex):
    model = Service
    fields = (
        ('name', 100),
        ('description', 500),
    )
    queryset = Service.objects.prefetch_related('device', 'virtual_machine')
    filterset = ipam.filtersets.ServiceFilterSet


@register_search()
class VLANIndex(SearchIndex):
    model = VLAN
    fields = (
        ('name', 100),
        ('vid', 100),
        ('description', 500),
    )
    queryset = VLAN.objects.prefetch_related('site', 'group', 'tenant', 'tenant__group', 'role')
    filterset = ipam.filtersets.VLANFilterSet


@register_search()
class VRFIndex(SearchIndex):
    model = VRF
    fields = (
        ('name', 100),
        ('rd', 200),
        ('description', 500),
    )
    queryset = VRF.objects.prefetch_related('tenant', 'tenant__group')
    filterset = ipam.filtersets.VRFFilterSet
