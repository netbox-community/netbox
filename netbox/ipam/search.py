from . import filtersets, models
from netbox.search import SearchIndex, register_search


@register_search()
class AggregateIndex(SearchIndex):
    model = models.Aggregate
    fields = (
        ('prefix', 100),
        ('description', 500),
        ('date_added', 2000),
    )
    queryset = models.Aggregate.objects.prefetch_related('rir')
    filterset = filtersets.AggregateFilterSet


@register_search()
class ASNIndex(SearchIndex):
    model = models.ASN
    fields = (
        ('asn', 100),
        ('description', 500),
    )
    queryset = models.ASN.objects.prefetch_related('rir', 'tenant', 'tenant__group')
    filterset = filtersets.ASNFilterSet


@register_search()
class FHRPGroupIndex(SearchIndex):
    model = models.FHRPGroup
    fields = (
        ('name', 100),
        ('group_id', 2000),
        ('description', 500),
    )


@register_search()
class IPAddressIndex(SearchIndex):
    model = models.IPAddress
    fields = (
        ('address', 100),
        ('dns_name', 300),
        ('description', 500),
    )
    queryset = models.IPAddress.objects.prefetch_related('vrf__tenant', 'tenant', 'tenant__group')
    filterset = filtersets.IPAddressFilterSet


@register_search()
class IPRangeIndex(SearchIndex):
    model = models.IPRange
    fields = (
        ('start_address', 100),
        ('end_address', 300),
        ('description', 500),
    )


@register_search()
class L2VPNIndex(SearchIndex):
    model = models.L2VPN
    fields = (
        ('name', 100),
        ('slug', 110),
        ('description', 500),
    )


@register_search()
class PrefixIndex(SearchIndex):
    model = models.Prefix
    fields = (
        ('prefix', 100),
        ('description', 500),
    )
    queryset = models.Prefix.objects.prefetch_related(
        'site', 'vrf__tenant', 'tenant', 'tenant__group', 'vlan', 'role'
    )
    filterset = filtersets.PrefixFilterSet


@register_search()
class RIRIndex(SearchIndex):
    model = models.RIR
    fields = (
        ('name', 100),
        ('slug', 110),
        ('description', 500),
    )


@register_search()
class RoleIndex(SearchIndex):
    model = models.Role
    fields = (
        ('name', 100),
        ('slug', 110),
        ('description', 500),
    )


@register_search()
class RouteTargetIndex(SearchIndex):
    model = models.RouteTarget
    fields = (
        ('name', 100),
        ('description', 500),
    )


@register_search()
class ServiceIndex(SearchIndex):
    model = models.Service
    fields = (
        ('name', 100),
        ('description', 500),
    )
    queryset = models.Service.objects.prefetch_related('device', 'virtual_machine')
    filterset = filtersets.ServiceFilterSet


@register_search()
class VLANIndex(SearchIndex):
    model = models.VLAN
    fields = (
        ('name', 100),
        ('vid', 100),
        ('description', 500),
    )
    queryset = models.VLAN.objects.prefetch_related('site', 'group', 'tenant', 'tenant__group', 'role')
    filterset = filtersets.VLANFilterSet


@register_search()
class VLANGroupIndex(SearchIndex):
    model = models.VLANGroup
    fields = (
        ('name', 100),
        ('slug', 110),
        ('description', 500),
        ('max_vid', 2000),
    )


@register_search()
class VRFIndex(SearchIndex):
    model = models.VRF
    fields = (
        ('name', 100),
        ('rd', 200),
        ('description', 500),
    )
    queryset = models.VRF.objects.prefetch_related('tenant', 'tenant__group')
    filterset = filtersets.VRFFilterSet
