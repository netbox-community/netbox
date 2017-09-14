from __future__ import unicode_literals


# VirtualMachine statuses (replicated from Device statuses)
STATUS_OFFLINE = 0
STATUS_ACTIVE = 1
STATUS_STAGED = 3
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
