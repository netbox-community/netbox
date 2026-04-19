"""
Side-effect declarations for the dcim app.

Every save() override, signal handler, and denormalized field update in dcim is
declared here. See netbox/side_effects.py for the framework.
"""
from netbox.side_effects import Effect, EffectTiming, EffectType, _fs, effect_registry

# ──────────────────────────────────────────────────────────────────────
# save() overrides
# ──────────────────────────────────────────────────────────────────────

effect_registry.register_many(

    # --- RackType.save ---
    Effect(
        effect_type=EffectType.FIELD_NORMALIZATION,
        source_model='dcim.racktype',
        target_fields=_fs(['_abs_max_weight', 'outer_unit']),
        timing=EffectTiming.PRE_SAVE,
        description='Computes _abs_max_weight in grams; clears outer_unit when no outer dims.',
        handler='dcim.models.racks.RackType.save',
    ),
    Effect(
        effect_type=EffectType.CASCADE_UPDATE,
        source_model='dcim.racktype',
        target_model='dcim.rack',
        timing=EffectTiming.POST_SAVE,
        description='Iterates ALL related Racks, calls copy_racktype_attrs() + save() on each.',
        produces_object_change=True,
        handler='dcim.models.racks.RackType.save',
    ),

    # --- Rack.save ---
    Effect(
        effect_type=EffectType.DENORMALIZATION,
        source_model='dcim.rack',
        target_fields=_fs(['_abs_max_weight', 'outer_unit', 'outer_width', 'outer_depth', 'outer_height', 'max_weight', 'weight', 'weight_unit']),
        timing=EffectTiming.PRE_SAVE,
        description='Copies physical attributes from rack_type via copy_racktype_attrs().',
        handler='dcim.models.racks.Rack.save',
    ),

    # --- PowerFeed.save ---
    Effect(
        effect_type=EffectType.DENORMALIZATION,
        source_model='dcim.powerfeed',
        source_fields=_fs(['voltage', 'amperage', 'max_utilization', 'phase']),
        target_fields=_fs(['available_power']),
        timing=EffectTiming.PRE_SAVE,
        description='Computes available_power from voltage * amperage * max_utilization (* sqrt3 for 3-phase).',
        handler='dcim.models.power.PowerFeed.save',
    ),

    # --- Module.save ---
    Effect(
        effect_type=EffectType.ENTITY_INSTANTIATION,
        source_model='dcim.module',
        target_model='dcim.consoleport',
        timing=EffectTiming.POST_SAVE,
        description='Creates console port instances from module_type templates on new modules.',
        produces_object_change=True,
        handler='dcim.models.modules.Module.save',
        only_on_create=True,
    ),
    Effect(
        effect_type=EffectType.ENTITY_INSTANTIATION,
        source_model='dcim.module',
        target_model='dcim.interface',
        timing=EffectTiming.POST_SAVE,
        description='Creates interface instances from module_type templates on new modules.',
        produces_object_change=True,
        handler='dcim.models.modules.Module.save',
        only_on_create=True,
    ),
    Effect(
        effect_type=EffectType.ENTITY_INSTANTIATION,
        source_model='dcim.module',
        target_model='dcim.powerport',
        timing=EffectTiming.POST_SAVE,
        description='Creates power port instances from module_type templates on new modules.',
        produces_object_change=True,
        handler='dcim.models.modules.Module.save',
        only_on_create=True,
    ),
    Effect(
        effect_type=EffectType.ENTITY_INSTANTIATION,
        source_model='dcim.module',
        target_model='dcim.portmapping',
        timing=EffectTiming.POST_SAVE,
        description='Creates port mappings for new module components.',
        produces_object_change=True,
        handler='dcim.models.modules.Module.save',
        only_on_create=True,
    ),

    # --- DeviceType.save ---
    Effect(
        effect_type=EffectType.CONDITIONAL_CLEANUP,
        source_model='dcim.devicetype',
        source_fields=_fs(['front_image', 'rear_image']),
        timing=EffectTiming.POST_SAVE,
        description='Deletes old front/rear image files from storage when changed.',
        handler='dcim.models.devices.DeviceType.save',
    ),

    # --- Device.save ---
    Effect(
        effect_type=EffectType.FIELD_NORMALIZATION,
        source_model='dcim.device',
        source_fields=_fs(['rack']),
        target_fields=_fs(['location']),
        timing=EffectTiming.PRE_SAVE,
        description='Sets location from rack.location if rack has one.',
        handler='dcim.models.devices.Device.save',
    ),
    Effect(
        effect_type=EffectType.FIELD_NORMALIZATION,
        source_model='dcim.device',
        target_fields=_fs(['airflow', 'platform']),
        timing=EffectTiming.PRE_SAVE,
        description='Defaults airflow and platform from device_type on create.',
        handler='dcim.models.devices.Device.save',
        only_on_create=True,
    ),
    Effect(
        effect_type=EffectType.ENTITY_INSTANTIATION,
        source_model='dcim.device',
        target_model='dcim.interface',
        timing=EffectTiming.POST_SAVE,
        description='Creates all component instances from device_type templates on new devices.',
        produces_object_change=True,
        handler='dcim.models.devices.Device.save',
        only_on_create=True,
    ),
    Effect(
        effect_type=EffectType.CASCADE_UPDATE,
        source_model='dcim.device',
        source_fields=_fs(['site', 'rack', 'location']),
        target_model='dcim.device',
        target_fields=_fs(['site', 'rack', 'location']),
        timing=EffectTiming.POST_SAVE,
        description='Propagates site/rack/location to child devices in device bays.',
        produces_object_change=True,
        handler='dcim.models.devices.Device.save',
    ),

    # --- ComponentModel.save (abstract — inherited by all device components) ---
    Effect(
        effect_type=EffectType.DENORMALIZATION,
        source_model='dcim.consoleport',
        target_fields=_fs(['_site', '_location', '_rack']),
        timing=EffectTiming.PRE_SAVE,
        description='Caches _site/_location/_rack from parent device.',
        handler='dcim.models.device_components.ComponentModel.save',
    ),
    Effect(
        effect_type=EffectType.DENORMALIZATION,
        source_model='dcim.consoleserverport',
        target_fields=_fs(['_site', '_location', '_rack']),
        timing=EffectTiming.PRE_SAVE,
        description='Caches _site/_location/_rack from parent device.',
        handler='dcim.models.device_components.ComponentModel.save',
    ),
    Effect(
        effect_type=EffectType.DENORMALIZATION,
        source_model='dcim.powerport',
        target_fields=_fs(['_site', '_location', '_rack']),
        timing=EffectTiming.PRE_SAVE,
        description='Caches _site/_location/_rack from parent device.',
        handler='dcim.models.device_components.ComponentModel.save',
    ),
    Effect(
        effect_type=EffectType.DENORMALIZATION,
        source_model='dcim.poweroutlet',
        target_fields=_fs(['_site', '_location', '_rack']),
        timing=EffectTiming.PRE_SAVE,
        description='Caches _site/_location/_rack from parent device.',
        handler='dcim.models.device_components.ComponentModel.save',
    ),
    Effect(
        effect_type=EffectType.DENORMALIZATION,
        source_model='dcim.interface',
        target_fields=_fs(['_site', '_location', '_rack']),
        timing=EffectTiming.PRE_SAVE,
        description='Caches _site/_location/_rack from parent device.',
        handler='dcim.models.device_components.ComponentModel.save',
    ),
    Effect(
        effect_type=EffectType.DENORMALIZATION,
        source_model='dcim.frontport',
        target_fields=_fs(['_site', '_location', '_rack']),
        timing=EffectTiming.PRE_SAVE,
        description='Caches _site/_location/_rack from parent device.',
        handler='dcim.models.device_components.ComponentModel.save',
    ),
    Effect(
        effect_type=EffectType.DENORMALIZATION,
        source_model='dcim.rearport',
        target_fields=_fs(['_site', '_location', '_rack']),
        timing=EffectTiming.PRE_SAVE,
        description='Caches _site/_location/_rack from parent device.',
        handler='dcim.models.device_components.ComponentModel.save',
    ),
    Effect(
        effect_type=EffectType.DENORMALIZATION,
        source_model='dcim.modulebay',
        target_fields=_fs(['_site', '_location', '_rack']),
        timing=EffectTiming.PRE_SAVE,
        description='Caches _site/_location/_rack from parent device.',
        handler='dcim.models.device_components.ComponentModel.save',
    ),
    Effect(
        effect_type=EffectType.DENORMALIZATION,
        source_model='dcim.devicebay',
        target_fields=_fs(['_site', '_location', '_rack']),
        timing=EffectTiming.PRE_SAVE,
        description='Caches _site/_location/_rack from parent device.',
        handler='dcim.models.device_components.ComponentModel.save',
    ),
    Effect(
        effect_type=EffectType.DENORMALIZATION,
        source_model='dcim.inventoryitem',
        target_fields=_fs(['_site', '_location', '_rack']),
        timing=EffectTiming.PRE_SAVE,
        description='Caches _site/_location/_rack from parent device.',
        handler='dcim.models.device_components.ComponentModel.save',
    ),

    # --- BaseInterface.save (abstract — Interface + VMInterface) ---
    Effect(
        effect_type=EffectType.CONDITIONAL_CLEANUP,
        source_model='dcim.interface',
        source_fields=_fs(['mode']),
        target_fields=_fs(['untagged_vlan']),
        timing=EffectTiming.PRE_SAVE,
        description='Clears untagged_vlan when mode is removed; clears tagged_vlans M2M when mode != tagged.',
        handler='dcim.models.device_components.BaseInterface.save',
    ),

    # --- Interface.save ---
    Effect(
        effect_type=EffectType.FIELD_NORMALIZATION,
        source_model='dcim.interface',
        source_fields=_fs(['rf_channel']),
        target_fields=_fs(['rf_channel_frequency', 'rf_channel_width']),
        timing=EffectTiming.PRE_SAVE,
        description='Fills RF frequency/width from rf_channel metadata when missing.',
        handler='dcim.models.device_components.Interface.save',
    ),

    # --- PortMapping.save ---
    Effect(
        effect_type=EffectType.DENORMALIZATION,
        source_model='dcim.portmapping',
        target_fields=_fs(['device']),
        timing=EffectTiming.PRE_SAVE,
        description='Sets device from front_port.device.',
        handler='dcim.models.device_components.PortMapping.save',
    ),

    # --- ModuleBay.save ---
    Effect(
        effect_type=EffectType.GRAPH_RECOMPUTATION,
        source_model='dcim.modulebay',
        source_fields=_fs(['module']),
        target_fields=_fs(['parent']),
        timing=EffectTiming.PRE_SAVE,
        description='Sets MPTT parent from module.module_bay for tree structure.',
        handler='dcim.models.device_components.ModuleBay.save',
    ),

    # --- PortTemplateMapping.save ---
    Effect(
        effect_type=EffectType.DENORMALIZATION,
        source_model='dcim.porttemplatemapping',
        target_fields=_fs(['device_type', 'module_type']),
        timing=EffectTiming.PRE_SAVE,
        description='Sets device_type/module_type from front_port template.',
        handler='dcim.models.device_component_templates.PortTemplateMapping.save',
    ),

    # --- Cable.save ---
    Effect(
        effect_type=EffectType.FIELD_NORMALIZATION,
        source_model='dcim.cable',
        source_fields=_fs(['length', 'length_unit']),
        target_fields=_fs(['_abs_length']),
        timing=EffectTiming.PRE_SAVE,
        description='Computes _abs_length in meters; clears length_unit when no length.',
        handler='dcim.models.cables.Cable.save',
    ),
    Effect(
        effect_type=EffectType.ENTITY_INSTANTIATION,
        source_model='dcim.cable',
        target_model='dcim.cabletermination',
        timing=EffectTiming.POST_SAVE,
        description='Creates/updates CableTermination rows via instantiation_registry.execute().',
        produces_object_change=True,
        handler='dcim.instantiation._cable_sync_terminations',
    ),
    Effect(
        effect_type=EffectType.GRAPH_RECOMPUTATION,
        source_model='dcim.cable',
        target_model='dcim.cablepath',
        timing=EffectTiming.POST_SAVE,
        description='Calls update_connected_endpoints directly for cable path rebuild.',
        handler='dcim.signals.update_connected_endpoints',
    ),

    # --- CableTermination.save ---
    Effect(
        effect_type=EffectType.DENORMALIZATION,
        source_model='dcim.cabletermination',
        target_fields=_fs(['_device', '_rack', '_location', '_site']),
        timing=EffectTiming.PRE_SAVE,
        description='Caches _device/_rack/_location/_site from termination GFK.',
        handler='dcim.models.cables.CableTermination.save',
    ),
    Effect(
        effect_type=EffectType.CASCADE_UPDATE,
        source_model='dcim.cabletermination',
        timing=EffectTiming.POST_SAVE,
        description='Updates cable/cable_end on the terminated object (Interface/FrontPort/etc.).',
        produces_object_change=True,
        handler='dcim.models.cables.CableTermination.save',
    ),

    # --- CablePath.save ---
    Effect(
        effect_type=EffectType.FIELD_NORMALIZATION,
        source_model='dcim.cablepath',
        target_fields=_fs(['_nodes']),
        timing=EffectTiming.PRE_SAVE,
        description='Flattens path list into _nodes.',
        handler='dcim.models.cables.CablePath.save',
    ),
    Effect(
        effect_type=EffectType.DENORMALIZATION,
        source_model='dcim.cablepath',
        timing=EffectTiming.POST_SAVE,
        description='Updates _path FK on all origin endpoint objects.',
        uses_bulk_sql=True,
        handler='dcim.models.cables.CablePath.save',
    ),
)

# ──────────────────────────────────────────────────────────────────────
# Signal handlers
# ──────────────────────────────────────────────────────────────────────

effect_registry.register_many(

    # --- handle_location_site_change (post_save Location) ---
    Effect(
        effect_type=EffectType.CASCADE_UPDATE,
        source_model='dcim.location',
        source_fields=_fs(['site']),
        target_model='dcim.location',
        target_fields=_fs(['site']),
        timing=EffectTiming.POST_SAVE,
        description='Bulk-updates site on ALL descendant locations.',
        uses_bulk_sql=True,
        handler='dcim.signals.handle_location_site_change',
    ),
    Effect(
        effect_type=EffectType.CASCADE_UPDATE,
        source_model='dcim.location',
        source_fields=_fs(['site']),
        target_model='dcim.rack',
        target_fields=_fs(['site']),
        timing=EffectTiming.POST_SAVE,
        description='Bulk-updates site on racks in changed locations.',
        uses_bulk_sql=True,
        handler='dcim.signals.handle_location_site_change',
    ),
    Effect(
        effect_type=EffectType.CASCADE_UPDATE,
        source_model='dcim.location',
        source_fields=_fs(['site']),
        target_model='dcim.device',
        target_fields=_fs(['site']),
        timing=EffectTiming.POST_SAVE,
        description='Bulk-updates site on devices in changed locations.',
        uses_bulk_sql=True,
        handler='dcim.signals.handle_location_site_change',
    ),
    Effect(
        effect_type=EffectType.DENORMALIZATION,
        source_model='dcim.location',
        source_fields=_fs(['site']),
        target_model='dcim.cabletermination',
        target_fields=_fs(['_site', '_location']),
        timing=EffectTiming.POST_SAVE,
        description='Bulk-updates _site/_location on cable terminations in changed locations.',
        uses_bulk_sql=True,
        handler='dcim.signals.handle_location_site_change',
    ),

    # --- handle_rack_site_change (post_save Rack) ---
    Effect(
        effect_type=EffectType.CASCADE_UPDATE,
        source_model='dcim.rack',
        source_fields=_fs(['site', 'location']),
        target_model='dcim.device',
        target_fields=_fs(['site', 'location']),
        timing=EffectTiming.POST_SAVE,
        description='Bulk-updates site/location on devices in rack.',
        uses_bulk_sql=True,
        handler='dcim.signals.handle_rack_site_change',
    ),

    # --- handle_device_site_change (post_save Device) ---
    Effect(
        effect_type=EffectType.DENORMALIZATION,
        source_model='dcim.device',
        source_fields=_fs(['site', 'location', 'rack']),
        target_model='dcim.consoleport',
        target_fields=_fs(['_site', '_location', '_rack']),
        timing=EffectTiming.POST_SAVE,
        description='Bulk-updates _site/_location/_rack on device components.',
        uses_bulk_sql=True,
        handler='dcim.signals.handle_device_site_change',
    ),
    Effect(
        effect_type=EffectType.DENORMALIZATION,
        source_model='dcim.device',
        source_fields=_fs(['site', 'location', 'rack']),
        target_model='dcim.interface',
        target_fields=_fs(['_site', '_location', '_rack']),
        timing=EffectTiming.POST_SAVE,
        description='Bulk-updates _site/_location/_rack on device interfaces.',
        uses_bulk_sql=True,
        handler='dcim.signals.handle_device_site_change',
    ),

    # --- assign_virtualchassis_master (post_save VirtualChassis) ---
    Effect(
        effect_type=EffectType.CASCADE_UPDATE,
        source_model='dcim.virtualchassis',
        source_fields=_fs(['master']),
        target_model='dcim.device',
        target_fields=_fs(['virtual_chassis', 'vc_position']),
        timing=EffectTiming.POST_SAVE,
        description='Sets virtual_chassis and vc_position=1 on master device.',
        produces_object_change=True,
        handler='dcim.signals.assign_virtualchassis_master',
        only_on_create=True,
    ),

    # --- update_connected_endpoints (called directly from Cable.save) ---
    Effect(
        effect_type=EffectType.GRAPH_RECOMPUTATION,
        source_model='dcim.cable',
        target_model='dcim.cablepath',
        timing=EffectTiming.POST_SAVE,
        description='Creates or rebuilds CablePath objects after Cable.save() completes.',
        handler='dcim.signals.update_connected_endpoints',
    ),

    # --- retrace_cable_paths (post_delete Cable) ---
    Effect(
        effect_type=EffectType.GRAPH_RECOMPUTATION,
        source_model='dcim.cable',
        target_model='dcim.cablepath',
        timing=EffectTiming.POST_DELETE,
        description='Retraces all CablePaths that contained the deleted cable.',
        handler='dcim.signals.retrace_cable_paths',
    ),

    # --- update_passthrough_port_paths (post_save/delete PortMapping) ---
    Effect(
        effect_type=EffectType.GRAPH_RECOMPUTATION,
        source_model='dcim.portmapping',
        target_model='dcim.cablepath',
        timing=EffectTiming.POST_SAVE,
        description='Retraces cable paths when port mappings change.',
        handler='dcim.signals.update_passthrough_port_paths',
    ),
    Effect(
        effect_type=EffectType.GRAPH_RECOMPUTATION,
        source_model='dcim.portmapping',
        target_model='dcim.cablepath',
        timing=EffectTiming.POST_DELETE,
        description='Retraces cable paths when port mappings are deleted.',
        handler='dcim.signals.update_passthrough_port_paths',
    ),

    # --- nullify_connected_endpoints (post_delete CableTermination) ---
    Effect(
        effect_type=EffectType.CONDITIONAL_CLEANUP,
        source_model='dcim.cabletermination',
        timing=EffectTiming.POST_DELETE,
        description='Nullifies cable/cable_end on termination target; clears _path; retraces cable paths.',
        uses_bulk_sql=True,
        handler='dcim.signals.nullify_connected_endpoints',
    ),

    # --- update_mac_address_interface (post_save Interface/VMInterface) ---
    Effect(
        effect_type=EffectType.CASCADE_UPDATE,
        source_model='dcim.interface',
        source_fields=_fs(['primary_mac_address']),
        target_model='dcim.macaddress',
        target_fields=_fs(['assigned_object_type', 'assigned_object_id']),
        timing=EffectTiming.POST_SAVE,
        description='Sets MACAddress.assigned_object on new interface with primary_mac_address.',
        produces_object_change=True,
        handler='dcim.signals.update_mac_address_interface',
        only_on_create=True,
    ),

    # --- sync_cached_scope_fields (post_save Location + Site) ---
    # Handler fires on any save but only meaningful when scope-affecting fields change.
    # Location: site or parent change affects scope. Site: region or group change.
    Effect(
        effect_type=EffectType.DENORMALIZATION,
        source_model='dcim.location',
        source_fields=_fs(['site', 'parent']),
        target_model='ipam.prefix',
        target_fields=_fs(['_location', '_site', '_site_group', '_region']),
        timing=EffectTiming.POST_SAVE,
        description='Bulk-updates scope cache fields on scoped Prefixes when location changes.',
        uses_bulk_sql=True,
        handler='dcim.signals.sync_cached_scope_fields',
    ),
    Effect(
        effect_type=EffectType.DENORMALIZATION,
        source_model='dcim.location',
        source_fields=_fs(['site', 'parent']),
        target_model='virtualization.cluster',
        target_fields=_fs(['_location', '_site', '_site_group', '_region']),
        timing=EffectTiming.POST_SAVE,
        description='Bulk-updates scope cache fields on scoped Clusters when location changes.',
        uses_bulk_sql=True,
        handler='dcim.signals.sync_cached_scope_fields',
    ),
    Effect(
        effect_type=EffectType.DENORMALIZATION,
        source_model='dcim.location',
        source_fields=_fs(['site', 'parent']),
        target_model='wireless.wirelesslan',
        target_fields=_fs(['_location', '_site', '_site_group', '_region']),
        timing=EffectTiming.POST_SAVE,
        description='Bulk-updates scope cache fields on scoped WirelessLANs when location changes.',
        uses_bulk_sql=True,
        handler='dcim.signals.sync_cached_scope_fields',
    ),
    Effect(
        effect_type=EffectType.DENORMALIZATION,
        source_model='dcim.site',
        source_fields=_fs(['region', 'group']),
        target_model='ipam.prefix',
        target_fields=_fs(['_location', '_site', '_site_group', '_region']),
        timing=EffectTiming.POST_SAVE,
        description='Bulk-updates scope cache fields on scoped Prefixes when site changes.',
        uses_bulk_sql=True,
        handler='dcim.signals.sync_cached_scope_fields',
    ),
    Effect(
        effect_type=EffectType.DENORMALIZATION,
        source_model='dcim.site',
        source_fields=_fs(['region', 'group']),
        target_model='virtualization.cluster',
        target_fields=_fs(['_location', '_site', '_site_group', '_region']),
        timing=EffectTiming.POST_SAVE,
        description='Bulk-updates scope cache fields on scoped Clusters when site changes.',
        uses_bulk_sql=True,
        handler='dcim.signals.sync_cached_scope_fields',
    ),
    Effect(
        effect_type=EffectType.DENORMALIZATION,
        source_model='dcim.site',
        source_fields=_fs(['region', 'group']),
        target_model='wireless.wirelesslan',
        target_fields=_fs(['_location', '_site', '_site_group', '_region']),
        timing=EffectTiming.POST_SAVE,
        description='Bulk-updates scope cache fields on scoped WirelessLANs when site changes.',
        uses_bulk_sql=True,
        handler='dcim.signals.sync_cached_scope_fields',
    ),
)
