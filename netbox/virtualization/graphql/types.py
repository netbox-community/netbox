from typing import Annotated, List

import strawberry
import strawberry_django

from dcim.graphql.types import ComponentObjectType
from extras.graphql.mixins import ConfigContextMixin
from ipam.graphql.mixins import IPAddressesMixin, VLANGroupsMixin
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
    # fields='__all__',
    exclude=('_name', 'interface_count', 'virtual_disk_count',),  # bug - temp
    filters=VirtualMachineFilter
)
class VirtualMachineType(ConfigContextMixin, NetBoxObjectType):
    pass


@strawberry_django.type(
    models.VMInterface,
    # fields='__all__',
    exclude=('mac_address', '_name',),  # bug - temp
    filters=VMInterfaceFilter
)
class VMInterfaceType(IPAddressesMixin, ComponentObjectType):

    def resolve_mode(self, info):
        return self.mode or None


@strawberry_django.type(
    models.VirtualDisk,
    # fields='__all__',
    exclude=('_name',),  # bug - temp
    filters=VirtualDiskFilter
)
class VirtualDiskType(ComponentObjectType):

    def resolve_mode(self, info):
        return self.mode or None
