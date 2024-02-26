from typing import TYPE_CHECKING, Annotated, List, Union

import strawberry
import strawberry_django
from circuits.graphql.types import ProviderType
from dcim.graphql.types import SiteType
from ipam import models

from netbox.graphql.scalars import BigInt
from netbox.graphql.types import (
    BaseObjectType,
    NetBoxObjectType,
    OrganizationalObjectType,
)

from .filters import *

__all__ = (
    'ASNType',
    'ASNRangeType',
    'AggregateType',
    'FHRPGroupType',
    'FHRPGroupAssignmentType',
    'IPAddressType',
    'IPRangeType',
    'PrefixType',
    'RIRType',
    'RoleType',
    'RouteTargetType',
    'ServiceType',
    'ServiceTemplateType',
    'VLANType',
    'VLANGroupType',
    'VRFType',
)


@strawberry.type
class IPAddressFamilyType:
    value: int
    label: str


@strawberry.type
class BaseIPAddressFamilyType:
    """
    Base type for models that need to expose their IPAddress family type.
    """

    @strawberry.field
    def family(self) -> IPAddressFamilyType:
        # Note that self, is an instance of models.IPAddress
        # thus resolves to the address family value.
        return IPAddressFamilyType(value=self.value, label=f'IPv{self.value}')


@strawberry_django.type(
    models.ASN,
    fields='__all__',
    filters=ASNFilter
)
class ASNType(NetBoxObjectType):
    asn: BigInt

    @strawberry_django.field
    def sites(self) -> List[SiteType]:
        return self.sites.all()

    @strawberry_django.field
    def providers(self) -> List[ProviderType]:
        return self.providers.all()


@strawberry_django.type(
    models.ASNRange,
    fields='__all__',
    filters=ASNRangeFilter
)
class ASNRangeType(NetBoxObjectType):
    start: BigInt
    end: BigInt


@strawberry_django.type(
    models.Aggregate,
    fields='__all__',
    filters=AggregateFilter
)
class AggregateType(NetBoxObjectType, BaseIPAddressFamilyType):
    prefix: str


@strawberry_django.type(
    models.FHRPGroup,
    fields='__all__',
    filters=FHRPGroupFilter
)
class FHRPGroupType(NetBoxObjectType):

    @strawberry_django.field
    def fhrpgroupassignment_set(self) -> List[Annotated["FHRPGroupAssignmentType", strawberry.lazy('ipam.graphql.types')]]:
        return self.fhrpgroupassignment_set.all()


@strawberry_django.type(
    models.FHRPGroupAssignment,
    exclude=('interface_type', 'interface_id'),
    filters=FHRPGroupAssignmentFilter
)
class FHRPGroupAssignmentType(BaseObjectType):
    # interface = graphene.Field('ipam.graphql.gfk_mixins.FHRPGroupInterfaceType')

    @strawberry_django.field
    def interface(self) -> Annotated[Union[
        Annotated["InterfaceType", strawberry.lazy('dcim.graphql.types')],
        Annotated["VMInterfaceType", strawberry.lazy('virtualization.graphql.types')],
    ], strawberry.union("FHRPGroupInterfaceType")]:
        return self.interface


@strawberry_django.type(
    models.IPAddress,
    exclude=('assigned_object_type', 'assigned_object_id', 'address'),
    filters=IPAddressFilter
)
class IPAddressType(NetBoxObjectType, BaseIPAddressFamilyType):
    address: str

    @strawberry_django.field
    def nat_outside(self) -> Annotated["IPAddressType", strawberry.lazy('ipam.graphql.types')]:
        return self.nat_outside

    @strawberry_django.field
    def tunnel_terminations(self) -> List[Annotated["TunnelTerminationType", strawberry.lazy('vpn.graphql.types')]]:
        return self.tunnel_terminations.all()

    @strawberry_django.field
    def services(self) -> List[Annotated["ServiceType", strawberry.lazy('ipam.graphql.types')]]:
        return self.services.all()

    @strawberry_django.field
    def assigned_object(self) -> Annotated[Union[
        Annotated["InterfaceType", strawberry.lazy('dcim.graphql.types')],
        Annotated["FHRPGroupType", strawberry.lazy('ipam.graphql.types')],
        Annotated["VMInterfaceType", strawberry.lazy('virtualization.graphql.types')],
    ], strawberry.union("IPAddressAssignmentType")]:
        return self.assigned_object


@strawberry_django.type(
    models.IPRange,
    # fields='__all__',
    exclude=('start_address', 'end_address',),  # bug - temp
    filters=IPRangeFilter
)
class IPRangeType(NetBoxObjectType):
    start_address: str
    end_address: str


@strawberry_django.type(
    models.Prefix,
    # fields='__all__',
    exclude=('prefix',),  # bug - temp
    filters=PrefixFilter
)
class PrefixType(NetBoxObjectType, BaseIPAddressFamilyType):
    prefix: str


@strawberry_django.type(
    models.RIR,
    fields='__all__',
    filters=RIRFilter
)
class RIRType(OrganizationalObjectType):

    @strawberry_django.field
    def asn_ranges(self) -> List[Annotated["ASNRangeType", strawberry.lazy('ipam.graphql.types')]]:
        return self.asn_ranges.all()

    @strawberry_django.field
    def asns(self) -> List[Annotated["ASNType", strawberry.lazy('ipam.graphql.types')]]:
        return self.asns.all()

    @strawberry_django.field
    def aggregates(self) -> List[Annotated["AggregateType", strawberry.lazy('ipam.graphql.types')]]:
        return self.aggregates.all()


@strawberry_django.type(
    models.Role,
    fields='__all__',
    filters=RoleFilter
)
class RoleType(OrganizationalObjectType):

    @strawberry_django.field
    def prefixes(self) -> List[Annotated["PrefixType", strawberry.lazy('ipam.graphql.types')]]:
        return self.prefixes.all()

    @strawberry_django.field
    def ip_ranges(self) -> List[Annotated["IPRangeType", strawberry.lazy('ipam.graphql.types')]]:
        return self.ip_ranges.all()

    @strawberry_django.field
    def vlans(self) -> List[Annotated["VLANType", strawberry.lazy('ipam.graphql.types')]]:
        return self.vlans.all()


@strawberry_django.type(
    models.RouteTarget,
    fields='__all__',
    filters=RouteTargetFilter
)
class RouteTargetType(NetBoxObjectType):

    @strawberry_django.field
    def exporting_l2vpns(self) -> List[Annotated["L2VPNType", strawberry.lazy('vpn.graphql.types')]]:
        return self.exporting_l2vpns.all()

    @strawberry_django.field
    def exporting_vrfs(self) -> List[Annotated["VRFType", strawberry.lazy('ipam.graphql.types')]]:
        return self.exporting_vrfs.all()

    @strawberry_django.field
    def importing_vrfs(self) -> List[Annotated["VRFType", strawberry.lazy('ipam.graphql.types')]]:
        return self.importing_vrfs.all()

    @strawberry_django.field
    def importing_l2vpns(self) -> List[Annotated["L2VPNType", strawberry.lazy('vpn.graphql.types')]]:
        return self.importing_l2vpns.all()


@strawberry_django.type(
    models.Service,
    fields='__all__',
    filters=ServiceFilter
)
class ServiceType(NetBoxObjectType):
    ports: List[int]

    @strawberry_django.field
    def ipaddresses(self) -> List[Annotated["IPAddressType", strawberry.lazy('ipam.graphql.types')]]:
        return self.ipaddresses.all()


@strawberry_django.type(
    models.ServiceTemplate,
    fields='__all__',
    filters=ServiceTemplateFilter
)
class ServiceTemplateType(NetBoxObjectType):
    ports: List[int]


@strawberry_django.type(
    models.VLAN,
    fields='__all__',
    filters=VLANFilter
)
class VLANType(NetBoxObjectType):

    @strawberry_django.field
    def interfaces_as_untagged(self) -> List[Annotated["InterfaceType", strawberry.lazy('dcim.graphql.types')]]:
        return self.interfaces_as_untagged.all()

    @strawberry_django.field
    def vminterfaces_as_untagged(self) -> List[Annotated["VMInterfaceType", strawberry.lazy('virtualization.graphql.types')]]:
        return self.vminterfaces_as_untagged.all()

    @strawberry_django.field
    def wirelesslan_set(self) -> List[Annotated["WirelessLANType", strawberry.lazy('wireless.graphql.types')]]:
        return self.wirelesslan_set.all()

    @strawberry_django.field
    def prefixes(self) -> List[Annotated["PrefixType", strawberry.lazy('ipam.graphql.types')]]:
        return self.prefixes.all()

    @strawberry_django.field
    def interfaces_as_tagged(self) -> List[Annotated["InterfaceType", strawberry.lazy('dcim.graphql.types')]]:
        return self.interfaces_as_tagged.all()

    @strawberry_django.field
    def vminterfaces_as_tagged(self) -> List[Annotated["VMInterfaceType", strawberry.lazy('virtualization.graphql.types')]]:
        return self.vminterfaces_as_tagged.all()


@strawberry_django.type(
    models.VLANGroup,
    exclude=('scope_type', 'scope_id'),
    filters=VLANGroupFilter
)
class VLANGroupType(OrganizationalObjectType):

    @strawberry_django.field
    def vlans(self) -> List[VLANType]:
        return self.vlans.all()

    @strawberry_django.field
    def scope(self) -> Annotated[Union[
        Annotated["ClusterType", strawberry.lazy('virtualization.graphql.types')],
        Annotated["ClusterGroupType", strawberry.lazy('virtualization.graphql.types')],
        Annotated["LocationType", strawberry.lazy('dcim.graphql.types')],
        Annotated["RackType", strawberry.lazy('dcim.graphql.types')],
        Annotated["RegionType", strawberry.lazy('dcim.graphql.types')],
        Annotated["SiteType", strawberry.lazy('dcim.graphql.types')],
        Annotated["SiteGroupType", strawberry.lazy('dcim.graphql.types')],
    ], strawberry.union("VLANGroupScopeType")]:
        return self.scope


@strawberry_django.type(
    models.VRF,
    fields='__all__',
    filters=VRFFilter
)
class VRFType(NetBoxObjectType):

    @strawberry_django.field
    def interfaces(self) -> List[Annotated["InterfaceType", strawberry.lazy('dcim.graphql.types')]]:
        return self.interfaces.all()

    @strawberry_django.field
    def ip_addresses(self) -> List[Annotated["IPAddressType", strawberry.lazy('ipam.graphql.types')]]:
        return self.ip_addresses.all()

    @strawberry_django.field
    def vminterfaces(self) -> List[Annotated["VMInterfaceType", strawberry.lazy('virtualization.graphql.types')]]:
        return self.vminterfaces.all()

    @strawberry_django.field
    def ip_ranges(self) -> List[Annotated["IPRangeType", strawberry.lazy('ipam.graphql.types')]]:
        return self.ip_ranges.all()

    @strawberry_django.field
    def export_targets(self) -> List[Annotated["RouteTargetType", strawberry.lazy('ipam.graphql.types')]]:
        return self.export_targets.all()

    @strawberry_django.field
    def import_targets(self) -> List[Annotated["RouteTargetType", strawberry.lazy('ipam.graphql.types')]]:
        return self.import_targets.all()

    @strawberry_django.field
    def prefixes(self) -> List[Annotated["PrefixType", strawberry.lazy('ipam.graphql.types')]]:
        return self.prefixes.all()
