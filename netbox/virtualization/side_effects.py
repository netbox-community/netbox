"""
Side-effect declarations for the virtualization app.
"""
from netbox.side_effects import Effect, EffectTiming, EffectType, _fs, effect_registry

effect_registry.register_many(

    # --- VirtualMachine.save ---
    Effect(
        effect_type=EffectType.DENORMALIZATION,
        source_model='virtualization.virtualmachine',
        source_fields=_fs(['cluster']),
        target_fields=_fs(['site']),
        timing=EffectTiming.PRE_SAVE,
        description='Sets site from cluster._site when cluster set and site empty.',
        handler='virtualization.models.virtualmachines.VirtualMachine.save',
    ),

    # --- VMInterface.save (inherits BaseInterface) ---
    Effect(
        effect_type=EffectType.CONDITIONAL_CLEANUP,
        source_model='virtualization.vminterface',
        source_fields=_fs(['mode']),
        target_fields=_fs(['untagged_vlan']),
        timing=EffectTiming.PRE_SAVE,
        description='Clears untagged_vlan when mode removed; clears tagged_vlans M2M when mode != tagged.',
        handler='dcim.models.device_components.BaseInterface.save',
    ),

    # --- update_virtualmachine_disk (post_save/delete VirtualDisk) ---
    Effect(
        effect_type=EffectType.DENORMALIZATION,
        source_model='virtualization.virtualdisk',
        source_fields=_fs(['size']),
        target_model='virtualization.virtualmachine',
        target_fields=_fs(['disk']),
        timing=EffectTiming.POST_SAVE,
        description='Updates VirtualMachine.disk with Sum aggregate of all VirtualDisk sizes.',
        uses_bulk_sql=True,
        handler='virtualization.signals.update_virtualmachine_disk',
    ),
    Effect(
        effect_type=EffectType.DENORMALIZATION,
        source_model='virtualization.virtualdisk',
        target_model='virtualization.virtualmachine',
        target_fields=_fs(['disk']),
        timing=EffectTiming.POST_DELETE,
        description='Recomputes VirtualMachine.disk aggregate after disk deletion.',
        uses_bulk_sql=True,
        handler='virtualization.signals.update_virtualmachine_disk',
    ),

    # --- update_virtualmachine_site (post_save Cluster) ---
    Effect(
        effect_type=EffectType.CASCADE_UPDATE,
        source_model='virtualization.cluster',
        source_fields=_fs(['_site']),
        target_model='virtualization.virtualmachine',
        target_fields=_fs(['site']),
        timing=EffectTiming.POST_SAVE,
        description='Bulk-updates VirtualMachine.site when cluster site changes.',
        uses_bulk_sql=True,
        handler='virtualization.signals.update_virtualmachine_site',
    ),
)
