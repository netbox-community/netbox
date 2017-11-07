from __future__ import unicode_literals

from dcim.constants import STATUS_ACTIVE, STATUS_OFFLINE, STATUS_STAGED

# VirtualMachine statuses (replicated from Device statuses)
STATUS_CHOICES = [
    [STATUS_ACTIVE, 'Active'],
    [STATUS_OFFLINE, 'Offline'],
    [STATUS_STAGED, 'Staged'],
]

# Bootstrap CSS classes for VirtualMachine statuses
VM_STATUS_CLASSES = {
    0: 'warning',
    1: 'success',
    3: 'primary',
}
