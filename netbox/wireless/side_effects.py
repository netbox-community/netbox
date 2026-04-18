"""
Side-effect declarations for the wireless app.
"""
from netbox.side_effects import Effect, EffectTiming, EffectType, _fs, effect_registry

effect_registry.register_many(

    # --- WirelessLink.save ---
    Effect(
        effect_type=EffectType.DENORMALIZATION,
        source_model='wireless.wirelesslink',
        source_fields=_fs(['interface_a', 'interface_b']),
        target_fields=_fs(['_interface_a_device', '_interface_b_device']),
        timing=EffectTiming.PRE_SAVE,
        description='Caches _interface_a_device/_interface_b_device from interface.device.',
        handler='wireless.models.WirelessLink.save',
    ),

    # --- update_connected_interfaces (post_save WirelessLink) ---
    Effect(
        effect_type=EffectType.CASCADE_UPDATE,
        source_model='wireless.wirelesslink',
        target_model='dcim.interface',
        target_fields=_fs(['wireless_link']),
        timing=EffectTiming.POST_SAVE,
        description='Sets wireless_link FK on both interfaces; creates cable paths.',
        produces_object_change=True,
        handler='wireless.signals.update_connected_interfaces',
    ),
    Effect(
        effect_type=EffectType.GRAPH_RECOMPUTATION,
        source_model='wireless.wirelesslink',
        target_model='dcim.cablepath',
        timing=EffectTiming.POST_SAVE,
        description='Creates cable paths for wireless link endpoints.',
        handler='wireless.signals.update_connected_interfaces',
    ),

    # --- nullify_connected_interfaces (post_delete WirelessLink) ---
    Effect(
        effect_type=EffectType.CONDITIONAL_CLEANUP,
        source_model='wireless.wirelesslink',
        target_model='dcim.interface',
        target_fields=_fs(['wireless_link']),
        timing=EffectTiming.POST_DELETE,
        description='Nullifies wireless_link on interfaces; deletes cable paths.',
        uses_bulk_sql=True,
        handler='wireless.signals.nullify_connected_interfaces',
    ),
)
