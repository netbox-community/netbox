from utilities.choices import ChoiceSet


#
# VirtualMachines
#

UNIT_MB = 'mb'
UNIT_GB = 'gb'
UNIT_TB = 'tb'

MEMORY_MULTIPLIERS = {
    UNIT_MB: 1024**0,
    UNIT_GB: 1024**1,
    UNIT_TB: 1024**2,
}

DISK_MULTIPLIERS = {
    UNIT_GB: 1024**0,
    UNIT_TB: 1024**1,
}


class DiskUnitChoices(ChoiceSet):

    CHOICES = (
        (UNIT_GB, 'GB'),
        (UNIT_TB, 'TB'),
    )


class MemoryUnitChoices(ChoiceSet):

    CHOICES = (
        (UNIT_MB, 'MB'),
        (UNIT_GB, 'GB'),
        (UNIT_TB, 'TB'),
    )


class VirtualMachineStatusChoices(ChoiceSet):

    STATUS_OFFLINE = 'offline'
    STATUS_ACTIVE = 'active'
    STATUS_PLANNED = 'planned'
    STATUS_STAGED = 'staged'
    STATUS_FAILED = 'failed'
    STATUS_DECOMMISSIONING = 'decommissioning'

    CHOICES = (
        (STATUS_OFFLINE, 'Offline'),
        (STATUS_ACTIVE, 'Active'),
        (STATUS_PLANNED, 'Planned'),
        (STATUS_STAGED, 'Staged'),
        (STATUS_FAILED, 'Failed'),
        (STATUS_DECOMMISSIONING, 'Decommissioning'),
    )

    CSS_CLASSES = {
        STATUS_OFFLINE: 'warning',
        STATUS_ACTIVE: 'success',
        STATUS_PLANNED: 'info',
        STATUS_STAGED: 'primary',
        STATUS_FAILED: 'danger',
        STATUS_DECOMMISSIONING: 'warning',
    }
