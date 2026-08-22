import logging

from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.models import F, Q
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from circuits.models import CircuitTermination
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

# The scope-relevant fields stashed before each model's save by cache_presave_scope_fields(),
# so that the post_save handlers can tell whether the save actually changed any of them and
# skip their work when it did not.
STASHED_SCOPE_FIELDS = {
    Site: ('region_id', 'group_id'),
    Location: ('site_id',),
    Rack: ('site_id', 'location_id'),
    Device: ('site_id', 'location_id', 'rack_id'),
}


#
# Location/rack/device assignment
#

def cache_presave_scope_fields(instance, raw=False, using=None, **kwargs):
    """
    Stash the scope-relevant field values currently in the database so that the post_save
    handlers below can determine whether this save actually changed any of them. The read
    locks the row, so overlapping saves of the same object serialize here and the
    comparison always runs against the final committed state.

    No stash is taken for a raw save, for a new instance, or outside a transaction: in
    autocommit, this read and the subsequent UPDATE would run in separate transactions, so
    the comparison could race a concurrent save. In each of those cases any stash left by a
    previous save of the same instance is cleared, as it no longer reflects the current
    database state. The post_save handlers treat a missing stash as "the values may have
    changed" and rebuild or repair unconditionally — except on a raw save, which they skip
    before consulting the stash at all, making the clearing there purely defensive.
    """
    if raw or instance.pk is None or not transaction.get_connection(using).in_atomic_block:
        # Clear any stash left by a previous save of this instance.
        instance._presave_scope_fields = None
        return
    fields = STASHED_SCOPE_FIELDS[instance.__class__]
    instance._presave_scope_fields = (
        instance.__class__.objects.using(using)
        .filter(pk=instance.pk)
        .order_by()  # Clear default ordering to avoid JOINs
        .select_for_update(no_key=True)  # no_key: Avoid blocking foreign key inserts that reference this object
        .values(*fields)
        .first()
    )


for _model in STASHED_SCOPE_FIELDS:
    pre_save.connect(cache_presave_scope_fields, sender=_model)


# update_fields may name a foreign key by either its name ('site') or its attname
# ('site_id') — Django accepts both — so deciding whether a save wrote a stashed field has
# to test both forms. Derived from each model's own meta rather than written out, so the two
# spellings cannot disagree.
STASHED_FIELD_ALIASES = {
    model: {
        field.attname: frozenset((field.attname, field.name))
        for field in model._meta.concrete_fields
        if field.attname in fields
    }
    for model, fields in STASHED_SCOPE_FIELDS.items()
}


def _unwritten_scope_fields(instance, update_fields):
    """
    Return the scope-relevant fields listed for the instance's model which this save did
    not write.
    """
    if update_fields is None:
        return frozenset()
    aliases = STASHED_FIELD_ALIASES[instance.__class__]
    return frozenset(field for field, names in aliases.items() if names.isdisjoint(update_fields))


def _scope_fields_unchanged(instance, update_fields=None):
    """
    Return True when the values stashed immediately before this save show that it changed
    none of the scope-relevant fields listed for the instance's model, meaning the caller's
    propagation or rebuild can be skipped in its entirety.
    """
    prev = getattr(instance, '_presave_scope_fields', None)
    if prev is None:
        return False
    unwritten = _unwritten_scope_fields(instance, update_fields)
    return all(value == getattr(instance, field) for field, value in prev.items() if field not in unwritten)


def _scope_values(instance, update_fields, using):
    """
    Return the values the scope-relevant fields hold in the database once this save has
    been applied, keyed by field name, for the propagation handlers to push down.

    Must be called inside the transaction the propagation runs in: the fallback read below
    locks the row for the remainder of it, so that no concurrent write can move the object
    out from under the values being propagated.

    Returns None when the row cannot be read at all, leaving the caller nothing to
    propagate.
    """
    values = {field: getattr(instance, field) for field in STASHED_SCOPE_FIELDS[instance.__class__]}
    unwritten = _unwritten_scope_fields(instance, update_fields)
    if not unwritten:
        return values
    stashed = getattr(instance, '_presave_scope_fields', None)
    if stashed is None:
        stashed = (
            instance.__class__.objects.using(using)
            .filter(pk=instance.pk)
            # Cleared for the same reason as in cache_presave_scope_fields().
            .order_by()
            .select_for_update(no_key=True)
            .values(*unwritten)
            .first()
        )
        # No row to read: it was deleted after this save committed, or was never inserted
        # (an instance with a pre-assigned primary key).
        if stashed is None:
            return None
    values.update({field: stashed[field] for field in unwritten})
    return values


@receiver(post_save, sender=Location)
def handle_location_site_change(instance, created, raw=False, using=None, update_fields=None, **kwargs):
    """
    Update child objects when a Location is saved. All updates are queryset update() calls,
    which fire no signals and generate no change records for the affected objects.

    Each query is pinned to the connection the Location was saved on: on an installation
    with database routers configured, letting the router pick the alias would both write to
    a different database than the one being saved and leave the row locks below outside the
    transaction opened here. For the same reason the new Site is assigned by ID: reading
    instance.site would fetch the related object over a router-selected connection whenever
    the save left it uncached (a rename, say).

    When the values read from the database immediately before this save show that the Site
    assignment is unchanged, the propagation is skipped: every value written below is
    derived from it, so there is nothing for the descendants to pick up. A raw save is
    skipped outright.
    """
    if created or raw:
        return

    # Skip the propagation when this save left the Site assignment untouched.
    if _scope_fields_unchanged(instance, update_fields):
        return

    with transaction.atomic(using=using, savepoint=False):
        scope = _scope_values(instance, update_fields, using)
        if scope is None:
            return
        site_id = scope['site_id']
        instance.get_descendants().using(using).update(site_id=site_id)
        # Materialized once so every statement below sees the same membership, even if a
        # concurrent commit renumbers the tree mid-handler.
        locations = list(instance.get_descendants(include_self=True).using(using).values_list('pk', flat=True))
        Rack.objects.using(using).filter(location__in=locations).update(site_id=site_id)
        Device.objects.using(using).filter(location__in=locations).update(site_id=site_id)
        PowerPanel.objects.using(using).filter(location__in=locations).update(site_id=site_id)
        CableTermination.objects.using(using).filter(_location__in=locations).update(_site_id=site_id)
        # Update component models for devices in these locations
        for model in COMPONENT_MODELS:
            model.objects.using(using).filter(device__location__in=locations).update(_site_id=site_id)

        # Objects scoped to descendant Locations receive no post_save of their own from the
        # queryset updates above, so their cached scope fields are updated here.
        site = (
            Site.objects.using(using)
            .filter(pk=site_id)
            .select_for_update(no_key=True)  # Lock the destination Site (without blocking FK inserts that reference it)
            .values('region_id', 'group_id')
            .first()
        )
        if site is not None:
            location_ct = ContentType.objects.db_manager(using).get_for_model(Location)
            for model in (Prefix, Cluster, WirelessLAN):
                model.objects.using(using).filter(scope_type=location_ct, scope_id__in=locations).update(
                    _location_id=F('scope_id'),
                    _site_id=site_id,
                    _region_id=site['region_id'],
                    _site_group_id=site['group_id'],
                )

            # CircuitTermination caches the same ancestry under its own generic
            # termination field rather than CachedScopeMixin.scope, so it is invisible to
            # both the loop above and sync_cached_scope_fields().
            CircuitTermination.objects.using(using).filter(
                termination_type=location_ct, termination_id__in=locations
            ).update(
                _location_id=F('termination_id'),
                _site_id=site_id,
                _region_id=site['region_id'],
                _site_group_id=site['group_id'],
            )


@receiver(post_save, sender=Rack)
def handle_rack_site_change(instance, created, raw=False, using=None, update_fields=None, **kwargs):
    """
    Update child Devices if Site or Location assignment has changed. Queries are pinned to
    the connection the Rack was saved on, and the new values are assigned by ID so that no
    related object is fetched over a router-selected connection.

    A save which changed neither assignment propagates nothing and is skipped, as does a
    raw save.
    """
    if created or raw:
        return

    # Skip the propagation when this save left the Site and Location assignments untouched.
    if _scope_fields_unchanged(instance, update_fields):
        return

    with transaction.atomic(using=using, savepoint=False):
        scope = _scope_values(instance, update_fields, using)
        if scope is None:
            return
        Device.objects.using(using).filter(rack=instance).update(
            site_id=scope['site_id'],
            location_id=scope['location_id'],
        )
        # Update component models for devices in this rack
        for model in COMPONENT_MODELS:
            model.objects.using(using).filter(device__rack=instance).update(
                _site_id=scope['site_id'],
                _location_id=scope['location_id'],
            )


@receiver(post_save, sender=Device)
def handle_device_site_change(instance, created, raw=False, using=None, update_fields=None, **kwargs):
    """
    Update child components to update the parent Site, Location, and Rack when a Device is saved.
    Queries are pinned to the connection the Device was saved on, and the new values are
    assigned by ID so that no related object is fetched over a router-selected connection.

    A save which changed none of the three assignments propagates nothing and is skipped,
    as does a raw save.
    """
    if created or raw:
        return

    # Skip the propagation when this save left the Site, Location, and Rack assignments untouched.
    if _scope_fields_unchanged(instance, update_fields):
        return

    with transaction.atomic(using=using, savepoint=False):
        scope = _scope_values(instance, update_fields, using)
        if scope is None:
            return
        for model in COMPONENT_MODELS:
            model.objects.using(using).filter(device=instance).update(
                _site_id=scope['site_id'],
                _location_id=scope['location_id'],
                _rack_id=scope['rack_id'],
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


def _get_scope_object(scope_type_id, scope_id, using):
    """
    Return the object referenced by a CachedScopeMixin generic scope, read on the given
    database connection. The ancestors which cache_related_objects() traverses are selected
    in the same query, so recomputing the cached fields from the returned object issues no
    further reads. Returns None if the scope is unset or dangling.
    """
    if scope_type_id is None or scope_id is None:
        return None
    scope_type = ContentType.objects.db_manager(using).get_for_id(scope_type_id)
    scope_model = scope_type.model_class()
    if scope_model is None:
        return None
    queryset = scope_model._base_manager.using(using)
    if scope_model is Location:
        queryset = queryset.select_related('site__region', 'site__group')
    elif scope_model is Site:
        queryset = queryset.select_related('region', 'group')
    return queryset.filter(pk=scope_id).first()


@receiver(post_save, sender=Location)
@receiver(post_save, sender=Site)
def sync_cached_scope_fields(instance, created, raw=False, using=None, update_fields=None, **kwargs):
    """
    Rebuild cached scope fields for all CachedScopeMixin-based models
    affected by a change to a Site or Location.

    When the values read from the database immediately before this save
    show that no scope-relevant field has changed, the rebuild is
    skipped, as is a raw save. Otherwise, cached fields are recomputed
    from each object's authoritative scope relationships — never copied
    from the saved instance — so rows holding stale cached values are
    also repaired. A partial save is judged on the fields it actually
    wrote.
    """
    if created or raw:
        return

    if isinstance(instance, Location):
        filters = {'_location': instance}
    elif isinstance(instance, Site):
        filters = {'_site': instance}
    else:
        return

    # Skip the rebuild when this save changed no scope-relevant field. The rebuild reads
    # each row's own scope rather than the instance, so it needs no _scope_values() here.
    if _scope_fields_unchanged(instance, update_fields):
        return

    # These models are explicitly listed because they all subclass CachedScopeMixin
    # and therefore require their cached scope fields to be recomputed.
    with transaction.atomic(using=using, savepoint=False):
        for model in (Prefix, Cluster, WirelessLAN):
            qs = model.objects.using(using).filter(**filters)

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
                # Resolve the scope (and the ancestors cache_related_objects() traverses) on
                # the saving connection, then hand it to a throwaway reference object with
                # its relations already populated, so that recomputing the cached fields
                # reads nothing further. Assigning ref._state.db alone would not suffice:
                # Django consults DATABASE_ROUTERS first for related-object lookups and only
                # falls back to the instance's recorded database when every router declines.
                ref = model()
                ref._state.db = using
                ref.scope = _get_scope_object(scope_type_id, scope_id, using)
                ref.cache_related_objects()
                qs.filter(scope_type_id=scope_type_id, scope_id=scope_id).update(
                    _location_id=ref._location_id,
                    _site_id=ref._site_id,
                    _site_group_id=ref._site_group_id,
                    _region_id=ref._region_id,
                )
