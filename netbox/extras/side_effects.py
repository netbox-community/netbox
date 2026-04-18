"""
Side-effect declarations for the extras app and the global event/notification pipeline.
"""
from netbox.side_effects import Effect, EffectTiming, EffectType, _fs, effect_registry

effect_registry.register_many(

    # --- ScriptModule.save ---
    Effect(
        effect_type=EffectType.ENTITY_INSTANTIATION,
        source_model='extras.scriptmodule',
        target_model='extras.script',
        timing=EffectTiming.POST_SAVE,
        description='sync_classes() creates/deletes Script rows to match module file contents.',
        handler='extras.models.scripts.ScriptModule.save',
    ),

    # --- Notification.save ---
    Effect(
        effect_type=EffectType.DENORMALIZATION,
        source_model='extras.notification',
        target_fields=_fs(['object_repr']),
        timing=EffectTiming.PRE_SAVE,
        description='Sets object_repr from related object.',
        handler='extras.models.notifications.Notification.save',
    ),

    # --- CustomFieldChoiceSet.save ---
    Effect(
        effect_type=EffectType.FIELD_NORMALIZATION,
        source_model='extras.customfieldchoiceset',
        source_fields=_fs(['extra_choices', 'order_alphabetically']),
        target_fields=_fs(['extra_choices']),
        timing=EffectTiming.PRE_SAVE,
        description='Sorts extra_choices alphabetically when order_alphabetically is set.',
        handler='extras.models.customfields.CustomFieldChoiceSet.save',
    ),

    # --- handle_cf_renamed (post_save CustomField) ---
    Effect(
        effect_type=EffectType.CASCADE_UPDATE,
        source_model='extras.customfield',
        source_fields=_fs(['name']),
        timing=EffectTiming.POST_SAVE,
        description='Renames custom field data key across all objects when CF name changes.',
        uses_bulk_sql=True,
        handler='extras.signals.handle_cf_renamed',
    ),

    # --- handle_cf_deleted (pre_delete CustomField) ---
    Effect(
        effect_type=EffectType.CONDITIONAL_CLEANUP,
        source_model='extras.customfield',
        timing=EffectTiming.PRE_DELETE,
        description='Removes stale custom field data from all objects.',
        uses_bulk_sql=True,
        handler='extras.signals.handle_cf_deleted',
    ),

    # --- handle_cf_added_obj_types (m2m_changed CustomField.object_types) ---
    Effect(
        effect_type=EffectType.ENTITY_INSTANTIATION,
        source_model='extras.customfield',
        timing=EffectTiming.POST_SAVE,
        description='Populates initial custom field data on objects when CF is assigned to new types.',
        handler='extras.signals.handle_cf_added_obj_types',
    ),

    # --- handle_cf_removed_obj_types ---
    Effect(
        effect_type=EffectType.CONDITIONAL_CLEANUP,
        source_model='extras.customfield',
        timing=EffectTiming.POST_SAVE,
        description='Removes stale custom field data when CF is unassigned from types.',
        handler='extras.signals.handle_cf_removed_obj_types',
    ),

    # --- notify_object_changed (post_save + pre_delete, ALL models) ---
    Effect(
        effect_type=EffectType.EVENT_DISPATCH,
        source_model='*',
        target_model='extras.notification',
        timing=EffectTiming.POST_SAVE,
        description='Creates Notification objects for subscribers on any model change.',
        uses_bulk_sql=True,
        handler='extras.signals.notify_object_changed',
    ),
    Effect(
        effect_type=EffectType.EVENT_DISPATCH,
        source_model='*',
        target_model='extras.notification',
        timing=EffectTiming.PRE_DELETE,
        description='Creates Notification objects for subscribers on any model delete.',
        uses_bulk_sql=True,
        handler='extras.signals.notify_object_changed',
    ),
)
