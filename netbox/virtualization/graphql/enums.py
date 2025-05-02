import strawberry

from virtualization.choices import *

__all__ = (
    'ClusterStatusEnum',
    'VirtualMachineStatusEnum',
)

ClusterStatusEnum = strawberry.enum(ClusterStatusChoices.as_enum(prefix='status'))
VirtualMachineStatusEnum = strawberry.enum(VirtualMachineStatusChoices.as_enum(prefix='status'))
