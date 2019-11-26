from dcim.choices import DeviceStatusChoices

# VirtualMachine statuses (replicated from Device statuses)
VM_STATUS_CHOICES = [
    [1, 'Active'],
    [0, 'Offline'],
    [3, 'Staged'],
]

# Bootstrap CSS classes for VirtualMachine statuses
VM_STATUS_CLASSES = {
    0: 'warning',
    1: 'success',
    3: 'primary',
}
