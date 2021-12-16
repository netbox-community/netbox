from utilities.choices import ChoiceSet


#
# VirtualMachines
#

class VirtualMachineStatusChoices(ChoiceSet):
    key = 'virtualization.VirtualMachine.status'

    STATUS_OFFLINE = 'offline'
    STATUS_ACTIVE = 'active'
    STATUS_PLANNED = 'planned'
    STATUS_STAGED = 'staged'
    STATUS_FAILED = 'failed'
    STATUS_DECOMMISSIONING = 'decommissioning'

    CHOICES = [
        (STATUS_OFFLINE, 'Offline', 'warning'),
        (STATUS_ACTIVE, 'Active', 'success'),
        (STATUS_PLANNED, 'Planned', 'info'),
        (STATUS_STAGED, 'Staged', 'primary'),
        (STATUS_FAILED, 'Failed', 'danger'),
        (STATUS_DECOMMISSIONING, 'Decommissioning', 'warning'),
    ]
