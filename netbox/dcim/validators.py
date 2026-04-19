"""
Extracted, composable validators for dcim models.
Each function is standalone and raises ValidationError on failure.
"""
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

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
    from dcim.choices import NONCONNECTABLE_IFACE_TYPES
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
