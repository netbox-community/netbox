"""
Declarative instantiation registrations for dcim models.

Replaces the imperative _instantiate_components loops in Device.save()
and Module.save() with structured declarations, plus master handler
functions that drive the actual runtime instantiation.
"""
from django.db.models import prefetch_related_objects
from django.db.models.signals import post_save

from netbox.instantiation import InstantiationSpec, instantiation_registry


def _instantiate_device_components(device, queryset, bulk_create=True):
    """
    Instantiate components for a Device from the specified component templates.

    Moved from Device._instantiate_components().
    """
    from extras.models import CustomField
    from utilities.prefetch import get_prefetchable_fields

    model = queryset.model.component_model

    if bulk_create:
        components = [obj.instantiate(device=device) for obj in queryset]
        if not components:
            return
        if cf_defaults := CustomField.objects.get_defaults_for_model(model):
            for component in components:
                component.custom_field_data = cf_defaults
        for component in components:
            component._site = device.site
            component._location = device.location
            component._rack = device.rack
        components = model.objects.bulk_create(components)
        prefetch_fields = get_prefetchable_fields(model)
        prefetch_related_objects(components, *prefetch_fields)
        for component in components:
            post_save.send(
                sender=model,
                instance=component,
                created=True,
                raw=False,
                using='default',
                update_fields=None
            )
    else:
        for obj in queryset:
            component = obj.instantiate(device=device)
            if cf_defaults := CustomField.objects.get_defaults_for_model(model):
                component.custom_field_data = cf_defaults
            component.save()


def _device_instantiate_all(instance, **context):
    """
    Master handler: instantiate all components for a new Device from its
    DeviceType templates. Replaces the imperative block in Device.save().
    """
    from dcim.utils import create_port_mappings, update_interface_bridges

    _instantiate_device_components(instance, instance.device_type.consoleporttemplates.all())
    _instantiate_device_components(instance, instance.device_type.consoleserverporttemplates.all())
    _instantiate_device_components(instance, instance.device_type.powerporttemplates.all())
    _instantiate_device_components(instance, instance.device_type.poweroutlettemplates.all())
    _instantiate_device_components(instance, instance.device_type.interfacetemplates.all())
    _instantiate_device_components(instance, instance.device_type.rearporttemplates.all())
    _instantiate_device_components(instance, instance.device_type.frontporttemplates.all())
    create_port_mappings(instance, instance.device_type)
    # MPTT models must be saved individually
    _instantiate_device_components(instance, instance.device_type.modulebaytemplates.all(), bulk_create=False)
    _instantiate_device_components(instance, instance.device_type.devicebaytemplates.all())
    # MPTT models must be saved individually
    _instantiate_device_components(instance, instance.device_type.inventoryitemtemplates.all(), bulk_create=False)
    # Interface bridges have to be set after interface instantiation
    update_interface_bridges(instance, instance.device_type.interfacetemplates.all())


def _module_instantiate_all(instance, **context):
    """
    Master handler: instantiate/adopt all components for a new Module from its
    ModuleType templates. Replaces the imperative block in Module.save().

    Context kwargs:
        adopt_components (bool): If True, adopt existing device components
            matching template names instead of creating new ones.
        disable_replication (bool): If True, skip creating new components
            (only adopt if adopt_components is also True).
    """
    from dcim.models.device_components import (
        ConsolePort, ConsoleServerPort, FrontPort, Interface, ModuleBay,
        PowerOutlet, PowerPort, RearPort,
    )
    from dcim.utils import create_port_mappings, update_interface_bridges
    from extras.models import CustomField
    from mptt.models import MPTTModel

    adopt_components = context.get('adopt_components', False)
    disable_replication = context.get('disable_replication', False)

    if disable_replication and not adopt_components:
        return

    for templates, component_attribute, component_model in [
        ("consoleporttemplates", "consoleports", ConsolePort),
        ("consoleserverporttemplates", "consoleserverports", ConsoleServerPort),
        ("interfacetemplates", "interfaces", Interface),
        ("powerporttemplates", "powerports", PowerPort),
        ("poweroutlettemplates", "poweroutlets", PowerOutlet),
        ("rearporttemplates", "rearports", RearPort),
        ("frontporttemplates", "frontports", FrontPort),
        ("modulebaytemplates", "modulebays", ModuleBay),
    ]:
        create_instances = []
        update_instances = []

        installed_components = {
            component.name: component
            for component in getattr(instance.device, component_attribute).filter(module__isnull=True)
        }

        for template in getattr(instance.module_type, templates).all():
            template_instance = template.instantiate(device=instance.device, module=instance)

            if adopt_components:
                existing_item = installed_components.get(template_instance.name)
                if existing_item:
                    existing_item.module = instance
                    update_instances.append(existing_item)
                    continue

            if not disable_replication:
                create_instances.append(template_instance)

        if cf_defaults := CustomField.objects.get_defaults_for_model(component_model):
            for component in create_instances:
                component.custom_field_data = cf_defaults

        for component in create_instances:
            component._site = instance.device.site
            component._location = instance.device.location
            component._rack = instance.device.rack

        if not issubclass(component_model, MPTTModel):
            component_model.objects.bulk_create(create_instances)
            for component in create_instances:
                post_save.send(
                    sender=component_model,
                    instance=component,
                    created=True,
                    raw=False,
                    using='default',
                    update_fields=None
                )
        else:
            for obj in create_instances:
                obj.save()

        update_fields = ['module']

        component_model.objects.bulk_update(update_instances, update_fields)
        for component in update_instances:
            post_save.send(
                sender=component_model,
                instance=component,
                created=False,
                raw=False,
                using='default',
                update_fields=update_fields
            )

        if issubclass(component_model, MPTTModel) and update_instances:
            component_model.objects.rebuild()

    create_port_mappings(instance.device, instance.module_type, instance)
    update_interface_bridges(instance.device, instance.module_type.interfacetemplates, instance)


# ──────────────────────────────────────────────────────────────────────
# Device creation → instantiate components from DeviceType templates
# Master handler drives all component creation at runtime.
# Per-component specs retained for introspection.
# ──────────────────────────────────────────────────────────────────────

instantiation_registry.register(
    InstantiationSpec(
        source_model='dcim.device',
        target_model='dcim.device',
        template_relation='device_type',
        handler=_device_instantiate_all,
        description='Master handler: instantiate all components from DeviceType templates on Device creation',
    ),
)

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

instantiation_registry.register(
    InstantiationSpec(
        source_model='dcim.device',
        target_model='dcim.portmapping',
        template_relation='device_type',
        description='Replicate front/rear port mappings from DeviceType on Device creation',
    ),
)

instantiation_registry.register(
    InstantiationSpec(
        source_model='dcim.device',
        target_model='dcim.interface',
        template_relation='device_type.interfacetemplates.all',
        description='Set bridge references on interfaces after instantiation from DeviceType templates',
    ),
)


# ──────────────────────────────────────────────────────────────────────
# Cable save → sync CableTerminations to match A/B termination lists
# ──────────────────────────────────────────────────────────────────────

def _cable_sync_terminations(instance, **context):
    """
    Sync CableTerminations when a Cable's termination lists or profile change.
    Replaces the imperative update_terminations() calls in Cable.save().
    """
    if instance._orig_profile != instance.profile:
        instance.update_terminations(force=True)
    elif instance._terminations_modified:
        instance.update_terminations()


instantiation_registry.register(
    InstantiationSpec(
        source_model='dcim.cable',
        target_model='dcim.cabletermination',
        template_relation='a_terminations',
        handler=_cable_sync_terminations,
        description='Sync CableTerminations to reflect cable A/B termination lists and profile changes',
    ),
)


# ──────────────────────────────────────────────────────────────────────
# Module creation → instantiate components from ModuleType templates
# Master handler drives all component creation/adoption at runtime.
# Per-component specs retained for introspection.
# ──────────────────────────────────────────────────────────────────────

instantiation_registry.register(
    InstantiationSpec(
        source_model='dcim.module',
        target_model='dcim.module',
        template_relation='module_type',
        handler=_module_instantiate_all,
        description='Master handler: instantiate/adopt all components from ModuleType templates on Module creation',
    ),
)

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
