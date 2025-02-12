from enum import Enum
import strawberry

__all__ = ['ClusterStatusEnum', 'VirtualMachineStatusEnum']


#
# Clusters
#

@strawberry.enum
class ClusterStatusEnum(Enum):

    STATUS_PLANNED = 'planned'
    STATUS_STAGING = 'staging'
    STATUS_ACTIVE = 'active'
    STATUS_DECOMMISSIONING = 'decommissioning'
    STATUS_OFFLINE = 'offline'


#
# VirtualMachines
#

@strawberry.enum
class VirtualMachineStatusEnum(Enum):

    STATUS_OFFLINE = 'offline'
    STATUS_ACTIVE = 'active'
    STATUS_PLANNED = 'planned'
    STATUS_STAGED = 'staged'
    STATUS_FAILED = 'failed'
    STATUS_DECOMMISSIONING = 'decommissioning'
