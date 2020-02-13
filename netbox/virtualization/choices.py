from dcim.choices import InterfaceTypeChoices
from utilities.choices import ChoiceSet


#
# VirtualMachines
#

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

    LEGACY_MAP = {
        STATUS_OFFLINE: 0,
        STATUS_ACTIVE: 1,
        STATUS_STAGED: 3,
    }


#
# Interface types (for VirtualMachines)
#

class VMInterfaceTypeChoices(ChoiceSet):

    TYPE_VIRTUAL = InterfaceTypeChoices.TYPE_VIRTUAL

    CHOICES = (
        (TYPE_VIRTUAL, 'Virtual'),
    )
