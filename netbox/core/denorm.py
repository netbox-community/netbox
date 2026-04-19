"""
Denormalization declarations for core models.
"""
from netbox.denorm import DenormSpec, denorm_registry

# ──────────────────────────────────────────────────────────────────────
# DataSource — reset status when sync_interval is cleared
# ──────────────────────────────────────────────────────────────────────

def _datasource_status_on_sync_clear(instance):
    """When sync_interval is cleared on an existing DataSource, reset QUEUED status."""
    if not instance._state.adding and not instance.sync_interval:
        from core.choices import DataSourceStatusChoices
        if instance.status == DataSourceStatusChoices.QUEUED and instance.last_synced:
            return DataSourceStatusChoices.COMPLETED
        elif instance.status == DataSourceStatusChoices.QUEUED:
            return DataSourceStatusChoices.NEW
    return instance.status


denorm_registry.register(
    'core.datasource',
    DenormSpec(
        field_name='status',
        compute=_datasource_status_on_sync_clear,
        depends_on=frozenset({'sync_interval', 'status'}),
    ),
)

# ──────────────────────────────────────────────────────────────────────
# ObjectChange — cache user_name and object_repr as static strings
# ──────────────────────────────────────────────────────────────────────

def _objectchange_user_name(instance):
    if not instance.user_name and instance.user:
        return instance.user.username
    return instance.user_name


def _objectchange_object_repr(instance):
    if not instance.object_repr and instance.changed_object:
        return str(instance.changed_object)[:200]
    return instance.object_repr


denorm_registry.register(
    'core.objectchange',
    DenormSpec(
        field_name='user_name',
        compute=_objectchange_user_name,
        depends_on=frozenset({'user', 'user_name'}),
    ),
    DenormSpec(
        field_name='object_repr',
        compute=_objectchange_object_repr,
        depends_on=frozenset({'changed_object_type', 'changed_object_id', 'object_repr'}),
    ),
)
