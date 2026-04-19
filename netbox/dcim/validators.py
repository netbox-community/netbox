"""
Extracted, composable validators for dcim models.
Each function is standalone and raises ValidationError on failure.
"""
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from dcim.choices import InterfaceModeChoices
from dcim.constants import VIRTUAL_IFACE_TYPES, WIRELESS_IFACE_TYPES
from netbox.validators import ModelValidator, ValidatorCategory, validator_registry

_fs = frozenset


# ──────────────────────────────────────────────────────────────────────
# Rack
# ──────────────────────────────────────────────────────────────────────

def validate_rack_location_site(instance):
    if instance.site_id and instance.location_id and instance.location.site_id != instance.site_id:
        raise ValidationError(
            _("Assigned location must belong to parent site ({site}).").format(site=instance.site)
        )


def validate_rack_outer_dimensions(instance):
    if any([instance.outer_width, instance.outer_depth, instance.outer_height]) and not instance.outer_unit:
        raise ValidationError(_("Must specify a unit when setting an outer dimension"))


def validate_rack_max_weight(instance):
    if instance.max_weight and not instance.weight_unit:
        raise ValidationError(_("Must specify a unit when setting a maximum weight"))


def validate_rack_height_vs_devices(instance):
    """Rack cannot shrink below installed devices."""
    if instance._state.adding:
        return
    from dcim.models import Device
    mounted = Device.objects.filter(rack=instance).exclude(position__isnull=True).order_by('position')

    effective_u_height = instance.rack_type.u_height if instance.rack_type else instance.u_height
    effective_starting_unit = instance.rack_type.starting_unit if instance.rack_type else instance.starting_unit

    if top_device := mounted.last():
        min_height = top_device.position + top_device.device_type.u_height - effective_starting_unit
        if effective_u_height < min_height:
            field = 'rack_type' if instance.rack_type else 'u_height'
            raise ValidationError({
                field: _(
                    "Rack must be at least {min_height}U tall to house currently installed devices."
                ).format(min_height=min_height)
            })

    if last_device := mounted.first():
        if effective_starting_unit > last_device.position:
            field = 'rack_type' if instance.rack_type else 'starting_unit'
            raise ValidationError({
                field: _("Rack unit numbering must begin at {position} or less to house "
                         "currently installed devices.").format(position=last_device.position)
            })

    if instance.location:
        if instance.location.site != instance.site:
            raise ValidationError({
                'location': _("Location must be from the same site, {site}.").format(site=instance.site)
            })


validator_registry.register('dcim.rack',
    ModelValidator(
        name='rack_location_site',
        model_label='dcim.rack',
        fields=_fs({'site', 'location'}),
        category=ValidatorCategory.CROSS_FIELD,
        validate=validate_rack_location_site,
        description='Location must belong to the assigned site',
    ),
    ModelValidator(
        name='rack_outer_dimensions',
        model_label='dcim.rack',
        fields=_fs({'outer_width', 'outer_depth', 'outer_height', 'outer_unit'}),
        category=ValidatorCategory.FIELD,
        validate=validate_rack_outer_dimensions,
        description='Outer dimensions require a unit',
    ),
    ModelValidator(
        name='rack_max_weight',
        model_label='dcim.rack',
        fields=_fs({'max_weight', 'weight_unit'}),
        category=ValidatorCategory.FIELD,
        validate=validate_rack_max_weight,
        description='Max weight requires a unit',
    ),
    ModelValidator(
        name='rack_height_vs_devices',
        model_label='dcim.rack',
        fields=_fs({'u_height', 'starting_unit', 'rack_type'}),
        category=ValidatorCategory.CROSS_MODEL,
        validate=validate_rack_height_vs_devices,
        queries_db=True,
        description='Rack height/starting unit cannot conflict with installed devices',
    ),
)

# ──────────────────────────────────────────────────────────────────────
# RackType
# ──────────────────────────────────────────────────────────────────────

def validate_racktype_outer_dimensions(instance):
    if any([instance.outer_width, instance.outer_depth, instance.outer_height]) and not instance.outer_unit:
        raise ValidationError(_("Must specify a unit when setting an outer dimension"))


def validate_racktype_max_weight(instance):
    if instance.max_weight and not instance.weight_unit:
        raise ValidationError(_("Must specify a unit when setting a maximum weight"))


validator_registry.register('dcim.racktype',
    ModelValidator(
        name='racktype_outer_dimensions',
        model_label='dcim.racktype',
        fields=_fs({'outer_width', 'outer_depth', 'outer_height', 'outer_unit'}),
        category=ValidatorCategory.FIELD,
        validate=validate_racktype_outer_dimensions,
        description='Outer dimensions require a unit',
    ),
    ModelValidator(
        name='racktype_max_weight',
        model_label='dcim.racktype',
        fields=_fs({'max_weight', 'weight_unit'}),
        category=ValidatorCategory.FIELD,
        validate=validate_racktype_max_weight,
        description='Max weight requires a unit',
    ),
)

# ──────────────────────────────────────────────────────────────────────
# RackReservation
# ──────────────────────────────────────────────────────────────────────

def validate_rackreservation_units(instance):
    """Reserved units must be valid for rack and not overlap other reservations."""
    if instance.units:
        invalid_units = [u for u in instance.units if u not in instance.rack.units]
        if invalid_units:
            raise ValidationError({
                'units': _(
                    "Invalid unit(s) for {height}U rack: {units}"
                ).format(height=instance.rack.u_height, units=', '.join([str(u) for u in invalid_units]))
            })

        conflicting = instance.rack.reservations.exclude(pk=instance.pk).filter(
            units__overlap=instance.units
        )
        if conflicting.exists():
            raise ValidationError({
                'units': _("One or more of the specified units has already been reserved.")
            })


validator_registry.register('dcim.rackreservation',
    ModelValidator(
        name='rackreservation_units',
        model_label='dcim.rackreservation',
        fields=_fs({'units', 'rack'}),
        category=ValidatorCategory.CROSS_MODEL,
        validate=validate_rackreservation_units,
        queries_db=True,
        description='Reserved units must be valid and non-overlapping',
    ),
)

# ──────────────────────────────────────────────────────────────────────
# Device — site/rack/location consistency
# ──────────────────────────────────────────────────────────────────────

def validate_device_site_rack_location(instance):
    if instance.rack and instance.site != instance.rack.site:
        raise ValidationError({
            'rack': _("Rack {rack} does not belong to site {site}.").format(
                rack=instance.rack, site=instance.site),
        })
    if instance.location and instance.site != instance.location.site:
        raise ValidationError({
            'location': _("Location {location} does not belong to site {site}.").format(
                location=instance.location, site=instance.site)
        })
    if instance.rack and instance.location and instance.rack.location != instance.location:
        raise ValidationError({
            'rack': _("Rack {rack} does not belong to location {location}.").format(
                rack=instance.rack, location=instance.location)
        })


def validate_device_rack_position(instance):
    import decimal
    if instance.rack is None:
        if instance.face:
            raise ValidationError({
                'face': _("Cannot select a rack face without assigning a rack."),
            })
        if instance.position:
            raise ValidationError({
                'position': _("Cannot select a rack position without assigning a rack."),
            })
    if instance.position and instance.position % decimal.Decimal(0.5):
        raise ValidationError({
            'position': _("Position must be in increments of 0.5 rack units.")
        })
    if instance.position and not instance.face:
        raise ValidationError({
            'face': _("Must specify rack face when defining rack position."),
        })


def validate_device_type_constraints(instance):
    from dcim.models import DeviceType
    if not hasattr(instance, 'device_type'):
        return
    if instance.position and instance.device_type.u_height == 0:
        raise ValidationError({
            'position': _(
                "A 0U device type ({device_type}) cannot be assigned to a rack position."
            ).format(device_type=instance.device_type)
        })
    if instance.rack:
        try:
            if instance.device_type.is_child_device and instance.face:
                raise ValidationError({
                    'face': _("Child device types cannot be assigned to a rack face. "
                              "This is an attribute of the parent device.")
                })
            if instance.device_type.is_child_device and instance.position:
                raise ValidationError({
                    'position': _("Child device types cannot be assigned to a rack position. "
                                  "This is an attribute of the parent device.")
                })
        except DeviceType.DoesNotExist:
            pass


def validate_device_rack_space(instance):
    """Check that the rack position has enough space."""
    from dcim.models import DeviceType
    if not instance.rack or not hasattr(instance, 'device_type'):
        return
    try:
        rack_face = instance.face if not instance.device_type.is_full_depth else None
        exclude_list = [instance.pk] if instance.pk else []
        available_units = instance.rack.get_available_units(
            u_height=instance.device_type.u_height, rack_face=rack_face, exclude=exclude_list
        )
        if instance.position and instance.position not in available_units:
            raise ValidationError({
                'position': _(
                    "U{position} is already occupied or does not have sufficient space to "
                    "accommodate this device type: {device_type} ({u_height}U)"
                ).format(
                    position=instance.position,
                    device_type=instance.device_type,
                    u_height=instance.device_type.u_height
                )
            })
    except DeviceType.DoesNotExist:
        pass


def validate_device_primary_ips(instance):
    vc_interfaces = instance.vc_interfaces(if_master=False)
    for field, label in [('primary_ip4', 4), ('primary_ip6', 6)]:
        ip = getattr(instance, field, None)
        if not ip:
            continue
        if ip.family != label:
            raise ValidationError({
                field: _("{ip} is not an IPv{v} address.").format(ip=ip, v=label)
            })
        if ip.assigned_object in vc_interfaces:
            continue
        if ip.nat_inside is not None and ip.nat_inside.assigned_object in vc_interfaces:
            continue
        raise ValidationError({
            field: _("The specified IP address ({ip}) is not assigned to this device.").format(ip=ip)
        })
    if instance.oob_ip:
        if instance.oob_ip.assigned_object in vc_interfaces:
            pass
        elif (instance.oob_ip.nat_inside is not None and
              instance.oob_ip.nat_inside.assigned_object in vc_interfaces):
            pass
        else:
            raise ValidationError({
                'oob_ip': f"The specified IP address ({instance.oob_ip}) is not assigned to this device."
            })


def validate_device_platform_manufacturer(instance):
    if hasattr(instance, 'device_type') and instance.platform:
        if instance.platform.manufacturer and instance.platform.manufacturer != instance.device_type.manufacturer:
            raise ValidationError({
                'platform': _(
                    "The assigned platform is limited to {platform_manufacturer} device types, but this device's "
                    "type belongs to {devicetype_manufacturer}."
                ).format(
                    platform_manufacturer=instance.platform.manufacturer,
                    devicetype_manufacturer=instance.device_type.manufacturer
                )
            })


def validate_device_cluster(instance):
    if instance.cluster and instance.cluster._site is not None and instance.cluster._site != instance.site:
        raise ValidationError({
            'cluster': _("The assigned cluster belongs to a different site ({site})").format(
                site=instance.cluster._site
            )
        })
    if instance.cluster and instance.cluster._location is not None and instance.cluster._location != instance.location:
        raise ValidationError({
            'cluster': _("The assigned cluster belongs to a different location ({location})").format(
                site=instance.cluster._location
            )
        })


def validate_device_vc_position(instance):
    if instance.virtual_chassis and instance.vc_position is None:
        raise ValidationError({
            'vc_position': _("A device assigned to a virtual chassis must have its position defined.")
        })


validator_registry.register('dcim.device',
    ModelValidator(
        name='device_site_rack_location',
        model_label='dcim.device',
        fields=_fs({'site', 'rack', 'location'}),
        category=ValidatorCategory.CROSS_FIELD,
        validate=validate_device_site_rack_location,
        description='Site, rack, and location must be consistent',
    ),
    ModelValidator(
        name='device_rack_position',
        model_label='dcim.device',
        fields=_fs({'rack', 'position', 'face'}),
        category=ValidatorCategory.CROSS_FIELD,
        validate=validate_device_rack_position,
        description='Rack position/face rules',
    ),
    ModelValidator(
        name='device_type_constraints',
        model_label='dcim.device',
        fields=_fs({'device_type', 'position', 'face', 'rack'}),
        category=ValidatorCategory.CROSS_FIELD,
        validate=validate_device_type_constraints,
        description='Device type height/child constraints vs rack placement',
    ),
    ModelValidator(
        name='device_rack_space',
        model_label='dcim.device',
        fields=_fs({'rack', 'position', 'face', 'device_type'}),
        category=ValidatorCategory.CROSS_MODEL,
        validate=validate_device_rack_space,
        queries_db=True,
        description='Rack position must have sufficient available space',
    ),
    ModelValidator(
        name='device_primary_ips',
        model_label='dcim.device',
        fields=_fs({'primary_ip4', 'primary_ip6', 'oob_ip'}),
        category=ValidatorCategory.CROSS_MODEL,
        validate=validate_device_primary_ips,
        queries_db=True,
        description='Primary/OOB IPs must be assigned to device interfaces',
    ),
    ModelValidator(
        name='device_platform_manufacturer',
        model_label='dcim.device',
        fields=_fs({'platform', 'device_type'}),
        category=ValidatorCategory.CROSS_FIELD,
        validate=validate_device_platform_manufacturer,
        description='Platform manufacturer must match device type manufacturer',
    ),
    ModelValidator(
        name='device_cluster',
        model_label='dcim.device',
        fields=_fs({'cluster', 'site', 'location'}),
        category=ValidatorCategory.CROSS_FIELD,
        validate=validate_device_cluster,
        description='Cluster site/location must match device',
    ),
    ModelValidator(
        name='device_vc_position',
        model_label='dcim.device',
        fields=_fs({'virtual_chassis', 'vc_position'}),
        category=ValidatorCategory.CROSS_FIELD,
        validate=validate_device_vc_position,
        description='VC member must have a position',
    ),
)

# ──────────────────────────────────────────────────────────────────────
# CableTermination
# ──────────────────────────────────────────────────────────────────────

def validate_cable_termination_unique(instance):
    """No duplicate terminations for the same object."""
    from dcim.models import CableTermination
    existing = CableTermination.objects.filter(
        termination_type=instance.termination_type,
        termination_id=instance.termination_id,
        cable_end=instance.cable_end,
    ).exclude(pk=instance.pk)
    if instance.cable_id:
        existing = existing.exclude(cable_id=instance.cable_id)
    if existing.exists():
        raise ValidationError(
            _("A cable termination for {type} {id} ({end}) already exists").format(
                type=instance.termination_type,
                id=instance.termination_id,
                end=instance.cable_end,
            )
        )


def validate_cable_termination_mark_connected(instance):
    """Cannot connect cable to an object flagged as mark_connected."""
    termination = getattr(instance, 'termination', None)
    if termination is not None and getattr(termination, "mark_connected", False):
        raise ValidationError(
            _("Cannot connect a cable to {obj_parent} > {obj} because it is marked as connected.").format(
                obj_parent=termination.parent_object,
                obj=termination,
            )
        )


def validate_cable_termination_iface_type(instance):
    """Non-connectable interface types cannot have cables."""
    from dcim.constants import NONCONNECTABLE_IFACE_TYPES
    if instance.termination_type.model == 'interface' and instance.termination.type in NONCONNECTABLE_IFACE_TYPES:
        raise ValidationError(
            _("Cables cannot be terminated to {type_display} interfaces").format(
                type_display=instance.termination.get_type_display()
            )
        )


def validate_cable_termination_provider_network(instance):
    """CircuitTermination attached to ProviderNetwork cannot be cabled."""
    if instance.termination_type.model == 'circuittermination' and instance.termination._provider_network is not None:
        raise ValidationError(_("Circuit terminations attached to a provider network may not be cabled."))


validator_registry.register('dcim.cabletermination',
    ModelValidator(
        name='cable_termination_mark_connected',
        model_label='dcim.cabletermination',
        fields=_fs({'termination_type', 'termination_id'}),
        category=ValidatorCategory.CROSS_MODEL,
        validate=validate_cable_termination_mark_connected,
        queries_db=True,
        description='Cannot cable to an object marked as connected',
    ),
    ModelValidator(
        name='cable_termination_unique',
        model_label='dcim.cabletermination',
        fields=_fs({'termination_type', 'termination_id', 'cable_end'}),
        category=ValidatorCategory.UNIQUENESS,
        validate=validate_cable_termination_unique,
        queries_db=True,
        description='No duplicate cable terminations for the same object',
    ),
    ModelValidator(
        name='cable_termination_iface_type',
        model_label='dcim.cabletermination',
        fields=_fs({'termination_type', 'termination_id'}),
        category=ValidatorCategory.CROSS_MODEL,
        validate=validate_cable_termination_iface_type,
        queries_db=True,
        description='Non-connectable interface types cannot have cables',
    ),
    ModelValidator(
        name='cable_termination_provider_network',
        model_label='dcim.cabletermination',
        fields=_fs({'termination_type', 'termination_id'}),
        category=ValidatorCategory.CROSS_MODEL,
        validate=validate_cable_termination_provider_network,
        queries_db=True,
        description='Circuit termination attached to provider network cannot be cabled',
    ),
)

# ──────────────────────────────────────────────────────────────────────
# DeviceBay
# ──────────────────────────────────────────────────────────────────────

def validate_devicebay_parent_supports_bays(instance):
    """Parent Device must support device bays."""
    if hasattr(instance, 'device') and not instance.device.device_type.is_parent_device:
        raise ValidationError(
            _("This type of device ({device_type}) does not support device bays.").format(
                device_type=instance.device.device_type
            )
        )


def validate_devicebay_no_self_install(instance):
    if instance.installed_device and getattr(instance, 'device', None) == instance.installed_device:
        raise ValidationError(_("Cannot install a device into itself."))


def validate_devicebay_installed_device(instance):
    """Installed device cannot already be in another bay."""
    if not instance.installed_device:
        return
    from dcim.models import DeviceBay
    conflicting = DeviceBay.objects.filter(
        installed_device=instance.installed_device
    ).exclude(pk=instance.pk)
    if conflicting.exists():
        raise ValidationError({
            'installed_device': _(
                "Cannot install device in more than one device bay."
            )
        })


validator_registry.register('dcim.devicebay',
    ModelValidator(
        name='devicebay_parent_supports_bays',
        model_label='dcim.devicebay',
        fields=_fs({'device'}),
        category=ValidatorCategory.CROSS_MODEL,
        validate=validate_devicebay_parent_supports_bays,
        queries_db=True,
        description='Parent device type must support device bays',
    ),
    ModelValidator(
        name='devicebay_no_self_install',
        model_label='dcim.devicebay',
        fields=_fs({'device', 'installed_device'}),
        category=ValidatorCategory.CROSS_FIELD,
        validate=validate_devicebay_no_self_install,
        description='Cannot install device into itself',
    ),
    ModelValidator(
        name='devicebay_installed_device',
        model_label='dcim.devicebay',
        fields=_fs({'installed_device'}),
        category=ValidatorCategory.CROSS_MODEL,
        validate=validate_devicebay_installed_device,
        queries_db=True,
        description='Device cannot be installed in more than one bay',
    ),
)

# ──────────────────────────────────────────────────────────────────────
# VirtualChassis
# ──────────────────────────────────────────────────────────────────────

def validate_vc_master_in_members(instance):
    if instance.pk and instance.master:
        if instance.master not in instance.members.all():
            raise ValidationError({
                'master': _("The master device must be a member of the virtual chassis.")
            })


def validate_device_vc_master_removal(instance):
    """Device cannot be removed from VC if it's the master."""
    if hasattr(instance, 'vc_master_for') and instance.vc_master_for and instance.vc_master_for != instance.virtual_chassis:
        raise ValidationError({
            'virtual_chassis': _(
                'Device cannot be removed from virtual chassis {virtual_chassis} because it is currently '
                'designated as its master.'
            ).format(virtual_chassis=instance.vc_master_for)
        })


validator_registry.register('dcim.device',
    ModelValidator(
        name='device_vc_master_removal',
        model_label='dcim.device',
        fields=_fs({'virtual_chassis'}),
        category=ValidatorCategory.CROSS_MODEL,
        validate=validate_device_vc_master_removal,
        queries_db=True,
        description='Cannot remove a device from VC if it is the master',
    ),
)


validator_registry.register('dcim.virtualchassis',
    ModelValidator(
        name='vc_master_in_members',
        model_label='dcim.virtualchassis',
        fields=_fs({'master'}),
        category=ValidatorCategory.CROSS_MODEL,
        validate=validate_vc_master_in_members,
        queries_db=True,
        description='VC master must be a member of the chassis',
    ),
)

# ──────────────────────────────────────────────────────────────────────
# DeviceType
# ──────────────────────────────────────────────────────────────────────

def validate_devicetype_u_height_increment(instance):
    import decimal
    if decimal.Decimal(instance.u_height) % decimal.Decimal(0.5):
        raise ValidationError({
            'u_height': _("U height must be in increments of 0.5 rack units.")
        })


def validate_devicetype_u_height_expansion(instance):
    """When increasing u_height, verify all mounted devices still fit."""
    if instance._state.adding:
        return
    if instance.u_height <= instance._original_u_height:
        return
    from dcim.models import Device
    for d in Device.objects.filter(device_type=instance, position__isnull=False):
        face_required = None if instance.is_full_depth else d.face
        u_available = d.rack.get_available_units(
            u_height=instance.u_height,
            rack_face=face_required,
            exclude=[d.pk]
        )
        if d.position not in u_available:
            raise ValidationError({
                'u_height': _(
                    "Device {device} in rack {rack} does not have sufficient space to accommodate a "
                    "height of {height}U"
                ).format(device=d, rack=d.rack, height=instance.u_height)
            })


def validate_devicetype_u_height_zero(instance):
    """Cannot set 0U if devices are racked."""
    if instance._state.adding:
        return
    if not (instance._original_u_height > 0 and instance.u_height == 0):
        return
    from dcim.models import Device
    racked_instance_count = Device.objects.filter(
        device_type=instance,
        position__isnull=False
    ).count()
    if racked_instance_count:
        from django.urls import reverse
        from django.utils.safestring import mark_safe
        url = f"{reverse('dcim:device_list')}?manufactuer_id={instance.manufacturer_id}&device_type_id={instance.pk}"
        raise ValidationError({
            'u_height': mark_safe(_(
                'Unable to set 0U height: Found <a href="{url}">{racked_instance_count} instances</a> already '
                'mounted within racks.'
            ).format(url=url, racked_instance_count=racked_instance_count))
        })


def validate_devicetype_subdevice_role(instance):
    from dcim.choices import SubdeviceRoleChoices
    if instance.subdevice_role != SubdeviceRoleChoices.ROLE_PARENT:
        if instance.pk:
            from dcim.models.device_component_templates import DeviceBayTemplate
            if DeviceBayTemplate.objects.filter(device_type=instance).exists():
                raise ValidationError({
                    'subdevice_role': _(
                        "Must delete all device bay templates associated with this device before "
                        "declassifying it as a parent device."
                    )
                })
    if instance.u_height and instance.subdevice_role == SubdeviceRoleChoices.ROLE_CHILD:
        raise ValidationError({
            'u_height': _("Child device types must be 0U.")
        })


validator_registry.register('dcim.devicetype',
    ModelValidator(
        name='devicetype_u_height_increment',
        model_label='dcim.devicetype',
        fields=_fs({'u_height'}),
        category=ValidatorCategory.FIELD,
        validate=validate_devicetype_u_height_increment,
        description='U height must be in 0.5 increments',
    ),
    ModelValidator(
        name='devicetype_u_height_expansion',
        model_label='dcim.devicetype',
        fields=_fs({'u_height'}),
        category=ValidatorCategory.CROSS_MODEL,
        validate=validate_devicetype_u_height_expansion,
        queries_db=True,
        description='Height expansion blocked if mounted devices cannot accommodate',
    ),
    ModelValidator(
        name='devicetype_u_height_zero',
        model_label='dcim.devicetype',
        fields=_fs({'u_height'}),
        category=ValidatorCategory.CROSS_MODEL,
        validate=validate_devicetype_u_height_zero,
        queries_db=True,
        description='Cannot set 0U if devices are currently racked',
    ),
    ModelValidator(
        name='devicetype_subdevice_role',
        model_label='dcim.devicetype',
        fields=_fs({'subdevice_role', 'u_height'}),
        category=ValidatorCategory.CROSS_MODEL,
        validate=validate_devicetype_subdevice_role,
        queries_db=True,
        description='Subdevice role vs bay templates and child u_height constraints',
    ),
)

# ──────────────────────────────────────────────────────────────────────
# Interface
# ──────────────────────────────────────────────────────────────────────

def validate_interface_virtual_cable(instance):
    from dcim.constants import VIRTUAL_IFACE_TYPES
    if instance.type in VIRTUAL_IFACE_TYPES and instance.cable:
        raise ValidationError({
            'type': _("{display_type} interfaces cannot have a cable attached.").format(
                display_type=instance.get_type_display()
            )
        })


def validate_interface_virtual_mark_connected(instance):
    from dcim.constants import VIRTUAL_IFACE_TYPES
    if instance.type in VIRTUAL_IFACE_TYPES and instance.mark_connected:
        raise ValidationError({
            'mark_connected': _("{display_type} interfaces cannot be marked as connected.".format(
                display_type=instance.get_type_display())
            )
        })


def validate_interface_parent_device(instance):
    if instance.pk and instance.parent_id == instance.pk:
        raise ValidationError({'parent': _("An interface cannot be its own parent.")})

    from dcim.choices import InterfaceTypeChoices
    if instance.type != InterfaceTypeChoices.TYPE_VIRTUAL and instance.parent is not None:
        raise ValidationError({'parent': _("Only virtual interfaces may be assigned to a parent interface.")})

    if instance.parent and instance.parent.device != instance.device:
        if instance.device.virtual_chassis is None:
            raise ValidationError({
                'parent': _(
                    "The selected parent interface ({interface}) belongs to a different device ({device})"
                ).format(interface=instance.parent, device=instance.parent.device)
            })
        if instance.parent.device.virtual_chassis != instance.device.virtual_chassis:
            raise ValidationError({
                'parent': _(
                    "The selected parent interface ({interface}) belongs to {device}, which is not part of "
                    "virtual chassis {virtual_chassis}."
                ).format(
                    interface=instance.parent,
                    device=instance.parent.device,
                    virtual_chassis=instance.device.virtual_chassis
                )
            })


def validate_interface_bridge_device(instance):
    if instance.bridge and instance.bridge.device != instance.device:
        if instance.device.virtual_chassis is None:
            raise ValidationError({
                'bridge': _(
                    "The selected bridge interface ({bridge}) belongs to a different device ({device})."
                ).format(bridge=instance.bridge, device=instance.bridge.device)
            })
        if instance.bridge.device.virtual_chassis != instance.device.virtual_chassis:
            raise ValidationError({
                'bridge': _(
                    "The selected bridge interface ({interface}) belongs to {device}, which is not part of virtual "
                    "chassis {virtual_chassis}."
                ).format(
                    interface=instance.bridge, device=instance.bridge.device, virtual_chassis=instance.device.virtual_chassis
                )
            })


def validate_interface_lag_device(instance):
    from dcim.choices import InterfaceTypeChoices
    if instance.type == InterfaceTypeChoices.TYPE_VIRTUAL and instance.lag is not None:
        raise ValidationError({'lag': _("Virtual interfaces cannot have a parent LAG interface.")})

    if instance.pk and instance.lag_id == instance.pk:
        raise ValidationError({'lag': _("A LAG interface cannot be its own parent.")})

    if instance.lag and instance.lag.device != instance.device:
        if instance.device.virtual_chassis is None:
            raise ValidationError({
                'lag': _(
                    "The selected LAG interface ({lag}) belongs to a different device ({device})."
                ).format(lag=instance.lag, device=instance.lag.device)
            })
        if instance.lag.device.virtual_chassis != instance.device.virtual_chassis:
            raise ValidationError({
                'lag': _(
                    "The selected LAG interface ({lag}) belongs to {device}, which is not part of virtual chassis "
                    "{virtual_chassis}.".format(
                        lag=instance.lag, device=instance.lag.device, virtual_chassis=instance.device.virtual_chassis)
                )
            })


def validate_interface_wireless_rf(instance):
    from dcim.constants import WIRELESS_IFACE_TYPES
    from wireless.utils import get_channel_attr

    is_wireless = instance.type in WIRELESS_IFACE_TYPES

    if instance.rf_channel and not is_wireless:
        raise ValidationError({'rf_channel': _("Channel may be set only on wireless interfaces.")})

    if instance.rf_channel_frequency:
        if not is_wireless:
            raise ValidationError({
                'rf_channel_frequency': _("Channel frequency may be set only on wireless interfaces."),
            })
        if instance.rf_channel and instance.rf_channel_frequency != get_channel_attr(instance.rf_channel, 'frequency'):
            raise ValidationError({
                'rf_channel_frequency': _("Cannot specify custom frequency with channel selected."),
            })

    if instance.rf_channel_width:
        if not is_wireless:
            raise ValidationError({'rf_channel_width': _("Channel width may be set only on wireless interfaces.")})
        if instance.rf_channel and instance.rf_channel_width != get_channel_attr(instance.rf_channel, 'width'):
            raise ValidationError({'rf_channel_width': _("Cannot specify custom width with channel selected.")})


def validate_interface_vlan_mode(instance):
    if not instance.mode and instance.untagged_vlan:
        raise ValidationError({'untagged_vlan': _("Interface mode does not support an untagged vlan.")})


def validate_interface_vlan_site(instance):
    if instance.untagged_vlan and instance.untagged_vlan.site not in [instance.device.site, None]:
        raise ValidationError({
            'untagged_vlan': _(
                "The untagged VLAN ({untagged_vlan}) must belong to the same site as the interface's parent "
                "device, or it must be global."
            ).format(untagged_vlan=instance.untagged_vlan)
        })


validator_registry.register('dcim.interface',
    ModelValidator(
        name='interface_virtual_cable',
        model_label='dcim.interface',
        fields=_fs({'type', 'cable'}),
        category=ValidatorCategory.CROSS_FIELD,
        validate=validate_interface_virtual_cable,
        description='Virtual interfaces cannot have cables',
    ),
    ModelValidator(
        name='interface_virtual_mark_connected',
        model_label='dcim.interface',
        fields=_fs({'type', 'mark_connected'}),
        category=ValidatorCategory.CROSS_FIELD,
        validate=validate_interface_virtual_mark_connected,
        description='Virtual interfaces cannot be marked as connected',
    ),
    ModelValidator(
        name='interface_parent_device',
        model_label='dcim.interface',
        fields=_fs({'parent', 'device', 'type'}),
        category=ValidatorCategory.CROSS_MODEL,
        validate=validate_interface_parent_device,
        queries_db=True,
        description='Parent interface must be on same device or VC member',
    ),
    ModelValidator(
        name='interface_bridge_device',
        model_label='dcim.interface',
        fields=_fs({'bridge', 'device'}),
        category=ValidatorCategory.CROSS_MODEL,
        validate=validate_interface_bridge_device,
        queries_db=True,
        description='Bridge must be on same device or VC member',
    ),
    ModelValidator(
        name='interface_lag_device',
        model_label='dcim.interface',
        fields=_fs({'lag', 'device', 'type'}),
        category=ValidatorCategory.CROSS_MODEL,
        validate=validate_interface_lag_device,
        queries_db=True,
        description='LAG must be on same device or VC member',
    ),
    ModelValidator(
        name='interface_wireless_rf',
        model_label='dcim.interface',
        fields=_fs({'type', 'rf_channel', 'rf_channel_frequency', 'rf_channel_width'}),
        category=ValidatorCategory.CROSS_FIELD,
        validate=validate_interface_wireless_rf,
        description='RF channel/frequency/width constraints for wireless interfaces',
    ),
    ModelValidator(
        name='interface_vlan_mode',
        model_label='dcim.interface',
        fields=_fs({'mode', 'untagged_vlan'}),
        category=ValidatorCategory.CROSS_FIELD,
        validate=validate_interface_vlan_mode,
        description='Untagged VLAN requires interface mode',
    ),
    ModelValidator(
        name='interface_vlan_site',
        model_label='dcim.interface',
        fields=_fs({'untagged_vlan', 'device'}),
        category=ValidatorCategory.CROSS_MODEL,
        validate=validate_interface_vlan_site,
        queries_db=True,
        description='Untagged VLAN must match device site',
    ),
)

# ──────────────────────────────────────────────────────────────────────
# InterfaceValidationMixin (dcim.Interface + dcim.InterfaceTemplate)
# ──────────────────────────────────────────────────────────────────────

def validate_interface_bridge_self(instance):
    if instance.pk and instance.bridge_id == instance.pk:
        raise ValidationError({'bridge': _("An interface cannot be bridged to itself.")})


def validate_interface_poe_constraints(instance):
    if instance.poe_mode and instance.type in VIRTUAL_IFACE_TYPES:
        raise ValidationError({
            'poe_mode': _("Virtual interfaces cannot have a PoE mode.")
        })
    if instance.poe_type and instance.type in VIRTUAL_IFACE_TYPES:
        raise ValidationError({
            'poe_type': _("Virtual interfaces cannot have a PoE type.")
        })
    if instance.poe_type and not instance.poe_mode:
        raise ValidationError({
            'poe_type': _("Must specify PoE mode when designating a PoE type.")
        })


def validate_interface_rf_role(instance):
    if instance.rf_role and instance.type not in WIRELESS_IFACE_TYPES:
        raise ValidationError({'rf_role': _("Wireless role may be set only on wireless interfaces.")})


_interface_mixin_validators = [
    ModelValidator(
        name='interface_bridge_self',
        model_label='',
        fields=_fs({'bridge'}),
        category=ValidatorCategory.FIELD,
        validate=validate_interface_bridge_self,
        description='An interface cannot be bridged to itself',
    ),
    ModelValidator(
        name='interface_poe_constraints',
        model_label='',
        fields=_fs({'poe_mode', 'poe_type', 'type'}),
        category=ValidatorCategory.CROSS_FIELD,
        validate=validate_interface_poe_constraints,
        description='PoE mode/type constraints for non-virtual interfaces',
    ),
    ModelValidator(
        name='interface_rf_role',
        model_label='',
        fields=_fs({'rf_role', 'type'}),
        category=ValidatorCategory.CROSS_FIELD,
        validate=validate_interface_rf_role,
        description='RF role may only be set on wireless interfaces',
    ),
]

for _label in ('dcim.interface', 'dcim.interfacetemplate'):
    validator_registry.register(_label, *_interface_mixin_validators)

# ──────────────────────────────────────────────────────────────────────
# CabledObjectModel
# ──────────────────────────────────────────────────────────────────────

def validate_cabledobject_cable_fields(instance):
    if instance.cable:
        if not instance.cable_end:
            raise ValidationError({
                "cable_end": _("Must specify cable end (A or B) when attaching a cable.")
            })
        if instance.cable_connector and not instance.cable_positions:
            raise ValidationError({
                "cable_positions": _("Must specify position(s) when specifying a cable connector.")
            })
        if instance.cable_positions and not instance.cable_connector:
            raise ValidationError({
                "cable_positions": _("Cable positions cannot be set without a cable connector.")
            })
        if instance.mark_connected:
            raise ValidationError({
                "mark_connected": _("Cannot mark as connected with a cable attached.")
            })
    else:
        if instance.cable_end:
            raise ValidationError({
                "cable_end": _("Cable end must not be set without a cable.")
            })
        if instance.cable_connector:
            raise ValidationError({
                "cable_connector": _("Cable connector must not be set without a cable.")
            })
        if instance.cable_positions:
            raise ValidationError({
                "cable_positions": _("Cable termination positions must not be set without a cable.")
            })


_cabled_models = [
    'dcim.consoleport', 'dcim.consoleserverport',
    'dcim.powerport', 'dcim.poweroutlet',
    'dcim.interface', 'dcim.frontport', 'dcim.rearport',
    'dcim.powerfeed', 'circuits.circuittermination',
]

for _label in _cabled_models:
    validator_registry.register(_label,
        ModelValidator(
            name='cabledobject_cable_fields',
            model_label=_label,
            fields=_fs({'cable', 'cable_end', 'cable_connector', 'cable_positions', 'mark_connected'}),
            category=ValidatorCategory.CROSS_FIELD,
            validate=validate_cabledobject_cable_fields,
            description='Cable, cable_end, connector, positions, and mark_connected consistency',
        ),
    )

# ──────────────────────────────────────────────────────────────────────
# BaseInterface (dcim.Interface + virtualization.VMInterface)
# ──────────────────────────────────────────────────────────────────────

def validate_baseinterface_qinq_svlan(instance):
    if instance.qinq_svlan and instance.mode != InterfaceModeChoices.MODE_Q_IN_Q:
        raise ValidationError({
            'qinq_svlan': _("Only Q-in-Q interfaces may specify a service VLAN.")
        })


def validate_baseinterface_primary_mac(instance):
    if (
            instance.primary_mac_address and
            instance.primary_mac_address.assigned_object is not None and
            instance.primary_mac_address.assigned_object != instance
    ):
        raise ValidationError({
            'primary_mac_address': _(
                "MAC address {mac_address} is assigned to a different interface ({interface})."
            ).format(
                mac_address=instance.primary_mac_address,
                interface=instance.primary_mac_address.assigned_object,
            )
        })


_baseinterface_validators = [
    ModelValidator(
        name='baseinterface_qinq_svlan',
        model_label='',
        fields=_fs({'qinq_svlan', 'mode'}),
        category=ValidatorCategory.CROSS_FIELD,
        validate=validate_baseinterface_qinq_svlan,
        description='SVLAN requires Q-in-Q mode',
    ),
    ModelValidator(
        name='baseinterface_primary_mac',
        model_label='',
        fields=_fs({'primary_mac_address'}),
        category=ValidatorCategory.CROSS_MODEL,
        validate=validate_baseinterface_primary_mac,
        queries_db=True,
        description='Primary MAC must be assigned to this interface',
    ),
]

for _label in ('dcim.interface', 'virtualization.vminterface'):
    validator_registry.register(_label, *_baseinterface_validators)

# ──────────────────────────────────────────────────────────────────────
# PowerPanel
# ──────────────────────────────────────────────────────────────────────

def validate_powerpanel_location_site(instance):
    if instance.location and instance.location.site != instance.site:
        raise ValidationError(
            _("Location {location} ({location_site}) is in a different site than {site}").format(
                location=instance.location, location_site=instance.location.site, site=instance.site)
        )


validator_registry.register('dcim.powerpanel',
    ModelValidator(
        name='powerpanel_location_site',
        model_label='dcim.powerpanel',
        fields=_fs({'location', 'site'}),
        category=ValidatorCategory.CROSS_FIELD,
        validate=validate_powerpanel_location_site,
        description='Location must belong to the assigned site',
    ),
)

# ──────────────────────────────────────────────────────────────────────
# Location
# ──────────────────────────────────────────────────────────────────────

def validate_location_parent_site(instance):
    if instance.parent and instance.parent.site != instance.site:
        raise ValidationError(_(
            "Parent location ({parent}) must belong to the same site ({site})."
        ).format(parent=instance.parent, site=instance.site))


validator_registry.register('dcim.location',
    ModelValidator(
        name='location_parent_site',
        model_label='dcim.location',
        fields=_fs({'parent', 'site'}),
        category=ValidatorCategory.CROSS_FIELD,
        validate=validate_location_parent_site,
        description='Parent location must belong to the same site',
    ),
)

# ──────────────────────────────────────────────────────────────────────
# PowerFeed
# ──────────────────────────────────────────────────────────────────────

def validate_powerfeed_rack_site(instance):
    if instance.rack and instance.rack.site != instance.power_panel.site:
        raise ValidationError(_(
            "Rack {rack} ({rack_site}) and power panel {powerpanel} ({powerpanel_site}) are in different sites."
        ).format(
            rack=instance.rack,
            rack_site=instance.rack.site,
            powerpanel=instance.power_panel,
            powerpanel_site=instance.power_panel.site
        ))


def validate_powerfeed_ac_voltage(instance):
    from dcim.choices import PowerFeedSupplyChoices
    if instance.voltage < 0 and instance.supply == PowerFeedSupplyChoices.SUPPLY_AC:
        raise ValidationError({
            "voltage": _("Voltage cannot be negative for AC supply")
        })


validator_registry.register('dcim.powerfeed',
    ModelValidator(
        name='powerfeed_rack_site',
        model_label='dcim.powerfeed',
        fields=_fs({'rack', 'power_panel'}),
        category=ValidatorCategory.CROSS_FIELD,
        validate=validate_powerfeed_rack_site,
        description='Rack must belong to same site as power panel',
    ),
    ModelValidator(
        name='powerfeed_ac_voltage',
        model_label='dcim.powerfeed',
        fields=_fs({'voltage', 'supply'}),
        category=ValidatorCategory.CROSS_FIELD,
        validate=validate_powerfeed_ac_voltage,
        description='AC voltage cannot be negative',
    ),
)

# ──────────────────────────────────────────────────────────────────────
# InventoryItem
# ──────────────────────────────────────────────────────────────────────

def validate_inventoryitem_parent_self(instance):
    if instance.pk and instance.parent_id == instance.pk:
        raise ValidationError({
            "parent": _("Cannot assign self as parent.")
        })


def validate_inventoryitem_parent_device(instance):
    if not instance._state.adding and instance.parent and instance.parent.device != instance.device:
        raise ValidationError({
            "parent": _("Parent inventory item does not belong to the same device.")
        })


def validate_inventoryitem_children_device(instance):
    if instance._state.adding:
        return
    first_child = instance.get_children().first()
    if first_child and first_child.device != instance.device:
        raise ValidationError(_("Cannot move an inventory item with dependent children"))


def validate_inventoryitem_component_device_new(instance):
    if instance._state.adding and instance.component and instance.component.device != instance.device:
        raise ValidationError({
            "device": _("Cannot assign inventory item to component on another device")
        })


validator_registry.register('dcim.inventoryitem',
    ModelValidator(
        name='inventoryitem_parent_self',
        model_label='dcim.inventoryitem',
        fields=_fs({'parent'}),
        category=ValidatorCategory.FIELD,
        validate=validate_inventoryitem_parent_self,
        description='InventoryItem cannot be its own parent',
    ),
    ModelValidator(
        name='inventoryitem_parent_device',
        model_label='dcim.inventoryitem',
        fields=_fs({'parent', 'device'}),
        category=ValidatorCategory.CROSS_MODEL,
        validate=validate_inventoryitem_parent_device,
        queries_db=True,
        description='Parent must belong to the same device',
    ),
    ModelValidator(
        name='inventoryitem_children_device',
        model_label='dcim.inventoryitem',
        fields=_fs({'device'}),
        category=ValidatorCategory.CROSS_MODEL,
        validate=validate_inventoryitem_children_device,
        queries_db=True,
        description='Cannot move item with children on different device',
    ),
    ModelValidator(
        name='inventoryitem_component_device_new',
        model_label='dcim.inventoryitem',
        fields=_fs({'component_type', 'component_id', 'device'}),
        category=ValidatorCategory.CROSS_MODEL,
        validate=validate_inventoryitem_component_device_new,
        queries_db=True,
        description='New item component must belong to same device',
    ),
)

# ──────────────────────────────────────────────────────────────────────
# Cable
# ──────────────────────────────────────────────────────────────────────

def validate_cable_length_unit(instance):
    if instance.length is not None and not instance.length_unit:
        raise ValidationError(_("Must specify a unit when setting a cable length"))


def validate_cable_new_terminations(instance):
    if instance._state.adding and instance.pk is None and (
        not instance.a_terminations or not instance.b_terminations
    ):
        raise ValidationError(_("Must define A and B terminations when creating a new cable."))


def validate_cable_profile(instance):
    if instance.profile:
        instance.profile_class().clean(instance)


def validate_cable_termination_types(instance):
    if not instance._terminations_modified:
        return
    for terms in (instance.a_terminations, instance.b_terminations):
        if len(terms) > 1 and not all(isinstance(t, type(terms[0])) for t in terms[1:]):
            raise ValidationError(_("Cannot connect different termination types to same end of cable."))


def validate_cable_termination_compatibility(instance):
    if not instance._terminations_modified:
        return
    if not (instance.a_terminations and instance.b_terminations):
        return
    from dcim.constants import COMPATIBLE_TERMINATION_TYPES
    a_type = instance.a_terminations[0]._meta.model_name
    b_type = instance.b_terminations[0]._meta.model_name
    if b_type not in COMPATIBLE_TERMINATION_TYPES.get(a_type):
        raise ValidationError(
            _("Incompatible termination types: {type_a} and {type_b}").format(type_a=a_type, type_b=b_type)
        )
    if a_type == b_type:
        a_pks = set(obj.pk for obj in instance.a_terminations if obj.pk)
        b_pks = set(obj.pk for obj in instance.b_terminations if obj.pk)
        if a_pks & b_pks:
            raise ValidationError(
                _("A and B terminations cannot connect to the same object.")
            )


validator_registry.register('dcim.cable',
    ModelValidator(
        name='cable_length_unit',
        model_label='dcim.cable',
        fields=_fs({'length', 'length_unit'}),
        category=ValidatorCategory.CROSS_FIELD,
        validate=validate_cable_length_unit,
        description='Cable length requires a unit',
    ),
    ModelValidator(
        name='cable_new_terminations',
        model_label='dcim.cable',
        fields=frozenset(),
        category=ValidatorCategory.CROSS_FIELD,
        validate=validate_cable_new_terminations,
        description='New cables must have A and B terminations',
    ),
    ModelValidator(
        name='cable_profile',
        model_label='dcim.cable',
        fields=_fs({'profile'}),
        category=ValidatorCategory.CROSS_FIELD,
        validate=validate_cable_profile,
        description='Terminations must match cable profile constraints',
    ),
    ModelValidator(
        name='cable_termination_types',
        model_label='dcim.cable',
        fields=frozenset(),
        category=ValidatorCategory.CROSS_FIELD,
        validate=validate_cable_termination_types,
        description='All terminations on each end must be the same type',
    ),
    ModelValidator(
        name='cable_termination_compatibility',
        model_label='dcim.cable',
        fields=frozenset(),
        category=ValidatorCategory.CROSS_MODEL,
        validate=validate_cable_termination_compatibility,
        queries_db=True,
        description='A/B termination types must be compatible',
    ),
)

# ──────────────────────────────────────────────────────────────────────
# ComponentModel — blocks changing device on existing components
# ──────────────────────────────────────────────────────────────────────

def validate_component_device_immutable(instance):
    from dcim.models.device_components import InventoryItem
    if type(instance) not in [InventoryItem] and instance.pk is not None and instance._original_device != instance.device_id:
        raise ValidationError({
            "device": _("Components cannot be moved to a different device.")
        })


_component_model_labels = [
    'dcim.consoleport', 'dcim.consoleserverport',
    'dcim.powerport', 'dcim.poweroutlet',
    'dcim.interface', 'dcim.frontport', 'dcim.rearport',
    'dcim.modulebay', 'dcim.devicebay',
]

for _label in _component_model_labels:
    validator_registry.register(_label,
        ModelValidator(
            name='component_device_immutable',
            model_label=_label,
            fields=_fs({'device'}),
            category=ValidatorCategory.FIELD,
            validate=validate_component_device_immutable,
            description='Components cannot be moved to a different device',
        ),
    )

# ──────────────────────────────────────────────────────────────────────
# PowerPort — allocated_draw ≤ maximum_draw
# ──────────────────────────────────────────────────────────────────────

def validate_powerport_draw(instance):
    if instance.maximum_draw is not None and instance.allocated_draw is not None:
        if instance.allocated_draw > instance.maximum_draw:
            raise ValidationError({
                'allocated_draw': _(
                    "Allocated draw cannot exceed the maximum draw ({maximum_draw}W)."
                ).format(maximum_draw=instance.maximum_draw)
            })


validator_registry.register('dcim.powerport',
    ModelValidator(
        name='powerport_draw',
        model_label='dcim.powerport',
        fields=_fs({'allocated_draw', 'maximum_draw'}),
        category=ValidatorCategory.CROSS_FIELD,
        validate=validate_powerport_draw,
        description='Allocated draw cannot exceed maximum draw',
    ),
)

# ──────────────────────────────────────────────────────────────────────
# PowerOutlet — parent power port on same device
# ──────────────────────────────────────────────────────────────────────

def validate_poweroutlet_power_port(instance):
    if instance.power_port and instance.power_port.device != instance.device:
        raise ValidationError(
            _("Parent power port ({power_port}) must belong to the same device").format(power_port=instance.power_port)
        )


validator_registry.register('dcim.poweroutlet',
    ModelValidator(
        name='poweroutlet_power_port',
        model_label='dcim.poweroutlet',
        fields=_fs({'power_port', 'device'}),
        category=ValidatorCategory.CROSS_MODEL,
        validate=validate_poweroutlet_power_port,
        queries_db=True,
        description='Parent power port must belong to the same device',
    ),
)

# ──────────────────────────────────────────────────────────────────────
# PortMapping — front/rear ports same device
# ──────────────────────────────────────────────────────────────────────

def validate_portmapping_same_device(instance):
    if instance.front_port.device_id != instance.rear_port.device_id:
        raise ValidationError({
            "rear_port": _("Rear port ({rear_port}) must belong to the same device").format(
                rear_port=instance.rear_port
            )
        })


validator_registry.register('dcim.portmapping',
    ModelValidator(
        name='portmapping_same_device',
        model_label='dcim.portmapping',
        fields=_fs({'front_port', 'rear_port'}),
        category=ValidatorCategory.CROSS_MODEL,
        validate=validate_portmapping_same_device,
        queries_db=True,
        description='Front and rear ports must belong to the same device',
    ),
)

# ──────────────────────────────────────────────────────────────────────
# PortMappingBase — rear port position ≤ rear_port.positions
# ──────────────────────────────────────────────────────────────────────

def validate_portmappingbase_rear_position(instance):
    if instance.rear_port_position > instance.rear_port.positions:
        raise ValidationError({
            "rear_port_position": _(
                "Invalid rear port position ({rear_port_position}): Rear port {name} has only {positions} "
                "positions."
            ).format(
                rear_port_position=instance.rear_port_position,
                name=instance.rear_port.name,
                positions=instance.rear_port.positions
            )
        })


for _label in ('dcim.portmapping', 'dcim.porttemplatemapping'):
    validator_registry.register(_label,
        ModelValidator(
            name='portmappingbase_rear_position',
            model_label=_label,
            fields=_fs({'rear_port_position', 'rear_port'}),
            category=ValidatorCategory.CROSS_MODEL,
            validate=validate_portmappingbase_rear_position,
            queries_db=True,
            description='Rear port position must not exceed rear port positions count',
        ),
    )

# ──────────────────────────────────────────────────────────────────────
# FrontPort / RearPort — positions ≥ mapping count
# ──────────────────────────────────────────────────────────────────────

def validate_frontport_positions(instance):
    if not instance._state.adding:
        mapping_count = instance.mappings.count()
        if instance.positions < mapping_count:
            raise ValidationError({
                "positions": _(
                    "The number of positions cannot be less than the number of mapped rear ports ({count})"
                ).format(count=mapping_count)
            })


def validate_rearport_positions(instance):
    if not instance._state.adding:
        mapping_count = instance.mappings.count()
        if instance.positions < mapping_count:
            raise ValidationError({
                "positions": _(
                    "The number of positions cannot be less than the number of mapped front ports "
                    "({count})"
                ).format(count=mapping_count)
            })


validator_registry.register('dcim.frontport',
    ModelValidator(
        name='frontport_positions',
        model_label='dcim.frontport',
        fields=_fs({'positions'}),
        category=ValidatorCategory.CROSS_MODEL,
        validate=validate_frontport_positions,
        queries_db=True,
        description='Positions must be >= mapped rear port count',
    ),
)

validator_registry.register('dcim.rearport',
    ModelValidator(
        name='rearport_positions',
        model_label='dcim.rearport',
        fields=_fs({'positions'}),
        category=ValidatorCategory.CROSS_MODEL,
        validate=validate_rearport_positions,
        queries_db=True,
        description='Positions must be >= mapped front port count',
    ),
)

# ──────────────────────────────────────────────────────────────────────
# ModuleBay — walks module/bay chain to prevent recursion
# ──────────────────────────────────────────────────────────────────────

def validate_modulebay_recursion(instance):
    if module := instance.module:
        module_bays = [instance.pk]
        modules = []
        while module:
            if module.pk in modules or module.module_bay.pk in module_bays:
                raise ValidationError(_("A module bay cannot belong to a module installed within it."))
            modules.append(module.pk)
            module_bays.append(module.module_bay.pk)
            module = module.module_bay.module if module.module_bay else None


validator_registry.register('dcim.modulebay',
    ModelValidator(
        name='modulebay_recursion',
        model_label='dcim.modulebay',
        fields=_fs({'module'}),
        category=ValidatorCategory.CROSS_MODEL,
        validate=validate_modulebay_recursion,
        queries_db=True,
        description='Module bay cannot belong to a module installed within it',
    ),
)

# ──────────────────────────────────────────────────────────────────────
# Module — bay/device match + recursion guard
# ──────────────────────────────────────────────────────────────────────

def validate_module_bay_device(instance):
    if hasattr(instance, "module_bay") and (instance.module_bay.device != instance.device):
        raise ValidationError(
            _("Module must be installed within a module bay belonging to the assigned device ({device}).").format(
                device=instance.device
            )
        )


def validate_module_recursion(instance):
    module = instance
    module_bays = []
    modules = []
    while module:
        module_module_bay = getattr(module, "module_bay", None)
        if module.pk in modules or (module_module_bay and module_module_bay.pk in module_bays):
            raise ValidationError(_("A module bay cannot belong to a module installed within it."))
        modules.append(module.pk)
        if module_module_bay:
            module_bays.append(module_module_bay.pk)
        module = module_module_bay.module if module_module_bay else None


validator_registry.register('dcim.module',
    ModelValidator(
        name='module_bay_device',
        model_label='dcim.module',
        fields=_fs({'module_bay', 'device'}),
        category=ValidatorCategory.CROSS_MODEL,
        validate=validate_module_bay_device,
        queries_db=True,
        description='Module bay must belong to the assigned device',
    ),
    ModelValidator(
        name='module_recursion',
        model_label='dcim.module',
        fields=_fs({'module_bay'}),
        category=ValidatorCategory.CROSS_MODEL,
        validate=validate_module_recursion,
        queries_db=True,
        description='Module bay cannot belong to a module installed within it',
    ),
)

# ──────────────────────────────────────────────────────────────────────
# MACAddress — primary MAC cannot be cleared/reassigned wrongly
# ──────────────────────────────────────────────────────────────────────

def validate_macaddress_primary(instance):
    from django.contrib.contenttypes.models import ContentType
    if instance._original_assigned_object_id and instance._original_assigned_object_type_id:
        assigned_object = instance.assigned_object
        ct = ContentType.objects.get_for_id(instance._original_assigned_object_type_id)
        original_assigned_object = ct.get_object_for_this_type(pk=instance._original_assigned_object_id)

        if (
            original_assigned_object.primary_mac_address
            and original_assigned_object.primary_mac_address.pk == instance.pk
        ):
            if not assigned_object:
                raise ValidationError(
                    _("Cannot unassign MAC Address while it is designated as the primary MAC for an object")
                )
            if original_assigned_object != assigned_object:
                raise ValidationError(
                    _("Cannot reassign MAC Address while it is designated as the primary MAC for an object")
                )


validator_registry.register('dcim.macaddress',
    ModelValidator(
        name='macaddress_primary',
        model_label='dcim.macaddress',
        fields=_fs({'assigned_object_type', 'assigned_object_id'}),
        category=ValidatorCategory.CROSS_MODEL,
        validate=validate_macaddress_primary,
        queries_db=True,
        description='Primary MAC cannot be unassigned or reassigned while designated as primary',
    ),
)

# ──────────────────────────────────────────────────────────────────────
# VirtualDeviceContext — primary IP family + interface membership
# ──────────────────────────────────────────────────────────────────────

def validate_vdc_primary_ips(instance):
    for primary_ip, family in ((instance.primary_ip4, 4), (instance.primary_ip6, 6)):
        if not primary_ip:
            continue
        if primary_ip.family != family:
            raise ValidationError({
                f'primary_ip{family}': _(
                    "{ip} is not an IPv{family} address."
                ).format(family=family, ip=primary_ip)
            })
        device_interfaces = instance.device.vc_interfaces(if_master=False)
        if primary_ip.assigned_object not in device_interfaces:
            raise ValidationError({
                f'primary_ip{family}': _('Primary IP address must belong to an interface on the assigned device.')
            })


validator_registry.register('dcim.virtualdevicecontext',
    ModelValidator(
        name='vdc_primary_ips',
        model_label='dcim.virtualdevicecontext',
        fields=_fs({'primary_ip4', 'primary_ip6', 'device'}),
        category=ValidatorCategory.CROSS_MODEL,
        validate=validate_vdc_primary_ips,
        queries_db=True,
        description='VDC primary IPs must match family and belong to device interfaces',
    ),
)

# ──────────────────────────────────────────────────────────────────────
# PowerFeed — rack vs panel site; AC voltage sign
# ──────────────────────────────────────────────────────────────────────

def validate_powerfeed_rack_site(instance):
    if instance.rack and instance.rack.site != instance.power_panel.site:
        raise ValidationError(_(
            "Rack {rack} ({rack_site}) and power panel {powerpanel} ({powerpanel_site}) are in different sites."
        ).format(
            rack=instance.rack,
            rack_site=instance.rack.site,
            powerpanel=instance.power_panel,
            powerpanel_site=instance.power_panel.site
        ))


def validate_powerfeed_voltage(instance):
    from dcim.choices import PowerFeedSupplyChoices
    if instance.voltage < 0 and instance.supply == PowerFeedSupplyChoices.SUPPLY_AC:
        raise ValidationError({
            "voltage": _("Voltage cannot be negative for AC supply")
        })


validator_registry.register('dcim.powerfeed',
    ModelValidator(
        name='powerfeed_rack_site',
        model_label='dcim.powerfeed',
        fields=_fs({'rack', 'power_panel'}),
        category=ValidatorCategory.CROSS_MODEL,
        validate=validate_powerfeed_rack_site,
        queries_db=True,
        description='Rack and power panel must belong to the same site',
    ),
    ModelValidator(
        name='powerfeed_voltage',
        model_label='dcim.powerfeed',
        fields=_fs({'voltage', 'supply'}),
        category=ValidatorCategory.CROSS_FIELD,
        validate=validate_powerfeed_voltage,
        description='AC voltage cannot be negative',
    ),
)

# ──────────────────────────────────────────────────────────────────────
# CachedScopeMixin — scope GFK consistency
# ──────────────────────────────────────────────────────────────────────

def validate_cached_scope(instance):
    if instance.scope_type and not (instance.scope or instance.scope_id):
        scope_type = instance.scope_type.model_class()
        raise ValidationError(
            _("Please select a {scope_type}.").format(scope_type=scope_type._meta.model_name)
        )


_cached_scope_labels = [
    'virtualization.cluster', 'ipam.prefix', 'wireless.wirelesslan',
]

for _label in _cached_scope_labels:
    validator_registry.register(_label,
        ModelValidator(
            name='cached_scope_consistency',
            model_label=_label,
            fields=_fs({'scope_type', 'scope_id'}),
            category=ValidatorCategory.CROSS_FIELD,
            validate=validate_cached_scope,
            description='Scope type requires a scope object to be selected',
        ),
    )

# ──────────────────────────────────────────────────────────────────────
# Component Templates
# ──────────────────────────────────────────────────────────────────────

def validate_component_template_device_type_immutable(instance):
    if not instance._state.adding and instance._original_device_type != instance.device_type_id:
        raise ValidationError({
            "device_type": _("Component templates cannot be moved to a different device type.")
        })


_component_template_labels = [
    'dcim.consoleporttemplate', 'dcim.consoleserverporttemplate',
    'dcim.powerporttemplate', 'dcim.poweroutlettemplate',
    'dcim.interfacetemplate', 'dcim.frontporttemplate', 'dcim.rearporttemplate',
    'dcim.modulebaytemplate', 'dcim.devicebaytemplate',
]

for _label in _component_template_labels:
    validator_registry.register(_label,
        ModelValidator(
            name='component_template_device_type_immutable',
            model_label=_label,
            fields=_fs({'device_type'}),
            category=ValidatorCategory.FIELD,
            validate=validate_component_template_device_type_immutable,
            description='Component templates cannot be moved to a different device type',
        ),
    )


def validate_modular_template_exclusive(instance):
    if instance.device_type and instance.module_type:
        raise ValidationError(
            _("A component template cannot be associated with both a device type and a module type.")
        )
    if not instance.device_type and not instance.module_type:
        raise ValidationError(
            _("A component template must be associated with either a device type or a module type.")
        )


_modular_template_labels = [
    'dcim.consoleporttemplate', 'dcim.consoleserverporttemplate',
    'dcim.powerporttemplate', 'dcim.poweroutlettemplate',
    'dcim.interfacetemplate', 'dcim.frontporttemplate', 'dcim.rearporttemplate',
    'dcim.modulebaytemplate',
]

for _label in _modular_template_labels:
    validator_registry.register(_label,
        ModelValidator(
            name='modular_template_exclusive',
            model_label=_label,
            fields=_fs({'device_type', 'module_type'}),
            category=ValidatorCategory.CROSS_FIELD,
            validate=validate_modular_template_exclusive,
            description='Template must belong to device type XOR module type',
        ),
    )


def validate_powerport_template_draw(instance):
    if instance.maximum_draw is not None and instance.allocated_draw is not None:
        if instance.allocated_draw > instance.maximum_draw:
            raise ValidationError({
                'allocated_draw': _(
                    "Allocated draw cannot exceed the maximum draw ({maximum_draw}W)."
                ).format(maximum_draw=instance.maximum_draw)
            })


validator_registry.register('dcim.powerporttemplate',
    ModelValidator(
        name='powerport_template_draw',
        model_label='dcim.powerporttemplate',
        fields=_fs({'allocated_draw', 'maximum_draw'}),
        category=ValidatorCategory.CROSS_FIELD,
        validate=validate_powerport_template_draw,
        description='Allocated draw cannot exceed maximum draw',
    ),
)


def validate_poweroutlet_template_power_port(instance):
    if instance.power_port:
        if instance.device_type and instance.power_port.device_type != instance.device_type:
            raise ValidationError(
                _("Parent power port ({power_port}) must belong to the same device type").format(
                    power_port=instance.power_port
                )
            )
        if instance.module_type and instance.power_port.module_type != instance.module_type:
            raise ValidationError(
                _("Parent power port ({power_port}) must belong to the same module type").format(
                    power_port=instance.power_port
                )
            )


validator_registry.register('dcim.poweroutlettemplate',
    ModelValidator(
        name='poweroutlet_template_power_port',
        model_label='dcim.poweroutlettemplate',
        fields=_fs({'power_port', 'device_type', 'module_type'}),
        category=ValidatorCategory.CROSS_MODEL,
        validate=validate_poweroutlet_template_power_port,
        queries_db=True,
        description='Power port template must belong to the same device/module type',
    ),
)


def validate_interface_template_bridge(instance):
    if instance.bridge:
        if instance.device_type and instance.device_type != instance.bridge.device_type:
            raise ValidationError({
                'bridge': _(
                    "Bridge interface ({bridge}) must belong to the same device type"
                ).format(bridge=instance.bridge)
            })
        if instance.module_type and instance.module_type != instance.bridge.module_type:
            raise ValidationError({
                'bridge': _(
                    "Bridge interface ({bridge}) must belong to the same module type"
                ).format(bridge=instance.bridge)
            })


validator_registry.register('dcim.interfacetemplate',
    ModelValidator(
        name='interface_template_bridge',
        model_label='dcim.interfacetemplate',
        fields=_fs({'bridge', 'device_type', 'module_type'}),
        category=ValidatorCategory.CROSS_MODEL,
        validate=validate_interface_template_bridge,
        queries_db=True,
        description='Bridge interface template must belong to same device/module type',
    ),
)


def validate_port_template_mapping_same_device_type(instance):
    if instance.front_port.device_type_id != instance.rear_port.device_type_id:
        raise ValidationError({
            "rear_port": _("Rear port ({rear_port}) must belong to the same device type").format(
                rear_port=instance.rear_port
            )
        })


validator_registry.register('dcim.porttemplatemapping',
    ModelValidator(
        name='port_template_mapping_same_device_type',
        model_label='dcim.porttemplatemapping',
        fields=_fs({'front_port', 'rear_port'}),
        category=ValidatorCategory.CROSS_MODEL,
        validate=validate_port_template_mapping_same_device_type,
        queries_db=True,
        description='Front and rear port templates must belong to the same device type',
    ),
)


def validate_frontport_template_positions(instance):
    if not instance._state.adding:
        mapping_count = instance.mappings.count()
        if instance.positions < mapping_count:
            raise ValidationError({
                "positions": _(
                    "The number of positions cannot be less than the number of mapped rear port templates ({count})"
                ).format(count=mapping_count)
            })


def validate_rearport_template_positions(instance):
    if not instance._state.adding:
        mapping_count = instance.mappings.count()
        if instance.positions < mapping_count:
            raise ValidationError({
                "positions": _(
                    "The number of positions cannot be less than the number of mapped front port templates "
                    "({count})"
                ).format(count=mapping_count)
            })


validator_registry.register('dcim.frontporttemplate',
    ModelValidator(
        name='frontport_template_positions',
        model_label='dcim.frontporttemplate',
        fields=_fs({'positions'}),
        category=ValidatorCategory.CROSS_MODEL,
        validate=validate_frontport_template_positions,
        queries_db=True,
        description='Positions must be >= mapped rear port template count',
    ),
)

validator_registry.register('dcim.rearporttemplate',
    ModelValidator(
        name='rearport_template_positions',
        model_label='dcim.rearporttemplate',
        fields=_fs({'positions'}),
        category=ValidatorCategory.CROSS_MODEL,
        validate=validate_rearport_template_positions,
        queries_db=True,
        description='Positions must be >= mapped front port template count',
    ),
)


def validate_devicebay_template_subdevice_role(instance):
    from dcim.choices import SubdeviceRoleChoices
    if instance.device_type and instance.device_type.subdevice_role != SubdeviceRoleChoices.ROLE_PARENT:
        raise ValidationError(
            _(
                'Subdevice role of device type ({device_type}) must be set to "parent" to allow device bays.'
            ).format(device_type=instance.device_type)
        )


validator_registry.register('dcim.devicebaytemplate',
    ModelValidator(
        name='devicebay_template_subdevice_role',
        model_label='dcim.devicebaytemplate',
        fields=_fs({'device_type'}),
        category=ValidatorCategory.CROSS_MODEL,
        validate=validate_devicebay_template_subdevice_role,
        queries_db=True,
        description='Device type must have parent subdevice role for device bays',
    ),
)
