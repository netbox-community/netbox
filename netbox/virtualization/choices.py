from utilities.choices import ChoiceSet


#
# Clusters
#

class ClusterStatusChoices(ChoiceSet):
    key = 'Cluster.status'

    STATUS_PLANNED = 'planned'
    STATUS_STAGING = 'staging'
    STATUS_ACTIVE = 'active'
    STATUS_DECOMMISSIONING = 'decommissioning'
    STATUS_OFFLINE = 'offline'

    CHOICES = [
        (STATUS_PLANNED, 'Planned', 'cyan'),
        (STATUS_STAGING, 'Staging', 'blue'),
        (STATUS_ACTIVE, 'Active', 'green'),
        (STATUS_DECOMMISSIONING, 'Decommissioning', 'yellow'),
        (STATUS_OFFLINE, 'Offline', 'red'),
    ]


#
# VirtualMachines
#

class VirtualMachineStatusChoices(ChoiceSet):
    key = 'VirtualMachine.status'

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
