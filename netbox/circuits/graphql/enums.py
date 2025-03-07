import strawberry

from circuits.choices import *

__all__ = (
    'CircuitStatusEnum',
    'CircuitCommitRateEnum',
    'CircuitTerminationSideEnum',
    'CircuitTerminationPortSpeedEnum',
    'CircuitPriorityEnum',
    'VirtualCircuitTerminationRoleEnum',
)


CircuitCommitRateEnum = strawberry.enum(CircuitCommitRateChoices.as_enum())
CircuitPriorityEnum = strawberry.enum(CircuitPriorityChoices.as_enum())
CircuitStatusEnum = strawberry.enum(CircuitStatusChoices.as_enum())
CircuitTerminationSideEnum = strawberry.enum(CircuitTerminationSideChoices.as_enum())
CircuitTerminationPortSpeedEnum = strawberry.enum(CircuitTerminationPortSpeedChoices.as_enum())
VirtualCircuitTerminationRoleEnum = strawberry.enum(VirtualCircuitTerminationRoleChoices.as_enum())
