"""
Side-effect declarations for cross-cutting concerns:
- Base model mixins (WeightMixin, DistanceMixin, CustomFieldsMixin)
- Denormalized field registry (netbox/denormalized.py)
- Counter cache system (utilities/counters.py)
- Search index (netbox/search/backends.py)

These affect many models across all apps.
"""
from netbox.side_effects import Effect, EffectTiming, EffectType, _fs, effect_registry

# ──────────────────────────────────────────────────────────────────────
# Base mixin save() effects
# ──────────────────────────────────────────────────────────────────────

# WeightMixin — inherited by Rack, RackType, Device, DeviceType, Module, ModuleType, PowerFeed
_weight_models = [
    'dcim.rack', 'dcim.racktype', 'dcim.device', 'dcim.devicetype',
    'dcim.module', 'dcim.moduletype', 'dcim.powerfeed',
]
for model in _weight_models:
    effect_registry.register(Effect(
        effect_type=EffectType.DENORMALIZATION,
        source_model=model,
        source_fields=_fs(['weight', 'weight_unit']),
        target_fields=_fs(['_abs_weight']),
        timing=EffectTiming.PRE_SAVE,
        description='Computes _abs_weight in grams from weight + weight_unit.',
        handler='netbox.models.mixins.WeightMixin.save',
    ))

# DistanceMixin — inherited by Cable, WirelessLink, CircuitTermination
_distance_models = ['dcim.cable', 'wireless.wirelesslink', 'circuits.circuittermination']
for model in _distance_models:
    effect_registry.register(Effect(
        effect_type=EffectType.DENORMALIZATION,
        source_model=model,
        source_fields=_fs(['distance', 'distance_unit']),
        target_fields=_fs(['_abs_distance']),
        timing=EffectTiming.PRE_SAVE,
        description='Computes _abs_distance in meters; clears distance_unit when no distance.',
        handler='netbox.models.mixins.DistanceMixin.save',
    ))

# CustomFieldsMixin — all models with custom fields
effect_registry.register(Effect(
    effect_type=EffectType.FIELD_NORMALIZATION,
    source_model='*',
    target_fields=_fs(['custom_field_data']),
    timing=EffectTiming.PRE_SAVE,
    description='Populates default custom field values for missing keys on all CF-enabled models.',
    handler='netbox.models.features.CustomFieldsMixin.save',
))

# ──────────────────────────────────────────────────────────────────────
# Denormalized field registry (netbox/denormalized.py)
# The existing denormalized.register() calls in apps.py are:
#   CableTermination._device → {_rack, _location, _site}
#   Prefix._site → {_region, _site_group}
#   Prefix._location → {_site}
#   CircuitTermination._site → {_region, _site_group}
#   CircuitTermination._location → {_site}
# ──────────────────────────────────────────────────────────────────────

effect_registry.register_many(
    # CableTermination._device → {_rack, _location, _site} from Device
    # The handler fires on any Device save but only relevant fields are rack/location/site
    Effect(
        effect_type=EffectType.DENORMALIZATION,
        source_model='dcim.device',
        source_fields=_fs(['rack', 'location', 'site']),
        target_model='dcim.cabletermination',
        target_fields=_fs(['_rack', '_location', '_site']),
        timing=EffectTiming.POST_SAVE,
        description='Denormalized field registry: updates CableTermination cache from Device.',
        uses_bulk_sql=True,
        handler='netbox.denormalized.update_denormalized_fields',
    ),
    # CableTermination._rack → {_location, _site} from Rack
    Effect(
        effect_type=EffectType.DENORMALIZATION,
        source_model='dcim.rack',
        source_fields=_fs(['location', 'site']),
        target_model='dcim.cabletermination',
        target_fields=_fs(['_location', '_site']),
        timing=EffectTiming.POST_SAVE,
        description='Denormalized field registry: updates CableTermination cache from Rack.',
        uses_bulk_sql=True,
        handler='netbox.denormalized.update_denormalized_fields',
    ),
    # CableTermination._location → {_site} from Location
    Effect(
        effect_type=EffectType.DENORMALIZATION,
        source_model='dcim.location',
        source_fields=_fs(['site']),
        target_model='dcim.cabletermination',
        target_fields=_fs(['_site']),
        timing=EffectTiming.POST_SAVE,
        description='Denormalized field registry: updates CableTermination cache from Location.',
        uses_bulk_sql=True,
        handler='netbox.denormalized.update_denormalized_fields',
    ),
    # CableTermination from Site: {region, group}
    Effect(
        effect_type=EffectType.DENORMALIZATION,
        source_model='dcim.site',
        source_fields=_fs(['region', 'group']),
        target_model='dcim.cabletermination',
        target_fields=_fs(['_region', '_site_group']),
        timing=EffectTiming.POST_SAVE,
        description='Denormalized field registry: updates CableTermination cache from Site.',
        uses_bulk_sql=True,
        handler='netbox.denormalized.update_denormalized_fields',
    ),
    # Prefix._site → {_region, _site_group} from Site
    Effect(
        effect_type=EffectType.DENORMALIZATION,
        source_model='dcim.site',
        source_fields=_fs(['region', 'group']),
        target_model='ipam.prefix',
        target_fields=_fs(['_region', '_site_group']),
        timing=EffectTiming.POST_SAVE,
        description='Denormalized field registry: updates Prefix scope cache from Site.',
        uses_bulk_sql=True,
        handler='netbox.denormalized.update_denormalized_fields',
    ),
    # Prefix._location → {_site} from Location
    Effect(
        effect_type=EffectType.DENORMALIZATION,
        source_model='dcim.location',
        source_fields=_fs(['site']),
        target_model='ipam.prefix',
        target_fields=_fs(['_site']),
        timing=EffectTiming.POST_SAVE,
        description='Denormalized field registry: updates Prefix scope cache from Location.',
        uses_bulk_sql=True,
        handler='netbox.denormalized.update_denormalized_fields',
    ),
    # CircuitTermination._site → {_region, _site_group} from Site
    Effect(
        effect_type=EffectType.DENORMALIZATION,
        source_model='dcim.site',
        source_fields=_fs(['region', 'group']),
        target_model='circuits.circuittermination',
        target_fields=_fs(['_region', '_site_group']),
        timing=EffectTiming.POST_SAVE,
        description='Denormalized field registry: updates CircuitTermination cache from Site.',
        uses_bulk_sql=True,
        handler='netbox.denormalized.update_denormalized_fields',
    ),
    # CircuitTermination._location → {_site} from Location
    Effect(
        effect_type=EffectType.DENORMALIZATION,
        source_model='dcim.location',
        source_fields=_fs(['site']),
        target_model='circuits.circuittermination',
        target_fields=_fs(['_site']),
        timing=EffectTiming.POST_SAVE,
        description='Denormalized field registry: updates CircuitTermination cache from Location.',
        uses_bulk_sql=True,
        handler='netbox.denormalized.update_denormalized_fields',
    ),
)

# ──────────────────────────────────────────────────────────────────────
# Counter cache system (utilities/counters.py)
# Connected via connect_counters() in dcim/apps.py and virtualization/apps.py
# Parents: Device, DeviceType, ModuleType, RackType, VirtualChassis, VirtualMachine
# ──────────────────────────────────────────────────────────────────────

_counter_relationships = [
    # (child_model, parent_model, fk_field, description)
    ('dcim.consoleport', 'dcim.device', 'device', 'Console port count on device'),
    ('dcim.consoleserverport', 'dcim.device', 'device', 'Console server port count on device'),
    ('dcim.powerport', 'dcim.device', 'device', 'Power port count on device'),
    ('dcim.poweroutlet', 'dcim.device', 'device', 'Power outlet count on device'),
    ('dcim.interface', 'dcim.device', 'device', 'Interface count on device'),
    ('dcim.frontport', 'dcim.device', 'device', 'Front port count on device'),
    ('dcim.rearport', 'dcim.device', 'device', 'Rear port count on device'),
    ('dcim.devicebay', 'dcim.device', 'device', 'Device bay count on device'),
    ('dcim.modulebay', 'dcim.device', 'device', 'Module bay count on device'),
    ('dcim.inventoryitem', 'dcim.device', 'device', 'Inventory item count on device'),
    ('dcim.consoleporttemplate', 'dcim.devicetype', 'device_type', 'Console port template count on device type'),
    ('dcim.consoleserverporttemplate', 'dcim.devicetype', 'device_type', 'Console server port template count'),
    ('dcim.powerporttemplate', 'dcim.devicetype', 'device_type', 'Power port template count on device type'),
    ('dcim.poweroutlettemplate', 'dcim.devicetype', 'device_type', 'Power outlet template count on device type'),
    ('dcim.interfacetemplate', 'dcim.devicetype', 'device_type', 'Interface template count on device type'),
    ('dcim.frontporttemplate', 'dcim.devicetype', 'device_type', 'Front port template count on device type'),
    ('dcim.rearporttemplate', 'dcim.devicetype', 'device_type', 'Rear port template count on device type'),
    ('dcim.devicebaytemplate', 'dcim.devicetype', 'device_type', 'Device bay template count on device type'),
    ('dcim.modulebaytemplate', 'dcim.devicetype', 'device_type', 'Module bay template count on device type'),
    ('dcim.inventoryitemtemplate', 'dcim.devicetype', 'device_type', 'Inventory item template count on device type'),
    ('dcim.device', 'dcim.devicetype', 'device_type', 'Device count on device type'),
    ('dcim.module', 'dcim.moduletype', 'module_type', 'Module count on module type'),
    ('dcim.rack', 'dcim.racktype', 'rack_type', 'Rack count on rack type'),
    ('dcim.device', 'dcim.virtualchassis', 'virtual_chassis', 'Device count on virtual chassis'),
    ('virtualization.vminterface', 'virtualization.virtualmachine', 'virtual_machine', 'VM interface count'),
    ('virtualization.virtualdisk', 'virtualization.virtualmachine', 'virtual_machine', 'Virtual disk count'),
]

for child, parent, fk_field, desc in _counter_relationships:
    effect_registry.register(Effect(
        effect_type=EffectType.COUNTER_CACHE,
        source_model=child,
        source_fields=_fs([fk_field]),
        target_model=parent,
        timing=EffectTiming.POST_SAVE,
        description=f'Counter cache: {desc}',
        uses_bulk_sql=True,
        handler='utilities.counters.post_save_receiver',
    ))
    effect_registry.register(Effect(
        effect_type=EffectType.COUNTER_CACHE,
        source_model=child,
        source_fields=_fs([fk_field]),
        target_model=parent,
        timing=EffectTiming.POST_DELETE,
        description=f'Counter cache (delete): {desc}',
        uses_bulk_sql=True,
        handler='utilities.counters.post_delete_receiver',
    ))

# ──────────────────────────────────────────────────────────────────────
# Search index (netbox/search/backends.py)
# ──────────────────────────────────────────────────────────────────────

effect_registry.register_many(
    Effect(
        effect_type=EffectType.OTHER,
        source_model='*',
        target_model='extras.cachedvalue',
        timing=EffectTiming.POST_SAVE,
        description='Updates search index CachedValue entries for indexed models.',
        uses_bulk_sql=True,
        handler='netbox.search.backends.CachedValueSearchBackend.caching_handler',
    ),
    Effect(
        effect_type=EffectType.OTHER,
        source_model='*',
        target_model='extras.cachedvalue',
        timing=EffectTiming.POST_DELETE,
        description='Removes search index CachedValue entries for deleted objects.',
        uses_bulk_sql=True,
        handler='netbox.search.backends.CachedValueSearchBackend.removal_handler',
    ),
)
