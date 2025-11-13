from typing import Annotated, TYPE_CHECKING

import strawberry
import strawberry_django
from strawberry.scalars import ID
from strawberry_django import FilterLookup

from core.graphql.filter_mixins_v1 import ChangeLogFilterMixinV1
from extras.graphql.filter_mixins_v1 import CustomFieldsFilterMixinV1, TagsFilterMixinV1
from netbox.graphql.filter_mixins_v1 import (
    NestedGroupModelFilterMixinV1,
    OrganizationalModelFilterMixinV1,
    PrimaryModelFilterMixinV1,
)
from tenancy import models
from .filter_mixins_v1 import ContactFilterMixinV1

if TYPE_CHECKING:
    from core.graphql.filters_v1 import ContentTypeFilterV1
    from circuits.graphql.filters_v1 import CircuitFilterV1, CircuitGroupFilterV1, VirtualCircuitFilterV1
    from dcim.graphql.filters_v1 import (
        CableFilterV1,
        DeviceFilterV1,
        LocationFilterV1,
        PowerFeedFilterV1,
        RackFilterV1,
        RackReservationFilterV1,
        SiteFilterV1,
        VirtualDeviceContextFilterV1,
    )
    from ipam.graphql.filters_v1 import (
        AggregateFilterV1,
        ASNFilterV1,
        ASNRangeFilterV1,
        IPAddressFilterV1,
        IPRangeFilterV1,
        PrefixFilterV1,
        RouteTargetFilterV1,
        VLANFilterV1,
        VLANGroupFilterV1,
        VRFFilterV1,
    )
    from netbox.graphql.filter_lookups import TreeNodeFilter
    from wireless.graphql.filters_v1 import WirelessLANFilterV1, WirelessLinkFilterV1
    from virtualization.graphql.filters_v1 import ClusterFilterV1, VirtualMachineFilterV1
    from vpn.graphql.filters_v1 import L2VPNFilterV1, TunnelFilterV1
    from .enums import *

__all__ = (
    'TenantFilterV1',
    'TenantGroupFilterV1',
    'ContactFilterV1',
    'ContactRoleFilterV1',
    'ContactGroupFilterV1',
    'ContactAssignmentFilterV1',
)


@strawberry_django.filter_type(models.Tenant, lookups=True)
class TenantFilterV1(PrimaryModelFilterMixinV1, ContactFilterMixinV1):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    slug: FilterLookup[str] | None = strawberry_django.filter_field()
    group: Annotated['TenantGroupFilterV1', strawberry.lazy('tenancy.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    group_id: Annotated['TreeNodeFilter', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )

    # Reverse relations
    aggregates: Annotated['AggregateFilterV1', strawberry.lazy('ipam.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    asns: Annotated['ASNFilterV1', strawberry.lazy('ipam.graphql.filters_v1')] | None = strawberry_django.filter_field()
    asn_ranges: Annotated['ASNRangeFilterV1', strawberry.lazy('ipam.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    cables: Annotated['CableFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    circuit_groups: Annotated['CircuitGroupFilterV1', strawberry.lazy('circuits.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    circuits: Annotated['CircuitFilterV1', strawberry.lazy('circuits.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    clusters: Annotated['ClusterFilterV1', strawberry.lazy('virtualization.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    devices: Annotated['DeviceFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    ip_addresses: Annotated['IPAddressFilterV1', strawberry.lazy('ipam.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    ip_ranges: Annotated['IPRangeFilterV1', strawberry.lazy('ipam.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    l2vpns: Annotated['L2VPNFilterV1', strawberry.lazy('vpn.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    locations: Annotated['LocationFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    power_feeds: Annotated['PowerFeedFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    prefixes: Annotated['PrefixFilterV1', strawberry.lazy('ipam.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    racks: Annotated['RackFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    rackreservations: Annotated['RackReservationFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    route_targets: Annotated['RouteTargetFilterV1', strawberry.lazy('ipam.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    sites: Annotated['SiteFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    tunnels: Annotated['TunnelFilterV1', strawberry.lazy('vpn.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    vdcs: Annotated['VirtualDeviceContextFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    virtual_machines: Annotated[
        'VirtualMachineFilterV1', strawberry.lazy('virtualization.graphql.filters_v1')
    ] | None = (
        strawberry_django.filter_field()
    )
    vlan_groups: Annotated['VLANGroupFilterV1', strawberry.lazy('ipam.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    vlans: Annotated['VLANFilterV1', strawberry.lazy('ipam.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    virtual_circuits: Annotated['VirtualCircuitFilterV1', strawberry.lazy('circuits.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    vrfs: Annotated['VRFFilterV1', strawberry.lazy('ipam.graphql.filters_v1')] | None = strawberry_django.filter_field()
    wireless_lans: Annotated['WirelessLANFilterV1', strawberry.lazy('wireless.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    wireless_links: Annotated['WirelessLinkFilterV1', strawberry.lazy('wireless.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.TenantGroup, lookups=True)
class TenantGroupFilterV1(OrganizationalModelFilterMixinV1):
    parent: Annotated['TenantGroupFilterV1', strawberry.lazy('tenancy.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    parent_id: ID | None = strawberry.UNSET
    tenants: Annotated['TenantFilterV1', strawberry.lazy('tenancy.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    children: Annotated['TenantGroupFilterV1', strawberry.lazy('tenancy.graphql.filters_v1'), True] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.Contact, lookups=True)
class ContactFilterV1(PrimaryModelFilterMixinV1):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    title: FilterLookup[str] | None = strawberry_django.filter_field()
    phone: FilterLookup[str] | None = strawberry_django.filter_field()
    email: FilterLookup[str] | None = strawberry_django.filter_field()
    address: FilterLookup[str] | None = strawberry_django.filter_field()
    link: FilterLookup[str] | None = strawberry_django.filter_field()
    groups: Annotated['ContactGroupFilterV1', strawberry.lazy('tenancy.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    assignments: Annotated['ContactAssignmentFilterV1', strawberry.lazy('tenancy.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.ContactRole, lookups=True)
class ContactRoleFilterV1(OrganizationalModelFilterMixinV1):
    pass


@strawberry_django.filter_type(models.ContactGroup, lookups=True)
class ContactGroupFilterV1(NestedGroupModelFilterMixinV1):
    parent: Annotated['ContactGroupFilterV1', strawberry.lazy('tenancy.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.ContactAssignment, lookups=True)
class ContactAssignmentFilterV1(CustomFieldsFilterMixinV1, TagsFilterMixinV1, ChangeLogFilterMixinV1):
    object_type: Annotated['ContentTypeFilterV1', strawberry.lazy('core.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    object_id: ID | None = strawberry_django.filter_field()
    contact: Annotated['ContactFilterV1', strawberry.lazy('tenancy.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    contact_id: ID | None = strawberry_django.filter_field()
    role: Annotated['ContactRoleFilterV1', strawberry.lazy('tenancy.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    role_id: ID | None = strawberry_django.filter_field()
    priority: Annotated['ContactPriorityEnum', strawberry.lazy('tenancy.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
