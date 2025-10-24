from typing import Annotated, List, TYPE_CHECKING, Union

import strawberry
import strawberry_django

from circuits.graphql.types_v1 import ProviderTypeV1
from dcim.graphql.types_v1 import SiteTypeV1
from extras.graphql.mixins_v1 import ContactsMixinV1
from ipam import models
from netbox.graphql.scalars import BigInt
from netbox.graphql.types_v1 import BaseObjectTypeV1, NetBoxObjectTypeV1, OrganizationalObjectTypeV1
from .filters_v1 import *
from .mixins_v1 import IPAddressesMixinV1

if TYPE_CHECKING:
    from dcim.graphql.types_v1 import (
        DeviceTypeV1,
        InterfaceTypeV1,
        LocationTypeV1,
        RackTypeV1,
        RegionTypeV1,
        SiteGroupTypeV1,
        SiteTypeV1,
    )
    from tenancy.graphql.types_v1 import TenantTypeV1
    from virtualization.graphql.types_v1 import (
        ClusterGroupTypeV1, ClusterTypeV1, VMInterfaceTypeV1, VirtualMachineTypeV1
    )
    from vpn.graphql.types_v1 import L2VPNTypeV1, TunnelTerminationTypeV1
    from wireless.graphql.types_v1 import WirelessLANTypeV1

__all__ = (
    'ASNTypeV1',
    'ASNRangeTypeV1',
    'AggregateTypeV1',
    'FHRPGroupTypeV1',
    'FHRPGroupAssignmentTypeV1',
    'IPAddressTypeV1',
    'IPRangeTypeV1',
    'PrefixTypeV1',
    'RIRTypeV1',
    'RoleTypeV1',
    'RouteTargetTypeV1',
    'ServiceTypeV1',
    'ServiceTemplateTypeV1',
    'VLANTypeV1',
    'VLANGroupTypeV1',
    'VLANTranslationPolicyTypeV1',
    'VLANTranslationRuleTypeV1',
    'VRFTypeV1',
)


@strawberry.type
class IPAddressFamilyTypeV1:
    value: int
    label: str


@strawberry.type
class BaseIPAddressFamilyTypeV1:
    """
    Base type for models that need to expose their IPAddress family type.
    """

    @strawberry.field
    def family(self) -> IPAddressFamilyTypeV1:
        # Note that self, is an instance of models.IPAddress
        # thus resolves to the address family value.
        return IPAddressFamilyTypeV1(value=self.family, label=f'IPv{self.family}')


@strawberry_django.type(
    models.ASN,
    fields='__all__',
    filters=ASNFilterV1,
    pagination=True
)
class ASNTypeV1(NetBoxObjectTypeV1, ContactsMixinV1):
    asn: BigInt
    rir: Annotated["RIRTypeV1", strawberry.lazy('ipam.graphql.types_v1')] | None
    tenant: Annotated["TenantTypeV1", strawberry.lazy('tenancy.graphql.types_v1')] | None

    sites: List[SiteTypeV1]
    providers: List[ProviderTypeV1]


@strawberry_django.type(
    models.ASNRange,
    fields='__all__',
    filters=ASNRangeFilterV1,
    pagination=True
)
class ASNRangeTypeV1(NetBoxObjectTypeV1):
    start: BigInt
    end: BigInt
    rir: Annotated["RIRTypeV1", strawberry.lazy('ipam.graphql.types_v1')] | None
    tenant: Annotated["TenantTypeV1", strawberry.lazy('tenancy.graphql.types_v1')] | None


@strawberry_django.type(
    models.Aggregate,
    fields='__all__',
    filters=AggregateFilterV1,
    pagination=True
)
class AggregateTypeV1(NetBoxObjectTypeV1, ContactsMixinV1, BaseIPAddressFamilyTypeV1):
    prefix: str
    rir: Annotated["RIRTypeV1", strawberry.lazy('ipam.graphql.types_v1')] | None
    tenant: Annotated["TenantTypeV1", strawberry.lazy('tenancy.graphql.types_v1')] | None


@strawberry_django.type(
    models.FHRPGroup,
    fields='__all__',
    filters=FHRPGroupFilterV1,
    pagination=True
)
class FHRPGroupTypeV1(NetBoxObjectTypeV1, IPAddressesMixinV1):

    fhrpgroupassignment_set: List[Annotated["FHRPGroupAssignmentTypeV1", strawberry.lazy('ipam.graphql.types_v1')]]


@strawberry_django.type(
    models.FHRPGroupAssignment,
    exclude=['interface_type', 'interface_id'],
    filters=FHRPGroupAssignmentFilterV1,
    pagination=True
)
class FHRPGroupAssignmentTypeV1(BaseObjectTypeV1):
    group: Annotated["FHRPGroupTypeV1", strawberry.lazy('ipam.graphql.types_v1')]

    @strawberry_django.field
    def interface(self) -> Annotated[Union[
        Annotated["InterfaceTypeV1", strawberry.lazy('dcim.graphql.types_v1')],
        Annotated["VMInterfaceTypeV1", strawberry.lazy('virtualization.graphql.types_v1')],
    ], strawberry.union("FHRPGroupInterfaceTypeV1")]:
        return self.interface


@strawberry_django.type(
    models.IPAddress,
    exclude=['assigned_object_type', 'assigned_object_id', 'address'],
    filters=IPAddressFilterV1,
    pagination=True
)
class IPAddressTypeV1(NetBoxObjectTypeV1, ContactsMixinV1, BaseIPAddressFamilyTypeV1):
    address: str
    vrf: Annotated["VRFTypeV1", strawberry.lazy('ipam.graphql.types_v1')] | None
    tenant: Annotated["TenantTypeV1", strawberry.lazy('tenancy.graphql.types_v1')] | None
    nat_inside: Annotated["IPAddressTypeV1", strawberry.lazy('ipam.graphql.types_v1')] | None

    nat_outside: List[Annotated["IPAddressTypeV1", strawberry.lazy('ipam.graphql.types_v1')]]
    tunnel_terminations: List[Annotated["TunnelTerminationTypeV1", strawberry.lazy('vpn.graphql.types_v1')]]
    services: List[Annotated["ServiceTypeV1", strawberry.lazy('ipam.graphql.types_v1')]]

    @strawberry_django.field
    def assigned_object(self) -> Annotated[Union[
        Annotated["InterfaceTypeV1", strawberry.lazy('dcim.graphql.types_v1')],
        Annotated["FHRPGroupTypeV1", strawberry.lazy('ipam.graphql.types_v1')],
        Annotated["VMInterfaceTypeV1", strawberry.lazy('virtualization.graphql.types_v1')],
    ], strawberry.union("IPAddressAssignmentTypeV1")] | None:
        return self.assigned_object


@strawberry_django.type(
    models.IPRange,
    fields='__all__',
    filters=IPRangeFilterV1,
    pagination=True
)
class IPRangeTypeV1(NetBoxObjectTypeV1, ContactsMixinV1):
    start_address: str
    end_address: str
    vrf: Annotated["VRFTypeV1", strawberry.lazy('ipam.graphql.types_v1')] | None
    tenant: Annotated["TenantTypeV1", strawberry.lazy('tenancy.graphql.types_v1')] | None
    role: Annotated["RoleTypeV1", strawberry.lazy('ipam.graphql.types_v1')] | None


@strawberry_django.type(
    models.Prefix,
    exclude=['scope_type', 'scope_id', '_location', '_region', '_site', '_site_group'],
    filters=PrefixFilterV1,
    pagination=True
)
class PrefixTypeV1(NetBoxObjectTypeV1, ContactsMixinV1, BaseIPAddressFamilyTypeV1):
    prefix: str
    vrf: Annotated["VRFTypeV1", strawberry.lazy('ipam.graphql.types_v1')] | None
    tenant: Annotated["TenantTypeV1", strawberry.lazy('tenancy.graphql.types_v1')] | None
    vlan: Annotated["VLANTypeV1", strawberry.lazy('ipam.graphql.types_v1')] | None
    role: Annotated["RoleTypeV1", strawberry.lazy('ipam.graphql.types_v1')] | None

    @strawberry_django.field
    def scope(self) -> Annotated[Union[
        Annotated["LocationTypeV1", strawberry.lazy('dcim.graphql.types_v1')],
        Annotated["RegionTypeV1", strawberry.lazy('dcim.graphql.types_v1')],
        Annotated["SiteGroupTypeV1", strawberry.lazy('dcim.graphql.types_v1')],
        Annotated["SiteTypeV1", strawberry.lazy('dcim.graphql.types_v1')],
    ], strawberry.union("PrefixScopeTypeV1")] | None:
        return self.scope


@strawberry_django.type(
    models.RIR,
    fields='__all__',
    filters=RIRFilterV1,
    pagination=True
)
class RIRTypeV1(OrganizationalObjectTypeV1):

    asn_ranges: List[Annotated["ASNRangeTypeV1", strawberry.lazy('ipam.graphql.types_v1')]]
    asns: List[Annotated["ASNTypeV1", strawberry.lazy('ipam.graphql.types_v1')]]
    aggregates: List[Annotated["AggregateTypeV1", strawberry.lazy('ipam.graphql.types_v1')]]


@strawberry_django.type(
    models.Role,
    fields='__all__',
    filters=RoleFilterV1,
    pagination=True
)
class RoleTypeV1(OrganizationalObjectTypeV1):

    prefixes: List[Annotated["PrefixTypeV1", strawberry.lazy('ipam.graphql.types_v1')]]
    ip_ranges: List[Annotated["IPRangeTypeV1", strawberry.lazy('ipam.graphql.types_v1')]]
    vlans: List[Annotated["VLANTypeV1", strawberry.lazy('ipam.graphql.types_v1')]]


@strawberry_django.type(
    models.RouteTarget,
    fields='__all__',
    filters=RouteTargetFilterV1,
    pagination=True
)
class RouteTargetTypeV1(NetBoxObjectTypeV1):
    tenant: Annotated["TenantTypeV1", strawberry.lazy('tenancy.graphql.types_v1')] | None

    importing_l2vpns: List[Annotated["L2VPNTypeV1", strawberry.lazy('vpn.graphql.types_v1')]]
    exporting_l2vpns: List[Annotated["L2VPNTypeV1", strawberry.lazy('vpn.graphql.types_v1')]]
    importing_vrfs: List[Annotated["VRFTypeV1", strawberry.lazy('ipam.graphql.types_v1')]]
    exporting_vrfs: List[Annotated["VRFTypeV1", strawberry.lazy('ipam.graphql.types_v1')]]


@strawberry_django.type(
    models.Service,
    exclude=('parent_object_type', 'parent_object_id'),
    filters=ServiceFilterV1,
    pagination=True
)
class ServiceTypeV1(NetBoxObjectTypeV1, ContactsMixinV1):
    ports: List[int]
    ipaddresses: List[Annotated["IPAddressTypeV1", strawberry.lazy('ipam.graphql.types_v1')]]

    @strawberry_django.field
    def parent(self) -> Annotated[Union[
        Annotated["DeviceTypeV1", strawberry.lazy('dcim.graphql.types_v1')],
        Annotated["VirtualMachineTypeV1", strawberry.lazy('virtualization.graphql.types_v1')],
        Annotated["FHRPGroupTypeV1", strawberry.lazy('ipam.graphql.types_v1')],
    ], strawberry.union("ServiceParentTypeV1")] | None:
        return self.parent


@strawberry_django.type(
    models.ServiceTemplate,
    fields='__all__',
    filters=ServiceTemplateFilterV1,
    pagination=True
)
class ServiceTemplateTypeV1(NetBoxObjectTypeV1):
    ports: List[int]


@strawberry_django.type(
    models.VLAN,
    exclude=['qinq_svlan'],
    filters=VLANFilterV1,
    pagination=True
)
class VLANTypeV1(NetBoxObjectTypeV1):
    site: Annotated["SiteTypeV1", strawberry.lazy('ipam.graphql.types_v1')] | None
    group: Annotated["VLANGroupTypeV1", strawberry.lazy('ipam.graphql.types_v1')] | None
    tenant: Annotated["TenantTypeV1", strawberry.lazy('tenancy.graphql.types_v1')] | None
    role: Annotated["RoleTypeV1", strawberry.lazy('ipam.graphql.types_v1')] | None

    interfaces_as_untagged: List[Annotated["InterfaceTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]
    vminterfaces_as_untagged: List[Annotated["VMInterfaceTypeV1", strawberry.lazy('virtualization.graphql.types_v1')]]
    wirelesslan_set: List[Annotated["WirelessLANTypeV1", strawberry.lazy('wireless.graphql.types_v1')]]
    prefixes: List[Annotated["PrefixTypeV1", strawberry.lazy('ipam.graphql.types_v1')]]
    interfaces_as_tagged: List[Annotated["InterfaceTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]
    vminterfaces_as_tagged: List[Annotated["VMInterfaceTypeV1", strawberry.lazy('virtualization.graphql.types_v1')]]

    @strawberry_django.field
    def qinq_svlan(self) -> Annotated["VLANTypeV1", strawberry.lazy('ipam.graphql.types_v1')] | None:
        return self.qinq_svlan


@strawberry_django.type(
    models.VLANGroup,
    exclude=['scope_type', 'scope_id'],
    filters=VLANGroupFilterV1,
    pagination=True
)
class VLANGroupTypeV1(OrganizationalObjectTypeV1):

    vlans: List[VLANTypeV1]
    vid_ranges: List[str]
    tenant: Annotated["TenantTypeV1", strawberry.lazy('tenancy.graphql.types_v1')] | None

    @strawberry_django.field
    def scope(self) -> Annotated[Union[
        Annotated["ClusterTypeV1", strawberry.lazy('virtualization.graphql.types_v1')],
        Annotated["ClusterGroupTypeV1", strawberry.lazy('virtualization.graphql.types_v1')],
        Annotated["LocationTypeV1", strawberry.lazy('dcim.graphql.types_v1')],
        Annotated["RackTypeV1", strawberry.lazy('dcim.graphql.types_v1')],
        Annotated["RegionTypeV1", strawberry.lazy('dcim.graphql.types_v1')],
        Annotated["SiteTypeV1", strawberry.lazy('dcim.graphql.types_v1')],
        Annotated["SiteGroupTypeV1", strawberry.lazy('dcim.graphql.types_v1')],
    ], strawberry.union("VLANGroupScopeTypeV1")] | None:
        return self.scope


@strawberry_django.type(
    models.VLANTranslationPolicy,
    fields='__all__',
    filters=VLANTranslationPolicyFilterV1,
    pagination=True
)
class VLANTranslationPolicyTypeV1(NetBoxObjectTypeV1):
    rules: List[Annotated["VLANTranslationRuleTypeV1", strawberry.lazy('ipam.graphql.types_v1')]]


@strawberry_django.type(
    models.VLANTranslationRule,
    fields='__all__',
    filters=VLANTranslationRuleFilterV1,
    pagination=True
)
class VLANTranslationRuleTypeV1(NetBoxObjectTypeV1):
    policy: Annotated[
        "VLANTranslationPolicyTypeV1",
        strawberry.lazy('ipam.graphql.types_v1')
    ] = strawberry_django.field(select_related=["policy"])


@strawberry_django.type(
    models.VRF,
    fields='__all__',
    filters=VRFFilterV1,
    pagination=True
)
class VRFTypeV1(NetBoxObjectTypeV1):
    tenant: Annotated["TenantTypeV1", strawberry.lazy('tenancy.graphql.types_v1')] | None

    interfaces: List[Annotated["InterfaceTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]
    ip_addresses: List[Annotated["IPAddressTypeV1", strawberry.lazy('ipam.graphql.types_v1')]]
    vminterfaces: List[Annotated["VMInterfaceTypeV1", strawberry.lazy('virtualization.graphql.types_v1')]]
    ip_ranges: List[Annotated["IPRangeTypeV1", strawberry.lazy('ipam.graphql.types_v1')]]
    export_targets: List[Annotated["RouteTargetTypeV1", strawberry.lazy('ipam.graphql.types_v1')]]
    import_targets: List[Annotated["RouteTargetTypeV1", strawberry.lazy('ipam.graphql.types_v1')]]
    prefixes: List[Annotated["PrefixTypeV1", strawberry.lazy('ipam.graphql.types_v1')]]
