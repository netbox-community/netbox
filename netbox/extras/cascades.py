"""
Declarative cascade registrations for extras models.

Replaces imperative signal handlers in extras/signals.py for custom field operations.
"""
from netbox.cascades import CascadeMethod, CascadeSpec, CascadeTiming, cascade_registry


# ──────────────────────────────────────────────────────────────────────
# CustomField M2M change → populate/remove custom field data
# Replaces: handle_cf_added_obj_types, handle_cf_removed_obj_types,
#           handle_cf_renamed, handle_cf_deleted
# ──────────────────────────────────────────────────────────────────────

def _cf_added_obj_types(sender, instance, action, pk_set, **kwargs):
    """When a CustomField gains object types, populate initial data on those types."""
    from django.contrib.contenttypes.models import ContentType

    if action == 'post_add' and pk_set:
        instance.populate_initial_data(ContentType.objects.filter(pk__in=pk_set))


def _cf_removed_obj_types(sender, instance, action, pk_set, **kwargs):
    """When a CustomField loses object types, remove stale data from those types."""
    from django.contrib.contenttypes.models import ContentType

    if action == 'post_remove' and pk_set:
        instance.remove_stale_data(ContentType.objects.filter(pk__in=pk_set))


def _cf_renamed(sender, instance, created, **kwargs):
    """When a CustomField is renamed, rename the key in all objects' custom_field_data."""
    if not created and instance.name != instance._name:
        instance.rename_object_data(old_name=instance._name, new_name=instance.name)


def _cf_deleted(sender, instance, **kwargs):
    """When a CustomField is deleted, remove stale data from all assigned types."""
    instance.remove_stale_data(instance.object_types.all())


cascade_registry.register(
    CascadeSpec(
        source_model='extras.customfield',
        target_model='(all models with custom fields)',
        timing=CascadeTiming.POST_SAVE,
        method=CascadeMethod.CUSTOM,
        handler=_cf_renamed,
        skip_on_create=False,
        description='Rename custom field key in all objects when CustomField name changes',
    ),
    CascadeSpec(
        source_model='extras.customfield',
        target_model='(all models with custom fields)',
        timing=CascadeTiming.PRE_DELETE,
        method=CascadeMethod.CUSTOM,
        handler=_cf_deleted,
        skip_on_create=False,
        description='Remove custom field data from all objects when CustomField is deleted',
    ),
)

# M2M cascades are registered separately since they use m2m_changed signal
# These are handled via the m2m cascade support (see connect_cascade_m2m_signals)
_CF_M2M_SPECS = {
    'post_add': CascadeSpec(
        source_model='extras.customfield',
        target_model='(all models with custom fields)',
        method=CascadeMethod.CUSTOM,
        handler=_cf_added_obj_types,
        skip_on_create=False,
        description='Populate initial custom field data when CustomField gains object types',
    ),
    'post_remove': CascadeSpec(
        source_model='extras.customfield',
        target_model='(all models with custom fields)',
        method=CascadeMethod.CUSTOM,
        handler=_cf_removed_obj_types,
        skip_on_create=False,
        description='Remove stale custom field data when CustomField loses object types',
    ),
}
