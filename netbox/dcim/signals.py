import logging

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
    logger = logging.getLogger('netbox.dcim.cable')

    # Cache the Cable on its two termination points
    if instance.termination_a.cable != instance:
        logger.debug("Updating termination A for cable {}".format(instance))
        instance.termination_a.cable = instance
        instance.termination_a.save()
    if instance.termination_b.cable != instance:
        logger.debug("Updating termination B for cable {}".format(instance))
        instance.termination_b.cable = instance
        instance.termination_b.save()

    # Check if this Cable has formed a complete path. If so, update both endpoints.
    endpoint_a, endpoint_b, path_status = instance.get_path_endpoints()
    if getattr(endpoint_a, 'is_path_endpoint', False) and getattr(endpoint_b, 'is_path_endpoint', False):
        logger.debug("Updating path endpoints: {} <---> {}".format(endpoint_a, endpoint_b))
        endpoint_a.connected_endpoint = endpoint_b
        endpoint_a.connection_status = path_status
        endpoint_a.save()
        endpoint_b.connected_endpoint = endpoint_a
        endpoint_b.connection_status = path_status
        endpoint_b.save()


@receiver(pre_delete, sender=Cable)
def nullify_connected_endpoints(instance, **kwargs):
    """
    When a Cable is deleted, check for and update its two connected endpoints
    """
    logger = logging.getLogger('netbox.dcim.cable')

    endpoint_a, endpoint_b, _ = instance.get_path_endpoints()

    # Disassociate the Cable from its termination points
    if instance.termination_a is not None:
        logger.debug("Nullifying termination A for cable {}".format(instance))
        instance.termination_a.cable = None
        instance.termination_a.save()
    if instance.termination_b is not None:
        logger.debug("Nullifying termination B for cable {}".format(instance))
        instance.termination_b.cable = None
        instance.termination_b.save()

    # If this Cable was part of a complete path, tear it down
    if hasattr(endpoint_a, 'connected_endpoint') and hasattr(endpoint_b, 'connected_endpoint'):
        logger.debug("Tearing down path ({} <---> {})".format(endpoint_a, endpoint_b))
        endpoint_a.connected_endpoint = None
        endpoint_a.connection_status = None
        endpoint_a.save()
        endpoint_b.connected_endpoint = None
        endpoint_b.connection_status = None
        endpoint_b.save()
