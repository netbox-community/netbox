"""
Side-effect declarations for the ipam app.
"""
from netbox.side_effects import Effect, EffectTiming, EffectType, _fs, effect_registry

# ──────────────────────────────────────────────────────────────────────
# save() overrides
# ──────────────────────────────────────────────────────────────────────

effect_registry.register_many(

    # --- VLANGroup.save ---
    Effect(
        effect_type=EffectType.DENORMALIZATION,
        source_model='ipam.vlangroup',
        source_fields=_fs(['vid_ranges']),
        target_fields=_fs(['_total_vlan_ids']),
        timing=EffectTiming.PRE_SAVE,
        description='Recomputes _total_vlan_ids from vid_ranges.',
        handler='ipam.models.vlans.VLANGroup.save',
    ),

    # --- Prefix.save ---
    Effect(
        effect_type=EffectType.FIELD_NORMALIZATION,
        source_model='ipam.prefix',
        source_fields=_fs(['prefix']),
        target_fields=_fs(['prefix']),
        timing=EffectTiming.PRE_SAVE,
        description='Normalizes prefix to canonical CIDR form (strips host bits).',
        handler='ipam.models.ip.Prefix.save',
    ),
    Effect(
        effect_type=EffectType.DENORMALIZATION,
        source_model='ipam.prefix',
        source_fields=_fs(['scope_type', 'scope_id']),
        target_fields=_fs(['_region', '_site_group', '_site', '_location']),
        timing=EffectTiming.PRE_SAVE,
        description='Caches _region/_site_group/_site/_location from scope GFK.',
        handler='dcim.models.mixins.CachedScopeMixin.save',
    ),

    # --- IPRange.save ---
    Effect(
        effect_type=EffectType.DENORMALIZATION,
        source_model='ipam.iprange',
        source_fields=_fs(['start_address', 'end_address']),
        target_fields=_fs(['size']),
        timing=EffectTiming.PRE_SAVE,
        description='Computes size from end_address - start_address + 1.',
        handler='ipam.models.ip.IPRange.save',
    ),

    # --- IPAddress.save ---
    Effect(
        effect_type=EffectType.FIELD_NORMALIZATION,
        source_model='ipam.ipaddress',
        source_fields=_fs(['dns_name']),
        target_fields=_fs(['dns_name']),
        timing=EffectTiming.PRE_SAVE,
        description='Lowercases dns_name.',
        handler='ipam.models.ip.IPAddress.save',
    ),
)

# ──────────────────────────────────────────────────────────────────────
# Signal handlers
# ──────────────────────────────────────────────────────────────────────

effect_registry.register_many(

    # --- handle_prefix_saved (post_save Prefix) ---
    Effect(
        effect_type=EffectType.DENORMALIZATION,
        source_model='ipam.prefix',
        source_fields=_fs(['prefix', 'vrf']),
        target_model='ipam.prefix',
        target_fields=_fs(['_children', '_depth']),
        timing=EffectTiming.POST_SAVE,
        description='Recalculates _children and _depth on ancestor and descendant prefixes.',
        uses_bulk_sql=True,
        handler='ipam.signals.handle_prefix_saved',
    ),

    # --- handle_prefix_deleted (post_delete Prefix) ---
    Effect(
        effect_type=EffectType.DENORMALIZATION,
        source_model='ipam.prefix',
        source_fields=_fs(['prefix', 'vrf']),
        target_model='ipam.prefix',
        target_fields=_fs(['_children', '_depth']),
        timing=EffectTiming.POST_DELETE,
        description='Recalculates _children and _depth after prefix deletion.',
        uses_bulk_sql=True,
        handler='ipam.signals.handle_prefix_deleted',
    ),

    # --- clear_primary_ip (pre_delete IPAddress) ---
    Effect(
        effect_type=EffectType.CASCADE_UPDATE,
        source_model='ipam.ipaddress',
        target_model='dcim.device',
        target_fields=_fs(['primary_ip4', 'primary_ip6']),
        timing=EffectTiming.PRE_DELETE,
        description='Clears primary_ip4/primary_ip6 on Device when IP is deleted.',
        produces_object_change=True,
        handler='ipam.signals.clear_primary_ip',
    ),
    Effect(
        effect_type=EffectType.CASCADE_UPDATE,
        source_model='ipam.ipaddress',
        target_model='virtualization.virtualmachine',
        target_fields=_fs(['primary_ip4', 'primary_ip6']),
        timing=EffectTiming.PRE_DELETE,
        description='Clears primary_ip4/primary_ip6 on VirtualMachine when IP is deleted.',
        produces_object_change=True,
        handler='ipam.signals.clear_primary_ip',
    ),

    # --- clear_oob_ip (pre_delete IPAddress) ---
    Effect(
        effect_type=EffectType.CASCADE_UPDATE,
        source_model='ipam.ipaddress',
        target_model='dcim.device',
        target_fields=_fs(['oob_ip']),
        timing=EffectTiming.PRE_DELETE,
        description='Clears oob_ip on Device when IP is deleted.',
        produces_object_change=True,
        handler='ipam.signals.clear_oob_ip',
    ),
)
