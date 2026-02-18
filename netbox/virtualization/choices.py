from django.utils.translation import gettext_lazy as _

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
        (STATUS_PLANNED, _('Planned'), 'cyan'),
        (STATUS_STAGING, _('Staging'), 'blue'),
        (STATUS_ACTIVE, _('Active'), 'green'),
        (STATUS_DECOMMISSIONING, _('Decommissioning'), 'yellow'),
        (STATUS_OFFLINE, _('Offline'), 'red'),
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
    STATUS_PAUSED = 'paused'

    CHOICES = [
        (STATUS_OFFLINE, _('Offline'), 'gray'),
        (STATUS_ACTIVE, _('Active'), 'green'),
        (STATUS_PLANNED, _('Planned'), 'cyan'),
        (STATUS_STAGED, _('Staged'), 'blue'),
        (STATUS_FAILED, _('Failed'), 'red'),
        (STATUS_DECOMMISSIONING, _('Decommissioning'), 'yellow'),
        (STATUS_PAUSED, _('Paused'), 'orange'),
    ]


class VirtualMachineStartOnBootChoices(ChoiceSet):
    key = 'VirtualMachine.start_on_boot'

    STATUS_ON = 'on'
    STATUS_OFF = 'off'
    STATUS_LAST_STATE = 'laststate'

    CHOICES = [
        (STATUS_ON, _('On'), 'green'),
        (STATUS_OFF, _('Off'), 'gray'),
        (STATUS_LAST_STATE, _('Last State'), 'cyan')
    ]
