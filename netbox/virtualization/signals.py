from django.db.models import Sum
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import VirtualDisk, VirtualMachine


@receiver((post_delete, post_save), sender=VirtualDisk)
def update_virtualmachine_disk(instance, **kwargs):
    """
    When a VirtualDisk has been modified, update the aggregate disk_size value of its VM.
    """
    vm = instance.virtual_machine
    VirtualMachine.objects.filter(pk=vm.pk).update(
        disk=vm.virtualdisks.aggregate(Sum('size'))['size__sum']
    )
