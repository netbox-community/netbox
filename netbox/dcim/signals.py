from __future__ import unicode_literals

from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from .models import Device, VirtualChassis


@receiver(post_save, sender=VirtualChassis)
def assign_virtualchassis_master(instance, created, **kwargs):
    """
    When a VirtualChassis is created, automatically assign its master device to the VC.
    """
    if created:
        Device.objects.filter(pk=instance.master.pk).update(virtual_chassis=instance, vc_position=None)


@receiver(pre_delete, sender=VirtualChassis)
def clear_virtualchassis_members(instance, **kwargs):
    """
    When a VirtualChassis is deleted, nullify the vc_position and vc_priority fields of its prior members.
    """
    Device.objects.filter(virtual_chassis=instance.pk).update(vc_position=None, vc_priority=None)
