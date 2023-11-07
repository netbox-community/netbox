from django import forms
from django.utils.translation import gettext as _

from netbox.forms import NetBoxModelFilterSetForm
from utilities.forms.fields import DynamicModelMultipleChoiceField, TagFilterField
from vpn.choices import *
from vpn.models import *

__all__ = (
    'IPSecProfileFilterForm',
    'TunnelFilterForm',
    'TunnelTerminationFilterForm',
)


class TunnelFilterForm(NetBoxModelFilterSetForm):
    model = Tunnel
    fieldsets = (
        (None, ('q', 'filter_id', 'tag')),
        (_('Tunnel'), ('status', 'encapsulation', 'tunnel_id')),
        (_('Security'), ('ipsec_profile_id', 'preshared_key')),
        (_('Tenancy'), ('tenant',)),
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


class IPSecProfileFilterForm(NetBoxModelFilterSetForm):
    model = IPSecProfile
    fieldsets = (
        (None, ('q', 'filter_id', 'tag')),
        (_('Profile'), ('protocol', 'ike_version')),
        (_('Phase 1 Parameters'), ('phase1_encryption', 'phase1_authentication', 'phase1_group', 'phase1_sa_lifetime')),
        (_('Phase 2 Parameters'), ('phase2_encryption', 'phase2_authentication', 'phase2_group', 'phase2_sa_lifetime')),
    )
    protocol = forms.MultipleChoiceField(
        label=_('Protocol'),
        choices=IPSecProtocolChoices,
        required=False
    )
    ike_version = forms.MultipleChoiceField(
        label=_('IKE version'),
        choices=IKEVersionChoices,
        required=False
    )
    ipsec_profile_id = DynamicModelMultipleChoiceField(
        queryset=IPSecProfile.objects.all(),
        required=False,
        label=_('IPSec profile')
    )
    phase1_encryption = forms.MultipleChoiceField(
        label=_('Encryption'),
        choices=EncryptionChoices,
        required=False
    )
    phase1_authentication = forms.MultipleChoiceField(
        label=_('Authentication'),
        choices=AuthenticationChoices,
        required=False
    )
    phase1_group = forms.MultipleChoiceField(
        label=_('Group'),
        choices=DHGroupChoices,
        required=False
    )
    phase1_sa_lifetime = forms.IntegerField(
        required=False,
        min_value=0,
        label=_('SA lifetime')
    )
    phase2_encryption = forms.MultipleChoiceField(
        label=_('Encryption'),
        choices=EncryptionChoices,
        required=False
    )
    phase2_authentication = forms.MultipleChoiceField(
        label=_('Authentication'),
        choices=AuthenticationChoices,
        required=False
    )
    phase2_group = forms.MultipleChoiceField(
        label=_('Group'),
        choices=DHGroupChoices,
        required=False
    )
    phase2_sa_lifetime = forms.IntegerField(
        required=False,
        min_value=0,
        label=_('SA lifetime')
    )
    tag = TagFilterField(model)
