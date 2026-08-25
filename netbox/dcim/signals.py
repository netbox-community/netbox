import logging

from django.db import transaction
from django.db.models import Q
from django.db.models.signals import post_delete, post_save, pre_save
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
from .utils import create_cablepaths, rebuild_cable_paths, rebuild_paths

# The scope-relevant fields stashed before each model's save by cache_presave_scope_fields(),
# so that the post_save handlers can tell whether the save actually changed any of them and
# skip their work when it did not. Only the models whose cascades are still carried out in
# Python are listed: the denormalized columns on device components, cable terminations, and
# the CachedScopeMixin models are maintained by database triggers (see the
# 'denormalization_triggers' migrations), which need no such stash.
STASHED_SCOPE_FIELDS = {
    Location: ('site_id',),
    Rack: ('site_id', 'location_id'),
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
    Cascade a Location's Site assignment down to the Racks, Devices, and PowerPanels it
    contains (and to descendant Locations). All updates are queryset update() calls, which
    fire no signals and generate no change records for the affected objects; the
    denormalized columns on device components and cable terminations are refreshed by the
    database triggers those updates fire in turn.

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
        chunked_update(instance.get_descendants().using(using), site_id=site_id)
        # Materialized once so every statement below sees the same membership, even if a
        # concurrent commit renumbers the tree mid-handler.
        locations = list(instance.get_descendants(include_self=True).using(using).values_list('pk', flat=True))
        chunked_update(Rack.objects.using(using).filter(location__in=locations), site_id=site_id)
        chunked_update(Device.objects.using(using).filter(location__in=locations), site_id=site_id)
        chunked_update(PowerPanel.objects.using(using).filter(location__in=locations), site_id=site_id)


@receiver(post_save, sender=Rack)
def handle_rack_site_change(instance, created, raw=False, using=None, update_fields=None, **kwargs):
    """
    Cascade a Rack's Site/Location assignment down to the Devices it contains; the
    denormalized columns on those Devices' components and cable terminations are refreshed
    by the database triggers the update fires in turn. Queries are pinned to the connection
    the Rack was saved on, and the new values are assigned by ID so that no related object
    is fetched over a router-selected connection.

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
        chunked_update(
            Device.objects.using(using).filter(rack=instance),
            site_id=scope['site_id'],
            location_id=scope['location_id'],
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
    model.objects.filter(pk=instance.termination_id).update(
        cable=None,
        cable_end=None,
        cable_connector=None,
        cable_positions=None,
    )

    # If the removed termination was a channelized interface, also clear the cable attributes mirrored onto its channel
    # subinterfaces. This must happen before the retrace below so that each channel's (now dead) path is torn down
    # rather than rebuilt from a stale cable reference.
    if model is Interface:
        Interface.objects.filter(parent_id=instance.termination_id, channel_id__isnull=False).update(
            cable=None, cable_end='', cable_connector=None, cable_positions=None
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


# Fields this receiver reacts to. A save() whose update_fields is disjoint from this set (e.g. a plain rename)
# cannot have touched channelization or cabling, so there's nothing for this receiver to do.
_CHANNELIZATION_RELEVANT_FIELDS = frozenset({'channels', 'channel_id', 'parent', 'parent_id', 'cable', 'cable_id'})


@receiver(post_save, sender=Interface)
def update_channelized_cable_paths(instance, created, raw=False, update_fields=None, **kwargs):
    """
    Rebuild cable paths when an interface's channelization changes without the Cable itself being modified: a channel
    subinterface is added, moved between parents, or has its channel_id changed, or channelization is toggled on an
    already-cabled interface. (The cable-tracing signals only fire when a Cable is saved.)
    """
    if raw:
        return
    if update_fields is not None and _CHANNELIZATION_RELEVANT_FIELDS.isdisjoint(update_fields):
        return

    parent_ids = set()

    # A channel subinterface was added, moved between parents, or had its channel_id changed. Gated on an actual
    # change (or creation) so a full re-save of an already-channelized child with neither field touched doesn't
    # propagate cable state and rebuild the parent's paths for unrelated changes.
    channelization_touched = (
        created or instance.channel_id != instance._original_channel_id
        or instance.parent_id != instance._original_parent_id
    )
    if channelization_touched and (instance.channel_id or instance._original_channel_id):
        parent_ids.update(pk for pk in (instance.parent_id, instance._original_parent_id) if pk)

    # Channelization was toggled on this interface while it carries a cable
    if instance.channels != instance._original_channels and instance.cable_id:
        parent_ids.add(instance.pk)

    # Tracks whether anything below mutated instance's own row via a queryset/bulk operation (which bypasses
    # this in-memory `instance`) rather than via save() -- see the refresh_from_db() call at the end.
    own_row_mutated = False

    # select_related('cable') avoids a per-parent round-trip to fetch the Cable, which both
    # propagate_channel_cables() and rebuild_cable_paths() dereference. (Cable.profile is a plain field, not a
    # relation, so it needs no prefetching.)
    parents = Interface.objects.filter(pk__in=parent_ids, cable__isnull=False).select_related('cable')
    for parent in parents:
        own_row_mutated = True
        if parent.channels:
            parent.propagate_channel_cables()
        rebuild_cable_paths(parent.cable)

    # A channel subinterface whose parent no longer provides a cable must not retain stale mirrored cable
    # attributes -- including when it was just detached from channelization entirely (channel_id and/or parent
    # cleared), since it then drops out of the old parent's propagation queryset above and would otherwise keep
    # its old cable cache indefinitely.
    if (instance.channel_id or instance._original_channel_id) and instance.cable_id:
        parent = instance.parent if instance.channel_id else None
        if not (parent and parent.channels and parent.cable_id):
            Interface.objects.filter(pk=instance.pk).update(
                cable=None, cable_end='', cable_connector=None, cable_positions=None
            )
            own_row_mutated = True
            for cablepath in CablePath.objects.filter(_nodes__contains=instance):
                if instance in cablepath.origins:
                    cablepath.delete()

    # A channel child's own cable_id/cable_end/cable_connector/cable_positions/_path may have just been mutated
    # at the DB level above -- mirrored from its parent (propagate_channel_cables(), which bulk_updates a
    # separately-fetched copy of this same row), cleared (the queryset .update() above), or rewritten by
    # rebuild_cable_paths()/CablePath.save()/.delete() (which set/clear _path on path origins via queryset
    # .update(), also bypassing this in-memory `instance`) -- without touching this in-memory `instance`. A
    # later full save() of this same instance by another caller in the same request (e.g.
    # MACAddressShortcutMixin.update()'s second instance.save() for a combined mac_address change) would
    # otherwise write those stale in-memory values back over what was just written. Gated on own_row_mutated so
    # a full re-save of an already-consistent channel child (nothing channelization-related touched) doesn't
    # pay for a refresh it doesn't need.
    if own_row_mutated:
        instance.refresh_from_db(fields=['cable', 'cable_end', 'cable_connector', 'cable_positions', '_path'])

    # Refresh the cached channelization state so that saving this same in-memory instance again compares against its
    # current values rather than re-triggering propagation from a stale baseline.
    instance._original_channels = instance.channels
    instance._original_channel_id = instance.channel_id
    instance._original_parent_id = instance.parent_id


@receiver(post_delete, sender=Interface)
def cleanup_channel_subinterface_paths(instance, **kwargs):
    """
    When a channel subinterface is deleted, rebuild its channelized parent's cable paths so the removed channel's path
    is torn down.
    """
    if instance.channel_id and instance.parent_id:
        parent = Interface.objects.filter(pk=instance.parent_id, cable__isnull=False).first()
        if parent and parent.channels:
            parent.propagate_channel_cables()
            rebuild_cable_paths(parent.cable)


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
