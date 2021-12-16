from utilities.choices import ChoiceSet


#
# Circuits
#

class CircuitStatusChoices(ChoiceSet):
    key = 'circuits.Circuit.status'

    STATUS_DEPROVISIONING = 'deprovisioning'
    STATUS_ACTIVE = 'active'
    STATUS_PLANNED = 'planned'
    STATUS_PROVISIONING = 'provisioning'
    STATUS_OFFLINE = 'offline'
    STATUS_DECOMMISSIONED = 'decommissioned'

    CHOICES = [
        (STATUS_PLANNED, 'Planned', 'info'),
        (STATUS_PROVISIONING, 'Provisioning', 'primary'),
        (STATUS_ACTIVE, 'Active', 'success'),
        (STATUS_OFFLINE, 'Offline', 'danger'),
        (STATUS_DEPROVISIONING, 'Deprovisioning', 'warning'),
        (STATUS_DECOMMISSIONED, 'Decommissioned', 'secondary'),
    ]


#
# CircuitTerminations
#

class CircuitTerminationSideChoices(ChoiceSet):

    SIDE_A = 'A'
    SIDE_Z = 'Z'

    CHOICES = (
        (SIDE_A, 'A'),
        (SIDE_Z, 'Z')
    )
