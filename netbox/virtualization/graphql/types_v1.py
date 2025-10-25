from typing import Annotated, List, TYPE_CHECKING, Union

import strawberry
import strawberry_django

from extras.graphql.mixins_v1 import ConfigContextMixinV1, ContactsMixinV1
from ipam.graphql.mixins_v1 import IPAddressesMixinV1, VLANGroupsMixinV1
from netbox.graphql.scalars import BigInt
from netbox.graphql.types_v1 import OrganizationalObjectTypeV1, NetBoxObjectTypeV1, PrimaryObjectTypeV1
from users.graphql.mixins_v1 import OwnerMixinV1
from virtualization import models
from .filters_v1 import *

if TYPE_CHECKING:
    from dcim.graphql.types_v1 import (
        DeviceRoleTypeV1,
        DeviceTypeV1,
        LocationTypeV1,
        MACAddressTypeV1,
        PlatformTypeV1,
        RegionTypeV1,
        SiteGroupTypeV1,
        SiteTypeV1,
    )
    from extras.graphql.types_v1 import ConfigTemplateTypeV1
    from ipam.graphql.types_v1 import IPAddressTypeV1, ServiceTypeV1, VLANTranslationPolicyTypeV1, VLANTypeV1, VRFTypeV1
    from tenancy.graphql.types_v1 import TenantTypeV1

__all__ = (
    'ClusterTypeV1',
    'ClusterGroupTypeV1',
    'ClusterTypeTypeV1',
    'VirtualDiskTypeV1',
    'VirtualMachineTypeV1',
    'VMInterfaceTypeV1',
)


@strawberry.type
class ComponentTypeV1(OwnerMixinV1, NetBoxObjectTypeV1):
    """
    Base type for device/VM components
    """
    virtual_machine: Annotated["VirtualMachineTypeV1", strawberry.lazy('virtualization.graphql.types_v1')]


@strawberry_django.type(
    models.Cluster,
    exclude=['scope_type', 'scope_id', '_location', '_region', '_site', '_site_group'],
    filters=ClusterFilterV1,
    pagination=True
)
class ClusterTypeV1(ContactsMixinV1, VLANGroupsMixinV1, PrimaryObjectTypeV1):
    type: Annotated["ClusterTypeTypeV1", strawberry.lazy('virtualization.graphql.types_v1')] | None
    group: Annotated["ClusterGroupTypeV1", strawberry.lazy('virtualization.graphql.types_v1')] | None
    tenant: Annotated["TenantTypeV1", strawberry.lazy('tenancy.graphql.types_v1')] | None
    virtual_machines: List[Annotated["VirtualMachineTypeV1", strawberry.lazy('virtualization.graphql.types_v1')]]
    devices: List[Annotated["DeviceTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]

    @strawberry_django.field
    def scope(self) -> Annotated[Union[
        Annotated["LocationTypeV1", strawberry.lazy('dcim.graphql.types_v1')],
        Annotated["RegionTypeV1", strawberry.lazy('dcim.graphql.types_v1')],
        Annotated["SiteGroupTypeV1", strawberry.lazy('dcim.graphql.types_v1')],
        Annotated["SiteTypeV1", strawberry.lazy('dcim.graphql.types_v1')],
    ], strawberry.union("ClusterScopeTypeV1")] | None:
        return self.scope


@strawberry_django.type(
    models.ClusterGroup,
    fields='__all__',
    filters=ClusterGroupFilterV1,
    pagination=True
)
class ClusterGroupTypeV1(ContactsMixinV1, VLANGroupsMixinV1, OrganizationalObjectTypeV1):

    clusters: List[Annotated["ClusterTypeV1", strawberry.lazy('virtualization.graphql.types_v1')]]


@strawberry_django.type(
    models.ClusterType,
    fields='__all__',
    filters=ClusterTypeFilterV1,
    pagination=True
)
class ClusterTypeTypeV1(OrganizationalObjectTypeV1):

    clusters: List[ClusterTypeV1]


@strawberry_django.type(
    models.VirtualMachine,
    fields='__all__',
    filters=VirtualMachineFilterV1,
    pagination=True
)
class VirtualMachineTypeV1(ConfigContextMixinV1, ContactsMixinV1, PrimaryObjectTypeV1):
    interface_count: BigInt
    virtual_disk_count: BigInt
    interface_count: BigInt
    config_template: Annotated["ConfigTemplateTypeV1", strawberry.lazy('extras.graphql.types_v1')] | None
    site: Annotated["SiteTypeV1", strawberry.lazy('dcim.graphql.types_v1')] | None
    cluster: Annotated["ClusterTypeV1", strawberry.lazy('virtualization.graphql.types_v1')] | None
    device: Annotated["DeviceTypeV1", strawberry.lazy('dcim.graphql.types_v1')] | None
    tenant: Annotated["TenantTypeV1", strawberry.lazy('tenancy.graphql.types_v1')] | None
    platform: Annotated["PlatformTypeV1", strawberry.lazy('dcim.graphql.types_v1')] | None
    role: Annotated["DeviceRoleTypeV1", strawberry.lazy('dcim.graphql.types_v1')] | None
    primary_ip4: Annotated["IPAddressTypeV1", strawberry.lazy('ipam.graphql.types_v1')] | None
    primary_ip6: Annotated["IPAddressTypeV1", strawberry.lazy('ipam.graphql.types_v1')] | None

    interfaces: List[Annotated["VMInterfaceTypeV1", strawberry.lazy('virtualization.graphql.types_v1')]]
    services: List[Annotated["ServiceTypeV1", strawberry.lazy('ipam.graphql.types_v1')]]
    virtualdisks: List[Annotated["VirtualDiskTypeV1", strawberry.lazy('virtualization.graphql.types_v1')]]


@strawberry_django.type(
    models.VMInterface,
    fields='__all__',
    filters=VMInterfaceFilterV1,
    pagination=True
)
class VMInterfaceTypeV1(IPAddressesMixinV1, ComponentTypeV1):
    _name: str
    mac_address: str | None
    parent: Annotated["VMInterfaceTypeV1", strawberry.lazy('virtualization.graphql.types_v1')] | None
    bridge: Annotated["VMInterfaceTypeV1", strawberry.lazy('virtualization.graphql.types_v1')] | None
    untagged_vlan: Annotated["VLANTypeV1", strawberry.lazy('ipam.graphql.types_v1')] | None
    vrf: Annotated["VRFTypeV1", strawberry.lazy('ipam.graphql.types_v1')] | None
    primary_mac_address: Annotated["MACAddressTypeV1", strawberry.lazy('dcim.graphql.types_v1')] | None
    qinq_svlan: Annotated["VLANTypeV1", strawberry.lazy('ipam.graphql.types_v1')] | None
    vlan_translation_policy: Annotated["VLANTranslationPolicyTypeV1", strawberry.lazy('ipam.graphql.types_v1')] | None

    tagged_vlans: List[Annotated["VLANTypeV1", strawberry.lazy('ipam.graphql.types_v1')]]
    bridge_interfaces: List[Annotated["VMInterfaceTypeV1", strawberry.lazy('virtualization.graphql.types_v1')]]
    child_interfaces: List[Annotated["VMInterfaceTypeV1", strawberry.lazy('virtualization.graphql.types_v1')]]
    mac_addresses: List[Annotated["MACAddressTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]


@strawberry_django.type(
    models.VirtualDisk,
    fields='__all__',
    filters=VirtualDiskFilterV1,
    pagination=True
)
class VirtualDiskTypeV1(ComponentTypeV1):
    pass
