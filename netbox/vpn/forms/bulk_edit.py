from django import forms
from django.utils.translation import gettext_lazy as _

from netbox.forms import NetBoxModelBulkEditForm, OrganizationalModelBulkEditForm, PrimaryModelBulkEditForm
from tenancy.models import Tenant
from utilities.forms import add_blank_choice
from utilities.forms.fields import DynamicModelChoiceField, DynamicModelMultipleChoiceField
from utilities.forms.rendering import FieldSet
from vpn.choices import *
from vpn.models import *

__all__ = (
    'IKEPolicyBulkEditForm',
    'IKEProposalBulkEditForm',
    'IPSecPolicyBulkEditForm',
    'IPSecProfileBulkEditForm',
    'IPSecProposalBulkEditForm',
    'L2VPNBulkEditForm',
    'L2VPNTerminationBulkEditForm',
    'TunnelBulkEditForm',
    'TunnelGroupBulkEditForm',
    'TunnelTerminationBulkEditForm',
)


class TunnelGroupBulkEditForm(OrganizationalModelBulkEditForm):
    model = TunnelGroup
    nullable_fields = ('description', 'comments')


class TunnelBulkEditForm(PrimaryModelBulkEditForm):
    status = forms.ChoiceField(
        label=_('Status'),
        choices=add_blank_choice(TunnelStatusChoices),
        required=False
    )
    group = DynamicModelChoiceField(
        queryset=TunnelGroup.objects.all(),
        label=_('Tunnel group'),
        required=False
    )
    encapsulation = forms.ChoiceField(
        label=_('Encapsulation'),
        choices=add_blank_choice(TunnelEncapsulationChoices),
        required=False
    )
    ipsec_profile = DynamicModelMultipleChoiceField(
        queryset=IPSecProfile.objects.all(),
        label=_('IPSec profile'),
        required=False
    )
    tenant = DynamicModelChoiceField(
        label=_('Tenant'),
        queryset=Tenant.objects.all(),
        required=False
    )
    tunnel_id = forms.IntegerField(
        label=_('Tunnel ID'),
        required=False
    )

    model = Tunnel
    fieldsets = (
        FieldSet('status', 'group', 'encapsulation', 'tunnel_id', 'description', name=_('Tunnel')),
        FieldSet('ipsec_profile', name=_('Security')),
        FieldSet('tenant', name=_('Tenancy')),
    )
    nullable_fields = (
        'group', 'ipsec_profile', 'tunnel_id', 'tenant', 'description', 'comments',
    )


class TunnelTerminationBulkEditForm(NetBoxModelBulkEditForm):
    role = forms.ChoiceField(
        label=_('Role'),
        choices=add_blank_choice(TunnelTerminationRoleChoices),
        required=False
    )

    model = TunnelTermination


class IKEProposalBulkEditForm(PrimaryModelBulkEditForm):
    authentication_method = forms.ChoiceField(
        label=_('Authentication method'),
        choices=add_blank_choice(AuthenticationMethodChoices),
        required=False
    )
    encryption_algorithm = forms.ChoiceField(
        label=_('Encryption algorithm'),
        choices=add_blank_choice(EncryptionAlgorithmChoices),
        required=False
    )
    authentication_algorithm = forms.ChoiceField(
        label=_('Authentication algorithm'),
        choices=add_blank_choice(AuthenticationAlgorithmChoices),
        required=False
    )
    group = forms.ChoiceField(
        label=_('Group'),
        choices=add_blank_choice(DHGroupChoices),
        required=False
    )
    sa_lifetime = forms.IntegerField(
        label=_('SA lifetime'),
        required=False
    )

    model = IKEProposal
    fieldsets = (
        FieldSet(
            'authentication_method', 'encryption_algorithm', 'authentication_algorithm', 'group', 'sa_lifetime',
            'description',
        ),
    )
    nullable_fields = (
        'sa_lifetime', 'description', 'comments',
    )


class IKEPolicyBulkEditForm(PrimaryModelBulkEditForm):
    version = forms.ChoiceField(
        label=_('Version'),
        choices=add_blank_choice(IKEVersionChoices),
        required=False
    )
    mode = forms.ChoiceField(
        label=_('Mode'),
        choices=add_blank_choice(IKEModeChoices),
        required=False
    )
    preshared_key = forms.CharField(
        label=_('Pre-shared key'),
        required=False
    )

    model = IKEPolicy
    fieldsets = (
        FieldSet('version', 'mode', 'preshared_key', 'description'),
    )
    nullable_fields = (
        'mode', 'preshared_key', 'description', 'comments',
    )


class IPSecProposalBulkEditForm(PrimaryModelBulkEditForm):
    encryption_algorithm = forms.ChoiceField(
        label=_('Encryption algorithm'),
        choices=add_blank_choice(EncryptionAlgorithmChoices),
        required=False
    )
    authentication_algorithm = forms.ChoiceField(
        label=_('Authentication algorithm'),
        choices=add_blank_choice(AuthenticationAlgorithmChoices),
        required=False
    )
    sa_lifetime_seconds = forms.IntegerField(
        label=_('SA lifetime (seconds)'),
        required=False
    )
    sa_lifetime_data = forms.IntegerField(
        label=_('SA lifetime (KB)'),
        required=False
    )

    model = IPSecProposal
    fieldsets = (
        FieldSet(
            'encryption_algorithm', 'authentication_algorithm', 'sa_lifetime_seconds', 'sa_lifetime_data',
            'description',
        ),
    )
    nullable_fields = (
        'sa_lifetime_seconds', 'sa_lifetime_data', 'description', 'comments',
    )


class IPSecPolicyBulkEditForm(PrimaryModelBulkEditForm):
    pfs_group = forms.ChoiceField(
        label=_('PFS group'),
        choices=add_blank_choice(DHGroupChoices),
        required=False
    )

    model = IPSecPolicy
    fieldsets = (
        FieldSet('pfs_group', 'description'),
    )
    nullable_fields = (
        'pfs_group', 'description', 'comments',
    )


class IPSecProfileBulkEditForm(PrimaryModelBulkEditForm):
    mode = forms.ChoiceField(
        label=_('Mode'),
        choices=add_blank_choice(IPSecModeChoices),
        required=False
    )
    ike_policy = DynamicModelChoiceField(
        label=_('IKE policy'),
        queryset=IKEPolicy.objects.all(),
        required=False
    )
    ipsec_policy = DynamicModelChoiceField(
        label=_('IPSec policy'),
        queryset=IPSecPolicy.objects.all(),
        required=False
    )

    model = IPSecProfile
    fieldsets = (
        FieldSet('mode', 'ike_policy', 'ipsec_policy', 'description', name=_('Profile')),
    )
    nullable_fields = (
        'description', 'comments',
    )


class L2VPNBulkEditForm(PrimaryModelBulkEditForm):
    status = forms.ChoiceField(
        label=_('Status'),
        choices=L2VPNStatusChoices,
    )
    type = forms.ChoiceField(
        label=_('Type'),
        choices=add_blank_choice(L2VPNTypeChoices),
        required=False
    )
    tenant = DynamicModelChoiceField(
        label=_('Tenant'),
        queryset=Tenant.objects.all(),
        required=False
    )

    model = L2VPN
    fieldsets = (
        FieldSet('status', 'type', 'tenant', 'description'),
    )
    nullable_fields = ('tenant', 'description', 'comments')


class L2VPNTerminationBulkEditForm(NetBoxModelBulkEditForm):
    model = L2VPN
