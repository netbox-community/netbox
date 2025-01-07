from enum import Enum
import strawberry

__all__ = [
    'CircuitStatusEnum',
    'CircuitCommitRateEnum',
    'CircuitTerminationSideEnum',
    'CircuitTerminationPortSpeedEnum',
    'CircuitPriorityEnum',
    'VirtualCircuitTerminationRoleEnum',
]

#
# Circuits
#


@strawberry.enum
class CircuitStatusEnum(Enum):
    STATUS_DEPROVISIONING = 'deprovisioning'
    STATUS_ACTIVE = 'active'
    STATUS_PLANNED = 'planned'
    STATUS_PROVISIONING = 'provisioning'
    STATUS_OFFLINE = 'offline'
    STATUS_DECOMMISSIONED = 'decommissioned'


@strawberry.enum
class CircuitCommitRateEnum(Enum):
    TEN_MBPS = 10000
    HUNDRED_MBPS = 100000
    ONE_GBPS = 1000000
    TEN_GBPS = 10000000
    TWENTY_FIVE_GBPS = 25000000
    FORTY_GBPS = 40000000
    HUNDRED_GBPS = 100000000
    TWO_HUNDRED_GBPS = 200000000
    FOUR_HUNDRED_GBPS = 400000000
    T1 = 1544
    E1 = 2048


#
# CircuitTerminations
#


@strawberry.enum
class CircuitTerminationSideEnum(Enum):
    SIDE_A = 'A'
    SIDE_Z = 'Z'


@strawberry.enum
class CircuitTerminationPortSpeedEnum(Enum):
    TEN_MBPS = 10000
    HUNDRED_MBPS = 100000
    ONE_GBPS = 1000000
    TEN_GBPS = 10000000
    TWENTY_FIVE_GBPS = 25000000
    FORTY_GBPS = 40000000
    HUNDRED_GBPS = 100000000
    TWO_HUNDRED_GBPS = 200000000
    FOUR_HUNDRED_GBPS = 400000000
    T1 = 1544
    E1 = 2048


@strawberry.enum
class CircuitPriorityEnum(Enum):
    PRIORITY_PRIMARY = 'primary'
    PRIORITY_SECONDARY = 'secondary'
    PRIORITY_TERTIARY = 'tertiary'
    PRIORITY_INACTIVE = 'inactive'


#
# Virtual circuits
#


@strawberry.enum
class VirtualCircuitTerminationRoleEnum(Enum):
    ROLE_PEER = 'peer'
    ROLE_HUB = 'hub'
    ROLE_SPOKE = 'spoke'
