from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import m2m_changed, post_save, pre_delete
from django.dispatch import receiver

from core.events import *
from core.signals import job_end, job_start
from extras.events import EventContext, process_event_rules
from extras.models import EventRule, Notification, Subscription
from netbox.config import get_config
from netbox.models.features import has_feature
from netbox.signals import post_clean
from utilities.data import get_config_value_ci
from utilities.exceptions import AbortRequest

from .cache import (
    invalidate_config_context_for_configcontext,
    invalidate_config_context_for_objects,
    invalidate_for_scope_delta,
)
from .constants import CC_FIELDS_BY_MODEL
from .models import ConfigContext, CustomField, TaggedItem
from .utils import run_validators

#
# Custom fields
#


def handle_cf_added_obj_types(instance, action, pk_set, **kwargs):
    """
    Handle the population of default/null values when a CustomField is added to one or more ContentTypes.
    """
    if action == 'post_add':
        instance.populate_initial_data(ContentType.objects.filter(pk__in=pk_set))


def handle_cf_removed_obj_types(instance, action, pk_set, **kwargs):
    """
    Handle the cleanup of old custom field data when a CustomField is removed from one or more ContentTypes.
    """
    if action == 'post_remove':
        instance.remove_stale_data(ContentType.objects.filter(pk__in=pk_set))


def handle_cf_renamed(instance, created, **kwargs):
    """
    Handle the renaming of custom field data on objects when a CustomField is renamed.
    """
    if not created and instance.name != instance._name:
        instance.rename_object_data(old_name=instance._name, new_name=instance.name)


def handle_cf_deleted(instance, **kwargs):
    """
    Handle the cleanup of old custom field data when a CustomField is deleted.
    """
    instance.remove_stale_data(instance.object_types.all())


post_save.connect(handle_cf_renamed, sender=CustomField)
pre_delete.connect(handle_cf_deleted, sender=CustomField)
m2m_changed.connect(handle_cf_added_obj_types, sender=CustomField.object_types.through)
m2m_changed.connect(handle_cf_removed_obj_types, sender=CustomField.object_types.through)


#
# Custom validation
#

@receiver(post_clean)
def run_save_validators(sender, instance, **kwargs):
    """
    Run any custom validation rules for the model prior to calling save().
    """
    model_name = f'{sender._meta.app_label}.{sender._meta.model_name}'
    validators = get_config_value_ci(get_config().CUSTOM_VALIDATORS, model_name, default=[])

    run_validators(instance, validators)


#
# Tags
#

@receiver(m2m_changed, sender=TaggedItem)
def validate_assigned_tags(sender, instance, action, model, pk_set, **kwargs):
    """
    Validate that any Tags being assigned to the instance are not restricted to non-applicable object types.
    """
    if action != 'pre_add':
        return
    ct = ContentType.objects.get_for_model(instance)
    # Retrieve any applied Tags that are restricted to certain object types
    for tag in model.objects.filter(pk__in=pk_set, object_types__isnull=False).prefetch_related('object_types'):
        if ct not in tag.object_types.all():
            raise AbortRequest(f"Tag {tag} cannot be assigned to {ct.model} objects.")


#
# Config context cache invalidation
#

@receiver(post_save, sender=ConfigContext)
def invalidate_on_configcontext_save(sender, instance, **kwargs):
    """
    Whenever a ConfigContext's scalar fields change (e.g. `data`, `weight`, `is_active`),
    invalidate the caches of all Devices/VMs currently in scope. M2M scope changes are handled
    separately by invalidate_on_configcontext_m2m_change().
    """
    invalidate_config_context_for_configcontext(instance)


@receiver(pre_delete, sender=ConfigContext)
def invalidate_on_configcontext_delete(sender, instance, **kwargs):
    """
    Before a ConfigContext is deleted, invalidate the caches of all Devices/VMs currently in
    scope. The scope is still readable here (pre_delete fires before the row and its M2M rows
    are removed).
    """
    invalidate_config_context_for_configcontext(instance)


def invalidate_on_configcontext_m2m_change(sender, instance, action, pk_set, scope_field, **kwargs):
    """
    Whenever a ConfigContext's scope M2M changes, invalidate the caches of all Devices/VMs that
    were or now are in scope.

    Strategy:
    - For post_add: the current scope is broader than (or equal to) the previous scope. Devices
      newly in scope are caught by invalidating the current affected set.
    - For post_remove: the current scope is narrower. We must also invalidate devices that
      matched only via the just-removed scope items.
    - For post_clear: the scope is now empty (matches all). The current full affected set is the
      broadest possible for this attribute; invalidating it suffices.
    """
    if action not in ('post_add', 'post_remove', 'post_clear'):
        return

    # Always invalidate based on the current (post-change) scope.
    invalidate_config_context_for_configcontext(instance)

    # For post_remove, also invalidate devices/VMs that matched via the removed scope items.
    if action == 'post_remove' and pk_set:
        invalidate_for_scope_delta(scope_field, pk_set)


def _connect_configcontext_m2m_handlers():
    """
    Wire `invalidate_on_configcontext_m2m_change` to every ConfigContext scope M2M's through
    model. The set of scope M2Ms is introspected from the model so new ones are picked up
    automatically. The receiver is curried with `scope_field` to identify which attribute changed.
    """
    for m2m_field in ConfigContext._meta.many_to_many:
        field_name = m2m_field.name
        through = getattr(ConfigContext, field_name).through

        def _handler(sender, instance, action, pk_set, _field=field_name, **kwargs):
            invalidate_on_configcontext_m2m_change(
                sender=sender,
                instance=instance,
                action=action,
                pk_set=pk_set,
                scope_field=_field,
                **kwargs,
            )

        m2m_changed.connect(_handler, sender=through, weak=False)


_connect_configcontext_m2m_handlers()


def _changed_fields(instance, fields):
    """
    Return True if any of `fields` differs between the prechange snapshot and the current state.
    If no snapshot exists (e.g. object loaded fresh from DB and saved without a snapshot), assume
    we cannot tell what changed and conservatively return True. The cost is one extra background
    re-render per non-instrumented save; the cost of returning False would be stale caches.
    """
    snapshot = getattr(instance, '_prechange_snapshot', None)
    if not snapshot:
        return True
    for field in fields:
        # Snapshot keys mirror Django's JSON serializer: FK ids are stored under the bare name
        # (no `_id` suffix). Convert.
        snap_key = field[:-3] if field.endswith('_id') else field
        if snapshot.get(snap_key) != getattr(instance, field, None):
            return True
    return False


def _make_object_save_handler(model_label):
    fields = CC_FIELDS_BY_MODEL[model_label]

    def _handler(sender, instance, created, **kwargs):
        if created:
            # No cache exists yet; the next read will render on demand. We could pre-render
            # eagerly via a background job, but lazy rendering is sufficient.
            return
        if _changed_fields(instance, fields):
            invalidate_config_context_for_objects(model_label, [instance.pk])

    return _handler


def _connect_object_save_handlers():
    from django.apps import apps as django_apps

    for model_label in CC_FIELDS_BY_MODEL:
        Model = django_apps.get_model(model_label)
        post_save.connect(_make_object_save_handler(model_label), sender=Model, weak=False)


_connect_object_save_handlers()


@receiver(m2m_changed, sender=TaggedItem)
def invalidate_on_device_vm_tag_change(sender, instance, action, **kwargs):
    """
    When tags are added or removed on a Device/VM, invalidate that object's cache.
    """
    if action not in ('post_add', 'post_remove', 'post_clear'):
        return
    from dcim.models import Device
    from virtualization.models import VirtualMachine

    if isinstance(instance, Device):
        invalidate_config_context_for_objects('dcim.device', [instance.pk])
    elif isinstance(instance, VirtualMachine):
        invalidate_config_context_for_objects('virtualization.virtualmachine', [instance.pk])


# Upstream object changes that affect ConfigContext matching even when the Device/VM itself is
# untouched. Two patterns are handled:
#
#   1. Direct FK changes (Site.region, Cluster.type, Tenant.group, ...): invalidate the caches of
#      Devices/VMs that reference the changed object.
#   2. MPTT reparents (Region.parent, SiteGroup.parent, ...): invalidate every Device/VM whose
#      attribute resolves into the changed node's subtree, because the ancestor list used by the
#      matching query has shifted.


def _make_direct_upstream_handler(fields, device_lookup, vm_lookup):
    def _handler(sender, instance, created, **kwargs):
        if created or not _changed_fields(instance, fields):
            return
        from dcim.models import Device
        from virtualization.models import VirtualMachine

        if device_lookup:
            invalidate_config_context_for_objects(
                'dcim.device',
                Device.objects.filter(**{device_lookup: instance.pk}).values_list('pk', flat=True),
            )
        if vm_lookup:
            invalidate_config_context_for_objects(
                'virtualization.virtualmachine',
                VirtualMachine.objects.filter(**{vm_lookup: instance.pk}).values_list('pk', flat=True),
            )

    return _handler


def _make_mptt_reparent_handler(device_attr, vm_attr):
    def _handler(sender, instance, created, **kwargs):
        if created or not _changed_fields(instance, ('parent_id',)):
            return
        from dcim.models import Device
        from virtualization.models import VirtualMachine

        subtree_pks = list(
            type(instance).objects.filter(pk=instance.pk)
            .get_descendants(include_self=True)
            .values_list('pk', flat=True)
        )

        if device_attr:
            invalidate_config_context_for_objects(
                'dcim.device',
                Device.objects.filter(**{device_attr: subtree_pks}).values_list('pk', flat=True),
            )
        if vm_attr:
            invalidate_config_context_for_objects(
                'virtualization.virtualmachine',
                VirtualMachine.objects.filter(**{vm_attr: subtree_pks}).values_list('pk', flat=True),
            )

    return _handler


def _connect_upstream_handlers():
    from django.apps import apps as django_apps

    # (app, model, fields_to_watch, device_lookup, vm_lookup)
    direct_triggers = (
        ('dcim', 'Site', ('region_id', 'group_id'), 'site_id', 'site_id'),
        ('dcim', 'Location', ('site_id',), 'location_id', None),
        ('virtualization', 'Cluster', ('type_id', 'group_id', 'site_id'), 'cluster_id', 'cluster_id'),
        ('tenancy', 'Tenant', ('group_id',), 'tenant_id', 'tenant_id'),
    )
    for app, name, fields, device_lookup, vm_lookup in direct_triggers:
        Model = django_apps.get_model(app, name)
        post_save.connect(
            _make_direct_upstream_handler(fields, device_lookup, vm_lookup),
            sender=Model,
            weak=False,
        )

    # (app, model, device_attr_path__in, vm_attr_path__in)
    mptt_triggers = (
        ('dcim', 'Region', 'site__region__in', 'site__region__in'),
        ('dcim', 'SiteGroup', 'site__group__in', 'site__group__in'),
        ('dcim', 'DeviceRole', 'role__in', 'role__in'),
        ('dcim', 'Platform', 'platform__in', 'platform__in'),
        ('tenancy', 'TenantGroup', 'tenant__group__in', 'tenant__group__in'),
        ('dcim', 'Location', 'location__in', None),
    )
    for app, name, device_attr, vm_attr in mptt_triggers:
        Model = django_apps.get_model(app, name)
        post_save.connect(
            _make_mptt_reparent_handler(device_attr, vm_attr),
            sender=Model,
            weak=False,
        )


_connect_upstream_handlers()


# Deletion of an upstream object referenced by a Device/VM via a SET_NULL foreign key (or by a
# Site/Tenant the object belongs to) silently nulls that FK with a bulk UPDATE that emits no
# post_save signal, so the object-save handlers above never fire. We therefore invalidate on
# pre_delete, while the references are still resolvable.
#
# Only SET_NULL relationships matter here: PROTECT relationships (Device.role/tenant/site,
# VM.cluster/site/role/tenant, etc.) cannot be deleted while a Device/VM references them, so no
# stale cache can result. The SET_NULL feeders into ConfigContext matching are:
#   - Platform        (Device.platform, VM.platform)
#   - Cluster         (Device.cluster)            -> also covers cluster_type/cluster_group scopes
#   - Region          (Site.region)
#   - SiteGroup       (Site.group)
#   - TenantGroup     (Tenant.group)
#
# We reuse invalidate_for_scope_delta(), which resolves the full set of Devices/VMs reachable via
# the given scope dimension (descendants included for MPTT models), exactly matching the objects
# whose FK is about to be nulled.

def _make_upstream_delete_handler(scope_field):
    def _handler(sender, instance, **kwargs):
        invalidate_for_scope_delta(scope_field, [instance.pk])

    return _handler


def _connect_upstream_delete_handlers():
    from django.apps import apps as django_apps

    # (app, model, scope_field)
    delete_triggers = (
        ('dcim', 'Platform', 'platforms'),
        ('dcim', 'Region', 'regions'),
        ('dcim', 'SiteGroup', 'site_groups'),
        ('virtualization', 'Cluster', 'clusters'),
        ('tenancy', 'TenantGroup', 'tenant_groups'),
    )
    for app, name, scope_field in delete_triggers:
        Model = django_apps.get_model(app, name)
        pre_delete.connect(
            _make_upstream_delete_handler(scope_field),
            sender=Model,
            weak=False,
        )


_connect_upstream_delete_handlers()


#
# Event rules
#

@receiver(job_start)
def process_job_start_event_rules(sender, **kwargs):
    """
    Process event rules for jobs starting.
    """
    event_rules = EventRule.objects.filter(
        event_types__contains=[JOB_STARTED],
        enabled=True,
        object_types=sender.object_type
    )
    event = EventContext(
        event_type=JOB_STARTED,
        data=sender.data,
        user=sender.user,
    )
    process_event_rules(event_rules, sender.object_type, event)


@receiver(job_end)
def process_job_end_event_rules(sender, **kwargs):
    """
    Process event rules for jobs terminating.
    """
    event_rules = EventRule.objects.filter(
        event_types__contains=[JOB_COMPLETED],
        enabled=True,
        object_types=sender.object_type
    )
    event = EventContext(
        event_type=JOB_COMPLETED,
        data=sender.data,
        user=sender.user,
    )
    process_event_rules(event_rules, sender.object_type, event)


#
# Notifications
#

@receiver((post_save, pre_delete))
def notify_object_changed(sender, instance, **kwargs):
    # Skip for newly-created objects
    if kwargs.get('created'):
        return

    # Determine event type
    if 'created' in kwargs:
        event_type = OBJECT_UPDATED
    else:
        event_type = OBJECT_DELETED

    # Skip unsupported object types
    if not has_feature(instance, 'notifications'):
        return

    ct = ContentType.objects.get_for_model(instance)

    # Find all subscribed Users
    subscribed_users = Subscription.objects.filter(
        object_type=ct,
        object_id=instance.pk
    ).values_list('user', flat=True)
    if not subscribed_users:
        return

    # Delete any existing Notifications for the object
    Notification.objects.filter(
        object_type=ct,
        object_id=instance.pk,
        user__in=subscribed_users
    ).delete()

    # Create Notifications for Subscribers
    Notification.objects.bulk_create([
        Notification(
            user_id=user,
            object=instance,
            object_repr=Notification.get_object_repr(instance),
            event_type=event_type
        )
        for user in subscribed_users
    ])
