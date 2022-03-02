from utilities.choices import ChoiceSet


#
# Circuits
#

class CircuitStatusChoices(ChoiceSet):
    key = 'Circuit.status'

    STATUS_DEPROVISIONING = 'deprovisioning'
    STATUS_ACTIVE = 'active'
    STATUS_PLANNED = 'planned'
    STATUS_PROVISIONING = 'provisioning'
    STATUS_OFFLINE = 'offline'
    STATUS_DECOMMISSIONED = 'decommissioned'

    CHOICES = [
        (STATUS_PLANNED, 'Planned', 'cyan'),
        (STATUS_PROVISIONING, 'Provisioning', 'blue'),
        (STATUS_ACTIVE, 'Active', 'green'),
        (STATUS_OFFLINE, 'Offline', 'red'),
        (STATUS_DEPROVISIONING, 'Deprovisioning', 'yellow'),
        (STATUS_DECOMMISSIONED, 'Decommissioned', 'gray'),
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
