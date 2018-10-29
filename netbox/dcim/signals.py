from django.db.models.signals import post_save, post_delete, pre_delete
from django.dispatch import receiver

from .models import Cable, Device, VirtualChassis


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


@receiver(post_save, sender=Cable)
def update_connected_endpoints(instance, **kwargs):
    """
    When a Cable is saved, update its connected endpoints.
    """
    termination_a, termination_b = instance.get_path_endpoints()
    if termination_a is not None and termination_b is not None:
        termination_a.connected_endpoint = termination_b
        termination_a.connection_status = True
        termination_a.save()
        termination_b.connected_endpoint = termination_a
        termination_b.connection_status = True
        termination_b.save()


@receiver(post_delete, sender=Cable)
def nullify_connected_endpoints(instance, **kwargs):
    """
    When a Cable is deleted, nullify its connected endpoints.
    """
    termination_a, termination_b = instance.get_path_endpoints()
    if termination_a is not None and termination_b is not None:
        termination_a.connected_endpoint = None
        termination_a.connection_status = None
        termination_a.save()
        termination_b.connected_endpoint = None
        termination_b.connection_status = None
        termination_b.save()
