from typing import Annotated, List

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
    fields='__all__',
    filters=ClusterFilter
)
class ClusterType(VLANGroupsMixin, NetBoxObjectType):
    type: Annotated["ClusterTypeType", strawberry.lazy('virtualization.graphql.types')] | None
    group: Annotated["ClusterGroupType", strawberry.lazy('virtualization.graphql.types')] | None
    tenant: Annotated["TenantType", strawberry.lazy('tenancy.graphql.types')] | None
    site: Annotated["SiteType", strawberry.lazy('dcim.graphql.types')] | None

    @strawberry_django.field
    def virtual_machines(self) -> List[Annotated["VirtualMachineType", strawberry.lazy('virtualization.graphql.types')]]:
        return self.virtual_machines.all()

    @strawberry_django.field
    def devices(self) -> List[Annotated["DeviceType", strawberry.lazy('dcim.graphql.types')]]:
        return self.devices.all()


@strawberry_django.type(
    models.ClusterGroup,
    fields='__all__',
    filters=ClusterGroupFilter
)
class ClusterGroupType(VLANGroupsMixin, OrganizationalObjectType):

    @strawberry_django.field
    def clusters(self) -> List[Annotated["ClusterType", strawberry.lazy('virtualization.graphql.types')]]:
        return self.clusters.all()


@strawberry_django.type(
    models.ClusterType,
    fields='__all__',
    filters=ClusterTypeFilter
)
class ClusterTypeType(OrganizationalObjectType):

    @strawberry_django.field
    def clusters(self) -> List[ClusterType]:
        return self.clusters.all()


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

    @strawberry_django.field
    def interfaces(self) -> List[Annotated["InterfaceType", strawberry.lazy('dcim.graphql.types')]]:
        return self.interfaces.all()

    @strawberry_django.field
    def services(self) -> List[Annotated["ServiceType", strawberry.lazy('ipam.graphql.types')]]:
        return self.services.all()

    @strawberry_django.field
    def virtualdisks(self) -> List[Annotated["VirtualDiskType", strawberry.lazy('virtualization.graphql.types')]]:
        return self.virtualdisks.all()


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

    @strawberry_django.field
    def tagged_vlans(self) -> List[Annotated["VLANType", strawberry.lazy('ipam.graphql.types')]]:
        return self.tagged_vlans.all()

    @strawberry_django.field
    def bridge_interfaces(self) -> List[Annotated["InterfaceType", strawberry.lazy('dcim.graphql.types')]]:
        return self.bridge_interfaces.all()

    @strawberry_django.field
    def child_interfaces(self) -> List[Annotated["InterfaceType", strawberry.lazy('dcim.graphql.types')]]:
        return self.child_interfaces.all()


@strawberry_django.type(
    models.VirtualDisk,
    fields='__all__',
    filters=VirtualDiskFilter
)
class VirtualDiskType(ComponentType):
    pass
