from typing import Annotated, List

import strawberry
import strawberry_django

from extras.graphql.mixins import CustomFieldsMixin, TagsMixin
from tenancy import models
from netbox.graphql.types import BaseObjectType, OrganizationalObjectType, NetBoxObjectType
from .filters import *

__all__ = (
    'ContactAssignmentType',
    'ContactGroupType',
    'ContactRoleType',
    'ContactType',
    'TenantType',
    'TenantGroupType',
)


class ContactAssignmentsMixin:
    # assignments = graphene.List('tenancy.graphql.types.ContactAssignmentType')

    def resolve_assignments(self, info):
        return self.assignments.restrict(info.context.user, 'view')


#
# Tenants
#

@strawberry_django.type(
    models.Tenant,
    fields='__all__',
    filters=TenantFilter
)
class TenantType(NetBoxObjectType):

    @strawberry_django.field
    def asns(self) -> List[Annotated["ASNType", strawberry.lazy('ipam.graphql.types')]]:
        return self.asns.all()

    @strawberry_django.field
    def circuits(self) -> List[Annotated["CircuitType", strawberry.lazy('circuits.graphql.types')]]:
        return self.circuits.all()

    @strawberry_django.field
    def sites(self) -> List[Annotated["SiteType", strawberry.lazy('dcim.graphql.types')]]:
        return self.sites.all()

    @strawberry_django.field
    def vlans(self) -> List[Annotated["VLANType", strawberry.lazy('ipam.graphql.types')]]:
        return self.vlans.all()

    @strawberry_django.field
    def wireless_lans(self) -> List[Annotated["WirelessLANType", strawberry.lazy('wireless.graphql.types')]]:
        return self.wireless_lans.all()

    @strawberry_django.field
    def route_targets(self) -> List[Annotated["RouteTargetType", strawberry.lazy('ipam.graphql.types')]]:
        return self.route_targets.all()

    @strawberry_django.field
    def locations(self) -> List[Annotated["LocationType", strawberry.lazy('dcim.graphql.types')]]:
        return self.locations.all()

    @strawberry_django.field
    def ip_ranges(self) -> List[Annotated["IPRangeType", strawberry.lazy('ipam.graphql.types')]]:
        return self.ip_ranges.all()

    @strawberry_django.field
    def rackreservations(self) -> List[Annotated["RackReservationType", strawberry.lazy('dcim.graphql.types')]]:
        return self.rackreservations.all()

    @strawberry_django.field
    def racks(self) -> List[Annotated["RackType", strawberry.lazy('dcim.graphql.types')]]:
        return self.racks.all()

    @strawberry_django.field
    def vdcs(self) -> List[Annotated["VirtualDeviceContextType", strawberry.lazy('dcim.graphql.types')]]:
        return self.vdcs.all()

    @strawberry_django.field
    def prefixes(self) -> List[Annotated["PrefixType", strawberry.lazy('ipam.graphql.types')]]:
        return self.prefixes.all()

    @strawberry_django.field
    def cables(self) -> List[Annotated["CableType", strawberry.lazy('dcim.graphql.types')]]:
        return self.cables.all()

    @strawberry_django.field
    def virtual_machines(self) -> List[Annotated["VirtualMachineType", strawberry.lazy('virtualization.graphql.types')]]:
        return self.virtual_machines.all()

    @strawberry_django.field
    def vrfs(self) -> List[Annotated["VRFType", strawberry.lazy('ipam.graphql.types')]]:
        return self.vrfs.all()

    @strawberry_django.field
    def asn_ranges(self) -> List[Annotated["ASNRangeType", strawberry.lazy('ipam.graphql.types')]]:
        return self.asn_ranges.all()

    @strawberry_django.field
    def wireless_links(self) -> List[Annotated["WirelessLinkType", strawberry.lazy('wireless.graphql.types')]]:
        return self.wireless_links.all()

    @strawberry_django.field
    def aggregates(self) -> List[Annotated["AggregateType", strawberry.lazy('ipam.graphql.types')]]:
        return self.aggregates.all()

    @strawberry_django.field
    def power_feeds(self) -> List[Annotated["PowerFeedType", strawberry.lazy('dcim.graphql.types')]]:
        return self.power_feeds.all()

    @strawberry_django.field
    def devices(self) -> List[Annotated["DeviceType", strawberry.lazy('dcim.graphql.types')]]:
        return self.devices.all()

    @strawberry_django.field
    def tunnels(self) -> List[Annotated["TunnelType", strawberry.lazy('vpn.graphql.types')]]:
        return self.tunnels.all()

    @strawberry_django.field
    def ip_addresses(self) -> List[Annotated["IPAddressType", strawberry.lazy('ipam.graphql.types')]]:
        return self.ip_addresses.all()

    @strawberry_django.field
    def clusters(self) -> List[Annotated["ClusterType", strawberry.lazy('virtualization.graphql.types')]]:
        return self.clusters.all()

    @strawberry_django.field
    def l2vpns(self) -> List[Annotated["L2VPNType", strawberry.lazy('vpn.graphql.types')]]:
        return self.l2vpns.all()


@strawberry_django.type(
    models.TenantGroup,
    # fields='__all__',
    exclude=('parent',),  # bug - temp
    filters=TenantGroupFilter
)
class TenantGroupType(OrganizationalObjectType):

    @strawberry_django.field
    def parent(self) -> Annotated["TenantGroupType", strawberry.lazy('tenancy.graphql.types')]:
        return self.parent

    @strawberry_django.field
    def tenants(self) -> List[TenantType]:
        return self.tenants.all()

    @strawberry_django.field
    def children(self) -> List[Annotated["TenantGroupType", strawberry.lazy('tenancy.graphql.types')]]:
        return self.children.all()


#
# Contacts
#

@strawberry_django.type(
    models.Contact,
    fields='__all__',
    filters=ContactFilter
)
class ContactType(ContactAssignmentsMixin, NetBoxObjectType):

    @strawberry_django.field
    def assignments(self) -> List[Annotated["ContactAssignmentType", strawberry.lazy('tenancy.graphql.types')]]:
        return self.assignments.all()


@strawberry_django.type(
    models.ContactRole,
    fields='__all__',
    filters=ContactRoleFilter
)
class ContactRoleType(ContactAssignmentsMixin, OrganizationalObjectType):

    @strawberry_django.field
    def assignments(self) -> List[Annotated["ContactAssignmentType", strawberry.lazy('tenancy.graphql.types')]]:
        return self.assignments.all()


@strawberry_django.type(
    models.ContactGroup,
    # fields='__all__',
    exclude=('parent',),  # bug - temp
    filters=ContactGroupFilter
)
class ContactGroupType(OrganizationalObjectType):

    @strawberry_django.field
    def parent(self) -> Annotated["ContactGroupType", strawberry.lazy('tenancy.graphql.types')]:
        return self.parent

    @strawberry_django.field
    def contacts(self) -> List[ContactType]:
        return self.clusters.all()

    @strawberry_django.field
    def children(self) -> List[Annotated["ContactGroupType", strawberry.lazy('tenancy.graphql.types')]]:
        return self.children.all()


@strawberry_django.type(
    models.ContactAssignment,
    fields='__all__',
    filters=ContactAssignmentFilter
)
class ContactAssignmentType(CustomFieldsMixin, TagsMixin, BaseObjectType):
    pass
