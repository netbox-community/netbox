from django.utils.translation import gettext_lazy as _

from utilities.choices import Choice, ChoiceSet

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
        Choice(
            STATUS_PLANNED, _('Planned'), color='cyan',
            description=_('Designated for future use but not yet installed')
        ),
        Choice(STATUS_PROVISIONING, _('Provisioning'), color='blue', description=_('Being configured for service')),
        Choice(STATUS_ACTIVE, _('Active'), color='green', description=_('Fully operational and in service')),
        Choice(STATUS_OFFLINE, _('Offline'), color='red', description=_('Installed but not currently in service')),
        Choice(STATUS_DEPROVISIONING, _('Deprovisioning'), color='yellow', description=_('Being removed from service')),
        Choice(
            STATUS_DECOMMISSIONED, _('Decommissioned'), color='gray',
            description=_('Retired and no longer in service')
        ),
    ]


class CircuitCommitRateChoices(ChoiceSet):
    key = 'Circuit.commit_rate'

    CHOICES = [
        Choice(10000, '10 Mbps'),
        Choice(100000, '100 Mbps'),
        Choice(1000000, '1 Gbps'),
        Choice(10000000, '10 Gbps'),
        Choice(25000000, '25 Gbps'),
        Choice(40000000, '40 Gbps'),
        Choice(100000000, '100 Gbps'),
        Choice(200000000, '200 Gbps'),
        Choice(400000000, '400 Gbps'),
        Choice(1544, 'T1 (1.544 Mbps)'),
        Choice(2048, 'E1 (2.048 Mbps)'),
    ]


#
# CircuitTerminations
#

class CircuitTerminationSideChoices(ChoiceSet):

    SIDE_A = 'A'
    SIDE_Z = 'Z'

    CHOICES = (
        Choice(SIDE_A, 'A'),
        Choice(SIDE_Z, 'Z')
    )


class CircuitTerminationPortSpeedChoices(ChoiceSet):
    key = 'CircuitTermination.port_speed'

    CHOICES = [
        Choice(10000, '10 Mbps'),
        Choice(100000, '100 Mbps'),
        Choice(1000000, '1 Gbps'),
        Choice(10000000, '10 Gbps'),
        Choice(25000000, '25 Gbps'),
        Choice(40000000, '40 Gbps'),
        Choice(100000000, '100 Gbps'),
        Choice(200000000, '200 Gbps'),
        Choice(400000000, '400 Gbps'),
        Choice(1544, 'T1 (1.544 Mbps)'),
        Choice(2048, 'E1 (2.048 Mbps)'),
    ]


class CircuitPriorityChoices(ChoiceSet):
    key = 'CircuitGroupAssignment.priority'

    PRIORITY_PRIMARY = 'primary'
    PRIORITY_SECONDARY = 'secondary'
    PRIORITY_TERTIARY = 'tertiary'
    PRIORITY_INACTIVE = 'inactive'

    CHOICES = [
        Choice(PRIORITY_PRIMARY, _('Primary')),
        Choice(PRIORITY_SECONDARY, _('Secondary')),
        Choice(PRIORITY_TERTIARY, _('Tertiary')),
        Choice(PRIORITY_INACTIVE, _('Inactive')),
    ]


#
# Virtual circuits
#

class VirtualCircuitTerminationRoleChoices(ChoiceSet):
    ROLE_PEER = 'peer'
    ROLE_HUB = 'hub'
    ROLE_SPOKE = 'spoke'

    CHOICES = [
        Choice(ROLE_PEER, _('Peer'), color='green', description=_('Connects to other peers as an equal endpoint')),
        Choice(ROLE_HUB, _('Hub'), color='blue', description=_('Central endpoint to which spokes connect')),
        Choice(ROLE_SPOKE, _('Spoke'), color='orange', description=_('Remote endpoint connecting to a hub')),
    ]
