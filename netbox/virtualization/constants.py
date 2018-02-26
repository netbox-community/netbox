from __future__ import unicode_literals

from dcim.constants import DEVICE_STATUS_ACTIVE, DEVICE_STATUS_OFFLINE, DEVICE_STATUS_STAGED

# VirtualMachine statuses (replicated from Device statuses)
VM_STATUS_CHOICES = [
    [DEVICE_STATUS_ACTIVE, 'Active'],
    [DEVICE_STATUS_OFFLINE, 'Offline'],
    [DEVICE_STATUS_STAGED, 'Staged'],
]

# Bootstrap CSS classes for VirtualMachine statuses
VM_STATUS_CLASSES = {
    0: 'warning',
    1: 'success',
    3: 'primary',
}
