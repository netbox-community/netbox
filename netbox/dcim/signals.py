import logging

from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save, pre_delete
from django.db import transaction
from django.dispatch import receiver

from .choices import CableStatusChoices
from .models import Cable, CablePath, Device, PathEndpoint, VirtualChassis
from .utils import object_to_path_node, trace_path


def create_cablepath(node):
    """
    Create CablePaths for all paths originating from the specified node.
    """
    path, destination, is_connected = trace_path(node)
    if path:
        cp = CablePath(origin=node, path=path, destination=destination, is_connected=is_connected)
        cp.save()


def rebuild_paths(obj):
    """
    Rebuild all CablePaths which traverse the specified node
    """
    node = object_to_path_node(obj)
    cable_paths = CablePath.objects.filter(path__contains=[node])

    with transaction.atomic():
        for cp in cable_paths:
            cp.delete()
            create_cablepath(cp.origin)


@receiver(post_save, sender=VirtualChassis)
def assign_virtualchassis_master(instance, created, **kwargs):
    """
    When a VirtualChassis is created, automatically assign its master device (if any) to the VC.
    """
    if created and instance.master:
        master = Device.objects.get(pk=instance.master.pk)
        master.virtual_chassis = instance
        master.vc_position = 1
        master.save()


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
def update_connected_endpoints(instance, created, **kwargs):
    """
    When a Cable is saved, check for and update its two connected endpoints
    """
    logger = logging.getLogger('netbox.dcim.cable')

    # Cache the Cable on its two termination points
    if instance.termination_a.cable != instance:
        logger.debug(f"Updating termination A for cable {instance}")
        instance.termination_a.cable = instance
        instance.termination_a.save()
    if instance.termination_b.cable != instance:
        logger.debug(f"Updating termination B for cable {instance}")
        instance.termination_b.cable = instance
        instance.termination_b.save()

    # Create/update cable paths
    if created:
        for termination in (instance.termination_a, instance.termination_b):
            if isinstance(termination, PathEndpoint):
                create_cablepath(termination)
            else:
                rebuild_paths(termination)
    elif instance.status != instance._orig_status:
        # We currently don't support modifying either termination of an existing Cable. (This
        # may change in the future.) However, we do need to capture status changes and update
        # any CablePaths accordingly.
        if instance.status != CableStatusChoices.STATUS_CONNECTED:
            CablePath.objects.filter(path__contains=[object_to_path_node(instance)]).update(is_connected=False)
        else:
            rebuild_paths(instance)


@receiver(pre_delete, sender=Cable)
def nullify_connected_endpoints(instance, **kwargs):
    """
    When a Cable is deleted, check for and update its two connected endpoints
    """
    logger = logging.getLogger('netbox.dcim.cable')

    # Disassociate the Cable from its termination points
    if instance.termination_a is not None:
        logger.debug(f"Nullifying termination A for cable {instance}")
        instance.termination_a.cable = None
        instance.termination_a.save()
    if instance.termination_b is not None:
        logger.debug(f"Nullifying termination B for cable {instance}")
        instance.termination_b.cable = None
        instance.termination_b.save()

    # Delete any dependent cable paths
    cable_paths = CablePath.objects.filter(path__contains=[object_to_path_node(instance)])
    retrace_queue = [cp.origin for cp in cable_paths]
    deleted, _ = cable_paths.delete()
    logger.info(f'Deleted {deleted} cable paths')

    # Retrace cable paths from the origins of deleted paths
    for origin in retrace_queue:
        # Delete and recreate all CablePaths for this origin point
        # TODO: We can probably be smarter about skipping unchanged paths
        CablePath.objects.filter(
            origin_type=ContentType.objects.get_for_model(origin),
            origin_id=origin.pk
        ).delete()
        create_cablepath(origin)
