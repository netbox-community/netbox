from netbox.search import SearchIndex, register_search
from . import models


@register_search
class AggregateIndex(SearchIndex):
    model = models.Aggregate
    fields = (
        ('prefix', 120),
        ('description', 500),
        ('date_added', 2000),
        ('comments', 5000),
    )
    display_attrs = ('rir', 'tenant', 'description')


@register_search
class ASNIndex(SearchIndex):
    model = models.ASN
    fields = (
        ('asn', 100),
        ('prefixed_name', 110),
        ('description', 500),
    )
    display_attrs = ('rir', 'tenant', 'description')


@register_search
class ASNRangeIndex(SearchIndex):
    model = models.ASNRange
    fields = (
        ('name', 100),
        ('description', 500),
    )
    display_attrs = ('rir', 'tenant', 'description')


@register_search
class FHRPGroupIndex(SearchIndex):
    model = models.FHRPGroup
    fields = (
        ('name', 100),
        ('group_id', 2000),
        ('description', 500),
        ('comments', 5000),
    )
    display_attrs = ('protocol', 'auth_type', 'description')


@register_search
class IPAddressIndex(SearchIndex):
    model = models.IPAddress
    fields = (
        ('address', 100),
        ('dns_name', 300),
        ('description', 500),
        ('comments', 5000),
    )
    display_attrs = ('vrf', 'tenant', 'status', 'role', 'description')


@register_search
class IPRangeIndex(SearchIndex):
    model = models.IPRange
    fields = (
        ('start_address', 100),
        ('end_address', 300),
        ('description', 500),
        ('comments', 5000),
    )
    display_attrs = ('vrf', 'tenant', 'status', 'role', 'description')


@register_search
class PrefixIndex(SearchIndex):
    model = models.Prefix
    fields = (
        ('prefix', 110),
        ('description', 500),
        ('comments', 5000),
    )
    display_attrs = ('site', 'vrf', 'tenant', 'vlan', 'status', 'role', 'description')


@register_search
class RIRIndex(SearchIndex):
    model = models.RIR
    fields = (
        ('name', 100),
        ('slug', 110),
        ('description', 500),
    )
    display_attrs = ('description',)


@register_search
class RoleIndex(SearchIndex):
    model = models.Role
    fields = (
        ('name', 100),
        ('slug', 110),
        ('description', 500),
    )
    display_attrs = ('description',)


@register_search
class RouteTargetIndex(SearchIndex):
    model = models.RouteTarget
    fields = (
        ('name', 100),
        ('description', 500),
        ('comments', 5000),
    )
    display_attrs = ('tenant', 'description')


@register_search
class ServiceIndex(SearchIndex):
    model = models.Service
    fields = (
        ('name', 100),
        ('description', 500),
        ('comments', 5000),
    )
    display_attrs = ('device', 'virtual_machine', 'description')


@register_search
class ServiceTemplateIndex(SearchIndex):
    model = models.ServiceTemplate
    fields = (
        ('name', 100),
        ('description', 500),
        ('comments', 5000),
    )
    display_attrs = ('description',)


@register_search
class VLANIndex(SearchIndex):
    model = models.VLAN
    fields = (
        ('name', 100),
        ('vid', 100),
        ('description', 500),
        ('comments', 5000),
    )
    display_attrs = ('site', 'group', 'tenant', 'status', 'role', 'description')


@register_search
class VLANGroupIndex(SearchIndex):
    model = models.VLANGroup
    fields = (
        ('name', 100),
        ('slug', 110),
        ('description', 500),
    )
    display_attrs = ('scope_type', 'description')


@register_search
class VRFIndex(SearchIndex):
    model = models.VRF
    fields = (
        ('name', 100),
        ('rd', 200),
        ('description', 500),
        ('comments', 5000),
    )
    display_attrs = ('rd', 'tenant', 'description')
