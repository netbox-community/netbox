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
    pass


@strawberry_django.type(
    models.ClusterGroup,
    fields='__all__',
    filters=ClusterGroupFilter
)
class ClusterGroupType(VLANGroupsMixin, OrganizationalObjectType):
    pass


@strawberry_django.type(
    models.ClusterType,
    fields='__all__',
    filters=ClusterTypeFilter
)
class ClusterTypeType(OrganizationalObjectType):
    pass


@strawberry_django.type(
    models.VirtualMachine,
    fields='__all__',
    filters=VirtualMachineFilter
)
class VirtualMachineType(ConfigContextMixin, NetBoxObjectType):
    pass


@strawberry_django.type(
    models.VMInterface,
    fields='__all__',
    filters=VMInterfaceFilter
)
class VMInterfaceType(IPAddressesMixin, ComponentObjectType):

    def resolve_mode(self, info):
        return self.mode or None


@strawberry_django.type(
    models.VirtualDisk,
    fields='__all__',
    filters=VirtualDiskFilter
)
class VirtualDiskType(ComponentObjectType):

    def resolve_mode(self, info):
        return self.mode or None
