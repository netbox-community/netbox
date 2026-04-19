"""
Declarative cascade registrations for dcim models.

Replaces imperative signal handlers in dcim/signals.py with structured
declarations that drive the same behavior from the cascade registry.
"""
from netbox.cascades import CascadeMethod, CascadeSpec, CascadeTiming, cascade_registry


# ──────────────────────────────────────────────────────────────────────
# Location site change → descendants, racks, devices, panels, terminations, components
# Replaces: handle_location_site_change signal handler
# ──────────────────────────────────────────────────────────────────────

def _location_descendant_filter(instance):
    return {'pk__in': instance.get_descendants().values_list('pk', flat=True)}

def _location_tree_filter(instance):
    """All locations including self and descendants."""
    return {'location__in': instance.get_descendants(include_self=True).values_list('pk', flat=True)}

def _device_in_location_tree(instance):
    locations = instance.get_descendants(include_self=True).values_list('pk', flat=True)
    return {'device__location__in': locations}

def _cable_term_in_location_tree(instance):
    locations = instance.get_descendants(include_self=True).values_list('pk', flat=True)
    return {'_location__in': locations}


cascade_registry.register(
    CascadeSpec(
        source_model='dcim.location',
        target_model='dcim.location',
        trigger_fields=frozenset({'site'}),
        field_mapping={'site': 'site'},
        filter_spec=_location_descendant_filter,
        description='Propagate site to all descendant locations',
    ),
    CascadeSpec(
        source_model='dcim.location',
        target_model='dcim.rack',
        trigger_fields=frozenset({'site'}),
        field_mapping={'site': 'site'},
        filter_spec=_location_tree_filter,
        description='Propagate site to racks in location tree',
    ),
    CascadeSpec(
        source_model='dcim.location',
        target_model='dcim.device',
        trigger_fields=frozenset({'site'}),
        field_mapping={'site': 'site'},
        filter_spec=_location_tree_filter,
        description='Propagate site to devices in location tree',
    ),
    CascadeSpec(
        source_model='dcim.location',
        target_model='dcim.powerpanel',
        trigger_fields=frozenset({'site'}),
        field_mapping={'site': 'site'},
        filter_spec=_location_tree_filter,
        description='Propagate site to power panels in location tree',
    ),
    CascadeSpec(
        source_model='dcim.location',
        target_model='dcim.cabletermination',
        trigger_fields=frozenset({'site'}),
        field_mapping={'_site': 'site'},
        filter_spec=_cable_term_in_location_tree,
        description='Propagate site to cable terminations in location tree',
    ),
)

# Component models that cache _site from their device
_COMPONENT_MODEL_LABELS = [
    'dcim.consoleport', 'dcim.consoleserverport', 'dcim.devicebay',
    'dcim.frontport', 'dcim.interface', 'dcim.inventoryitem',
    'dcim.modulebay', 'dcim.poweroutlet', 'dcim.powerport', 'dcim.rearport',
]

for component_label in _COMPONENT_MODEL_LABELS:
    cascade_registry.register(
        CascadeSpec(
            source_model='dcim.location',
            target_model=component_label,
            trigger_fields=frozenset({'site'}),
            field_mapping={'_site': 'site'},
            filter_spec=_device_in_location_tree,
            description=f'Propagate site to {component_label} via device in location tree',
        ),
    )

# ──────────────────────────────────────────────────────────────────────
# Rack site/location change → devices + components
# Replaces: handle_rack_site_change signal handler
# ──────────────────────────────────────────────────────────────────────

cascade_registry.register(
    CascadeSpec(
        source_model='dcim.rack',
        target_model='dcim.device',
        trigger_fields=frozenset({'site', 'location'}),
        field_mapping={'site': 'site', 'location': 'location'},
        filter_spec=lambda inst: {'rack': inst},
        description='Propagate site/location to devices in rack',
    ),
)

for component_label in _COMPONENT_MODEL_LABELS:
    cascade_registry.register(
        CascadeSpec(
            source_model='dcim.rack',
            target_model=component_label,
            trigger_fields=frozenset({'site', 'location'}),
            field_mapping={'_site': 'site', '_location': 'location'},
            filter_spec=lambda inst: {'device__rack': inst},
            description=f'Propagate site/location to {component_label} via device in rack',
        ),
    )

# ──────────────────────────────────────────────────────────────────────
# Device site/location/rack change → components
# Replaces: handle_device_site_change signal handler
# ──────────────────────────────────────────────────────────────────────

for component_label in _COMPONENT_MODEL_LABELS:
    cascade_registry.register(
        CascadeSpec(
            source_model='dcim.device',
            target_model=component_label,
            trigger_fields=frozenset({'site', 'location', 'rack'}),
            field_mapping={'_site': 'site', '_location': 'location', '_rack': 'rack'},
            filter_spec=lambda inst: {'device': inst},
            description=f'Propagate site/location/rack to {component_label}',
        ),
    )

# ──────────────────────────────────────────────────────────────────────
# VirtualChassis create → assign master device
# Replaces: assign_virtualchassis_master signal handler
# ──────────────────────────────────────────────────────────────────────

def _assign_vc_master(instance, **kwargs):
    """When a VirtualChassis is created, assign its master device to the VC."""
    if instance.master:
        from dcim.models import Device
        master = Device.objects.get(pk=instance.master.pk)
        master.virtual_chassis = instance
        master.vc_position = 1
        master.save()


cascade_registry.register(
    CascadeSpec(
        source_model='dcim.virtualchassis',
        target_model='dcim.device',
        method=CascadeMethod.CUSTOM,
        handler=_assign_vc_master,
        only_on_create=True,
        skip_on_create=False,
        description='Assign master device to newly created VirtualChassis',
    ),
)

# ──────────────────────────────────────────────────────────────────────
# CableTermination delete → nullify cable on termination target
# Replaces: nullify_connected_endpoints signal handler (the cascade part)
# Note: the graph recomputation part (retrace cable paths) will be
# handled by the GraphRegistry.
# ──────────────────────────────────────────────────────────────────────

def _nullify_cable_on_termination(instance, **kwargs):
    """When a CableTermination is deleted, clear cable/cable_end on the target object."""
    model = instance.termination_type.model_class()
    model.objects.filter(pk=instance.termination_id).update(cable=None, cable_end='')


cascade_registry.register(
    CascadeSpec(
        source_model='dcim.cabletermination',
        target_model='(dynamic)',
        timing=CascadeTiming.POST_DELETE,
        method=CascadeMethod.CUSTOM,
        handler=_nullify_cable_on_termination,
        skip_on_create=False,
        description='Nullify cable reference on termination target when CableTermination is deleted',
    ),
)

# ──────────────────────────────────────────────────────────────────────
# Interface/VMInterface create → assign MACAddress
# Replaces: update_mac_address_interface signal handler
# ──────────────────────────────────────────────────────────────────────

def _assign_mac_address(instance, **kwargs):
    """When an Interface is created with a primary MAC, assign the MAC to the interface."""
    if kwargs.get('raw'):
        return
    if instance.primary_mac_address:
        instance.primary_mac_address.assigned_object = instance
        instance.primary_mac_address.save()


cascade_registry.register(
    CascadeSpec(
        source_model='dcim.interface',
        target_model='dcim.macaddress',
        method=CascadeMethod.CUSTOM,
        handler=_assign_mac_address,
        only_on_create=True,
        skip_on_create=False,
        description='Assign primary MAC address to newly created Interface',
    ),
    CascadeSpec(
        source_model='virtualization.vminterface',
        target_model='dcim.macaddress',
        method=CascadeMethod.CUSTOM,
        handler=_assign_mac_address,
        only_on_create=True,
        skip_on_create=False,
        description='Assign primary MAC address to newly created VMInterface',
    ),
)

# ──────────────────────────────────────────────────────────────────────
# Location/Site change → sync cached scope fields on Prefix, Cluster, WirelessLAN
# Replaces: sync_cached_scope_fields signal handler
# ──────────────────────────────────────────────────────────────────────

def _sync_scope_fields_for_location(instance, **kwargs):
    """Recompute cached scope fields on CachedScopeMixin models scoped to this Location."""
    from ipam.models import Prefix
    from virtualization.models import Cluster
    from wireless.models import WirelessLAN

    for model in (Prefix, Cluster, WirelessLAN):
        qs = model.objects.filter(_location=instance)
        objects_to_update = []
        for obj in qs:
            obj.cache_related_objects()
            objects_to_update.append(obj)
        if objects_to_update:
            model.objects.bulk_update(
                objects_to_update,
                ['_location', '_site', '_site_group', '_region']
            )


def _sync_scope_fields_for_site(instance, **kwargs):
    """Recompute cached scope fields on CachedScopeMixin models scoped to this Site."""
    from ipam.models import Prefix
    from virtualization.models import Cluster
    from wireless.models import WirelessLAN

    for model in (Prefix, Cluster, WirelessLAN):
        qs = model.objects.filter(_site=instance)
        objects_to_update = []
        for obj in qs:
            obj.cache_related_objects()
            objects_to_update.append(obj)
        if objects_to_update:
            model.objects.bulk_update(
                objects_to_update,
                ['_location', '_site', '_site_group', '_region']
            )


cascade_registry.register(
    CascadeSpec(
        source_model='dcim.location',
        target_model='(scope:prefix,cluster,wirelesslan)',
        method=CascadeMethod.CUSTOM,
        handler=_sync_scope_fields_for_location,
        description='Recompute cached scope fields on Prefix/Cluster/WirelessLAN when Location changes',
    ),
    CascadeSpec(
        source_model='dcim.site',
        target_model='(scope:prefix,cluster,wirelesslan)',
        method=CascadeMethod.CUSTOM,
        handler=_sync_scope_fields_for_site,
        description='Recompute cached scope fields on Prefix/Cluster/WirelessLAN when Site changes',
    ),
)
