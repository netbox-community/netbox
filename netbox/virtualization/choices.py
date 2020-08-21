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
