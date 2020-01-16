from dcim.choices import InterfaceTypeChoices
from utilities.choices import ChoiceSet


#
# VirtualMachines
#

class VirtualMachineStatusChoices(ChoiceSet):

    STATUS_ACTIVE = 'active'
    STATUS_OFFLINE = 'offline'
    STATUS_STAGED = 'staged'

    CHOICES = (
        (STATUS_ACTIVE, 'Active'),
        (STATUS_OFFLINE, 'Offline'),
        (STATUS_STAGED, 'Staged'),
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
