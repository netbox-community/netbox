from django.db.models.signals import post_save, pre_delete
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

    # Cache the Cable on its two termination points
    instance.termination_a.cable = instance
    instance.termination_a.save()
    instance.termination_b.cable = instance
    instance.termination_b.save()

    # Check if this Cable has formed a complete path. If so, update both endpoints.
    endpoint_a, endpoint_b = instance.get_path_endpoints()
    if endpoint_a is not None and endpoint_b is not None:
        endpoint_a.connected_endpoint = endpoint_b
        endpoint_a.connection_status = True
        endpoint_a.save()
        endpoint_b.connected_endpoint = endpoint_a
        endpoint_b.connection_status = True
        endpoint_b.save()


@receiver(pre_delete, sender=Cable)
def nullify_connected_endpoints(instance, **kwargs):

    # Disassociate the Cable from its termination points
    if instance.termination_a is not None:
        instance.termination_a.cable = None
        instance.termination_a.save()
    if instance.termination_b is not None:
        instance.termination_b.cable = None
        instance.termination_b.save()

    # If this Cable was part of a complete path, tear it down
    endpoint_a, endpoint_b = instance.get_path_endpoints()
    if endpoint_a is not None and endpoint_b is not None:
        endpoint_a.connected_endpoint = None
        endpoint_a.connection_status = None
        endpoint_a.save()
        endpoint_b.connected_endpoint = None
        endpoint_b.connection_status = None
        endpoint_b.save()
