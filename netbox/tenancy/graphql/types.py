from typing import Annotated, List

import strawberry
import strawberry_django

from extras.graphql.mixins import CustomFieldsMixin, TagsMixin
from netbox.graphql.types import BaseObjectType, OrganizationalObjectType, NetBoxObjectType
from tenancy import models
from .mixins import ContactAssignmentsMixin
from .filters import *

__all__ = (
    'ContactAssignmentType',
    'ContactGroupType',
    'ContactRoleType',
    'ContactType',
    'TenantType',
    'TenantGroupType',
)


#
# Tenants
#

@strawberry_django.type(
    models.Tenant,
    fields='__all__',
    filters=TenantFilter
)
class TenantType(NetBoxObjectType):
    group: Annotated["TenantGroupType", strawberry.lazy('tenancy.graphql.types')] | None

    asns: List[Annotated["ASNType", strawberry.lazy('ipam.graphql.types')]]
    circuits: List[Annotated["CircuitType", strawberry.lazy('circuits.graphql.types')]]
    sites: List[Annotated["SiteType", strawberry.lazy('dcim.graphql.types')]]
    vlans: List[Annotated["VLANType", strawberry.lazy('ipam.graphql.types')]]
    wireless_lans: List[Annotated["WirelessLANType", strawberry.lazy('wireless.graphql.types')]]
    route_targets: List[Annotated["RouteTargetType", strawberry.lazy('ipam.graphql.types')]]
    locations: List[Annotated["LocationType", strawberry.lazy('dcim.graphql.types')]]
    ip_ranges: List[Annotated["IPRangeType", strawberry.lazy('ipam.graphql.types')]]
    rackreservations: List[Annotated["RackReservationType", strawberry.lazy('dcim.graphql.types')]]
    racks: List[Annotated["RackType", strawberry.lazy('dcim.graphql.types')]]
    vdcs: List[Annotated["VirtualDeviceContextType", strawberry.lazy('dcim.graphql.types')]]
    prefixes: List[Annotated["PrefixType", strawberry.lazy('ipam.graphql.types')]]
    cables: List[Annotated["CableType", strawberry.lazy('dcim.graphql.types')]]
    virtual_machines: List[Annotated["VirtualMachineType", strawberry.lazy('virtualization.graphql.types')]]
    vrfs: List[Annotated["VRFType", strawberry.lazy('ipam.graphql.types')]]
    asn_ranges: List[Annotated["ASNRangeType", strawberry.lazy('ipam.graphql.types')]]
    wireless_links: List[Annotated["WirelessLinkType", strawberry.lazy('wireless.graphql.types')]]
    aggregates: List[Annotated["AggregateType", strawberry.lazy('ipam.graphql.types')]]
    power_feeds: List[Annotated["PowerFeedType", strawberry.lazy('dcim.graphql.types')]]
    devices: List[Annotated["DeviceType", strawberry.lazy('dcim.graphql.types')]]
    tunnels: List[Annotated["TunnelType", strawberry.lazy('vpn.graphql.types')]]
    ip_addresses: List[Annotated["IPAddressType", strawberry.lazy('ipam.graphql.types')]]
    clusters: List[Annotated["ClusterType", strawberry.lazy('virtualization.graphql.types')]]
    l2vpns: List[Annotated["L2VPNType", strawberry.lazy('vpn.graphql.types')]]


@strawberry_django.type(
    models.TenantGroup,
    fields='__all__',
    filters=TenantGroupFilter
)
class TenantGroupType(OrganizationalObjectType):
    parent: Annotated["TenantGroupType", strawberry.lazy('tenancy.graphql.types')] | None

    tenants: List[TenantType]
    children: List[Annotated["TenantGroupType", strawberry.lazy('tenancy.graphql.types')]]


#
# Contacts
#

@strawberry_django.type(
    models.Contact,
    fields='__all__',
    filters=ContactFilter
)
class ContactType(ContactAssignmentsMixin, NetBoxObjectType):
    group: Annotated["ContactGroupType", strawberry.lazy('tenancy.graphql.types')] | None


@strawberry_django.type(
    models.ContactRole,
    fields='__all__',
    filters=ContactRoleFilter
)
class ContactRoleType(ContactAssignmentsMixin, OrganizationalObjectType):
    pass


@strawberry_django.type(
    models.ContactGroup,
    fields='__all__',
    filters=ContactGroupFilter
)
class ContactGroupType(OrganizationalObjectType):
    parent: Annotated["ContactGroupType", strawberry.lazy('tenancy.graphql.types')] | None

    contacts: List[ContactType]
    children: List[Annotated["ContactGroupType", strawberry.lazy('tenancy.graphql.types')]]


@strawberry_django.type(
    models.ContactAssignment,
    fields='__all__',
    filters=ContactAssignmentFilter
)
class ContactAssignmentType(CustomFieldsMixin, TagsMixin, BaseObjectType):
    object_type: Annotated["ContentTypeType", strawberry.lazy('netbox.graphql.types')] | None
    contact: Annotated["ContactType", strawberry.lazy('tenancy.graphql.types')] | None
    role: Annotated["ContactRoleType", strawberry.lazy('tenancy.graphql.types')] | None
