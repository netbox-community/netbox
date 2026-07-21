import logging

from django.db.models import Q
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from dcim.choices import CableEndChoices, LinkStatusChoices
from netbox.search.backends import search_backend
from utilities.querysets import chunked_update
from virtualization.models import VMInterface

from .models import (
    Cable,
    CablePath,
    CableTermination,
    Device,
    Interface,
    Location,
    PathEndpoint,
    PortMapping,
    PowerPanel,
    Rack,
    VirtualChassis,
)
from .models.cables import trace_paths
from .search import DeviceIndex
from .utils import create_cablepaths, rebuild_paths

#
# Location/rack/device assignment
#


@receiver(post_save, sender=Location)
def handle_location_site_change(instance, created, **kwargs):
    """
    Cascade a Location's Site assignment down to the Racks, Devices, and PowerPanels it contains
    (and to descendant Locations).
    """
    if not created:
        chunked_update(instance.get_descendants(), site=instance.site)
        locations = instance.get_descendants(include_self=True).values_list('pk', flat=True)
        chunked_update(Rack.objects.filter(location__in=locations), site=instance.site)
        chunked_update(Device.objects.filter(location__in=locations), site=instance.site)
        chunked_update(PowerPanel.objects.filter(location__in=locations), site=instance.site)


@receiver(post_save, sender=Rack)
def handle_rack_site_change(instance, created, **kwargs):
    """
    Cascade a Rack's Site/Location assignment down to the Devices it contains.
    """
    if not created:
        chunked_update(Device.objects.filter(rack=instance), site=instance.site, location=instance.location)


#
# Virtual chassis
#

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


@receiver(post_save, sender=VirtualChassis)
def update_virtualchassis_member_search_cache(instance, created, raw=False, update_fields=None, **kwargs):
    """
    Refresh the search cache for member Devices when a VirtualChassis is renamed. DeviceIndex caches
    virtual_chassis as its string value, so a rename would otherwise leave stale CachedValue entries.
    """
    if raw or created:
        return
    # The VC name is the only VC attribute cached on member Devices; skip saves that can't change it.
    if update_fields is not None and 'name' not in update_fields:
        return
    search_backend.cache(
        Device.objects.filter(virtual_chassis=instance).select_related('virtual_chassis'),
        indexer=DeviceIndex,
        remove_existing=True
    )


#
# Cables
#

@receiver(trace_paths, sender=Cable)
def update_connected_endpoints(instance, created, raw=False, **kwargs):
    """
    When a Cable is saved with new terminations, retrace any affected cable paths.
    """
    logger = logging.getLogger('netbox.dcim.cable')
    if raw:
        logger.debug(f"Skipping endpoint updates for imported cable {instance}")
        return

    # Update cable paths if new terminations have been set
    if instance._terminations_modified:
        a_terminations = []
        b_terminations = []
        # Note: instance.terminations.all() is not safe to use here as it might be stale
        for t in CableTermination.objects.filter(cable=instance):
            if t.cable_end == CableEndChoices.SIDE_A:
                a_terminations.append(t.termination)
            else:
                b_terminations.append(t.termination)
        for nodes in [a_terminations, b_terminations]:
            # Examine type of first termination to determine object type (all must be the same)
            if not nodes:
                continue
            if isinstance(nodes[0], PathEndpoint):
                create_cablepaths(nodes)
            else:
                rebuild_paths(nodes)

    # Update status of CablePaths if Cable status has been changed
    elif instance.status != instance._orig_status:
        if instance.status != LinkStatusChoices.STATUS_CONNECTED:
            chunked_update(CablePath.objects.filter(_nodes__contains=instance), is_active=False)
        else:
            rebuild_paths([instance])


@receiver(post_delete, sender=Cable)
def retrace_cable_paths(instance, **kwargs):
    """
    When a Cable is deleted, check for and update its connected endpoints
    """
    for cablepath in CablePath.objects.filter(_nodes__contains=instance):
        cablepath.retrace()


@receiver((post_delete, post_save), sender=PortMapping)
def update_passthrough_port_paths(instance, **kwargs):
    """
    When a PortMapping is created or deleted, retrace any CablePaths which traverse its front and/or rear ports.
    """
    for cablepath in CablePath.objects.filter(
        Q(_nodes__contains=instance.front_port) | Q(_nodes__contains=instance.rear_port)
    ):
        cablepath.retrace()


@receiver(post_delete, sender=CableTermination)
def nullify_connected_endpoints(instance, **kwargs):
    """
    Disassociate the Cable from the termination object, and retrace any affected CablePaths.
    """
    model = instance.termination_type.model_class()
    model.objects.filter(pk=instance.termination_id).update(cable=None, cable_end='')

    # If the parent Cable is being deleted in this same operation, skip the
    # per-termination retrace; retrace_cable_paths() will retrace each affected
    # path once after the Cable is deleted.
    if Cable._is_being_deleted(instance.cable_id):
        return

    for cablepath in CablePath.objects.filter(_nodes__contains=instance.cable):
        # Remove the deleted CableTermination if it's one of the path's originating nodes
        if instance.termination in cablepath.origins:
            cablepath.origins.remove(instance.termination)
            # Clear _path on the removed origin to prevent stale connection display
            model.objects.filter(pk=instance.termination_id, _path=cablepath.pk).update(_path=None)
        cablepath.retrace()


@receiver(post_save, sender=Interface)
@receiver(post_save, sender=VMInterface)
def update_mac_address_interface(instance, created, raw, **kwargs):
    """
    When creating a new Interface or VMInterface, check whether a MACAddress has been designated as its primary. If so,
    assign the MACAddress to the interface.
    """
    if created and not raw and instance.primary_mac_address:
        instance.primary_mac_address.assigned_object = instance
        instance.primary_mac_address.save()
