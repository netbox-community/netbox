from typing import TYPE_CHECKING, Annotated

import strawberry
import strawberry_django

from circuits.graphql.types import ProviderType
from dcim.graphql.types import SiteType
from extras.graphql.mixins import ContactsMixin
from ipam import models
from netbox.graphql.scalars import BigInt
from netbox.graphql.types import BaseObjectType, NetBoxObjectType, OrganizationalObjectType, PrimaryObjectType

from .filters import *
from .mixins import IPAddressesMixin

if TYPE_CHECKING:
    from dcim.graphql.types import (
        DeviceType,
        InterfaceType,
        LocationType,
        RackType,
        RegionType,
        SiteGroupType,
    )
    from tenancy.graphql.types import TenantType
    from virtualization.graphql.types import ClusterGroupType, ClusterType, VirtualMachineType, VMInterfaceType
    from vpn.graphql.types import L2VPNType, TunnelTerminationType
    from wireless.graphql.types import WirelessLANType

__all__ = (
    'ASNRangeType',
    'ASNType',
    'AggregateType',
    'FHRPGroupAssignmentType',
    'FHRPGroupType',
    'IPAddressType',
    'IPRangeType',
    'PrefixType',
    'RIRType',
    'RoleType',
    'RouteTargetType',
    'ServiceTemplateType',
    'ServiceType',
    'VLANGroupType',
    'VLANTranslationPolicyType',
    'VLANTranslationRuleType',
    'VLANType',
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
    filters=ASNFilter,
    pagination=True
)
class ASNType(ContactsMixin, PrimaryObjectType):
    asn: BigInt
    rir: Annotated["RIRType", strawberry.lazy('ipam.graphql.types')] | None
    tenant: Annotated["TenantType", strawberry.lazy('tenancy.graphql.types')] | None

    sites: list[SiteType]
    providers: list[ProviderType]


@strawberry_django.type(
    models.ASNRange,
    fields='__all__',
    filters=ASNRangeFilter,
    pagination=True
)
class ASNRangeType(OrganizationalObjectType):
    start: BigInt
    end: BigInt
    rir: Annotated["RIRType", strawberry.lazy('ipam.graphql.types')] | None
    tenant: Annotated["TenantType", strawberry.lazy('tenancy.graphql.types')] | None


@strawberry_django.type(
    models.Aggregate,
    fields='__all__',
    filters=AggregateFilter,
    pagination=True
)
class AggregateType(ContactsMixin, BaseIPAddressFamilyType, PrimaryObjectType):
    prefix: str
    rir: Annotated["RIRType", strawberry.lazy('ipam.graphql.types')] | None
    tenant: Annotated["TenantType", strawberry.lazy('tenancy.graphql.types')] | None


@strawberry_django.type(
    models.FHRPGroup,
    fields='__all__',
    filters=FHRPGroupFilter,
    pagination=True
)
class FHRPGroupType(IPAddressesMixin, PrimaryObjectType):
    fhrpgroupassignment_set: list[Annotated["FHRPGroupAssignmentType", strawberry.lazy('ipam.graphql.types')]]


@strawberry_django.type(
    models.FHRPGroupAssignment,
    exclude=['interface_type', 'interface_id'],
    filters=FHRPGroupAssignmentFilter,
    pagination=True
)
class FHRPGroupAssignmentType(BaseObjectType):
    group: Annotated['FHRPGroupType', strawberry.lazy('ipam.graphql.types')]

    @strawberry_django.field
    def interface(self) -> Annotated[
        Annotated['InterfaceType', strawberry.lazy('dcim.graphql.types')]
        | Annotated['VMInterfaceType', strawberry.lazy('virtualization.graphql.types')],
        strawberry.union('FHRPGroupInterfaceType'),
    ]:
        return self.interface


@strawberry_django.type(
    models.IPAddress,
    exclude=['assigned_object_type', 'assigned_object_id', 'address'],
    filters=IPAddressFilter,
    pagination=True
)
class IPAddressType(ContactsMixin, BaseIPAddressFamilyType, PrimaryObjectType):
    address: str
    vrf: Annotated['VRFType', strawberry.lazy('ipam.graphql.types')] | None
    tenant: Annotated['TenantType', strawberry.lazy('tenancy.graphql.types')] | None
    nat_inside: Annotated['IPAddressType', strawberry.lazy('ipam.graphql.types')] | None

    nat_outside: list[Annotated['IPAddressType', strawberry.lazy('ipam.graphql.types')]]
    tunnel_terminations: list[Annotated['TunnelTerminationType', strawberry.lazy('vpn.graphql.types')]]
    services: list[Annotated['ServiceType', strawberry.lazy('ipam.graphql.types')]]

    @strawberry_django.field
    def assigned_object(self) -> Annotated[
        Annotated['InterfaceType', strawberry.lazy('dcim.graphql.types')]
        | Annotated['FHRPGroupType', strawberry.lazy('ipam.graphql.types')]
        | Annotated['VMInterfaceType', strawberry.lazy('virtualization.graphql.types')],
        strawberry.union('IPAddressAssignmentType'),
    ] | None:
        return self.assigned_object


@strawberry_django.type(
    models.IPRange,
    fields='__all__',
    filters=IPRangeFilter,
    pagination=True
)
class IPRangeType(ContactsMixin, PrimaryObjectType):
    start_address: str
    end_address: str
    vrf: Annotated["VRFType", strawberry.lazy('ipam.graphql.types')] | None
    tenant: Annotated["TenantType", strawberry.lazy('tenancy.graphql.types')] | None
    role: Annotated["RoleType", strawberry.lazy('ipam.graphql.types')] | None


@strawberry_django.type(
    models.Prefix,
    exclude=['scope_type', 'scope_id', '_location', '_region', '_site', '_site_group'],
    filters=PrefixFilter,
    pagination=True
)
class PrefixType(ContactsMixin, BaseIPAddressFamilyType, PrimaryObjectType):
    prefix: str
    vrf: Annotated['VRFType', strawberry.lazy('ipam.graphql.types')] | None
    tenant: Annotated['TenantType', strawberry.lazy('tenancy.graphql.types')] | None
    vlan: Annotated['VLANType', strawberry.lazy('ipam.graphql.types')] | None
    role: Annotated['RoleType', strawberry.lazy('ipam.graphql.types')] | None

    @strawberry_django.field
    def scope(self) -> Annotated[
        Annotated['LocationType', strawberry.lazy('dcim.graphql.types')]
        | Annotated['RegionType', strawberry.lazy('dcim.graphql.types')]
        | Annotated['SiteGroupType', strawberry.lazy('dcim.graphql.types')]
        | Annotated['SiteType', strawberry.lazy('dcim.graphql.types')],
        strawberry.union('PrefixScopeType'),
    ] | None:
        return self.scope


@strawberry_django.type(
    models.RIR,
    fields='__all__',
    filters=RIRFilter,
    pagination=True
)
class RIRType(OrganizationalObjectType):

    asn_ranges: list[Annotated["ASNRangeType", strawberry.lazy('ipam.graphql.types')]]
    asns: list[Annotated["ASNType", strawberry.lazy('ipam.graphql.types')]]
    aggregates: list[Annotated["AggregateType", strawberry.lazy('ipam.graphql.types')]]


@strawberry_django.type(
    models.Role,
    fields='__all__',
    filters=RoleFilter,
    pagination=True
)
class RoleType(OrganizationalObjectType):

    prefixes: list[Annotated["PrefixType", strawberry.lazy('ipam.graphql.types')]]
    ip_ranges: list[Annotated["IPRangeType", strawberry.lazy('ipam.graphql.types')]]
    vlans: list[Annotated["VLANType", strawberry.lazy('ipam.graphql.types')]]


@strawberry_django.type(
    models.RouteTarget,
    fields='__all__',
    filters=RouteTargetFilter,
    pagination=True
)
class RouteTargetType(PrimaryObjectType):
    tenant: Annotated["TenantType", strawberry.lazy('tenancy.graphql.types')] | None

    importing_l2vpns: list[Annotated["L2VPNType", strawberry.lazy('vpn.graphql.types')]]
    exporting_l2vpns: list[Annotated["L2VPNType", strawberry.lazy('vpn.graphql.types')]]
    importing_vrfs: list[Annotated["VRFType", strawberry.lazy('ipam.graphql.types')]]
    exporting_vrfs: list[Annotated["VRFType", strawberry.lazy('ipam.graphql.types')]]


@strawberry_django.type(
    models.Service,
    exclude=('parent_object_type', 'parent_object_id'),
    filters=ServiceFilter,
    pagination=True
)
class ServiceType(ContactsMixin, PrimaryObjectType):
    ports: list[int]
    ipaddresses: list[Annotated['IPAddressType', strawberry.lazy('ipam.graphql.types')]]

    @strawberry_django.field
    def parent(self) -> Annotated[
        Annotated['DeviceType', strawberry.lazy('dcim.graphql.types')]
        | Annotated['VirtualMachineType', strawberry.lazy('virtualization.graphql.types')]
        | Annotated['FHRPGroupType', strawberry.lazy('ipam.graphql.types')],
        strawberry.union('ServiceParentType'),
    ] | None:
        return self.parent


@strawberry_django.type(
    models.ServiceTemplate,
    fields='__all__',
    filters=ServiceTemplateFilter,
    pagination=True
)
class ServiceTemplateType(PrimaryObjectType):
    ports: list[int]


@strawberry_django.type(
    models.VLAN,
    exclude=['qinq_svlan'],
    filters=VLANFilter,
    pagination=True
)
class VLANType(PrimaryObjectType):
    site: Annotated["SiteType", strawberry.lazy('ipam.graphql.types')] | None
    group: Annotated["VLANGroupType", strawberry.lazy('ipam.graphql.types')] | None
    tenant: Annotated["TenantType", strawberry.lazy('tenancy.graphql.types')] | None
    role: Annotated["RoleType", strawberry.lazy('ipam.graphql.types')] | None

    interfaces_as_untagged: list[Annotated["InterfaceType", strawberry.lazy('dcim.graphql.types')]]
    vminterfaces_as_untagged: list[Annotated["VMInterfaceType", strawberry.lazy('virtualization.graphql.types')]]
    wirelesslan_set: list[Annotated["WirelessLANType", strawberry.lazy('wireless.graphql.types')]]
    prefixes: list[Annotated["PrefixType", strawberry.lazy('ipam.graphql.types')]]
    interfaces_as_tagged: list[Annotated["InterfaceType", strawberry.lazy('dcim.graphql.types')]]
    vminterfaces_as_tagged: list[Annotated["VMInterfaceType", strawberry.lazy('virtualization.graphql.types')]]

    @strawberry_django.field
    def qinq_svlan(self) -> Annotated["VLANType", strawberry.lazy('ipam.graphql.types')] | None:
        return self.qinq_svlan


@strawberry_django.type(
    models.VLANGroup,
    exclude=['scope_type', 'scope_id'],
    filters=VLANGroupFilter,
    pagination=True
)
class VLANGroupType(OrganizationalObjectType):

    vlans: list[VLANType]
    vid_ranges: list[str]
    tenant: Annotated['TenantType', strawberry.lazy('tenancy.graphql.types')] | None

    @strawberry_django.field
    def scope(self) -> Annotated[
        Annotated['ClusterType', strawberry.lazy('virtualization.graphql.types')]
        | Annotated['ClusterGroupType', strawberry.lazy('virtualization.graphql.types')]
        | Annotated['LocationType', strawberry.lazy('dcim.graphql.types')]
        | Annotated['RackType', strawberry.lazy('dcim.graphql.types')]
        | Annotated['RegionType', strawberry.lazy('dcim.graphql.types')]
        | Annotated['SiteType', strawberry.lazy('dcim.graphql.types')]
        | Annotated['SiteGroupType', strawberry.lazy('dcim.graphql.types')],
        strawberry.union('VLANGroupScopeType'),
    ] | None:
        return self.scope


@strawberry_django.type(
    models.VLANTranslationPolicy,
    fields='__all__',
    filters=VLANTranslationPolicyFilter,
    pagination=True
)
class VLANTranslationPolicyType(PrimaryObjectType):
    rules: list[Annotated["VLANTranslationRuleType", strawberry.lazy('ipam.graphql.types')]]


@strawberry_django.type(
    models.VLANTranslationRule,
    fields='__all__',
    filters=VLANTranslationRuleFilter,
    pagination=True
)
class VLANTranslationRuleType(NetBoxObjectType):
    policy: Annotated[
        "VLANTranslationPolicyType",
        strawberry.lazy('ipam.graphql.types')
    ] = strawberry_django.field(select_related=["policy"])


@strawberry_django.type(
    models.VRF,
    fields='__all__',
    filters=VRFFilter,
    pagination=True
)
class VRFType(PrimaryObjectType):
    tenant: Annotated["TenantType", strawberry.lazy('tenancy.graphql.types')] | None

    interfaces: list[Annotated["InterfaceType", strawberry.lazy('dcim.graphql.types')]]
    ip_addresses: list[Annotated["IPAddressType", strawberry.lazy('ipam.graphql.types')]]
    vminterfaces: list[Annotated["VMInterfaceType", strawberry.lazy('virtualization.graphql.types')]]
    ip_ranges: list[Annotated["IPRangeType", strawberry.lazy('ipam.graphql.types')]]
    export_targets: list[Annotated["RouteTargetType", strawberry.lazy('ipam.graphql.types')]]
    import_targets: list[Annotated["RouteTargetType", strawberry.lazy('ipam.graphql.types')]]
    prefixes: list[Annotated["PrefixType", strawberry.lazy('ipam.graphql.types')]]
