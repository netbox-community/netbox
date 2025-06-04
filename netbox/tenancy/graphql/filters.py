from typing import Annotated, TYPE_CHECKING

import strawberry
import strawberry_django
from strawberry.scalars import ID
from strawberry_django import FilterLookup

from core.graphql.filter_mixins import ChangeLogFilterMixin
from extras.graphql.filter_mixins import CustomFieldsFilterMixin, TagsFilterMixin
from netbox.graphql.filter_mixins import (
    NestedGroupModelFilterMixin,
    OrganizationalModelFilterMixin,
    PrimaryModelFilterMixin,
)
from tenancy import models
from .filter_mixins import ContactFilterMixin

if TYPE_CHECKING:
    from core.graphql.filters import ContentTypeFilter
    from circuits.graphql.filters import CircuitFilter, CircuitGroupFilter, VirtualCircuitFilter
    from dcim.graphql.filters import (
        CableFilter,
        DeviceFilter,
        LocationFilter,
        PowerFeedFilter,
        RackFilter,
        RackReservationFilter,
        SiteFilter,
        VirtualDeviceContextFilter,
    )
    from ipam.graphql.filters import (
        AggregateFilter,
        ASNFilter,
        ASNRangeFilter,
        IPAddressFilter,
        IPRangeFilter,
        PrefixFilter,
        RouteTargetFilter,
        VLANFilter,
        VLANGroupFilter,
        VRFFilter,
    )
    from netbox.graphql.filter_lookups import TreeNodeFilter
    from wireless.graphql.filters import WirelessLANFilter, WirelessLinkFilter
    from virtualization.graphql.filters import ClusterFilter, VirtualMachineFilter
    from vpn.graphql.filters import L2VPNFilter, TunnelFilter
    from .enums import *

__all__ = (
    'TenantFilter',
    'TenantGroupFilter',
    'ContactFilter',
    'ContactRoleFilter',
    'ContactGroupFilter',
    'ContactAssignmentFilter',
)


@strawberry_django.filter_type(models.Tenant, lookups=True)
class TenantFilter(PrimaryModelFilterMixin, ContactFilterMixin):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    slug: FilterLookup[str] | None = strawberry_django.filter_field()
    group: Annotated['TenantGroupFilter', strawberry.lazy('tenancy.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    group_id: Annotated['TreeNodeFilter', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )

    # Reverse relations
    aggregates: Annotated['AggregateFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    asns: Annotated['ASNFilter', strawberry.lazy('ipam.graphql.filters')] | None = strawberry_django.filter_field()
    asn_ranges: Annotated['ASNRangeFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    cables: Annotated['CableFilter', strawberry.lazy('dcim.graphql.filters')] | None = strawberry_django.filter_field()
    circuit_groups: Annotated['CircuitGroupFilter', strawberry.lazy('circuits.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    circuits: Annotated['CircuitFilter', strawberry.lazy('circuits.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    clusters: Annotated['ClusterFilter', strawberry.lazy('virtualization.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    devices: Annotated['DeviceFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    ip_addresses: Annotated['IPAddressFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    ip_ranges: Annotated['IPRangeFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    l2vpns: Annotated['L2VPNFilter', strawberry.lazy('vpn.graphql.filters')] | None = strawberry_django.filter_field()
    locations: Annotated['LocationFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    power_feeds: Annotated['PowerFeedFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    prefixes: Annotated['PrefixFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    racks: Annotated['RackFilter', strawberry.lazy('dcim.graphql.filters')] | None = strawberry_django.filter_field()
    rackreservations: Annotated['RackReservationFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    route_targets: Annotated['RouteTargetFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    sites: Annotated['SiteFilter', strawberry.lazy('dcim.graphql.filters')] | None = strawberry_django.filter_field()
    tunnels: Annotated['TunnelFilter', strawberry.lazy('vpn.graphql.filters')] | None = strawberry_django.filter_field()
    vdcs: Annotated['VirtualDeviceContextFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    virtual_machines: Annotated['VirtualMachineFilter', strawberry.lazy('virtualization.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    vlan_groups: Annotated['VLANGroupFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    vlans: Annotated['VLANFilter', strawberry.lazy('ipam.graphql.filters')] | None = strawberry_django.filter_field()
    virtual_circuits: Annotated['VirtualCircuitFilter', strawberry.lazy('circuits.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    vrfs: Annotated['VRFFilter', strawberry.lazy('ipam.graphql.filters')] | None = strawberry_django.filter_field()
    wireless_lans: Annotated['WirelessLANFilter', strawberry.lazy('wireless.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    wireless_links: Annotated['WirelessLinkFilter', strawberry.lazy('wireless.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.TenantGroup, lookups=True)
class TenantGroupFilter(OrganizationalModelFilterMixin):
    parent: Annotated['TenantGroupFilter', strawberry.lazy('tenancy.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    parent_id: ID | None = strawberry.UNSET
    tenants: Annotated['TenantFilter', strawberry.lazy('tenancy.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    children: Annotated['TenantGroupFilter', strawberry.lazy('tenancy.graphql.filters'), True] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.Contact, lookups=True)
class ContactFilter(PrimaryModelFilterMixin):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    title: FilterLookup[str] | None = strawberry_django.filter_field()
    phone: FilterLookup[str] | None = strawberry_django.filter_field()
    email: FilterLookup[str] | None = strawberry_django.filter_field()
    address: FilterLookup[str] | None = strawberry_django.filter_field()
    link: FilterLookup[str] | None = strawberry_django.filter_field()
    groups: Annotated['ContactGroupFilter', strawberry.lazy('tenancy.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    assignments: Annotated['ContactAssignmentFilter', strawberry.lazy('tenancy.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.ContactRole, lookups=True)
class ContactRoleFilter(OrganizationalModelFilterMixin):
    pass


@strawberry_django.filter_type(models.ContactGroup, lookups=True)
class ContactGroupFilter(NestedGroupModelFilterMixin):
    parent: Annotated['ContactGroupFilter', strawberry.lazy('tenancy.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.ContactAssignment, lookups=True)
class ContactAssignmentFilter(CustomFieldsFilterMixin, TagsFilterMixin, ChangeLogFilterMixin):
    object_type: Annotated['ContentTypeFilter', strawberry.lazy('core.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    object_id: ID | None = strawberry_django.filter_field()
    contact: Annotated['ContactFilter', strawberry.lazy('tenancy.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    contact_id: ID | None = strawberry_django.filter_field()
    role: Annotated['ContactRoleFilter', strawberry.lazy('tenancy.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    role_id: ID | None = strawberry_django.filter_field()
    priority: Annotated['ContactPriorityEnum', strawberry.lazy('tenancy.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
