from typing import TYPE_CHECKING, Annotated

import netaddr
import strawberry
import strawberry_django
from django.db.models import Q
from netaddr.core import AddrFormatError
from strawberry.scalars import ID
from strawberry_django import BaseFilterLookup, ComparisonFilterLookup, DateFilterLookup, FilterLookup, StrFilterLookup

from dcim.graphql.filter_mixins import ScopedFilterMixin
from dcim.models import Device
from ipam import models
from ipam.utils import normalize_port_mapping, port_mapping_q
from netbox.graphql.filters import (
    ChangeLoggedModelFilter,
    NetBoxModelFilter,
    OrganizationalModelFilter,
    PrimaryModelFilter,
    register_filter,
)
from tenancy.graphql.filter_mixins import ContactFilterMixin, TenancyFilterMixin
from virtualization.models import VMInterface

if TYPE_CHECKING:
    from circuits.graphql.filters import ProviderFilter
    from core.graphql.filters import ContentTypeFilter
    from dcim.graphql.filters import SiteFilter
    from netbox.graphql.filter_lookups import BigIntegerLookup, IntegerLookup, IntegerRangeArrayLookup
    from vpn.graphql.filters import L2VPNFilter

    from .enums import *

__all__ = (
    'ASNFilter',
    'ASNRangeFilter',
    'AggregateFilter',
    'FHRPGroupAssignmentFilter',
    'FHRPGroupFilter',
    'IPAddressFilter',
    'IPRangeFilter',
    'PrefixFilter',
    'RIRFilter',
    'RoleFilter',
    'RouteTargetFilter',
    'ServiceFilter',
    'ServiceTemplateFilter',
    'VLANFilter',
    'VLANGroupFilter',
    'VLANTranslationPolicyFilter',
    'VLANTranslationRuleFilter',
    'VRFFilter',
)


@register_filter(models.ASN, lookups=True)
class ASNFilter(TenancyFilterMixin, PrimaryModelFilter):
    rir: Annotated['RIRFilter', strawberry.lazy('ipam.graphql.filters')] | None = strawberry_django.filter_field()
    rir_id: ID | None = strawberry_django.filter_field()
    role: Annotated['RoleFilter', strawberry.lazy('ipam.graphql.filters')] | None = strawberry_django.filter_field()
    role_id: ID | None = strawberry_django.filter_field()
    asn: Annotated['BigIntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    sites: (
        Annotated['SiteFilter', strawberry.lazy('dcim.graphql.filters')] | None
    ) = strawberry_django.filter_field()
    providers: (
        Annotated['ProviderFilter', strawberry.lazy('circuits.graphql.filters')] | None
    ) = strawberry_django.filter_field()


@register_filter(models.ASNRange, lookups=True)
class ASNRangeFilter(TenancyFilterMixin, OrganizationalModelFilter):
    name: StrFilterLookup | None = strawberry_django.filter_field()
    slug: StrFilterLookup | None = strawberry_django.filter_field()
    rir: Annotated['RIRFilter', strawberry.lazy('ipam.graphql.filters')] | None = strawberry_django.filter_field()
    rir_id: ID | None = strawberry_django.filter_field()
    start: Annotated['BigIntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    end: Annotated['BigIntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )


@register_filter(models.Aggregate, lookups=True)
class AggregateFilter(ContactFilterMixin, TenancyFilterMixin, PrimaryModelFilter):
    prefix: StrFilterLookup | None = strawberry_django.filter_field()
    rir: Annotated['RIRFilter', strawberry.lazy('ipam.graphql.filters')] | None = strawberry_django.filter_field()
    rir_id: ID | None = strawberry_django.filter_field()
    date_added: DateFilterLookup | None = strawberry_django.filter_field()

    @strawberry_django.filter_field()
    def contains(self, value: list[str], prefix) -> Q:
        """
        Return aggregates whose `prefix` contains any of the supplied networks.
        Mirrors PrefixFilter.contains but operates on the Aggregate.prefix field itself.
        """
        if not value:
            return Q()
        q = Q()
        for subnet in value:
            try:
                query = str(netaddr.IPNetwork(subnet.strip()).cidr)
            except (AddrFormatError, ValueError):
                continue
            q |= Q(**{f"{prefix}prefix__net_contains": query})
        return q

    @strawberry_django.filter_field()
    def family(
        self,
        value: Annotated['IPAddressFamilyEnum', strawberry.lazy('ipam.graphql.enums')],
        prefix,
    ) -> Q:
        return Q(**{f"{prefix}prefix__family": value.value})


@register_filter(models.FHRPGroup, lookups=True)
class FHRPGroupFilter(PrimaryModelFilter):
    group_id: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    name: StrFilterLookup | None = strawberry_django.filter_field()
    protocol: BaseFilterLookup[Annotated['FHRPGroupProtocolEnum', strawberry.lazy('ipam.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )
    auth_type: BaseFilterLookup[Annotated['FHRPGroupAuthTypeEnum', strawberry.lazy('ipam.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )
    auth_key: StrFilterLookup | None = strawberry_django.filter_field()
    ip_addresses: Annotated['IPAddressFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )


@register_filter(models.FHRPGroupAssignment, lookups=True)
class FHRPGroupAssignmentFilter(ChangeLoggedModelFilter):
    interface_type: Annotated['ContentTypeFilter', strawberry.lazy('core.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    interface_id: StrFilterLookup | None = strawberry_django.filter_field()
    group: Annotated['FHRPGroupFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    group_id: ID | None = strawberry_django.filter_field()
    priority: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )

    @strawberry_django.filter_field()
    def device_id(self, value: list[str], prefix) -> Q:
        return self.filter_device('id', value, prefix)

    @strawberry_django.filter_field()
    def device(self, value: list[str], prefix) -> Q:
        return self.filter_device('name', value, prefix)

    @strawberry_django.filter_field()
    def virtual_machine_id(self, value: list[str], prefix) -> Q:
        return Q(**{f"{prefix}interface_id__in": VMInterface.objects.filter(virtual_machine_id__in=value)})

    @strawberry_django.filter_field()
    def virtual_machine(self, value: list[str], prefix) -> Q:
        return Q(**{f"{prefix}interface_id__in": VMInterface.objects.filter(virtual_machine__name__in=value)})

    def filter_device(self, field, value, prefix) -> Q:
        """Helper to standardize logic for device and device_id filters"""
        devices = Device.objects.filter(**{f'{field}__in': value})
        interface_ids = []
        for device in devices:
            interface_ids.extend(device.vc_interfaces().values_list('id', flat=True))
        return Q(**{f"{prefix}interface_id__in": interface_ids})


@register_filter(models.IPAddress, lookups=True)
class IPAddressFilter(ContactFilterMixin, TenancyFilterMixin, PrimaryModelFilter):
    address: StrFilterLookup | None = strawberry_django.filter_field()
    vrf: Annotated['VRFFilter', strawberry.lazy('ipam.graphql.filters')] | None = strawberry_django.filter_field()
    vrf_id: ID | None = strawberry_django.filter_field()
    status: BaseFilterLookup[Annotated['IPAddressStatusEnum', strawberry.lazy('ipam.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )
    role: BaseFilterLookup[Annotated['IPAddressRoleEnum', strawberry.lazy('ipam.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )
    assigned_object_type: Annotated['ContentTypeFilter', strawberry.lazy('core.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    assigned_object_id: ID | None = strawberry_django.filter_field()
    nat_inside: Annotated['IPAddressFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    nat_inside_id: ID | None = strawberry_django.filter_field()
    nat_outside: Annotated['IPAddressFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    nat_outside_id: ID | None = strawberry_django.filter_field()
    dns_name: StrFilterLookup | None = strawberry_django.filter_field()

    @strawberry_django.filter_field()
    def assigned(self, value: bool, prefix) -> Q:
        return Q(**{f"{prefix}assigned_object_id__isnull": not value})

    @strawberry_django.filter_field()
    def parent(self, value: list[str], prefix) -> Q:
        if not value:
            return Q()
        q = Q()
        for subnet in value:
            try:
                query = str(netaddr.IPNetwork(subnet.strip()).cidr)
            except (AddrFormatError, ValueError):
                continue
            q |= Q(**{f"{prefix}address__net_host_contained": query})
        return q

    @strawberry_django.filter_field()
    def family(
        self,
        value: Annotated['IPAddressFamilyEnum', strawberry.lazy('ipam.graphql.enums')],
        prefix,
    ) -> Q:
        return Q(**{f"{prefix}address__family": value.value})


@register_filter(models.IPRange, lookups=True)
class IPRangeFilter(ContactFilterMixin, TenancyFilterMixin, PrimaryModelFilter):
    start_address: StrFilterLookup | None = strawberry_django.filter_field()
    end_address: StrFilterLookup | None = strawberry_django.filter_field()
    size: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    vrf: Annotated['VRFFilter', strawberry.lazy('ipam.graphql.filters')] | None = strawberry_django.filter_field()
    vrf_id: ID | None = strawberry_django.filter_field()
    status: BaseFilterLookup[Annotated['IPRangeStatusEnum', strawberry.lazy('ipam.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )
    role: Annotated['RoleFilter', strawberry.lazy('ipam.graphql.filters')] | None = strawberry_django.filter_field()
    mark_utilized: FilterLookup[bool] | None = strawberry_django.filter_field()

    @strawberry_django.filter_field()
    def parent(self, value: list[str], prefix) -> Q:
        if not value:
            return Q()
        q = Q()
        for subnet in value:
            try:
                query = str(netaddr.IPNetwork(subnet.strip()).cidr)
            except (AddrFormatError, ValueError):
                continue
            q |= Q(
                **{
                    f"{prefix}start_address__net_host_contained": query,
                    f"{prefix}end_address__net_host_contained": query,
                }
            )
        return q

    @strawberry_django.filter_field()
    def contains(self, value: list[str], prefix) -> Q:
        if not value:
            return Q()
        q = Q()
        for subnet in value:
            try:
                net = netaddr.IPNetwork(subnet.strip())
                query_start = str(netaddr.IPAddress(net.first))
                query_end = str(netaddr.IPAddress(net.last))
            except (AddrFormatError, ValueError):
                continue
            q |= Q(
                **{
                    f"{prefix}start_address__host__inet__lte": query_start,
                    f"{prefix}end_address__host__inet__gte": query_end,
                }
            )
        return q


@register_filter(models.Prefix, lookups=True)
class PrefixFilter(ContactFilterMixin, ScopedFilterMixin, TenancyFilterMixin, PrimaryModelFilter):
    prefix: StrFilterLookup | None = strawberry_django.filter_field()
    vrf: Annotated['VRFFilter', strawberry.lazy('ipam.graphql.filters')] | None = strawberry_django.filter_field()
    vrf_id: ID | None = strawberry_django.filter_field()
    vlan: Annotated['VLANFilter', strawberry.lazy('ipam.graphql.filters')] | None = strawberry_django.filter_field()
    vlan_id: ID | None = strawberry_django.filter_field()
    status: BaseFilterLookup[Annotated['PrefixStatusEnum', strawberry.lazy('ipam.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )
    role: Annotated['RoleFilter', strawberry.lazy('ipam.graphql.filters')] | None = strawberry_django.filter_field()
    role_id: ID | None = strawberry_django.filter_field()
    is_pool: FilterLookup[bool] | None = strawberry_django.filter_field()
    mark_utilized: FilterLookup[bool] | None = strawberry_django.filter_field()

    @strawberry_django.filter_field()
    def contains(self, value: list[str], prefix) -> Q:
        if not value:
            return Q()
        q = Q()
        for subnet in value:
            try:
                query = str(netaddr.IPNetwork(subnet.strip()).cidr)
            except (AddrFormatError, ValueError):
                continue
            q |= Q(**{f"{prefix}prefix__net_contains": query})
        return q

    @strawberry_django.filter_field()
    def family(
        self,
        value: Annotated['IPAddressFamilyEnum', strawberry.lazy('ipam.graphql.enums')],
        prefix,
    ) -> Q:
        return Q(**{f"{prefix}prefix__family": value.value})


@register_filter(models.RIR, lookups=True)
class RIRFilter(OrganizationalModelFilter):
    is_private: FilterLookup[bool] | None = strawberry_django.filter_field()


@register_filter(models.Role, lookups=True)
class RoleFilter(OrganizationalModelFilter):
    weight: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )


@register_filter(models.RouteTarget, lookups=True)
class RouteTargetFilter(TenancyFilterMixin, PrimaryModelFilter):
    name: StrFilterLookup | None = strawberry_django.filter_field()
    importing_vrfs: Annotated['VRFFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    exporting_vrfs: Annotated['VRFFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    importing_l2vpns: Annotated['L2VPNFilter', strawberry.lazy('vpn.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    exporting_l2vpns: Annotated['L2VPNFilter', strawberry.lazy('vpn.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )


# Custom (method-based) GraphQL filters can't be inherited from a mixin — strawberry_django only picks
# up filter_field methods declared on the filter_type class itself — so the filters below keep thin
# wrappers here. Each method reads *all* of its siblings' values off ``self`` so a combined
# protocol/port query matches a single mapping rather than each condition independently.

# GraphQL port filter name -> the port lookup it applies, in the order the conditions are built. The
# names deliberately carry the same `port__gt` double-underscore form as their REST counterparts in
# ipam.filtersets.SERVICE_PORT_FILTERS, so both APIs offer an identically-spelled set of lookups.
# (GraphQL reserves only *leading* double underscores, for introspection.) The schema is built with
# auto_camel_case=False, so these names reach the schema verbatim.
# See ipam.utils.PORT_MAPPING_LOOKUPS for the lookup -> SQL operator mapping.
GRAPHQL_PORT_FILTERS = {
    'port': 'exact',
    'port__gt': 'gt',
    'port__gte': 'gte',
    'port__lt': 'lt',
    'port__lte': 'lte',
}

# `protocol` plus every port lookup, in the order their conditions are built. All of these must be
# satisfied by one single mapping, so they can't be applied as each resolver runs; the first one
# actually supplied owns the combined predicate (see _owns_predicate).
CORRELATED_PORT_FILTERS = ('protocol', *GRAPHQL_PORT_FILTERS)


def _supplied(filters, name):
    """
    Return the list of values supplied for a sibling filter field, or None if it was not supplied. Only
    a list is a real value: an omitted field is None/UNSET, and an unset method-based filter can resolve
    to the bound method itself, so anything non-list is reported as absent rather than surfacing as a
    TypeError downstream.
    """
    value = getattr(filters, name, None)
    return list(value) if isinstance(value, (list, tuple)) else None


def _port_mapping_args(filters):
    """
    Collect the correlated protocol/port arguments from every sibling field on the filter instance, in
    the ``(protocols, port_tests)`` shapes ``port_mapping_q()`` expects.
    """
    protocols = [v.value for v in _supplied(filters, 'protocol') or ()]
    port_tests = [
        (lookup, values)
        for name, lookup in GRAPHQL_PORT_FILTERS.items()
        if (values := _supplied(filters, name))
    ]
    return protocols, port_tests


def _owns_predicate(filters, name):
    """
    True for exactly one of the correlated filter fields: the first one supplied, in
    ``CORRELATED_PORT_FILTERS`` order. The others contribute nothing, so a query combining N of them
    builds the (deliberately sequential) scan once rather than ANDing N identical copies of it.
    """
    for candidate in CORRELATED_PORT_FILTERS:
        if _supplied(filters, candidate) is not None:
            return candidate == name
    return False


def _port_mapping_prefix_q(model, protocols, port_tests, prefix):
    qs_filter = port_mapping_q(protocols, port_tests)
    if prefix:
        # Nested relation (e.g. prefix='services__'): the incoming queryset is a *different* model, so
        # resolve the matching PKs on the target model and match them through the prefix.
        return Q(**{f'{prefix}pk__in': model.objects.filter(qs_filter).values('pk')})
    # Root query: the incoming queryset already targets this model, so return the lookup directly rather
    # than wrapping it in an extra pk__in self-subquery.
    return qs_filter


def _make_port_mapping_filters(model):
    # strawberry_django only collects filter_field methods declared on the filter_type class itself (not
    # from a mixin), so the Service/ServiceTemplate filters are produced by this factory and assigned
    # into each class body. This keeps the protocol/port correlation logic in a single place.

    def correlated(filters, name, prefix):
        # Deliberately ignores the resolver's own `value` in favour of reading every sibling off
        # `filters`: only the owning field applies the predicate, and it needs them all.
        if not _owns_predicate(filters, name):
            return Q()
        protocols, port_tests = _port_mapping_args(filters)
        return _port_mapping_prefix_q(model, protocols, port_tests, prefix)

    @strawberry_django.filter_field
    def protocol(
        self,
        queryset,
        value: list[Annotated['ServiceProtocolEnum', strawberry.lazy('ipam.graphql.enums')]],
        prefix,
    ):
        return correlated(self, 'protocol', prefix)

    # `port` and its range lookups. Values within one lookup are OR'd (as ?port=80&port=443 is on the
    # REST API); the lookups themselves are AND'd, and so must hold for one single mapping.
    @strawberry_django.filter_field
    def port(self, queryset, value: list[int], prefix):
        return correlated(self, 'port', prefix)

    @strawberry_django.filter_field
    def port__gt(self, queryset, value: list[int], prefix):
        return correlated(self, 'port__gt', prefix)

    @strawberry_django.filter_field
    def port__gte(self, queryset, value: list[int], prefix):
        return correlated(self, 'port__gte', prefix)

    @strawberry_django.filter_field
    def port__lt(self, queryset, value: list[int], prefix):
        return correlated(self, 'port__lt', prefix)

    @strawberry_django.filter_field
    def port__lte(self, queryset, value: list[int], prefix):
        return correlated(self, 'port__lte', prefix)

    @strawberry_django.filter_field
    def port_mappings(self, queryset, value: list[str], prefix):
        # Whole-mapping lookup (e.g. ["tcp/80", "udp/53"], matching any). Each value names one complete
        # protocol/port pair, so unlike protocol/port this needs no correlation and reduces to a
        # GIN-indexable array overlap. Values are normalized so 'TCP/080' finds the stored 'tcp/80'.
        mappings = [normalize_port_mapping(mapping) for mapping in value]
        return Q(**{f'{prefix}port_mappings__overlap': mappings})

    return protocol, port, port__gt, port__gte, port__lt, port__lte, port_mappings


@register_filter(models.Service, lookups=True)
class ServiceFilter(ContactFilterMixin, PrimaryModelFilter):
    name: StrFilterLookup | None = strawberry_django.filter_field()
    ip_addresses: Annotated['IPAddressFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    parent_object_type: Annotated['ContentTypeFilter', strawberry.lazy('core.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    parent_object_id: ID | None = strawberry_django.filter_field()
    protocol, port, port__gt, port__gte, port__lt, port__lte, port_mappings = (
        _make_port_mapping_filters(models.Service)
    )


@register_filter(models.ServiceTemplate, lookups=True)
class ServiceTemplateFilter(PrimaryModelFilter):
    name: StrFilterLookup | None = strawberry_django.filter_field()
    protocol, port, port__gt, port__gte, port__lt, port__lte, port_mappings = (
        _make_port_mapping_filters(models.ServiceTemplate)
    )


@register_filter(models.VLAN, lookups=True)
class VLANFilter(TenancyFilterMixin, PrimaryModelFilter):
    site: Annotated['SiteFilter', strawberry.lazy('dcim.graphql.filters')] | None = strawberry_django.filter_field()
    site_id: ID | None = strawberry_django.filter_field()
    group: Annotated['VLANGroupFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    group_id: ID | None = strawberry_django.filter_field()
    vid: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    name: StrFilterLookup | None = strawberry_django.filter_field()
    status: BaseFilterLookup[Annotated['VLANStatusEnum', strawberry.lazy('ipam.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )
    role: Annotated['RoleFilter', strawberry.lazy('ipam.graphql.filters')] | None = strawberry_django.filter_field()
    role_id: ID | None = strawberry_django.filter_field()
    qinq_svlan: Annotated['VLANFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    qinq_svlan_id: ID | None = strawberry_django.filter_field()
    qinq_cvlans: Annotated['VLANFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    qinq_role: BaseFilterLookup[Annotated['VLANQinQRoleEnum', strawberry.lazy('ipam.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )
    l2vpn_terminations: Annotated['L2VPNFilter', strawberry.lazy('vpn.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )


@register_filter(models.VLANGroup, lookups=True)
class VLANGroupFilter(ScopedFilterMixin, OrganizationalModelFilter):
    vid_ranges: Annotated['IntegerRangeArrayLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    total_vlan_ids: ComparisonFilterLookup[int] | None = strawberry_django.filter_field()


@register_filter(models.VLANTranslationPolicy, lookups=True)
class VLANTranslationPolicyFilter(PrimaryModelFilter):
    name: StrFilterLookup | None = strawberry_django.filter_field()


@register_filter(models.VLANTranslationRule, lookups=True)
class VLANTranslationRuleFilter(NetBoxModelFilter):
    policy: Annotated['VLANTranslationPolicyFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    policy_id: ID | None = strawberry_django.filter_field()
    description: StrFilterLookup | None = strawberry_django.filter_field()
    local_vid: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    remote_vid: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )


@register_filter(models.VRF, lookups=True)
class VRFFilter(TenancyFilterMixin, PrimaryModelFilter):
    name: StrFilterLookup | None = strawberry_django.filter_field()
    rd: StrFilterLookup | None = strawberry_django.filter_field()
    enforce_unique: FilterLookup[bool] | None = strawberry_django.filter_field()
    import_targets: Annotated['RouteTargetFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    export_targets: Annotated['RouteTargetFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
