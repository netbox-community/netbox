from dcim.choices import InterfaceTypeChoices
from utilities.choices import ChoiceSet


#
# VirtualMachines
#

class VirtualMachineStatusChoices(ChoiceSet):

    STATUS_ACTIVE = 'active'
    STATUS_OFFLINE = 'offline'
    STATUS_STAGED = 'staged'
    STATUS_DECOMMISSIONING = 'decommissioning'

    CHOICES = (
        (STATUS_ACTIVE, 'Active'),
        (STATUS_OFFLINE, 'Offline'),
        (STATUS_STAGED, 'Staged'),
        (STATUS_DECOMMISSIONING, 'Decommissioning'),
    )

    LEGACY_MAP = {
        STATUS_OFFLINE: 0,
        STATUS_ACTIVE: 1,
        STATUS_STAGED: 3,
        STATUS_DECOMMISSIONING: 4,
    }


#
# Interface types (for VirtualMachines)
#

class VMInterfaceTypeChoices(ChoiceSet):

    TYPE_VIRTUAL = InterfaceTypeChoices.TYPE_VIRTUAL

    CHOICES = (
        (TYPE_VIRTUAL, 'Virtual'),
    )
