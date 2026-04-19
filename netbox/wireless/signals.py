import logging

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from dcim.exceptions import UnsupportedCablePath
from dcim.models import CablePath
from dcim.utils import create_cablepaths
from utilities.exceptions import AbortRequest

from .models import WirelessLink

# ──────────────────────────────────────────────────────────────────────
# Cascade handlers (update_connected_interfaces, nullify_connected_interfaces)
# have been moved to wireless/cascades.py as declarative CascadeSpecs.
#
# Cable path creation on WirelessLink create and cable path deletion
# on WirelessLink delete will be moved to GraphRegistry in a future phase.
# For now, keep cable path creation here.
# ──────────────────────────────────────────────────────────────────────


@receiver(post_save, sender=WirelessLink)
def create_wireless_cable_paths(instance, created, raw=False, **kwargs):
    """
    When a WirelessLink is first created, create cable paths for its interfaces.
    """
    logger = logging.getLogger('netbox.wireless.wirelesslink')
    if raw:
        logger.debug(f"Skipping cable path creation for imported wireless link {instance}")
        return

    if created:
        for interface in (instance.interface_a, instance.interface_b):
            try:
                create_cablepaths([interface])
            except UnsupportedCablePath as e:
                raise AbortRequest(e)


@receiver(post_delete, sender=WirelessLink)
def delete_wireless_cable_paths(instance, **kwargs):
    """
    When a WirelessLink is deleted, delete and retrace any dependent cable paths.
    The interface nullification is handled by wireless/cascades.py.
    """
    for cablepath in CablePath.objects.filter(_nodes__contains=instance):
        cablepath.delete()
