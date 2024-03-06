from typing import Annotated, List

import strawberry
import strawberry_django

from dcim.graphql.types import ComponentObjectType
from extras.graphql.mixins import ConfigContextMixin
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


@strawberry_django.type(
    models.Cluster,
    fields='__all__',
    filters=ClusterFilter
)
class ClusterType(VLANGroupsMixin, NetBoxObjectType):

    @strawberry_django.field
    def virtual_machines(self) -> List[Annotated["VirtualMachineType", strawberry.lazy('virtualization.graphql.types')]]:
        return self.virtual_machines.all()

    @strawberry_django.field
    def vlan_groups(self) -> List[Annotated["VLANGroupType", strawberry.lazy('ipam.graphql.types')]]:
        return self.vlan_groups.all()

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
    def vlan_groups(self) -> List[Annotated["VLANGroupType", strawberry.lazy('ipam.graphql.types')]]:
        return self.vlan_groups.all()

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
class VirtualMachineType(ConfigContextMixin, NetBoxObjectType):
    _name: str
    interface_count: BigInt
    virtual_disk_count: BigInt

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
class VMInterfaceType(IPAddressesMixin, ComponentObjectType):
    _name: str
    mac_address: str | None

    @strawberry_django.field
    def ip_addresses(self) -> List[Annotated["IPAddressType", strawberry.lazy('ipam.graphql.types')]]:
        return self.ip_addresses.all()

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
class VirtualDiskType(ComponentObjectType):
    _name: str
