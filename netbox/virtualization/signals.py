from django.db.models import Sum
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Cluster, VirtualDisk, VirtualMachine


@receiver((post_delete, post_save), sender=VirtualDisk)
def update_virtualmachine_disk(instance, **kwargs):
    """
    When a VirtualDisk has been modified, update the aggregate disk_size value of its VM.
    """
    vm = instance.virtual_machine
    VirtualMachine.objects.filter(pk=vm.pk).update(
        disk=vm.virtualdisks.aggregate(Sum('size'))['size__sum']
    )


@receiver(post_save, sender=Cluster)
def update_virtualmachine_site(instance, **kwargs):
    """
    Update the assigned site for all VMs to match that of the Cluster (if any).
    """
    if instance._site:
        VirtualMachine.objects.filter(cluster=instance).update(site=instance._site)
