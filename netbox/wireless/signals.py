import logging

from dcim.exceptions import UnsupportedCablePath
from dcim.models import CablePath
from dcim.utils import create_cablepaths
from utilities.exceptions import AbortRequest

# ──────────────────────────────────────────────────────────────────────
# Cascade handlers (update_connected_interfaces, nullify_connected_interfaces)
# have been moved to wireless/cascades.py as declarative CascadeSpecs.
#
# Cable path handlers are now dispatched by GraphRegistry (netbox/graphs.py).
# ──────────────────────────────────────────────────────────────────────


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


def delete_wireless_cable_paths(instance, **kwargs):
    """
    When a WirelessLink is deleted, delete and retrace any dependent cable paths.
    The interface nullification is handled by wireless/cascades.py.
    """
    for cablepath in CablePath.objects.filter(_nodes__contains=instance):
        cablepath.delete()
