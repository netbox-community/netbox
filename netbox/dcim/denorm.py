"""
Denormalization declarations for dcim models.
"""
import math

from netbox.denorm import DenormSpec, denorm_registry
from wireless.utils import get_channel_attr

# ──────────────────────────────────────────────────────────────────────
# ComponentModel (abstract) — all device components inherit these
# ──────────────────────────────────────────────────────────────────────

_component_models = [
    'dcim.consoleport',
    'dcim.consoleserverport',
    'dcim.powerport',
    'dcim.poweroutlet',
    'dcim.interface',
    'dcim.frontport',
    'dcim.rearport',
    'dcim.modulebay',
    'dcim.devicebay',
    'dcim.inventoryitem',
]

for model_label in _component_models:
    denorm_registry.register(
        model_label,
        DenormSpec(field_name='_site', source_path='device.site', depends_on=frozenset({'device'})),
        DenormSpec(field_name='_location', source_path='device.location', depends_on=frozenset({'device'})),
        DenormSpec(field_name='_rack', source_path='device.rack', depends_on=frozenset({'device'})),
    )

# ──────────────────────────────────────────────────────────────────────
# PortMapping — device from front_port
# ──────────────────────────────────────────────────────────────────────

denorm_registry.register(
    'dcim.portmapping',
    DenormSpec(field_name='device', source_path='front_port.device', depends_on=frozenset({'front_port'})),
)

# ──────────────────────────────────────────────────────────────────────
# PortTemplateMapping — device_type/module_type from front_port template
# ──────────────────────────────────────────────────────────────────────

denorm_registry.register(
    'dcim.porttemplatemapping',
    DenormSpec(
        field_name='device_type',
        source_path='front_port.device_type',
        depends_on=frozenset({'front_port'}),
    ),
    DenormSpec(
        field_name='module_type',
        source_path='front_port.module_type',
        depends_on=frozenset({'front_port'}),
    ),
)

# ──────────────────────────────────────────────────────────────────────
# CableTermination — cache from termination GFK
# ──────────────────────────────────────────────────────────────────────

def _cable_termination_cache_related(instance):
    """
    Replaces CableTermination.cache_related_objects().
    Computes _device, _rack, _location, _site from the termination GFK.
    Returns a dict of field values (used by individual DenormSpecs below).
    """
    # Cache the full computation on the instance to avoid repeated GFK resolution
    if not hasattr(instance, '_denorm_cache'):
        cache = {'_device': None, '_rack': None, '_location': None, '_site': None}
        termination = instance.termination
        if termination is not None:
            if getattr(termination, 'device', None):
                cache['_device'] = termination.device
                cache['_rack'] = termination.device.rack
                cache['_location'] = termination.device.location
                cache['_site'] = termination.device.site
            elif getattr(termination, 'rack', None):
                cache['_rack'] = termination.rack
                cache['_location'] = termination.rack.location
                cache['_site'] = termination.rack.site
            elif getattr(termination, 'site', None):
                cache['_site'] = termination.site
        instance._denorm_cache = cache
    return instance._denorm_cache


denorm_registry.register(
    'dcim.cabletermination',
    DenormSpec(
        field_name='_device',
        compute=lambda inst: _cable_termination_cache_related(inst)['_device'],
        depends_on=frozenset({'termination_type', 'termination_id'}),
    ),
    DenormSpec(
        field_name='_rack',
        compute=lambda inst: _cable_termination_cache_related(inst)['_rack'],
        depends_on=frozenset({'termination_type', 'termination_id'}),
    ),
    DenormSpec(
        field_name='_location',
        compute=lambda inst: _cable_termination_cache_related(inst)['_location'],
        depends_on=frozenset({'termination_type', 'termination_id'}),
    ),
    DenormSpec(
        field_name='_site',
        compute=lambda inst: _cable_termination_cache_related(inst)['_site'],
        depends_on=frozenset({'termination_type', 'termination_id'}),
    ),
)

# ──────────────────────────────────────────────────────────────────────
# PowerFeed — available_power from voltage/amperage/utilization/phase
# ──────────────────────────────────────────────────────────────────────

def _compute_available_power(instance):
    kva = abs(instance.voltage) * instance.amperage * (instance.max_utilization / 100)
    from dcim.choices import PowerFeedPhaseChoices
    if instance.phase == PowerFeedPhaseChoices.PHASE_3PHASE:
        return round(kva * 1.732)
    return round(kva)


denorm_registry.register(
    'dcim.powerfeed',
    DenormSpec(
        field_name='available_power',
        compute=_compute_available_power,
        depends_on=frozenset({'voltage', 'amperage', 'max_utilization', 'phase'}),
    ),
)

# ──────────────────────────────────────────────────────────────────────
# Rack — copy attributes from RackType
# ──────────────────────────────────────────────────────────────────────

def _rack_abs_max_weight(instance):
    if instance.max_weight and instance.weight_unit:
        from utilities.conversion import to_grams
        return to_grams(instance.max_weight, instance.weight_unit)
    return None


def _rack_outer_unit(instance):
    if not any([instance.outer_width, instance.outer_depth, instance.outer_height]):
        return None
    return instance.outer_unit


denorm_registry.register(
    'dcim.rack',
    DenormSpec(
        field_name='_abs_max_weight',
        compute=_rack_abs_max_weight,
        depends_on=frozenset({'max_weight', 'weight_unit'}),
    ),
    DenormSpec(
        field_name='outer_unit',
        compute=_rack_outer_unit,
        depends_on=frozenset({'outer_width', 'outer_depth', 'outer_height', 'outer_unit'}),
    ),
)

# ──────────────────────────────────────────────────────────────────────
# Rack — copy attributes from RackType (replaces copy_racktype_attrs())
# ──────────────────────────────────────────────────────────────────────

_RACKTYPE_FIELDS = (
    'form_factor', 'width', 'u_height', 'starting_unit', 'desc_units',
    'outer_width', 'outer_height', 'outer_depth', 'outer_unit',
    'mounting_depth', 'weight', 'weight_unit', 'max_weight',
)

for _field in _RACKTYPE_FIELDS:
    def _make_racktype_copier(field_name):
        def _copy(instance):
            if instance.rack_type:
                return getattr(instance.rack_type, field_name)
            return getattr(instance, field_name)
        return _copy

    denorm_registry.register(
        'dcim.rack',
        DenormSpec(
            field_name=_field,
            compute=_make_racktype_copier(_field),
            depends_on=frozenset({'rack_type', _field}),
        ),
    )


# Same for RackType
denorm_registry.register(
    'dcim.racktype',
    DenormSpec(
        field_name='_abs_max_weight',
        compute=_rack_abs_max_weight,
        depends_on=frozenset({'max_weight', 'weight_unit'}),
    ),
    DenormSpec(
        field_name='outer_unit',
        compute=_rack_outer_unit,
        depends_on=frozenset({'outer_width', 'outer_depth', 'outer_height', 'outer_unit'}),
    ),
)

# ──────────────────────────────────────────────────────────────────────
# ModuleBay — MPTT parent from module
# ──────────────────────────────────────────────────────────────────────

def _modulebay_parent(instance):
    if instance.module:
        return instance.module.module_bay
    return None


denorm_registry.register(
    'dcim.modulebay',
    DenormSpec(
        field_name='parent',
        compute=_modulebay_parent,
        depends_on=frozenset({'module'}),
    ),
)


# ──────────────────────────────────────────────────────────────────────
# BaseInterface (Interface / VMInterface) — clear untagged_vlan when no mode
# ──────────────────────────────────────────────────────────────────────

def _baseinterface_untagged_vlan(instance):
    if not instance.mode:
        return None
    return instance.untagged_vlan


for _iface_label in ('dcim.interface', 'virtualization.vminterface'):
    denorm_registry.register(
        _iface_label,
        DenormSpec(
            field_name='untagged_vlan',
            compute=_baseinterface_untagged_vlan,
            depends_on=frozenset({'mode', 'untagged_vlan'}),
        ),
    )

# ──────────────────────────────────────────────────────────────────────
# Device — default airflow/platform from DeviceType (creation only),
#           location from Rack (every save)
# ──────────────────────────────────────────────────────────────────────

def _device_default_airflow(instance):
    if not instance.airflow and instance.device_type:
        return instance.device_type.airflow
    return instance.airflow


def _device_default_platform(instance):
    if not instance.platform and instance.device_type:
        return instance.device_type.default_platform
    return instance.platform


def _device_location_from_rack(instance):
    if instance.rack and instance.rack.location:
        return instance.rack.location
    return instance.location


denorm_registry.register(
    'dcim.device',
    DenormSpec(
        field_name='airflow',
        compute=_device_default_airflow,
        depends_on=frozenset({'airflow', 'device_type'}),
        only_on_create=True,
    ),
    DenormSpec(
        field_name='platform',
        compute=_device_default_platform,
        depends_on=frozenset({'platform', 'device_type'}),
        only_on_create=True,
    ),
    DenormSpec(
        field_name='location',
        compute=_device_location_from_rack,
        depends_on=frozenset({'rack', 'location'}),
    ),
)

# ──────────────────────────────────────────────────────────────────────
# Interface — rf_channel_frequency/width from rf_channel
# ──────────────────────────────────────────────────────────────────────

def _interface_rf_channel_frequency(instance):
    if instance.rf_channel and not instance.rf_channel_frequency:
        return get_channel_attr(instance.rf_channel, 'frequency')
    return instance.rf_channel_frequency


def _interface_rf_channel_width(instance):
    if instance.rf_channel and not instance.rf_channel_width:
        return get_channel_attr(instance.rf_channel, 'width')
    return instance.rf_channel_width


denorm_registry.register(
    'dcim.interface',
    DenormSpec(
        field_name='rf_channel_frequency',
        compute=_interface_rf_channel_frequency,
        depends_on=frozenset({'rf_channel', 'rf_channel_frequency'}),
    ),
    DenormSpec(
        field_name='rf_channel_width',
        compute=_interface_rf_channel_width,
        depends_on=frozenset({'rf_channel', 'rf_channel_width'}),
    ),
)
