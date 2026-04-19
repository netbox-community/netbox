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


def _cf_renamed(instance, **kwargs):
    """When a CustomField is renamed, rename the key in all objects' custom_field_data."""
    created = kwargs.get('created', False)
    if not created and instance.name != instance._name:
        instance.rename_object_data(old_name=instance._name, new_name=instance.name)


def _cf_deleted(instance, **kwargs):
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


# ──────────────────────────────────────────────────────────────────────
# ImageAttachment post-delete → delete image file from disk
# PARTIAL: The delete() override is kept because it must restore
# image.name after file deletion for UI display during the request.
# ──────────────────────────────────────────────────────────────────────

def _imageattachment_delete_file(instance, **kwargs):
    """Delete image file from disk after DB row is deleted, then restore filename for display."""
    _name = instance.image.name
    instance.image.delete(save=False)
    instance.image.name = _name


cascade_registry.register(
    CascadeSpec(
        source_model='extras.imageattachment',
        target_model='(filesystem)',
        timing=CascadeTiming.POST_DELETE,
        method=CascadeMethod.CUSTOM,
        handler=_imageattachment_delete_file,
        skip_on_create=False,
        description='Delete image file from disk and restore filename for post-request display',
    ),
)


# ──────────────────────────────────────────────────────────────────────
# Script delete → soft-delete support
# METADATA-ONLY: The delete() override accepts a custom soft_delete
# parameter that can't be passed via signals.
# ──────────────────────────────────────────────────────────────────────

cascade_registry.register(
    CascadeSpec(
        source_model='extras.script',
        target_model='extras.script',
        timing=CascadeTiming.PRE_DELETE,
        method=CascadeMethod.CUSTOM,
        handler=None,
        skip_on_create=False,
        description='Script.delete() supports soft_delete param: sets is_executable=False '
                    'instead of deleting when jobs exist. Handled directly in model delete() '
                    'because the soft_delete flag is a method parameter, not model state.',
    ),
)


# ──────────────────────────────────────────────────────────────────────
# SyncedDataMixin save/delete → AutoSyncRecord management
# Now handled by sentinel cascade registration in netbox/models/validators.py
# via __mixin:SyncedDataMixin__ sentinel.
# ──────────────────────────────────────────────────────────────────────
