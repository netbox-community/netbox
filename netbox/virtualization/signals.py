from django.db.models import Sum
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Cluster, VirtualDisk, VirtualMachine


@receiver((post_delete, post_save), sender=VirtualDisk)
def update_virtualmachine_disk(instance, using=None, **kwargs):
    """
    When a VirtualDisk has been modified, update the aggregate disk_size value of its VM.
    """
    disks = VirtualDisk.objects.using(using).filter(virtual_machine_id=instance.virtual_machine_id)
    VirtualMachine.objects.using(using).filter(pk=instance.virtual_machine_id).update(
        disk=disks.aggregate(Sum('size'))['size__sum']
    )


@receiver(post_save, sender=Cluster)
def update_virtualmachine_site(instance, using=None, **kwargs):
    """
    Update the assigned site for all VMs to match that of the Cluster (if any).
    """
    if instance._site_id:
        VirtualMachine.objects.using(using).filter(cluster=instance).update(site_id=instance._site_id)
