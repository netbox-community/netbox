"""
Denormalization declarations for abstract model mixins.

These are registered for every concrete model that uses the mixin.
"""
from netbox.denorm import DenormSpec, denorm_registry

# ──────────────────────────────────────────────────────────────────────
# WeightMixin — _abs_weight from weight + weight_unit
# ──────────────────────────────────────────────────────────────────────

def _abs_weight(instance):
    if instance.weight and instance.weight_unit:
        from utilities.conversion import to_grams
        return to_grams(instance.weight, instance.weight_unit)
    return None


_weight_spec = DenormSpec(
    field_name='_abs_weight',
    compute=_abs_weight,
    depends_on=frozenset({'weight', 'weight_unit'}),
)

# Concrete models using WeightMixin
for model_label in ['dcim.devicetype', 'dcim.moduletype', 'dcim.rack', 'dcim.racktype']:
    denorm_registry.register(model_label, _weight_spec)

# ──────────────────────────────────────────────────────────────────────
# DistanceMixin — _abs_distance from distance + distance_unit
# ──────────────────────────────────────────────────────────────────────

def _abs_distance(instance):
    if instance.distance is not None and instance.distance_unit:
        from utilities.conversion import to_meters
        return to_meters(instance.distance, instance.distance_unit)
    return None


def _distance_unit_cleanup(instance):
    """Clear distance_unit when distance is None."""
    if instance.distance is None:
        return None
    return instance.distance_unit


_distance_specs = [
    DenormSpec(
        field_name='_abs_distance',
        compute=_abs_distance,
        depends_on=frozenset({'distance', 'distance_unit'}),
    ),
    DenormSpec(
        field_name='distance_unit',
        compute=_distance_unit_cleanup,
        depends_on=frozenset({'distance', 'distance_unit'}),
    ),
]

# Concrete models using DistanceMixin
for model_label in ['circuits.circuit', 'wireless.wirelesslink']:
    denorm_registry.register(model_label, *_distance_specs)

# ──────────────────────────────────────────────────────────────────────
# Cable — _abs_length from length + length_unit (same pattern as distance)
# ──────────────────────────────────────────────────────────────────────

def _cable_abs_length(instance):
    if instance.length is not None and instance.length_unit:
        from utilities.conversion import to_meters
        return to_meters(instance.length, instance.length_unit)
    return None


def _cable_length_unit_cleanup(instance):
    if instance.length is None:
        return None
    return instance.length_unit


denorm_registry.register(
    'dcim.cable',
    DenormSpec(
        field_name='_abs_length',
        compute=_cable_abs_length,
        depends_on=frozenset({'length', 'length_unit'}),
    ),
    DenormSpec(
        field_name='length_unit',
        compute=_cable_length_unit_cleanup,
        depends_on=frozenset({'length', 'length_unit'}),
    ),
)

# ──────────────────────────────────────────────────────────────────────
# CablePath — _nodes from path
# ──────────────────────────────────────────────────────────────────────

def _cablepath_nodes(instance):
    import itertools
    if instance.path:
        return list(itertools.chain(*instance.path))
    return []


denorm_registry.register(
    'dcim.cablepath',
    DenormSpec(
        field_name='_nodes',
        compute=_cablepath_nodes,
        depends_on=frozenset({'path'}),
    ),
)
