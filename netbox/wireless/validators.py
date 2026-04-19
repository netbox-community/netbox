"""
Extracted, composable validators for wireless models.
Each function is standalone and raises ValidationError on failure.
"""
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from dcim.constants import WIRELESS_IFACE_TYPES
from netbox.validators import ModelValidator, ValidatorCategory, validator_registry

_fs = frozenset


# ──────────────────────────────────────────────────────────────────────
# WirelessLink
# ──────────────────────────────────────────────────────────────────────

def validate_wirelesslink_interface_types(instance):
    if hasattr(instance, "interface_a") and instance.interface_a.type not in WIRELESS_IFACE_TYPES:
        raise ValidationError({
            'interface_a': _(
                "{type} is not a wireless interface."
            ).format(type=instance.interface_a.get_type_display())
        })
    if hasattr(instance, "interface_b") and instance.interface_b.type not in WIRELESS_IFACE_TYPES:
        raise ValidationError({
            'interface_b': _(
                "{type} is not a wireless interface."
            ).format(type=instance.interface_b.get_type_display())
        })


validator_registry.register('wireless.wirelesslink',
    ModelValidator(
        name='wirelesslink_interface_types',
        model_label='wireless.wirelesslink',
        fields=_fs({'interface_a', 'interface_b'}),
        category=ValidatorCategory.CROSS_FIELD,
        validate=validate_wirelesslink_interface_types,
        description='Both interfaces must be wireless types',
    ),
)
