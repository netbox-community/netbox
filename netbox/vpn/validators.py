"""
Extracted, composable validators for vpn models.
"""
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from netbox.validators import ModelValidator, ValidatorCategory, validator_registry

_fs = frozenset


def validate_l2vpn_termination_unique(instance):
    """Only one L2VPN termination per assigned object; P2P has max 2."""
    from vpn.models import L2VPNTermination
    from vpn.choices import L2VPNTypeChoices

    existing = L2VPNTermination.objects.filter(
        assigned_object_type=instance.assigned_object_type,
        assigned_object_id=instance.assigned_object_id,
    ).exclude(pk=instance.pk)
    if existing.exists():
        raise ValidationError({
            'assigned_object': _("This object is already assigned to an L2VPN termination.")
        })

    if instance.l2vpn and instance.l2vpn.type in L2VPNTypeChoices.P2P:
        count = L2VPNTermination.objects.filter(l2vpn=instance.l2vpn).exclude(pk=instance.pk).count()
        if count >= 2:
            raise ValidationError(
                _("A point-to-point L2VPN may have no more than two terminations.")
            )


def validate_tunnel_termination_unique(instance):
    """Termination object cannot be on multiple tunnels."""
    if not instance.termination_id:
        return
    from vpn.models import TunnelTermination
    existing = TunnelTermination.objects.filter(
        termination_type=instance.termination_type,
        termination_id=instance.termination_id,
    ).exclude(pk=instance.pk)
    if existing.exists():
        raise ValidationError({
            'termination': _("This interface is already assigned to a tunnel.")
        })


validator_registry.register('vpn.l2vpntermination',
    ModelValidator(
        name='l2vpn_termination_unique',
        model_label='vpn.l2vpntermination',
        fields=_fs({'assigned_object_type', 'assigned_object_id', 'l2vpn'}),
        category=ValidatorCategory.UNIQUENESS,
        validate=validate_l2vpn_termination_unique,
        queries_db=True,
        description='One L2VPN termination per object; P2P max 2',
    ),
)

validator_registry.register('vpn.tunneltermination',
    ModelValidator(
        name='tunnel_termination_unique',
        model_label='vpn.tunneltermination',
        fields=_fs({'termination_type', 'termination_id'}),
        category=ValidatorCategory.UNIQUENESS,
        validate=validate_tunnel_termination_unique,
        queries_db=True,
        description='Interface can only be assigned to one tunnel',
    ),
)

# ──────────────────────────────────────────────────────────────────────
# IKEPolicy
# ──────────────────────────────────────────────────────────────────────

def validate_ikepolicy_mode(instance):
    from vpn.choices import IKEVersionChoices
    if instance.version == IKEVersionChoices.VERSION_1 and not instance.mode:
        raise ValidationError(_("Mode is required for selected IKE version"))
    if instance.version == IKEVersionChoices.VERSION_2 and instance.mode:
        raise ValidationError(_("Mode cannot be used for selected IKE version"))


validator_registry.register('vpn.ikepolicy',
    ModelValidator(
        name='ikepolicy_mode',
        model_label='vpn.ikepolicy',
        fields=_fs({'version', 'mode'}),
        category=ValidatorCategory.CROSS_FIELD,
        validate=validate_ikepolicy_mode,
        description='IKEv1 requires mode; IKEv2 forbids it',
    ),
)

# ──────────────────────────────────────────────────────────────────────
# IPSecProposal
# ──────────────────────────────────────────────────────────────────────

def validate_ipsecproposal_algorithm(instance):
    if not instance.encryption_algorithm and not instance.authentication_algorithm:
        raise ValidationError(_("Encryption and/or authentication algorithm must be defined"))


validator_registry.register('vpn.ipsecproposal',
    ModelValidator(
        name='ipsecproposal_algorithm',
        model_label='vpn.ipsecproposal',
        fields=_fs({'encryption_algorithm', 'authentication_algorithm'}),
        category=ValidatorCategory.CROSS_FIELD,
        validate=validate_ipsecproposal_algorithm,
        description='At least one algorithm must be defined',
    ),
)
