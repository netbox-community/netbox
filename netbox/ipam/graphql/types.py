from typing import Annotated, List, Union

import strawberry
import strawberry_django

from circuits.graphql.types import ProviderType
from dcim.graphql.types import SiteType
from ipam import models
from netbox.graphql.scalars import BigInt
from netbox.graphql.types import BaseObjectType, NetBoxObjectType, OrganizationalObjectType
from .filters import *
from .mixins import IPAddressesMixin

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
    'VLANTranslationPolicyType',
    'VLANTranslationRuleType',
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
        return IPAddressFamilyType(value=self.family, label=f'IPv{self.family}')


@strawberry_django.type(
    models.ASN,
    fields='__all__',
    filters=ASNFilter
)
class ASNType(NetBoxObjectType):
    asn: BigInt
    rir: Annotated["RIRType", strawberry.lazy('ipam.graphql.types')] | None
    tenant: Annotated["TenantType", strawberry.lazy('tenancy.graphql.types')] | None

    sites: List[SiteType]
    providers: List[ProviderType]


@strawberry_django.type(
    models.ASNRange,
    fields='__all__',
    filters=ASNRangeFilter
)
class ASNRangeType(NetBoxObjectType):
    start: BigInt
    end: BigInt
    rir: Annotated["RIRType", strawberry.lazy('ipam.graphql.types')] | None
    tenant: Annotated["TenantType", strawberry.lazy('tenancy.graphql.types')] | None


@strawberry_django.type(
    models.Aggregate,
    fields='__all__',
    filters=AggregateFilter
)
class AggregateType(NetBoxObjectType, BaseIPAddressFamilyType):
    prefix: str
    rir: Annotated["RIRType", strawberry.lazy('ipam.graphql.types')] | None
    tenant: Annotated["TenantType", strawberry.lazy('tenancy.graphql.types')] | None


@strawberry_django.type(
    models.FHRPGroup,
    fields='__all__',
    filters=FHRPGroupFilter
)
class FHRPGroupType(NetBoxObjectType, IPAddressesMixin):

    fhrpgroupassignment_set: List[Annotated["FHRPGroupAssignmentType", strawberry.lazy('ipam.graphql.types')]]


@strawberry_django.type(
    models.FHRPGroupAssignment,
    exclude=('interface_type', 'interface_id'),
    filters=FHRPGroupAssignmentFilter
)
class FHRPGroupAssignmentType(BaseObjectType):
    group: Annotated["FHRPGroupType", strawberry.lazy('ipam.graphql.types')]

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
    vrf: Annotated["VRFType", strawberry.lazy('ipam.graphql.types')] | None
    tenant: Annotated["TenantType", strawberry.lazy('tenancy.graphql.types')] | None
    nat_inside: Annotated["IPAddressType", strawberry.lazy('ipam.graphql.types')] | None

    nat_outside: List[Annotated["IPAddressType", strawberry.lazy('ipam.graphql.types')]]
    tunnel_terminations: List[Annotated["TunnelTerminationType", strawberry.lazy('vpn.graphql.types')]]
    services: List[Annotated["ServiceType", strawberry.lazy('ipam.graphql.types')]]

    @strawberry_django.field
    def assigned_object(self) -> Annotated[Union[
        Annotated["InterfaceType", strawberry.lazy('dcim.graphql.types')],
        Annotated["FHRPGroupType", strawberry.lazy('ipam.graphql.types')],
        Annotated["VMInterfaceType", strawberry.lazy('virtualization.graphql.types')],
    ], strawberry.union("IPAddressAssignmentType")] | None:
        return self.assigned_object


@strawberry_django.type(
    models.IPRange,
    fields='__all__',
    filters=IPRangeFilter
)
class IPRangeType(NetBoxObjectType):
    start_address: str
    end_address: str
    vrf: Annotated["VRFType", strawberry.lazy('ipam.graphql.types')] | None
    tenant: Annotated["TenantType", strawberry.lazy('tenancy.graphql.types')] | None
    role: Annotated["RoleType", strawberry.lazy('ipam.graphql.types')] | None


@strawberry_django.type(
    models.Prefix,
    exclude=('scope_type', 'scope_id', '_location', '_region', '_site', '_site_group'),
    filters=PrefixFilter
)
class PrefixType(NetBoxObjectType, BaseIPAddressFamilyType):
    prefix: str
    vrf: Annotated["VRFType", strawberry.lazy('ipam.graphql.types')] | None
    tenant: Annotated["TenantType", strawberry.lazy('tenancy.graphql.types')] | None
    vlan: Annotated["VLANType", strawberry.lazy('ipam.graphql.types')] | None
    role: Annotated["RoleType", strawberry.lazy('ipam.graphql.types')] | None

    @strawberry_django.field
    def scope(self) -> Annotated[Union[
        Annotated["LocationType", strawberry.lazy('dcim.graphql.types')],
        Annotated["RegionType", strawberry.lazy('dcim.graphql.types')],
        Annotated["SiteGroupType", strawberry.lazy('dcim.graphql.types')],
        Annotated["SiteType", strawberry.lazy('dcim.graphql.types')],
    ], strawberry.union("PrefixScopeType")] | None:
        return self.scope


@strawberry_django.type(
    models.RIR,
    fields='__all__',
    filters=RIRFilter
)
class RIRType(OrganizationalObjectType):

    asn_ranges: List[Annotated["ASNRangeType", strawberry.lazy('ipam.graphql.types')]]
    asns: List[Annotated["ASNType", strawberry.lazy('ipam.graphql.types')]]
    aggregates: List[Annotated["AggregateType", strawberry.lazy('ipam.graphql.types')]]


@strawberry_django.type(
    models.Role,
    fields='__all__',
    filters=RoleFilter
)
class RoleType(OrganizationalObjectType):

    prefixes: List[Annotated["PrefixType", strawberry.lazy('ipam.graphql.types')]]
    ip_ranges: List[Annotated["IPRangeType", strawberry.lazy('ipam.graphql.types')]]
    vlans: List[Annotated["VLANType", strawberry.lazy('ipam.graphql.types')]]


@strawberry_django.type(
    models.RouteTarget,
    fields='__all__',
    filters=RouteTargetFilter
)
class RouteTargetType(NetBoxObjectType):
    tenant: Annotated["TenantType", strawberry.lazy('tenancy.graphql.types')] | None

    importing_l2vpns: List[Annotated["L2VPNType", strawberry.lazy('vpn.graphql.types')]]
    exporting_l2vpns: List[Annotated["L2VPNType", strawberry.lazy('vpn.graphql.types')]]
    importing_vrfs: List[Annotated["VRFType", strawberry.lazy('ipam.graphql.types')]]
    exporting_vrfs: List[Annotated["VRFType", strawberry.lazy('ipam.graphql.types')]]


@strawberry_django.type(
    models.Service,
    fields='__all__',
    filters=ServiceFilter
)
class ServiceType(NetBoxObjectType):
    ports: List[int]
    device: Annotated["DeviceType", strawberry.lazy('dcim.graphql.types')] | None
    virtual_machine: Annotated["VirtualMachineType", strawberry.lazy('virtualization.graphql.types')] | None

    ipaddresses: List[Annotated["IPAddressType", strawberry.lazy('ipam.graphql.types')]]


@strawberry_django.type(
    models.ServiceTemplate,
    fields='__all__',
    filters=ServiceTemplateFilter
)
class ServiceTemplateType(NetBoxObjectType):
    ports: List[int]


@strawberry_django.type(
    models.VLAN,
    exclude=('qinq_svlan',),
    filters=VLANFilter
)
class VLANType(NetBoxObjectType):
    site: Annotated["SiteType", strawberry.lazy('ipam.graphql.types')] | None
    group: Annotated["VLANGroupType", strawberry.lazy('ipam.graphql.types')] | None
    tenant: Annotated["TenantType", strawberry.lazy('tenancy.graphql.types')] | None
    role: Annotated["RoleType", strawberry.lazy('ipam.graphql.types')] | None

    interfaces_as_untagged: List[Annotated["InterfaceType", strawberry.lazy('dcim.graphql.types')]]
    vminterfaces_as_untagged: List[Annotated["VMInterfaceType", strawberry.lazy('virtualization.graphql.types')]]
    wirelesslan_set: List[Annotated["WirelessLANType", strawberry.lazy('wireless.graphql.types')]]
    prefixes: List[Annotated["PrefixType", strawberry.lazy('ipam.graphql.types')]]
    interfaces_as_tagged: List[Annotated["InterfaceType", strawberry.lazy('dcim.graphql.types')]]
    vminterfaces_as_tagged: List[Annotated["VMInterfaceType", strawberry.lazy('virtualization.graphql.types')]]

    @strawberry_django.field
    def qinq_svlan(self) -> Annotated["VLANType", strawberry.lazy('ipam.graphql.types')] | None:
        return self.qinq_svlan


@strawberry_django.type(
    models.VLANGroup,
    exclude=('scope_type', 'scope_id'),
    filters=VLANGroupFilter
)
class VLANGroupType(OrganizationalObjectType):

    vlans: List[VLANType]
    vid_ranges: List[str]

    @strawberry_django.field
    def scope(self) -> Annotated[Union[
        Annotated["ClusterType", strawberry.lazy('virtualization.graphql.types')],
        Annotated["ClusterGroupType", strawberry.lazy('virtualization.graphql.types')],
        Annotated["LocationType", strawberry.lazy('dcim.graphql.types')],
        Annotated["RackType", strawberry.lazy('dcim.graphql.types')],
        Annotated["RegionType", strawberry.lazy('dcim.graphql.types')],
        Annotated["SiteType", strawberry.lazy('dcim.graphql.types')],
        Annotated["SiteGroupType", strawberry.lazy('dcim.graphql.types')],
    ], strawberry.union("VLANGroupScopeType")] | None:
        return self.scope


@strawberry_django.type(
    models.VLANTranslationPolicy,
    fields='__all__',
    filters=VLANTranslationPolicyFilter
)
class VLANTranslationPolicyType(NetBoxObjectType):
    rules: List[Annotated["VLANTranslationRuleType", strawberry.lazy('ipam.graphql.types')]]


@strawberry_django.type(
    models.VLANTranslationRule,
    fields='__all__',
    filters=VLANTranslationRuleFilter
)
class VLANTranslationRuleType(NetBoxObjectType):
    policy: Annotated[
        "VLANTranslationPolicyType",
        strawberry.lazy('ipam.graphql.types')
    ] = strawberry_django.field(select_related=["policy"])


@strawberry_django.type(
    models.VRF,
    fields='__all__',
    filters=VRFFilter
)
class VRFType(NetBoxObjectType):
    tenant: Annotated["TenantType", strawberry.lazy('tenancy.graphql.types')] | None

    interfaces: List[Annotated["InterfaceType", strawberry.lazy('dcim.graphql.types')]]
    ip_addresses: List[Annotated["IPAddressType", strawberry.lazy('ipam.graphql.types')]]
    vminterfaces: List[Annotated["VMInterfaceType", strawberry.lazy('virtualization.graphql.types')]]
    ip_ranges: List[Annotated["IPRangeType", strawberry.lazy('ipam.graphql.types')]]
    export_targets: List[Annotated["RouteTargetType", strawberry.lazy('ipam.graphql.types')]]
    import_targets: List[Annotated["RouteTargetType", strawberry.lazy('ipam.graphql.types')]]
    prefixes: List[Annotated["PrefixType", strawberry.lazy('ipam.graphql.types')]]
