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
        (STATUS_OFFLINE, 'Offline', 'gray'),
        (STATUS_ACTIVE, 'Active', 'green'),
        (STATUS_PLANNED, 'Planned', 'cyan'),
        (STATUS_STAGED, 'Staged', 'blue'),
        (STATUS_FAILED, 'Failed', 'red'),
        (STATUS_DECOMMISSIONING, 'Decommissioning', 'yellow'),
    ]
