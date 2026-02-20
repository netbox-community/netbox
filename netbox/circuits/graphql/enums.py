import strawberry

from circuits.choices import *

__all__ = (
    'CircuitPriorityEnum',
    'CircuitStatusEnum',
    'CircuitTerminationSideEnum',
    'VirtualCircuitTerminationRoleEnum',
)


CircuitPriorityEnum = strawberry.enum(CircuitPriorityChoices.as_enum(prefix='priority'))
CircuitStatusEnum = strawberry.enum(CircuitStatusChoices.as_enum('status'))
CircuitTerminationSideEnum = strawberry.enum(CircuitTerminationSideChoices.as_enum(prefix='side'))
VirtualCircuitTerminationRoleEnum = strawberry.enum(VirtualCircuitTerminationRoleChoices.as_enum(prefix='role'))
