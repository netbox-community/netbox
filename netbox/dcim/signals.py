import logging

from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.models import F, Q
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from dcim.choices import CableEndChoices, LinkStatusChoices
from ipam.models import Prefix
from netbox.search.backends import search_backend
from virtualization.models import Cluster, VMInterface
from wireless.models import WirelessLAN

from .models import (
    Cable,
    CablePath,
    CableTermination,
    ConsolePort,
    ConsoleServerPort,
    Device,
    DeviceBay,
    FrontPort,
    Interface,
    InventoryItem,
    Location,
    ModuleBay,
    PathEndpoint,
    PortMapping,
    PowerOutlet,
    PowerPanel,
    PowerPort,
    Rack,
    RearPort,
    Site,
    VirtualChassis,
)
from .models.cables import trace_paths
from .search import DeviceIndex
from .utils import create_cablepaths, rebuild_paths

COMPONENT_MODELS = (
    ConsolePort,
    ConsoleServerPort,
    DeviceBay,
    FrontPort,
    Interface,
    InventoryItem,
    ModuleBay,
    PowerOutlet,
    PowerPort,
    RearPort,
)


#
# Location/rack/device assignment
#

@receiver(pre_save, sender=Location)
@receiver(pre_save, sender=Site)
def cache_presave_scope_fields(instance, raw=False, using=None, **kwargs):
    """
    Stash the scope-relevant field values currently in the database so that the post_save
    handlers below can determine whether this save actually changed any of them. The read
    locks the row, so overlapping saves of the same object serialize here and the
    comparison always runs against the final committed state.

    Outside of a transaction no stash is taken (and any stash left by a previous
    transactional save of the same instance is cleared): in autocommit, this read and the
    subsequent UPDATE would run in separate transactions, so the comparison could race a
    concurrent save. The post_save handlers treat a missing stash as "the values may have
    changed" and rebuild or repair unconditionally.
    """
    if raw or instance.pk is None:
        return
    if not transaction.get_connection(using).in_atomic_block:
        instance._presave_scope_fields = None
        return
    fields = ('region_id', 'group_id') if isinstance(instance, Site) else ('site_id',)
    instance._presave_scope_fields = (
        instance.__class__.objects.using(using)
        .filter(pk=instance.pk)
        # no_key: serializes overlapping saves of this object without blocking foreign
        # key inserts that reference it
        .select_for_update(no_key=True)
        .values(*fields)
        .first()
    )


@receiver(post_save, sender=Location)
def handle_location_site_change(instance, created, **kwargs):
    """
    Update child objects when a Location is saved. All updates are queryset update() calls,
    which fire no signals and generate no change records for the affected objects.
    """
    if created:
        return
    with transaction.atomic(savepoint=False):
        instance.get_descendants().update(site=instance.site)
        # Materialized once so every statement below sees the same membership, even if a
        # concurrent commit renumbers the tree mid-handler.
        locations = list(instance.get_descendants(include_self=True).values_list('pk', flat=True))
        Rack.objects.filter(location__in=locations).update(site=instance.site)
        Device.objects.filter(location__in=locations).update(site=instance.site)
        PowerPanel.objects.filter(location__in=locations).update(site=instance.site)
        CableTermination.objects.filter(_location__in=locations).update(_site=instance.site)
        # Update component models for devices in these locations
        for model in COMPONENT_MODELS:
            model.objects.filter(device__location__in=locations).update(_site=instance.site)

        # Objects scoped to descendant Locations receive no post_save of their own from the
        # queryset updates above, so their cached scope fields are updated here whenever the
        # Site assignment has actually changed. (Objects scoped to this Location itself are
        # recomputed by sync_cached_scope_fields on this same save.) Values are read fresh
        # from the database rather than taken from the saved instance, whose cached site
        # relation may be stale.
        prev = getattr(instance, '_presave_scope_fields', None)
        if prev is None or prev['site_id'] != instance.site_id:
            # Lock the destination Site (without blocking FK inserts that reference it) so
            # a concurrent scope change on that Site serializes against this move; an
            # unlocked read could stamp region/group values from before that change.
            site = (
                Site.objects.filter(pk=instance.site_id)
                .select_for_update(no_key=True)
                .values('region_id', 'group_id')
                .first()
            )
            if site is not None:
                # Select rows through the authoritative scope rather than the cached
                # _location, which may itself be stale; scope_id doubles as the correct
                # _location value for Location-scoped rows.
                location_ct = ContentType.objects.get_for_model(Location)
                for model in (Prefix, Cluster, WirelessLAN):
                    model.objects.filter(scope_type=location_ct, scope_id__in=locations).update(
                        _location_id=F('scope_id'),
                        _site_id=instance.site_id,
                        _region_id=site['region_id'],
                        _site_group_id=site['group_id'],
                    )


@receiver(post_save, sender=Rack)
def handle_rack_site_change(instance, created, **kwargs):
    """
    Update child Devices if Site or Location assignment has changed.
    """
    if not created:
        Device.objects.filter(rack=instance).update(site=instance.site, location=instance.location)
        # Update component models for devices in this rack
        for model in COMPONENT_MODELS:
            model.objects.filter(device__rack=instance).update(
                _site=instance.site,
                _location=instance.location,
            )


@receiver(post_save, sender=Device)
def handle_device_site_change(instance, created, **kwargs):
    """
    Update child components to update the parent Site, Location, and Rack when a Device is saved.
    """
    if not created:
        for model in COMPONENT_MODELS:
            model.objects.filter(device=instance).update(
                _site=instance.site,
                _location=instance.location,
                _rack=instance.rack,
            )


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
            CablePath.objects.filter(_nodes__contains=instance).update(is_active=False)
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
    model.objects.filter(pk=instance.termination_id).update(
        cable=None,
        cable_end=None,
        cable_connector=None,
        cable_positions=None,
    )

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

@receiver(post_save, sender=Interface)
@receiver(post_save, sender=VMInterface)
def update_wwn_address_interface(instance, created, raw, **kwargs):
    """
    When creating a new Interface or VMInterface, check whether a WWNAddress has been designated as its primary. If so,
    assign the WWNAddress to the interface.
    """
    if created and not raw and instance.primary_wwn_address:
        instance.primary_wwn_address.assigned_object = instance
        instance.primary_wwn_address.save()

@receiver(post_save, sender=Location)
@receiver(post_save, sender=Site)
def sync_cached_scope_fields(instance, created, **kwargs):
    """
    Rebuild cached scope fields for all CachedScopeMixin-based models
    affected by a change to a Site or Location.

    When the values read from the database immediately before this save
    show that no scope-relevant field has changed, the rebuild is
    skipped. Otherwise, cached fields are recomputed from each object's
    authoritative scope relationships — never copied from the saved
    instance — so rows holding stale cached values are also repaired.
    """
    if created:
        return

    if isinstance(instance, Location):
        filters = {'_location': instance}
    elif isinstance(instance, Site):
        filters = {'_site': instance}
    else:
        return

    # Skip the rebuild when this save changed no scope-relevant field. The pre-save values
    # are read from the database by cache_presave_scope_fields() immediately before the
    # write, with the row locked, so the comparison holds even when overlapping saves race
    # on the same object. The stash exists only for saves made inside a transaction; when
    # it's absent (autocommit saves), rebuild unconditionally.
    prev = getattr(instance, '_presave_scope_fields', None)
    if prev is not None:
        if isinstance(instance, Site):
            if prev['region_id'] == instance.region_id and prev['group_id'] == instance.group_id:
                return
        # The dispatch above ensures the instance can only be a Location here
        elif prev['site_id'] == instance.site_id:
            return

    # These models are explicitly listed because they all subclass CachedScopeMixin
    # and therefore require their cached scope fields to be recomputed.
    with transaction.atomic(savepoint=False):
        for model in (Prefix, Cluster, WirelessLAN):
            qs = model.objects.filter(**filters)

            # Recompute the cached fields once per distinct scope, then apply each result with a
            # single UPDATE. This avoids loading every object into memory as well as the per-row
            # CASE WHEN statement generated by bulk_update(), and does not trigger post_save
            # signals, avoiding spurious change log entries. Ordering explicitly by the selected
            # columns orders the scope groups and keeps the models' default ordering out of the
            # DISTINCT (which would defeat the grouping); within each UPDATE, row lock order is
            # plan-dependent, as it was with bulk_update(). The atomic block keeps the rebuild
            # all-or-nothing outside a request transaction.
            scopes = qs.values_list('scope_type_id', 'scope_id').order_by('scope_type_id', 'scope_id').distinct()
            for scope_type_id, scope_id in scopes:
                ref = model(scope_type_id=scope_type_id, scope_id=scope_id)
                ref.cache_related_objects()
                qs.filter(scope_type_id=scope_type_id, scope_id=scope_id).update(
                    _location=ref._location,
                    _site=ref._site,
                    _site_group=ref._site_group,
                    _region=ref._region,
                )
