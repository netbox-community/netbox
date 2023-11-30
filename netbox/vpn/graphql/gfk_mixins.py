import graphene

from dcim.graphql.types import InterfaceType
from dcim.models import Interface
from ipam.graphql.types import VLANType
from ipam.models import VLAN
from virtualization.graphql.types import VMInterfaceType
from virtualization.models import VMInterface

__all__ = (
    'L2VPNAssignmentType',
)


class L2VPNAssignmentType(graphene.Union):
    class Meta:
        types = (
            InterfaceType,
            VLANType,
            VMInterfaceType,
        )

    @classmethod
    def resolve_type(cls, instance, info):
        if type(instance) is Interface:
            return InterfaceType
        if type(instance) is VLAN:
            return VLANType
        if type(instance) is VMInterface:
            return VMInterfaceType
