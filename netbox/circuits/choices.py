from utilities.choices import ChoiceSet


#
# Circuits
#

class CircuitStatusChoices(ChoiceSet):

    STATUS_DEPROVISIONING = 'deprovisioning'
    STATUS_ACTIVE = 'active'
    STATUS_PLANNED = 'planned'
    STATUS_PROVISIONING = 'provisioning'
    STATUS_OFFLINE = 'offline'
    STATUS_DECOMMISSIONED = 'decommissioned'

    CHOICES = (
        (STATUS_PLANNED, 'Planned'),
        (STATUS_PROVISIONING, 'Provisioning'),
        (STATUS_ACTIVE, 'Active'),
        (STATUS_OFFLINE, 'Offline'),
        (STATUS_DEPROVISIONING, 'Deprovisioning'),
        (STATUS_DECOMMISSIONED, 'Decommissioned'),
    )

    CSS_CLASSES = {
        STATUS_DEPROVISIONING: 'warning',
        STATUS_ACTIVE: 'success',
        STATUS_PLANNED: 'info',
        STATUS_PROVISIONING: 'primary',
        STATUS_OFFLINE: 'danger',
        STATUS_DECOMMISSIONED: 'default',
    }


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
