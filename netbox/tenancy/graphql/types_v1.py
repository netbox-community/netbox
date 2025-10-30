from typing import Annotated, List, TYPE_CHECKING

import strawberry
import strawberry_django

from extras.graphql.mixins_v1 import CustomFieldsMixinV1, TagsMixinV1, ContactsMixinV1
from netbox.graphql.types_v1 import (
    BaseObjectTypeV1, OrganizationalObjectTypeV1, PrimaryObjectTypeV1
)
from tenancy import models
from .filters_v1 import *
from .mixins_v1 import ContactAssignmentsMixinV1

if TYPE_CHECKING:
    from circuits.graphql.types_v1 import CircuitTypeV1
    from dcim.graphql.types_v1 import (
        CableTypeV1,
        DeviceTypeV1,
        LocationTypeV1,
        PowerFeedTypeV1,
        RackTypeV1,
        RackReservationTypeV1,
        SiteTypeV1,
        VirtualDeviceContextTypeV1,
    )
    from ipam.graphql.types_v1 import (
        AggregateTypeV1,
        ASNTypeV1,
        ASNRangeTypeV1,
        IPAddressTypeV1,
        IPRangeTypeV1,
        PrefixTypeV1,
        RouteTargetTypeV1,
        VLANTypeV1,
        VRFTypeV1,
    )
    from netbox.graphql.types_v1 import ContentTypeTypeV1
    from wireless.graphql.types_v1 import WirelessLANTypeV1, WirelessLinkTypeV1
    from virtualization.graphql.types_v1 import ClusterTypeV1, VirtualMachineTypeV1
    from vpn.graphql.types_v1 import L2VPNTypeV1, TunnelTypeV1

__all__ = (
    'ContactAssignmentTypeV1',
    'ContactGroupTypeV1',
    'ContactRoleTypeV1',
    'ContactTypeV1',
    'TenantTypeV1',
    'TenantGroupTypeV1',
)


#
# Tenants
#

@strawberry_django.type(
    models.Tenant,
    fields='__all__',
    filters=TenantFilterV1,
    pagination=True
)
class TenantTypeV1(ContactsMixinV1, PrimaryObjectTypeV1):
    group: Annotated['TenantGroupTypeV1', strawberry.lazy('tenancy.graphql.types_v1')] | None
    asns: List[Annotated['ASNTypeV1', strawberry.lazy('ipam.graphql.types_v1')]]
    circuits: List[Annotated['CircuitTypeV1', strawberry.lazy('circuits.graphql.types_v1')]]
    sites: List[Annotated['SiteTypeV1', strawberry.lazy('dcim.graphql.types_v1')]]
    vlans: List[Annotated['VLANTypeV1', strawberry.lazy('ipam.graphql.types_v1')]]
    wireless_lans: List[Annotated['WirelessLANTypeV1', strawberry.lazy('wireless.graphql.types_v1')]]
    route_targets: List[Annotated['RouteTargetTypeV1', strawberry.lazy('ipam.graphql.types_v1')]]
    locations: List[Annotated['LocationTypeV1', strawberry.lazy('dcim.graphql.types_v1')]]
    ip_ranges: List[Annotated['IPRangeTypeV1', strawberry.lazy('ipam.graphql.types_v1')]]
    rackreservations: List[Annotated['RackReservationTypeV1', strawberry.lazy('dcim.graphql.types_v1')]]
    racks: List[Annotated['RackTypeV1', strawberry.lazy('dcim.graphql.types_v1')]]
    vdcs: List[Annotated['VirtualDeviceContextTypeV1', strawberry.lazy('dcim.graphql.types_v1')]]
    prefixes: List[Annotated['PrefixTypeV1', strawberry.lazy('ipam.graphql.types_v1')]]
    cables: List[Annotated['CableTypeV1', strawberry.lazy('dcim.graphql.types_v1')]]
    virtual_machines: List[Annotated['VirtualMachineTypeV1', strawberry.lazy('virtualization.graphql.types_v1')]]
    vrfs: List[Annotated['VRFTypeV1', strawberry.lazy('ipam.graphql.types_v1')]]
    asn_ranges: List[Annotated['ASNRangeTypeV1', strawberry.lazy('ipam.graphql.types_v1')]]
    wireless_links: List[Annotated['WirelessLinkTypeV1', strawberry.lazy('wireless.graphql.types_v1')]]
    aggregates: List[Annotated['AggregateTypeV1', strawberry.lazy('ipam.graphql.types_v1')]]
    power_feeds: List[Annotated['PowerFeedTypeV1', strawberry.lazy('dcim.graphql.types_v1')]]
    devices: List[Annotated['DeviceTypeV1', strawberry.lazy('dcim.graphql.types_v1')]]
    tunnels: List[Annotated['TunnelTypeV1', strawberry.lazy('vpn.graphql.types_v1')]]
    ip_addresses: List[Annotated['IPAddressTypeV1', strawberry.lazy('ipam.graphql.types_v1')]]
    clusters: List[Annotated['ClusterTypeV1', strawberry.lazy('virtualization.graphql.types_v1')]]
    l2vpns: List[Annotated['L2VPNTypeV1', strawberry.lazy('vpn.graphql.types_v1')]]


@strawberry_django.type(
    models.TenantGroup,
    fields='__all__',
    filters=TenantGroupFilterV1,
    pagination=True
)
class TenantGroupTypeV1(OrganizationalObjectTypeV1):
    parent: Annotated['TenantGroupTypeV1', strawberry.lazy('tenancy.graphql.types_v1')] | None

    tenants: List[TenantTypeV1]
    children: List[Annotated['TenantGroupTypeV1', strawberry.lazy('tenancy.graphql.types_v1')]]


#
# Contacts
#

@strawberry_django.type(
    models.Contact,
    fields='__all__',
    filters=ContactFilterV1,
    pagination=True
)
class ContactTypeV1(ContactAssignmentsMixinV1, PrimaryObjectTypeV1):
    groups: List[Annotated['ContactGroupTypeV1', strawberry.lazy('tenancy.graphql.types_v1')]]


@strawberry_django.type(
    models.ContactRole,
    fields='__all__',
    filters=ContactRoleFilterV1,
    pagination=True
)
class ContactRoleTypeV1(ContactAssignmentsMixinV1, OrganizationalObjectTypeV1):
    pass


@strawberry_django.type(
    models.ContactGroup,
    fields='__all__',
    filters=ContactGroupFilterV1,
    pagination=True
)
class ContactGroupTypeV1(OrganizationalObjectTypeV1):
    parent: Annotated['ContactGroupTypeV1', strawberry.lazy('tenancy.graphql.types_v1')] | None

    contacts: List[ContactTypeV1]
    children: List[Annotated['ContactGroupTypeV1', strawberry.lazy('tenancy.graphql.types_v1')]]


@strawberry_django.type(
    models.ContactAssignment,
    fields='__all__',
    filters=ContactAssignmentFilterV1,
    pagination=True
)
class ContactAssignmentTypeV1(CustomFieldsMixinV1, TagsMixinV1, BaseObjectTypeV1):
    object_type: Annotated['ContentTypeTypeV1', strawberry.lazy('netbox.graphql.types_v1')] | None
    contact: Annotated['ContactTypeV1', strawberry.lazy('tenancy.graphql.types_v1')] | None
    role: Annotated['ContactRoleTypeV1', strawberry.lazy('tenancy.graphql.types_v1')] | None
