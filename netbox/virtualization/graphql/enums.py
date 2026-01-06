import strawberry

from virtualization.choices import *

__all__ = (
    'ClusterStatusEnum',
    'VirtualMachineStatusEnum',
    'VirtualMachineStatusEnum',
)

ClusterStatusEnum = strawberry.enum(ClusterStatusChoices.as_enum(prefix='status'))
VirtualMachineStartOnBootEnum = strawberry.enum(VirtualMachineStartOnBootChoices.as_enum(prefix='start_on_boot'))
VirtualMachineStatusEnum = strawberry.enum(VirtualMachineStatusChoices.as_enum(prefix='status'))
