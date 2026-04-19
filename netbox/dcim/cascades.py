"""
Declarative cascade registrations for dcim models.

Replaces imperative signal handlers in dcim/signals.py and cascade logic
in save() methods with structured declarations.
"""
from netbox.cascades import CascadeMethod, CascadeSpec, CascadeTiming, cascade_registry


# ──────────────────────────────────────────────────────────────────────
# RackType save → push attributes to all Racks of this type
# Replaces: imperative loop in RackType.save()
# ──────────────────────────────────────────────────────────────────────

def _racktype_push_to_racks(instance, **kwargs):
    """Copy RackType attributes to all associated Racks and save each."""
    from dcim.models import Rack
    for rack in Rack.objects.filter(rack_type=instance):
        rack.snapshot()
        rack.copy_racktype_attrs()
        rack.save()


cascade_registry.register(
    CascadeSpec(
        source_model='dcim.racktype',
        target_model='dcim.rack',
        method=CascadeMethod.CUSTOM,
        handler=_racktype_push_to_racks,
        skip_on_create=False,
        description='Push RackType attributes (outer dims, weight, etc.) to all Racks of this type',
    ),
)


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


# ──────────────────────────────────────────────────────────────────────
# Device save → update site/rack/location on child devices in bays
# Replaces: imperative loop in Device.save()
# ──────────────────────────────────────────────────────────────────────

def _device_update_children(instance, **kwargs):
    """Update site/rack/location on child devices installed in this device's bays."""
    from dcim.models import Device
    for device in Device.objects.filter(parent_bay__device=instance):
        device.site = instance.site
        device.rack = instance.rack
        device.location = instance.location
        device.save()


cascade_registry.register(
    CascadeSpec(
        source_model='dcim.device',
        target_model='dcim.device',
        trigger_fields=frozenset({'site', 'rack', 'location'}),
        method=CascadeMethod.CUSTOM,
        handler=_device_update_children,
        description='Propagate site/rack/location to child devices in device bays',
    ),
)


# ──────────────────────────────────────────────────────────────────────
# CableTermination save → set cable on termination target
# Replaces: imperative code in CableTermination.save()
# ──────────────────────────────────────────────────────────────────────

def _cable_termination_set_cable(instance, **kwargs):
    """After saving a CableTermination, link the cable to the terminated object."""
    termination = instance.termination._meta.model.objects.get(pk=instance.termination_id)
    termination.snapshot()
    termination.set_cable_termination(instance)
    termination.save()


cascade_registry.register(
    CascadeSpec(
        source_model='dcim.cabletermination',
        target_model='(dynamic)',
        method=CascadeMethod.CUSTOM,
        handler=_cable_termination_set_cable,
        skip_on_create=False,
        description='Set cable reference on terminated object when CableTermination is saved',
    ),
)


# ──────────────────────────────────────────────────────────────────────
# CircuitTermination save → update Circuit.termination_a/z pointers
# Replaces: imperative code in CircuitTermination.save()
# ──────────────────────────────────────────────────────────────────────

def _circuit_termination_update_pointers(instance, **kwargs):
    """Update Circuit's cached termination_a/z FK when CircuitTermination changes."""
    from circuits.models import Circuit

    if not instance.term_side:
        return

    is_new = kwargs.get('created', False)
    orig_circuit_id = getattr(instance, '_orig_circuit_id', None)
    orig_term_side = getattr(instance, '_orig_term_side', None)
    circuit_changed = orig_circuit_id is not None and orig_circuit_id != instance.circuit_id
    term_side_changed = orig_term_side is not None and orig_term_side != instance.term_side

    if (circuit_changed or term_side_changed) and orig_term_side:
        old_termination_name = f'termination_{orig_term_side.lower()}'
        Circuit.objects.filter(pk=orig_circuit_id).update(**{old_termination_name: None})

    if is_new or circuit_changed or term_side_changed:
        termination_name = f'termination_{instance.term_side.lower()}'
        Circuit.objects.filter(pk=instance.circuit_id).update(**{termination_name: instance.pk})

        instance._orig_circuit_id = instance.circuit_id
        instance._orig_term_side = instance.term_side


cascade_registry.register(
    CascadeSpec(
        source_model='circuits.circuittermination',
        target_model='circuits.circuit',
        trigger_fields=frozenset({'circuit', 'term_side'}),
        method=CascadeMethod.CUSTOM,
        handler=_circuit_termination_update_pointers,
        skip_on_create=False,
        description='Update Circuit termination_a/z FK pointers when CircuitTermination is saved',
    ),
)


# ──────────────────────────────────────────────────────────────────────
# CablePath save → update _path FK on origin objects
# Replaces: imperative code in CablePath.save()
# ──────────────────────────────────────────────────────────────────────

def _cablepath_update_origins(instance, **kwargs):
    """After saving a CablePath, set _path FK on all origin endpoints."""
    from dcim.models.cables import decompile_path_node

    if instance.path:
        origin_model = instance.origin_type.model_class()
        origin_ids = [decompile_path_node(node)[1] for node in instance.path[0]]
        origin_model.objects.filter(pk__in=origin_ids).update(_path=instance.pk)


cascade_registry.register(
    CascadeSpec(
        source_model='dcim.cablepath',
        target_model='(dynamic:path endpoints)',
        method=CascadeMethod.CUSTOM,
        handler=_cablepath_update_origins,
        skip_on_create=False,
        description='Set _path FK on origin endpoints when CablePath is saved',
    ),
)


# ──────────────────────────────────────────────────────────────────────
# CableTermination pre-delete → clear cable association on terminated object
# Replaces: imperative code in CableTermination.delete()
# ──────────────────────────────────────────────────────────────────────

def _cable_termination_clear_on_delete(instance, **kwargs):
    """Before deleting a CableTermination, clear the cable link on the terminated object."""
    termination = instance.termination._meta.model.objects.get(pk=instance.termination_id)
    termination.snapshot()
    termination.clear_cable_termination(instance)
    termination.save()


cascade_registry.register(
    CascadeSpec(
        source_model='dcim.cabletermination',
        target_model='(dynamic)',
        timing=CascadeTiming.PRE_DELETE,
        method=CascadeMethod.CUSTOM,
        handler=_cable_termination_clear_on_delete,
        skip_on_create=False,
        description='Clear cable association on terminated object before CableTermination is deleted',
    ),
)


# ──────────────────────────────────────────────────────────────────────
# CablePath pre-delete → nullify _path FK on origin endpoints
# Replaces: imperative code in CablePath.delete()
# ──────────────────────────────────────────────────────────────────────

def _cablepath_clear_origins_on_delete(instance, **kwargs):
    """Before deleting a CablePath, clear _path on all origin endpoints to prevent stale references."""
    from dcim.utils import decompile_path_node

    if instance.path:
        origin_model = instance.origin_type.model_class()
        origin_ids = [decompile_path_node(node)[1] for node in instance.path[0]]
        origin_model.objects.filter(pk__in=origin_ids, _path=instance.pk).update(_path=None)


cascade_registry.register(
    CascadeSpec(
        source_model='dcim.cablepath',
        target_model='(dynamic:path endpoints)',
        timing=CascadeTiming.PRE_DELETE,
        method=CascadeMethod.CUSTOM,
        handler=_cablepath_clear_origins_on_delete,
        skip_on_create=False,
        description='Nullify _path FK on origin endpoints before CablePath is deleted',
    ),
)


# ──────────────────────────────────────────────────────────────────────
# VirtualChassis pre-delete → validate cross-chassis LAGs + clear vc fields
# Replaces: imperative code in VirtualChassis.delete()
# ──────────────────────────────────────────────────────────────────────

def _virtualchassis_pre_delete(instance, **kwargs):
    """Validate no cross-chassis LAGs exist, then clear vc_position/vc_priority on members."""
    from django.db.models import F, ProtectedError
    from django.utils.translation import gettext_lazy as _

    from dcim.models import Interface

    interfaces = Interface.objects.filter(
        device__in=instance.members.all(),
        lag__isnull=False
    ).exclude(
        lag__device=F('device')
    )
    if interfaces:
        raise ProtectedError(_(
            "Unable to delete virtual chassis {self}. There are member interfaces which form a cross-chassis LAG "
            "interfaces."
        ).format(self=instance))

    for device in instance.members.all():
        device.vc_position = None
        device.vc_priority = None
        device.save()


cascade_registry.register(
    CascadeSpec(
        source_model='dcim.virtualchassis',
        target_model='dcim.device',
        timing=CascadeTiming.PRE_DELETE,
        method=CascadeMethod.CUSTOM,
        handler=_virtualchassis_pre_delete,
        skip_on_create=False,
        description='Validate no cross-chassis LAGs and clear vc_position/vc_priority on member devices before VirtualChassis is deleted',
    ),
)


# ──────────────────────────────────────────────────────────────────────
# DeviceType post-delete → remove uploaded image files
# Replaces: imperative code in DeviceType.delete()
# ──────────────────────────────────────────────────────────────────────

def _devicetype_delete_images(instance, **kwargs):
    """After deleting a DeviceType, remove any uploaded front/rear image files."""
    if instance.front_image:
        instance.front_image.delete(save=False)
    if instance.rear_image:
        instance.rear_image.delete(save=False)


cascade_registry.register(
    CascadeSpec(
        source_model='dcim.devicetype',
        target_model='(filesystem)',
        timing=CascadeTiming.POST_DELETE,
        method=CascadeMethod.CUSTOM,
        handler=_devicetype_delete_images,
        skip_on_create=False,
        description='Delete uploaded front/rear image files after DeviceType is deleted',
    ),
)


# ──────────────────────────────────────────────────────────────────────
# DeviceType save → delete stale image files when images change
# Replaces: imperative code in DeviceType.save()
# ──────────────────────────────────────────────────────────────────────

def _devicetype_clean_old_images(instance, **kwargs):
    """After saving a DeviceType, delete any previously uploaded images that were replaced."""
    from django.core.files.storage import default_storage
    original_front = getattr(instance, '_original_front_image', None)
    original_rear = getattr(instance, '_original_rear_image', None)
    if original_front and instance.front_image != original_front:
        default_storage.delete(original_front)
    if original_rear and instance.rear_image != original_rear:
        default_storage.delete(original_rear)


cascade_registry.register(
    CascadeSpec(
        source_model='dcim.devicetype',
        target_model='(filesystem)',
        trigger_fields=frozenset({'front_image', 'rear_image'}),
        method=CascadeMethod.CUSTOM,
        handler=_devicetype_clean_old_images,
        skip_on_create=True,
        description='Delete stale front/rear image files after DeviceType save',
    ),
)


# ──────────────────────────────────────────────────────────────────────
# BaseInterface save → clear tagged VLANs when mode is not 'tagged'
# Replaces: imperative M2M clear in BaseInterface.save()
# ──────────────────────────────────────────────────────────────────────

def _baseinterface_clear_tagged_vlans(instance, **kwargs):
    from dcim.choices import InterfaceModeChoices
    if not kwargs.get('created', False) and instance.mode != InterfaceModeChoices.MODE_TAGGED:
        instance.tagged_vlans.clear()


cascade_registry.register(
    CascadeSpec(
        source_model='dcim.interface',
        target_model='ipam.vlan',
        trigger_fields=frozenset({'mode'}),
        method=CascadeMethod.CUSTOM,
        handler=_baseinterface_clear_tagged_vlans,
        skip_on_create=False,
        description='Clear tagged VLANs when interface mode is not tagged',
    ),
    CascadeSpec(
        source_model='virtualization.vminterface',
        target_model='ipam.vlan',
        trigger_fields=frozenset({'mode'}),
        method=CascadeMethod.CUSTOM,
        handler=_baseinterface_clear_tagged_vlans,
        skip_on_create=False,
        description='Clear tagged VLANs when VMInterface mode is not tagged',
    ),
)


# ──────────────────────────────────────────────────────────────────────
# Cable save → update terminations + trace paths (METADATA-ONLY)
# Cable.save() uses a double-save pattern that can't be decomposed.
# These specs describe the side effects for introspection only.
# ──────────────────────────────────────────────────────────────────────

cascade_registry.register(
    CascadeSpec(
        source_model='dcim.cable',
        target_model='dcim.cabletermination',
        method=CascadeMethod.CUSTOM,
        handler=None,
        skip_on_create=False,
        description='PARTIAL: Cable.save() calls update_terminations() between two saves — cannot be decomposed',
    ),
    CascadeSpec(
        source_model='dcim.cable',
        target_model='(graph:cablepath)',
        method=CascadeMethod.CUSTOM,
        handler=None,
        skip_on_create=False,
        description='PARTIAL: Cable.save() sends trace_paths signal for path recomputation (see also GraphRegistry)',
    ),
)
