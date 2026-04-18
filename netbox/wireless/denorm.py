"""
Denormalization declarations for wireless models.
"""
from netbox.denorm import DenormSpec, denorm_registry

# ──────────────────────────────────────────────────────────────────────
# WirelessLink — device cache from interfaces
# ──────────────────────────────────────────────────────────────────────

denorm_registry.register(
    'wireless.wirelesslink',
    DenormSpec(
        field_name='_interface_a_device',
        source_path='interface_a.device',
        depends_on=frozenset({'interface_a'}),
    ),
    DenormSpec(
        field_name='_interface_b_device',
        source_path='interface_b.device',
        depends_on=frozenset({'interface_b'}),
    ),
)
