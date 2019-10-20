from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from .models import Cable, Device, VirtualChassis


@receiver(post_save, sender=VirtualChassis)
def assign_virtualchassis_master(instance, created, **kwargs):
    """
    When a VirtualChassis is created, automatically assign its master device to the VC.
    """
    if created:
        devices = Device.objects.filter(pk=instance.master.pk)
        for device in devices:
            device.virtual_chassis = instance
            device.vc_position = None
            device.save()


@receiver(pre_delete, sender=VirtualChassis)
def clear_virtualchassis_members(instance, **kwargs):
    """
    When a VirtualChassis is deleted, nullify the vc_position and vc_priority fields of its prior members.
    """
    devices = Device.objects.filter(virtual_chassis=instance.pk)
    for device in devices:
        device.vc_position = None
        device.vc_priority = None
        device.save()


@receiver(post_save, sender=Cable)
def update_connected_endpoints(instance, **kwargs):
    """
    When a Cable is saved, check for and update its two connected endpoints
    """

    # Cache the Cable on its two termination points
    if instance.termination_a.cable != instance:
        instance.termination_a.cable = instance
        instance.termination_a.save()
    if instance.termination_b.cable != instance:
        instance.termination_b.cable = instance
        instance.termination_b.save()

    # Update all endpoints affected by this cable
    endpoints = instance.get_related_endpoints()
    update_endpoints(endpoints)


@receiver(pre_delete, sender=Cable)
def nullify_connected_endpoints(instance, **kwargs):
    """
    When a Cable is deleted, check for and update its two connected endpoints
    """
    endpoints = instance.get_related_endpoints()

    # Disassociate the Cable from its termination points
    if instance.termination_a is not None:
        instance.termination_a.cable = None
        instance.termination_a.save()
    if instance.termination_b is not None:
        instance.termination_b.cable = None
        instance.termination_b.save()

    # Update all endpoints affected by this cable
    update_endpoints(endpoints, without_cable=instance)


def update_endpoints(endpoints, without_cable=None):
    """
    Update all endpoints affected by this cable
    """
    for endpoint in endpoints:
        if not hasattr(endpoint, 'connected_endpoint'):
            continue

        if endpoint.cable == without_cable:
            # We collected the endpoints before deleting the cable, so trace with the cable removed
            endpoint.cable = None

        path = endpoint.trace()

        # The trace returns left and right, we just want a single list
        # We also want to skip the first endpoint, which is the starting point itself
        endpoints = [
            item for sublist in (
                [left, right] for left, cable, right in path
            )
            for item in sublist if item
        ][1:]

        endpoint.connected_endpoint = endpoints[-1] if endpoints else None
        endpoint.via_endpoints = endpoints[:-1]
        endpoint.save()
