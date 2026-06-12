"""
Invalidation helpers for the pre-rendered config-context cache on Device and VirtualMachine.

Every signal handler in extras/signals.py that needs to invalidate cached config-context data
funnels through this module, so the synchronous NULL-out and background job enqueue are
expressed in exactly one place.
"""
from django.apps import apps
from django.db import transaction
from django.db.models import F, Q

from dcim.models import Device
from extras.jobs import RenderConfigContextJob
from extras.models.tags import TaggedItem
from virtualization.models import VirtualMachine


def invalidate_config_context_for_objects(model_label, pks):
    """
    Synchronously NULL the `_config_context_data` cache on the given objects (bumping the
    generation counter so an in-flight render can't overwrite the invalidation), then enqueue a
    background job to repopulate them once the surrounding transaction commits.

    Args:
        model_label: 'dcim.device' or 'virtualization.virtualmachine'.
        pks: Any iterable of object PKs (queryset, list, set, generator). An empty iterable is a no-op.
    """
    pks = list(pks)
    if not pks:
        return

    Model = apps.get_model(model_label)
    updated = Model.objects.filter(pk__in=pks).update(
        _config_context_data=None,
        _config_context_generation=F('_config_context_generation') + 1,
    )
    if not updated:
        return

    # Defer enqueue until after the current transaction commits, so the background worker doesn't
    # try to read uncommitted state. transaction.on_commit() is a no-op outside a transaction,
    # in which case the callback runs immediately.
    #
    # We deliberately enqueue a *parameterless* sweep (model_label=None, pks=None) that re-renders
    # every object whose cache is currently NULL, rather than a job scoped to these specific PKs.
    # JobRunner.enqueue_once() coalesces against any already-pending job of the same class (object_id
    # is NULL for all of these, so get_jobs(None) matches them all); a job carrying a specific PKs
    # list would therefore be silently dropped whenever another invalidation already had one enqueued,
    # leaving those objects NULLed but never re-rendered. A global NULL-sweep makes coalescing correct:
    # whichever sweep runs next picks up *all* outstanding NULL caches across both models. (Reads
    # remain correct in the interim because get_config_context() renders on demand when the cache is
    # NULL; the sweep only restores the pre-rendered fast path.)
    transaction.on_commit(
        lambda: RenderConfigContextJob.enqueue_once(instance=None)
    )


def invalidate_config_context_for_configcontext(configcontext):
    """
    Invalidate caches for all objects currently in scope for the given ConfigContext.
    """
    for queryset in configcontext.get_affected_objects():
        invalidate_config_context_for_objects(
            queryset.model._meta.label_lower,
            queryset.values_list('pk', flat=True),
        )


def invalidate_for_scope_delta(scope_field, scope_pks):
    """
    Invalidate the cache of every Device/VirtualMachine that is matchable via the given scope
    items, regardless of which ConfigContext those items belong to. Used when items are removed
    from a ConfigContext scope (so we don't know the new affected set under that scope, only the
    items that used to extend it).

    `scope_field` is the ConfigContext M2M attribute name ('sites', 'regions', 'tags', ...).
    `scope_pks` is the iterable of PKs of scope items that were removed/cleared.
    """
    scope_pks = list(scope_pks or ())
    if not scope_pks:
        return

    device_q = None
    vm_q = None

    # MPTT-based scopes: any device/VM whose corresponding attribute is a descendant
    # of any of the changed items.
    mptt_attrs = {
        'regions': ('dcim', 'Region', 'site__region__in'),
        'site_groups': ('dcim', 'SiteGroup', 'site__group__in'),
        'roles': ('dcim', 'DeviceRole', 'role__in'),
        'platforms': ('dcim', 'Platform', 'platform__in'),
        'locations': ('dcim', 'Location', 'location__in'),  # Devices only
    }
    direct_attrs = {
        'sites': 'site__in',
        'cluster_types': 'cluster__type__in',
        'cluster_groups': 'cluster__group__in',
        'clusters': 'cluster__in',
        'tenant_groups': 'tenant__group__in',
        'tenants': 'tenant__in',
        'device_types': 'device_type__in',  # Devices only
    }

    if scope_field in mptt_attrs:
        app, model_name, attr_path = mptt_attrs[scope_field]
        Model = apps.get_model(app, model_name)
        descendant_pks = list(
            Model.objects.filter(pk__in=scope_pks)
            .get_descendants(include_self=True)
            .values_list('pk', flat=True)
        )
        device_q = Q(**{attr_path: descendant_pks})
        if scope_field != 'locations':
            vm_q = Q(**{attr_path: descendant_pks})
    elif scope_field in direct_attrs:
        attr_path = direct_attrs[scope_field]
        device_q = Q(**{attr_path: scope_pks})
        if scope_field != 'device_types':
            vm_q = Q(**{attr_path: scope_pks})
    elif scope_field == 'tags':
        device_tagged = TaggedItem.objects.filter(
            tag_id__in=scope_pks,
            content_type__app_label='dcim',
            content_type__model='device',
        ).values_list('object_id', flat=True)
        vm_tagged = TaggedItem.objects.filter(
            tag_id__in=scope_pks,
            content_type__app_label='virtualization',
            content_type__model='virtualmachine',
        ).values_list('object_id', flat=True)
        device_q = Q(pk__in=device_tagged)
        vm_q = Q(pk__in=vm_tagged)
    else:
        return

    if device_q is not None:
        invalidate_config_context_for_objects(
            'dcim.device', Device.objects.filter(device_q).values_list('pk', flat=True)
        )
    if vm_q is not None:
        invalidate_config_context_for_objects(
            'virtualization.virtualmachine', VirtualMachine.objects.filter(vm_q).values_list('pk', flat=True)
        )
