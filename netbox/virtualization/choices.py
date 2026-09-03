from django.utils.translation import gettext_lazy as _

from utilities.choices import Choice, ChoiceSet

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
        Choice(
            STATUS_PLANNED, _('Planned'), color='cyan',
            description=_('Designated for future use but not yet in service')
        ),
        Choice(
            STATUS_STAGING, _('Staging'), color='blue',
            description=_('Being prepared for production use')
        ),
        Choice(
            STATUS_ACTIVE, _('Active'), color='green',
            description=_('Fully operational and in service')
        ),
        Choice(
            STATUS_DECOMMISSIONING, _('Decommissioning'), color='yellow',
            description=_('Being removed from service')
        ),
        Choice(
            STATUS_OFFLINE, _('Offline'), color='red',
            description=_('Not currently in service')
        ),
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
        Choice(
            STATUS_OFFLINE, _('Offline'), color='gray',
            description=_('Powered off or not currently running')
        ),
        Choice(
            STATUS_ACTIVE, _('Active'), color='green',
            description=_('Powered on and operational')
        ),
        Choice(
            STATUS_PLANNED, _('Planned'), color='cyan',
            description=_('Designated for future use but not yet provisioned')
        ),
        Choice(
            STATUS_STAGED, _('Staged'), color='blue',
            description=_('Provisioned but not yet in service')
        ),
        Choice(
            STATUS_FAILED, _('Failed'), color='red',
            description=_('In an error state or otherwise not functioning')
        ),
        Choice(
            STATUS_DECOMMISSIONING, _('Decommissioning'), color='yellow',
            description=_('Being removed from service')
        ),
        Choice(
            STATUS_PAUSED, _('Paused'), color='orange',
            description=_('Suspended with its state retained in memory')
        ),
    ]


class VirtualMachineStartOnBootChoices(ChoiceSet):
    key = 'VirtualMachine.start_on_boot'

    STATUS_ON = 'on'
    STATUS_OFF = 'off'
    STATUS_LAST_STATE = 'laststate'

    CHOICES = [
        Choice(
            STATUS_ON, _('On'), color='green',
            description=_('Automatically start when the host boots')
        ),
        Choice(
            STATUS_OFF, _('Off'), color='gray',
            description=_('Do not start automatically when the host boots')
        ),
        Choice(
            STATUS_LAST_STATE, _('Last State'), color='cyan',
            description=_('Restore the power state the machine had before the host shut down')
        ),
    ]
