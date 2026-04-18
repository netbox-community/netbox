"""
Side-effect declarations for the core app — changelog, event pipeline, data sync.
"""
from netbox.side_effects import Effect, EffectTiming, EffectType, _fs, effect_registry

effect_registry.register_many(

    # --- ObjectChange.save ---
    Effect(
        effect_type=EffectType.DENORMALIZATION,
        source_model='core.objectchange',
        target_fields=_fs(['user_name', 'object_repr']),
        timing=EffectTiming.PRE_SAVE,
        description='Caches user_name from user and object_repr from changed_object.',
        handler='core.models.change_logging.ObjectChange.save',
    ),

    # --- DataSource.save ---
    Effect(
        effect_type=EffectType.CONDITIONAL_CLEANUP,
        source_model='core.datasource',
        source_fields=_fs(['sync_interval']),
        target_model='core.job',
        timing=EffectTiming.PRE_SAVE,
        description='Deletes pending sync jobs when sync_interval is cleared.',
        handler='core.models.data.DataSource.save',
    ),

    # --- SyncedDataMixin.save ---
    Effect(
        effect_type=EffectType.CASCADE_UPDATE,
        source_model='core.managedfile',
        source_fields=_fs(['auto_sync_enabled', 'data_file']),
        target_model='core.autosyncrecord',
        timing=EffectTiming.POST_SAVE,
        description='Creates/updates/deletes AutoSyncRecord based on auto_sync_enabled.',
        handler='netbox.models.features.SyncedDataMixin.save',
    ),

    # --- handle_changed_object (post_save + m2m_changed, ALL models) ---
    Effect(
        effect_type=EffectType.EVENT_DISPATCH,
        source_model='*',
        target_model='core.objectchange',
        timing=EffectTiming.POST_SAVE,
        description='Creates ObjectChange audit log entry and enqueues events for webhooks.',
        handler='core.signals.handle_changed_object',
    ),

    # --- handle_deleted_object (pre_delete, ALL models) ---
    Effect(
        effect_type=EffectType.EVENT_DISPATCH,
        source_model='*',
        target_model='core.objectchange',
        timing=EffectTiming.PRE_DELETE,
        description='Creates ObjectChange for delete; may cascade snapshot/save related objects for logging.',
        handler='core.signals.handle_deleted_object',
    ),

    # --- enqueue_sync_job (post_save DataSource) ---
    Effect(
        effect_type=EffectType.OTHER,
        source_model='core.datasource',
        source_fields=_fs(['sync_interval']),
        timing=EffectTiming.POST_SAVE,
        description='Enqueues or deletes scheduled SyncDataSourceJob based on sync_interval.',
        handler='core.signals.enqueue_sync_job',
    ),

    # --- auto_sync (post_sync DataSource) ---
    Effect(
        effect_type=EffectType.CASCADE_UPDATE,
        source_model='core.datasource',
        timing=EffectTiming.POST_SAVE,
        description='After DataSource sync, runs sync(save=True) on all AutoSyncRecord objects.',
        handler='core.signals.auto_sync',
    ),

    # --- update_config (post_save ConfigRevision) ---
    Effect(
        effect_type=EffectType.OTHER,
        source_model='core.configrevision',
        timing=EffectTiming.POST_SAVE,
        description='Activates new configuration revision (reloads cached config).',
        handler='core.signals.update_config',
    ),

    # --- update_object_types (post_migrate) ---
    Effect(
        effect_type=EffectType.OTHER,
        source_model='*',
        target_model='core.objecttype',
        timing=EffectTiming.POST_SAVE,
        description='Creates/updates ObjectType registry entries after migrations.',
        handler='core.signals.update_object_types',
    ),
)
