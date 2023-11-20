from django import forms
from django.utils.translation import gettext as _

from netbox.forms import NetBoxModelFilterSetForm
from tenancy.forms import TenancyFilterForm
from utilities.forms.fields import DynamicModelMultipleChoiceField, TagFilterField
from vpn.choices import *
from vpn.models import *

__all__ = (
    'IKEPolicyFilterForm',
    'IKEProposalFilterForm',
    'IPSecPolicyFilterForm',
    'IPSecProfileFilterForm',
    'IPSecProposalFilterForm',
    'TunnelFilterForm',
    'TunnelTerminationFilterForm',
)


class TunnelFilterForm(TenancyFilterForm, NetBoxModelFilterSetForm):
    model = Tunnel
    fieldsets = (
        (None, ('q', 'filter_id', 'tag')),
        (_('Tunnel'), ('status', 'encapsulation', 'tunnel_id')),
        (_('Security'), ('ipsec_profile_id',)),
        (_('Tenancy'), ('tenant_group_id', 'tenant_id')),
    )
    status = forms.MultipleChoiceField(
        label=_('Status'),
        choices=TunnelStatusChoices,
        required=False
    )
    encapsulation = forms.MultipleChoiceField(
        label=_('Encapsulation'),
        choices=TunnelEncapsulationChoices,
        required=False
    )
    ipsec_profile_id = DynamicModelMultipleChoiceField(
        queryset=IPSecProfile.objects.all(),
        required=False,
        label=_('IPSec profile')
    )
    tunnel_id = forms.IntegerField(
        required=False,
        label=_('Tunnel ID')
    )
    tag = TagFilterField(model)


class TunnelTerminationFilterForm(NetBoxModelFilterSetForm):
    model = TunnelTermination
    fieldsets = (
        (None, ('q', 'filter_id', 'tag')),
        (_('Termination'), ('tunnel_id', 'role')),
    )
    tunnel_id = DynamicModelMultipleChoiceField(
        queryset=Tunnel.objects.all(),
        required=False,
        label=_('Tunnel')
    )
    role = forms.MultipleChoiceField(
        label=_('Role'),
        choices=TunnelTerminationRoleChoices,
        required=False
    )
    tag = TagFilterField(model)


class IKEProposalFilterForm(NetBoxModelFilterSetForm):
    model = IKEProposal
    fieldsets = (
        (None, ('q', 'filter_id', 'tag')),
        (_('Parameters'), ('authentication_method', 'encryption_algorithm', 'authentication_algorithm', 'group')),
    )
    authentication_method = forms.MultipleChoiceField(
        label=_('Authentication method'),
        choices=AuthenticationMethodChoices,
        required=False
    )
    encryption_algorithm = forms.MultipleChoiceField(
        label=_('Encryption algorithm'),
        choices=EncryptionAlgorithmChoices,
        required=False
    )
    authentication_algorithm = forms.MultipleChoiceField(
        label=_('Authentication algorithm'),
        choices=AuthenticationAlgorithmChoices,
        required=False
    )
    group = forms.MultipleChoiceField(
        label=_('Group'),
        choices=DHGroupChoices,
        required=False
    )
    tag = TagFilterField(model)


class IKEPolicyFilterForm(NetBoxModelFilterSetForm):
    model = IKEPolicy
    fieldsets = (
        (None, ('q', 'filter_id', 'tag')),
        (_('Parameters'), ('version', 'mode', 'proposal_id')),
    )
    version = forms.MultipleChoiceField(
        label=_('IKE version'),
        choices=IKEVersionChoices,
        required=False
    )
    mode = forms.MultipleChoiceField(
        label=_('Mode'),
        choices=IKEModeChoices,
        required=False
    )
    proposal_id = DynamicModelMultipleChoiceField(
        queryset=IKEProposal.objects.all(),
        required=False,
        label=_('Proposal')
    )
    tag = TagFilterField(model)


class IPSecProposalFilterForm(NetBoxModelFilterSetForm):
    model = IPSecProposal
    fieldsets = (
        (None, ('q', 'filter_id', 'tag')),
        (_('Parameters'), ('encryption_algorithm', 'authentication_algorithm')),
    )
    encryption_algorithm = forms.MultipleChoiceField(
        label=_('Encryption algorithm'),
        choices=EncryptionAlgorithmChoices,
        required=False
    )
    authentication_algorithm = forms.MultipleChoiceField(
        label=_('Authentication algorithm'),
        choices=AuthenticationAlgorithmChoices,
        required=False
    )
    tag = TagFilterField(model)


class IPSecPolicyFilterForm(NetBoxModelFilterSetForm):
    model = IPSecPolicy
    fieldsets = (
        (None, ('q', 'filter_id', 'tag')),
        (_('Parameters'), ('proposal', 'pfs_group')),
    )
    proposal_id = DynamicModelMultipleChoiceField(
        queryset=IKEProposal.objects.all(),
        required=False,
        label=_('Proposal')
    )
    pfs_group = forms.MultipleChoiceField(
        label=_('Mode'),
        choices=DHGroupChoices,
        required=False
    )
    tag = TagFilterField(model)


class IPSecProfileFilterForm(NetBoxModelFilterSetForm):
    model = IPSecProfile
    fieldsets = (
        (None, ('q', 'filter_id', 'tag')),
        (_('Profile'), ('protocol', 'ike_version')),
        (_('Phase 1 Parameters'), (
            'phase1_encryption', 'phase1_authentication', 'phase1_group', 'phase1_sa_lifetime',
        )),
        (_('Phase 2 Parameters'), (
            'phase2_encryption', 'phase2_authentication', 'phase2_group', 'phase2_sa_lifetime',
            'phase2_sa_lifetime_data',
        )),
    )
    mode = forms.MultipleChoiceField(
        label=_('Mode'),
        choices=IPSecModeChoices,
        required=False
    )
    ike_policy_id = DynamicModelMultipleChoiceField(
        queryset=IKEPolicy.objects.all(),
        required=False,
        label=_('IKE policy')
    )
    ipsec_policy_id = DynamicModelMultipleChoiceField(
        queryset=IPSecPolicy.objects.all(),
        required=False,
        label=_('IPSec policy')
    )
    tag = TagFilterField(model)
