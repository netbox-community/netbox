"""
Side-effect declarations for the circuits app.
"""
from netbox.side_effects import Effect, EffectTiming, EffectType, _fs, effect_registry

effect_registry.register_many(

    # --- CircuitTermination.save ---
    Effect(
        effect_type=EffectType.DENORMALIZATION,
        source_model='circuits.circuittermination',
        target_fields=_fs(['_provider_network', '_location', '_site', '_region', '_site_group']),
        timing=EffectTiming.PRE_SAVE,
        description='Caches scope fields from termination GFK via cache_related_objects().',
        handler='circuits.models.circuits.CircuitTermination.save',
    ),
    Effect(
        effect_type=EffectType.CASCADE_UPDATE,
        source_model='circuits.circuittermination',
        source_fields=_fs(['circuit', 'term_side']),
        target_model='circuits.circuit',
        target_fields=_fs(['termination_a', 'termination_z']),
        timing=EffectTiming.POST_SAVE,
        description='Updates Circuit.termination_a/termination_z denorm pointers.',
        uses_bulk_sql=True,
        handler='circuits.models.circuits.CircuitTermination.save',
    ),

    # --- rebuild_cablepaths (post_save/delete CircuitTermination) ---
    Effect(
        effect_type=EffectType.GRAPH_RECOMPUTATION,
        source_model='circuits.circuittermination',
        target_model='dcim.cablepath',
        timing=EffectTiming.POST_SAVE,
        description='Rebuilds cable paths for peer termination after circuit termination change.',
        handler='circuits.signals.rebuild_cablepaths',
    ),
    Effect(
        effect_type=EffectType.GRAPH_RECOMPUTATION,
        source_model='circuits.circuittermination',
        target_model='dcim.cablepath',
        timing=EffectTiming.POST_DELETE,
        description='Rebuilds cable paths for peer termination after circuit termination delete.',
        handler='circuits.signals.rebuild_cablepaths',
    ),
)
