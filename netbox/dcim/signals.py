import logging

from django.db.models import Q

from dcim.choices import CableEndChoices, LinkStatusChoices

from .models import (
    CablePath,
    CableTermination,
    PathEndpoint,
)
from .utils import create_cablepaths, rebuild_paths

# ──────────────────────────────────────────────────────────────────────
# Cascade handlers (location/rack/device site propagation, VC master,
# MAC address, scope fields, cable termination nullification) have been
# moved to dcim/cascades.py as declarative CascadeSpecs.
# ──────────────────────────────────────────────────────────────────────

# ──────────────────────────────────────────────────────────────────────
# Cable graph operations
# All dispatched by GraphRegistry (netbox/graphs.py) for post_delete,
# or called directly from Cable.save() for post-save path rebuild.
# The custom trace_paths signal has been eliminated.
# ──────────────────────────────────────────────────────────────────────

def update_connected_endpoints(instance, created=False, raw=False, **kwargs):
    """
    When a Cable is saved with new terminations, retrace any affected cable paths.
    """
    logger = logging.getLogger('netbox.dcim.cable')
    if raw:
        logger.debug(f"Skipping endpoint updates for imported cable {instance}")
        return

    if instance._terminations_modified:
        a_terminations = []
        b_terminations = []
        for t in CableTermination.objects.filter(cable=instance):
            if t.cable_end == CableEndChoices.SIDE_A:
                a_terminations.append(t.termination)
            else:
                b_terminations.append(t.termination)
        for nodes in [a_terminations, b_terminations]:
            if not nodes:
                continue
            if isinstance(nodes[0], PathEndpoint):
                create_cablepaths(nodes)
            else:
                rebuild_paths(nodes)

    elif instance.status != instance._orig_status:
        if instance.status != LinkStatusChoices.STATUS_CONNECTED:
            CablePath.objects.filter(_nodes__contains=instance).update(is_active=False)
        else:
            rebuild_paths([instance])


def retrace_cable_paths(instance, **kwargs):
    """
    When a Cable is deleted, check for and update its connected endpoints.
    """
    for cablepath in CablePath.objects.filter(_nodes__contains=instance):
        cablepath.retrace()


def update_passthrough_port_paths(instance, **kwargs):
    """
    When a PortMapping is created or deleted, retrace any CablePaths which traverse its front
    and/or rear ports.
    """
    for cablepath in CablePath.objects.filter(
        Q(_nodes__contains=instance.front_port) | Q(_nodes__contains=instance.rear_port)
    ):
        cablepath.retrace()


def retrace_paths_on_termination_delete(instance, **kwargs):
    """
    When a CableTermination is deleted, retrace any affected CablePaths.
    The cascade part (nullifying cable on the target) is in dcim/cascades.py.
    """
    for cablepath in CablePath.objects.filter(_nodes__contains=instance.cable):
        if instance.termination in cablepath.origins:
            cablepath.origins.remove(instance.termination)
            model = instance.termination_type.model_class()
            model.objects.filter(pk=instance.termination_id, _path=cablepath.pk).update(_path=None)
        cablepath.retrace()
