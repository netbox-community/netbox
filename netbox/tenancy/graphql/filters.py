from typing import Annotated, TYPE_CHECKING
import strawberry
from strawberry.scalars import ID
import strawberry_django
from strawberry_django import (
    FilterLookup,
)
from netbox.graphql.filter_mixins import (
    PrimaryModelFilterMixin,
    OrganizationalModelFilterMixin,
    NestedGroupModelFilterMixin,
)
from extras.graphql.filter_mixins import CustomFieldsFilterMixin, TagsFilterMixin
from core.graphql.filter_mixins import ChangeLogFilterMixin
from tenancy import models
from .filter_mixins import ContactFilterMixin

if TYPE_CHECKING:
    from core.graphql.filter_lookups import TreeNodeFilter
    from circuits.graphql.filters import *
    from dcim.graphql.filters import *
    from ipam.graphql.filters import *
    from wireless.graphql.filters import *
    from virtualization.graphql.filters import *
    from vpn.graphql.filters import *

__all__ = (
    'TenantFilter',
    'TenantGroupFilter',
    'ContactFilter',
    'ContactRoleFilter',
    'ContactGroupFilter',
    'ContactAssignmentFilter',
)


@strawberry_django.filter(models.Tenant, lookups=True)
class TenantFilter(PrimaryModelFilterMixin, ContactFilterMixin):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    slug: FilterLookup[str] | None = strawberry_django.filter_field()
    group: Annotated['TenantGroupFilter', strawberry.lazy('tenancy.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    group_id: Annotated['TreeNodeFilter', strawberry.lazy('core.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    asns: Annotated['ASNFilter', strawberry.lazy('ipam.graphql.filters')] | None = strawberry_django.filter_field()
    circuits: Annotated['CircuitFilter', strawberry.lazy('circuits.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    sites: Annotated['SiteFilter', strawberry.lazy('dcim.graphql.filters')] | None = strawberry_django.filter_field()
    vlans: Annotated['VLANFilter', strawberry.lazy('ipam.graphql.filters')] | None = strawberry_django.filter_field()
    wireless_lans: Annotated['WirelessLANFilter', strawberry.lazy('wireless.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    route_targets: Annotated['RouteTargetFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    locations: Annotated['LocationFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    ip_ranges: Annotated['IPRangeFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    rackreservations: Annotated['RackReservationFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    racks: Annotated['RackFilter', strawberry.lazy('dcim.graphql.filters')] | None = strawberry_django.filter_field()
    vdcs: Annotated['VirtualDeviceContextFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    prefixes: Annotated['PrefixFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    cables: Annotated['CableFilter', strawberry.lazy('dcim.graphql.filters')] | None = strawberry_django.filter_field()
    virtual_machines: Annotated['VirtualMachineFilter', strawberry.lazy('virtualization.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    vrfs: Annotated['VRFFilter', strawberry.lazy('ipam.graphql.filters')] | None = strawberry_django.filter_field()
    asn_ranges: Annotated['ASNRangeFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    wireless_links: Annotated['WirelessLinkFilter', strawberry.lazy('wireless.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    aggregates: Annotated['AggregateFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    power_feeds: Annotated['PowerFeedFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    devices: Annotated['DeviceFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    tunnels: Annotated['TunnelFilter', strawberry.lazy('vpn.graphql.filters')] | None = strawberry_django.filter_field()
    ip_addresses: Annotated['IPAddressFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    clusters: Annotated['ClusterFilter', strawberry.lazy('virtualization.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    l2vpns: Annotated['L2VPNFilter', strawberry.lazy('vpn.graphql.filters')] | None = strawberry_django.filter_field()


@strawberry_django.filter(models.TenantGroup, lookups=True)
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


@strawberry_django.filter(models.Contact, lookups=True)
class ContactFilter(PrimaryModelFilterMixin):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    title: FilterLookup[str] | None = strawberry_django.filter_field()
    phone: FilterLookup[str] | None = strawberry_django.filter_field()
    email: FilterLookup[str] | None = strawberry_django.filter_field()
    address: FilterLookup[str] | None = strawberry_django.filter_field()
    link: FilterLookup[str] | None = strawberry_django.filter_field()
    group: Annotated['ContactGroupFilter', strawberry.lazy('tenancy.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    group_id: Annotated['TreeNodeFilter', strawberry.lazy('core.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    assignments: Annotated['ContactAssignmentFilter', strawberry.lazy('tenancy.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter(models.ContactRole, lookups=True)
class ContactRoleFilter(OrganizationalModelFilterMixin):
    pass


@strawberry_django.filter(models.ContactGroup, lookups=True)
class ContactGroupFilter(NestedGroupModelFilterMixin):
    parent: Annotated['ContactGroupFilter', strawberry.lazy('tenancy.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter(models.ContactAssignment, lookups=True)
class ContactAssignmentFilter(CustomFieldsFilterMixin, TagsFilterMixin, ChangeLogFilterMixin):
    object_id: ID | None = strawberry_django.filter_field()
    contact: Annotated['ContactFilter', strawberry.lazy('tenancy.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    contact_id: ID | None = strawberry_django.filter_field()
    role: Annotated['ContactRoleFilter', strawberry.lazy('tenancy.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    role_id: ID | None = strawberry_django.filter_field()
    priority: FilterLookup[str] | None = strawberry_django.filter_field()
