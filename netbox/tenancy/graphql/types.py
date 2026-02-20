from typing import TYPE_CHECKING, Annotated

import strawberry
import strawberry_django

from extras.graphql.mixins import ContactsMixin, CustomFieldsMixin, TagsMixin
from netbox.graphql.types import BaseObjectType, NestedGroupObjectType, OrganizationalObjectType, PrimaryObjectType
from tenancy import models

from .filters import *
from .mixins import ContactAssignmentsMixin

if TYPE_CHECKING:
    from circuits.graphql.types import CircuitType
    from dcim.graphql.types import (
        CableType,
        DeviceType,
        LocationType,
        PowerFeedType,
        RackReservationType,
        RackType,
        SiteType,
        VirtualDeviceContextType,
    )
    from ipam.graphql.types import (
        AggregateType,
        ASNRangeType,
        ASNType,
        IPAddressType,
        IPRangeType,
        PrefixType,
        RouteTargetType,
        VLANType,
        VRFType,
    )
    from netbox.graphql.types import ContentTypeType
    from virtualization.graphql.types import ClusterType, VirtualMachineType
    from vpn.graphql.types import L2VPNType, TunnelType
    from wireless.graphql.types import WirelessLANType, WirelessLinkType

__all__ = (
    'ContactAssignmentType',
    'ContactGroupType',
    'ContactRoleType',
    'ContactType',
    'TenantGroupType',
    'TenantType',
)


#
# Tenants
#

@strawberry_django.type(
    models.Tenant,
    fields='__all__',
    filters=TenantFilter,
    pagination=True
)
class TenantType(ContactsMixin, PrimaryObjectType):
    group: Annotated['TenantGroupType', strawberry.lazy('tenancy.graphql.types')] | None
    asns: list[Annotated['ASNType', strawberry.lazy('ipam.graphql.types')]]
    circuits: list[Annotated['CircuitType', strawberry.lazy('circuits.graphql.types')]]
    sites: list[Annotated['SiteType', strawberry.lazy('dcim.graphql.types')]]
    vlans: list[Annotated['VLANType', strawberry.lazy('ipam.graphql.types')]]
    wireless_lans: list[Annotated['WirelessLANType', strawberry.lazy('wireless.graphql.types')]]
    route_targets: list[Annotated['RouteTargetType', strawberry.lazy('ipam.graphql.types')]]
    locations: list[Annotated['LocationType', strawberry.lazy('dcim.graphql.types')]]
    ip_ranges: list[Annotated['IPRangeType', strawberry.lazy('ipam.graphql.types')]]
    rackreservations: list[Annotated['RackReservationType', strawberry.lazy('dcim.graphql.types')]]
    racks: list[Annotated['RackType', strawberry.lazy('dcim.graphql.types')]]
    vdcs: list[Annotated['VirtualDeviceContextType', strawberry.lazy('dcim.graphql.types')]]
    prefixes: list[Annotated['PrefixType', strawberry.lazy('ipam.graphql.types')]]
    cables: list[Annotated['CableType', strawberry.lazy('dcim.graphql.types')]]
    virtual_machines: list[Annotated['VirtualMachineType', strawberry.lazy('virtualization.graphql.types')]]
    vrfs: list[Annotated['VRFType', strawberry.lazy('ipam.graphql.types')]]
    asn_ranges: list[Annotated['ASNRangeType', strawberry.lazy('ipam.graphql.types')]]
    wireless_links: list[Annotated['WirelessLinkType', strawberry.lazy('wireless.graphql.types')]]
    aggregates: list[Annotated['AggregateType', strawberry.lazy('ipam.graphql.types')]]
    power_feeds: list[Annotated['PowerFeedType', strawberry.lazy('dcim.graphql.types')]]
    devices: list[Annotated['DeviceType', strawberry.lazy('dcim.graphql.types')]]
    tunnels: list[Annotated['TunnelType', strawberry.lazy('vpn.graphql.types')]]
    ip_addresses: list[Annotated['IPAddressType', strawberry.lazy('ipam.graphql.types')]]
    clusters: list[Annotated['ClusterType', strawberry.lazy('virtualization.graphql.types')]]
    l2vpns: list[Annotated['L2VPNType', strawberry.lazy('vpn.graphql.types')]]


@strawberry_django.type(
    models.TenantGroup,
    fields='__all__',
    filters=TenantGroupFilter,
    pagination=True
)
class TenantGroupType(NestedGroupObjectType):
    parent: Annotated['TenantGroupType', strawberry.lazy('tenancy.graphql.types')] | None

    tenants: list[TenantType]
    children: list[Annotated['TenantGroupType', strawberry.lazy('tenancy.graphql.types')]]


#
# Contacts
#

@strawberry_django.type(
    models.Contact,
    fields='__all__',
    filters=ContactFilter,
    pagination=True
)
class ContactType(ContactAssignmentsMixin, PrimaryObjectType):
    groups: list[Annotated['ContactGroupType', strawberry.lazy('tenancy.graphql.types')]]


@strawberry_django.type(
    models.ContactRole,
    fields='__all__',
    filters=ContactRoleFilter,
    pagination=True
)
class ContactRoleType(ContactAssignmentsMixin, OrganizationalObjectType):
    pass


@strawberry_django.type(
    models.ContactGroup,
    fields='__all__',
    filters=ContactGroupFilter,
    pagination=True
)
class ContactGroupType(NestedGroupObjectType):
    parent: Annotated['ContactGroupType', strawberry.lazy('tenancy.graphql.types')] | None

    contacts: list[ContactType]
    children: list[Annotated['ContactGroupType', strawberry.lazy('tenancy.graphql.types')]]


@strawberry_django.type(
    models.ContactAssignment,
    fields='__all__',
    filters=ContactAssignmentFilter,
    pagination=True
)
class ContactAssignmentType(CustomFieldsMixin, TagsMixin, BaseObjectType):
    object_type: Annotated['ContentTypeType', strawberry.lazy('netbox.graphql.types')] | None
    contact: Annotated['ContactType', strawberry.lazy('tenancy.graphql.types')] | None
    role: Annotated['ContactRoleType', strawberry.lazy('tenancy.graphql.types')] | None
