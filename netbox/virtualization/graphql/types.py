from typing import Annotated, List, Union

import strawberry
import strawberry_django

from extras.graphql.mixins import ConfigContextMixin, ContactsMixin
from ipam.graphql.mixins import IPAddressesMixin, VLANGroupsMixin
from netbox.graphql.scalars import BigInt
from netbox.graphql.types import OrganizationalObjectType, NetBoxObjectType
from virtualization import models
from .filters import *

__all__ = (
    'ClusterType',
    'ClusterGroupType',
    'ClusterTypeType',
    'VirtualDiskType',
    'VirtualMachineType',
    'VMInterfaceType',
)


@strawberry.type
class ComponentType(NetBoxObjectType):
    """
    Base type for device/VM components
    """
    _name: str
    virtual_machine: Annotated["VirtualMachineType", strawberry.lazy('virtualization.graphql.types')]


@strawberry_django.type(
    models.Cluster,
    exclude=('scope_type', 'scope_id', '_location', '_region', '_site', '_site_group'),
    filters=ClusterFilter
)
class ClusterType(VLANGroupsMixin, NetBoxObjectType):
    type: Annotated["ClusterTypeType", strawberry.lazy('virtualization.graphql.types')] | None
    group: Annotated["ClusterGroupType", strawberry.lazy('virtualization.graphql.types')] | None
    tenant: Annotated["TenantType", strawberry.lazy('tenancy.graphql.types')] | None
    virtual_machines: List[Annotated["VirtualMachineType", strawberry.lazy('virtualization.graphql.types')]]
    devices: List[Annotated["DeviceType", strawberry.lazy('dcim.graphql.types')]]

    @strawberry_django.field
    def scope(self) -> Annotated[Union[
        Annotated["LocationType", strawberry.lazy('dcim.graphql.types')],
        Annotated["RegionType", strawberry.lazy('dcim.graphql.types')],
        Annotated["SiteGroupType", strawberry.lazy('dcim.graphql.types')],
        Annotated["SiteType", strawberry.lazy('dcim.graphql.types')],
    ], strawberry.union("ClusterScopeType")] | None:
        return self.scope


@strawberry_django.type(
    models.ClusterGroup,
    fields='__all__',
    filters=ClusterGroupFilter
)
class ClusterGroupType(VLANGroupsMixin, OrganizationalObjectType):

    clusters: List[Annotated["ClusterType", strawberry.lazy('virtualization.graphql.types')]]


@strawberry_django.type(
    models.ClusterType,
    fields='__all__',
    filters=ClusterTypeFilter
)
class ClusterTypeType(OrganizationalObjectType):

    clusters: List[ClusterType]


@strawberry_django.type(
    models.VirtualMachine,
    fields='__all__',
    filters=VirtualMachineFilter
)
class VirtualMachineType(ConfigContextMixin, ContactsMixin, NetBoxObjectType):
    _name: str
    interface_count: BigInt
    virtual_disk_count: BigInt
    interface_count: BigInt
    config_template: Annotated["ConfigTemplateType", strawberry.lazy('extras.graphql.types')] | None
    site: Annotated["SiteType", strawberry.lazy('dcim.graphql.types')] | None
    cluster: Annotated["ClusterType", strawberry.lazy('virtualization.graphql.types')] | None
    device: Annotated["DeviceType", strawberry.lazy('dcim.graphql.types')] | None
    tenant: Annotated["TenantType", strawberry.lazy('tenancy.graphql.types')] | None
    platform: Annotated["PlatformType", strawberry.lazy('dcim.graphql.types')] | None
    role: Annotated["DeviceRoleType", strawberry.lazy('dcim.graphql.types')] | None
    primary_ip4: Annotated["IPAddressType", strawberry.lazy('ipam.graphql.types')] | None
    primary_ip6: Annotated["IPAddressType", strawberry.lazy('ipam.graphql.types')] | None

    interfaces: List[Annotated["VMInterfaceType", strawberry.lazy('virtualization.graphql.types')]]
    services: List[Annotated["ServiceType", strawberry.lazy('ipam.graphql.types')]]
    virtualdisks: List[Annotated["VirtualDiskType", strawberry.lazy('virtualization.graphql.types')]]


@strawberry_django.type(
    models.VMInterface,
    fields='__all__',
    filters=VMInterfaceFilter
)
class VMInterfaceType(IPAddressesMixin, ComponentType):
    mac_address: str | None
    parent: Annotated["VMInterfaceType", strawberry.lazy('virtualization.graphql.types')] | None
    bridge: Annotated["VMInterfaceType", strawberry.lazy('virtualization.graphql.types')] | None
    untagged_vlan: Annotated["VLANType", strawberry.lazy('ipam.graphql.types')] | None
    vrf: Annotated["VRFType", strawberry.lazy('ipam.graphql.types')] | None
    qinq_svlan: Annotated["VLANType", strawberry.lazy('ipam.graphql.types')] | None
    vlan_translation_policy: Annotated["VLANTranslationPolicyType", strawberry.lazy('ipam.graphql.types')] | None

    tagged_vlans: List[Annotated["VLANType", strawberry.lazy('ipam.graphql.types')]]
    bridge_interfaces: List[Annotated["VMInterfaceType", strawberry.lazy('virtualization.graphql.types')]]
    child_interfaces: List[Annotated["VMInterfaceType", strawberry.lazy('virtualization.graphql.types')]]


@strawberry_django.type(
    models.VirtualDisk,
    fields='__all__',
    filters=VirtualDiskFilter
)
class VirtualDiskType(ComponentType):
    pass
