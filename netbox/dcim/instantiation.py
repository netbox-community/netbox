"""
Declarative instantiation registrations for dcim models.

Replaces the imperative _instantiate_components loops in Device.save()
and Module.save() with structured declarations.
"""
from netbox.instantiation import InstantiationSpec, instantiation_registry

# ──────────────────────────────────────────────────────────────────────
# Device creation → instantiate components from DeviceType templates
# Replaces: imperative loop in Device.save()
# ──────────────────────────────────────────────────────────────────────

_DEVICE_COMPONENT_TEMPLATES = [
    ('dcim.consoleport', 'device_type.consoleporttemplates.all', True),
    ('dcim.consoleserverport', 'device_type.consoleserverporttemplates.all', True),
    ('dcim.powerport', 'device_type.powerporttemplates.all', True),
    ('dcim.poweroutlet', 'device_type.poweroutlettemplates.all', True),
    ('dcim.interface', 'device_type.interfacetemplates.all', True),
    ('dcim.rearport', 'device_type.rearporttemplates.all', True),
    ('dcim.frontport', 'device_type.frontporttemplates.all', True),
    ('dcim.modulebay', 'device_type.modulebaytemplates.all', False),
    ('dcim.devicebay', 'device_type.devicebaytemplates.all', True),
    ('dcim.inventoryitem', 'device_type.inventoryitemtemplates.all', False),
]

for target_model, template_relation, bulk in _DEVICE_COMPONENT_TEMPLATES:
    instantiation_registry.register(
        InstantiationSpec(
            source_model='dcim.device',
            target_model=target_model,
            template_relation=template_relation,
            bulk_create=bulk,
            description=f'Create {target_model.split(".")[1]} from DeviceType templates on Device creation',
        ),
    )

# Port mappings are a special case — created after ports
instantiation_registry.register(
    InstantiationSpec(
        source_model='dcim.device',
        target_model='dcim.portmapping',
        template_relation='device_type',
        description='Replicate front/rear port mappings from DeviceType on Device creation',
    ),
)

# Interface bridges updated after all interfaces created
instantiation_registry.register(
    InstantiationSpec(
        source_model='dcim.device',
        target_model='dcim.interface',
        template_relation='device_type.interfacetemplates.all',
        description='Set bridge references on interfaces after instantiation from DeviceType templates',
    ),
)


# ──────────────────────────────────────────────────────────────────────
# Module creation → instantiate components from ModuleType templates
# Replaces: imperative loop in Module.save()
# ──────────────────────────────────────────────────────────────────────

_MODULE_COMPONENT_TEMPLATES = [
    ('dcim.consoleport', 'module_type.consoleporttemplates.all', True),
    ('dcim.consoleserverport', 'module_type.consoleserverporttemplates.all', True),
    ('dcim.powerport', 'module_type.powerporttemplates.all', True),
    ('dcim.poweroutlet', 'module_type.poweroutlettemplates.all', True),
    ('dcim.interface', 'module_type.interfacetemplates.all', True),
    ('dcim.rearport', 'module_type.rearporttemplates.all', True),
    ('dcim.frontport', 'module_type.frontporttemplates.all', True),
]

for target_model, template_relation, bulk in _MODULE_COMPONENT_TEMPLATES:
    instantiation_registry.register(
        InstantiationSpec(
            source_model='dcim.module',
            target_model=target_model,
            template_relation=template_relation,
            bulk_create=bulk,
            description=f'Create {target_model.split(".")[1]} from ModuleType templates on Module creation',
        ),
    )
