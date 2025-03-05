import strawberry

from virtualization.choices import *

__all__ = (
    'ClusterStatusEnum',
    'VirtualMachineStatusEnum',
)

ClusterStatusEnum = strawberry.enum(ClusterStatusChoices.as_enum())
VirtualMachineStatusEnum = strawberry.enum(VirtualMachineStatusChoices.as_enum())
