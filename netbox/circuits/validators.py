"""
Extracted, composable validators for circuits models.
Each function is standalone and raises ValidationError on failure.
"""
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from netbox.validators import ModelValidator, ValidatorCategory, validator_registry

_fs = frozenset


# ──────────────────────────────────────────────────────────────────────
# Circuit
# ──────────────────────────────────────────────────────────────────────

def validate_circuit_provider_account(instance):
    if instance.provider_account and instance.provider != instance.provider_account.provider:
        raise ValidationError({'provider_account': "The assigned account must belong to the assigned provider."})


validator_registry.register('circuits.circuit',
    ModelValidator(
        name='circuit_provider_account',
        model_label='circuits.circuit',
        fields=_fs({'provider', 'provider_account'}),
        category=ValidatorCategory.CROSS_FIELD,
        validate=validate_circuit_provider_account,
        description='Provider account must belong to the assigned provider',
    ),
)

# ──────────────────────────────────────────────────────────────────────
# VirtualCircuit
# ──────────────────────────────────────────────────────────────────────

def validate_virtualcircuit_provider_account(instance):
    if instance.provider_account and instance.provider_network.provider != instance.provider_account.provider:
        raise ValidationError({
            'provider_account': "The assigned account must belong to the provider of the assigned network."
        })


validator_registry.register('circuits.virtualcircuit',
    ModelValidator(
        name='virtualcircuit_provider_account',
        model_label='circuits.virtualcircuit',
        fields=_fs({'provider_account', 'provider_network'}),
        category=ValidatorCategory.CROSS_FIELD,
        validate=validate_virtualcircuit_provider_account,
        description='Provider account must belong to the provider of the assigned network',
    ),
)

# ──────────────────────────────────────────────────────────────────────
# VirtualCircuitTermination
# ──────────────────────────────────────────────────────────────────────

def validate_virtualcircuittermination_interface(instance):
    if instance.interface and not instance.interface.is_virtual:
        raise ValidationError("Virtual circuits may be terminated only to virtual interfaces.")


validator_registry.register('circuits.virtualcircuittermination',
    ModelValidator(
        name='virtualcircuittermination_interface',
        model_label='circuits.virtualcircuittermination',
        fields=_fs({'interface'}),
        category=ValidatorCategory.CROSS_FIELD,
        validate=validate_virtualcircuittermination_interface,
        description='Virtual circuits may only terminate to virtual interfaces',
    ),
)

# ──────────────────────────────────────────────────────────────────────
# CircuitTermination
# ──────────────────────────────────────────────────────────────────────

def validate_circuittermination_object(instance):
    if instance.termination is None:
        raise ValidationError(_("A circuit termination must attach to a terminating object."))


validator_registry.register('circuits.circuittermination',
    ModelValidator(
        name='circuittermination_object',
        model_label='circuits.circuittermination',
        fields=_fs({'termination_type', 'termination_id'}),
        category=ValidatorCategory.FIELD,
        validate=validate_circuittermination_object,
        description='Circuit termination must have a terminating object',
    ),
)
