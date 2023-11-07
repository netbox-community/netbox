from django import forms
from django.utils.translation import gettext_lazy as _

from netbox.forms import NetBoxModelBulkEditForm
from tenancy.models import Tenant
from utilities.forms import add_blank_choice
from utilities.forms.fields import CommentField, DynamicModelChoiceField, DynamicModelMultipleChoiceField
from vpn.choices import *
from vpn.models import *

__all__ = (
    'IPSecProfileBulkEditForm',
    'TunnelBulkEditForm',
    'TunnelTerminationBulkEditForm',
)


class TunnelBulkEditForm(NetBoxModelBulkEditForm):
    status = forms.ChoiceField(
        label=_('Status'),
        choices=add_blank_choice(TunnelStatusChoices),
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
    preshared_key = forms.CharField(
        label=_('Pre-shared key'),
        required=False
    )
    tenant = DynamicModelChoiceField(
        label=_('Tenant'),
        queryset=Tenant.objects.all(),
        required=False
    )
    description = forms.CharField(
        label=_('Description'),
        max_length=200,
        required=False
    )
    tunnel_id = forms.IntegerField(
        label=_('Tunnel ID'),
        required=False
    )
    comments = CommentField()

    model = Tunnel
    fieldsets = (
        (_('Tunnel'), ('status', 'encapsulation', 'tunnel_id', 'description')),
        (_('Security'), ('ipsec_profile', 'preshared_key')),
        (_('Tenancy'), ('tenant',)),
    )
    nullable_fields = (
        'ipsec_profile', 'preshared_key', 'tunnel_id', 'tenant', 'description', 'comments',
    )


class TunnelTerminationBulkEditForm(NetBoxModelBulkEditForm):
    role = forms.ChoiceField(
        label=_('Role'),
        choices=add_blank_choice(TunnelTerminationRoleChoices),
        required=False
    )

    model = TunnelTermination
    fieldsets = (
        (None, ('role',)),
    )


class IPSecProfileBulkEditForm(NetBoxModelBulkEditForm):
    protocol = forms.ChoiceField(
        label=_('Protocol'),
        choices=add_blank_choice(IPSecProtocolChoices),
        required=False
    )
    ike_version = forms.ChoiceField(
        label=_('IKE version'),
        choices=add_blank_choice(IKEVersionChoices),
        required=False
    )
    description = forms.CharField(
        label=_('Description'),
        max_length=200,
        required=False
    )
    phase1_encryption = forms.ChoiceField(
        label=_('Encryption'),
        choices=add_blank_choice(EncryptionChoices),
        required=False
    )
    phase1_authentication = forms.ChoiceField(
        label=_('Authentication'),
        choices=add_blank_choice(AuthenticationChoices),
        required=False
    )
    phase1_group = forms.ChoiceField(
        label=_('Group'),
        choices=add_blank_choice(DHGroupChoices),
        required=False
    )
    phase1_sa_lifetime = forms.IntegerField(
        required=False
    )
    phase2_encryption = forms.ChoiceField(
        label=_('Encryption'),
        choices=add_blank_choice(EncryptionChoices),
        required=False
    )
    phase2_authentication = forms.ChoiceField(
        label=_('Authentication'),
        choices=add_blank_choice(AuthenticationChoices),
        required=False
    )
    phase2_group = forms.ChoiceField(
        label=_('Group'),
        choices=add_blank_choice(DHGroupChoices),
        required=False
    )
    phase2_sa_lifetime = forms.IntegerField(
        required=False
    )
    comments = CommentField()

    model = IPSecProfile
    fieldsets = (
        (_('Profile'), ('protocol', 'ike_version', 'description')),
        (_('Phase 1 Parameters'), ('phase1_encryption', 'phase1_authentication', 'phase1_group', 'phase1_sa_lifetime')),
        (_('Phase 2 Parameters'), ('phase2_encryption', 'phase2_authentication', 'phase2_group', 'phase2_sa_lifetime')),
    )
    nullable_fields = (
        'description', 'phase1_sa_lifetime', 'phase2_sa_lifetime', 'comments',
    )
