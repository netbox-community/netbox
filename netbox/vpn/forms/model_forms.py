from django.utils.translation import gettext_lazy as _

from dcim.models import Interface
from ipam.models import IPAddress
from netbox.forms import NetBoxModelForm
from tenancy.forms import TenancyForm
from utilities.forms.fields import CommentField, DynamicModelChoiceField
from virtualization.models import VMInterface
from vpn.models import *

__all__ = (
    'IPSecProfileForm',
    'TunnelForm',
    'TunnelTerminationForm',
)


class TunnelForm(TenancyForm, NetBoxModelForm):
    ipsec_profile = DynamicModelChoiceField(
        queryset=IPSecProfile.objects.all(),
        label=_('IPSec Profile')
    )
    comments = CommentField()

    fieldsets = (
        (_('Tunnel'), ('name', 'status', 'encapsulation', 'description', 'tunnel_id', 'tags')),
        (_('Security'), ('ipsec_profile', 'preshared_key')),
        (_('Tenancy'), ('tenant_group', 'tenant')),
    )

    class Meta:
        model = Tunnel
        fields = [
            'name', 'status', 'encapsulation', 'description', 'tunnel_id', 'ipsec_profile', 'preshared_key',
            'tenant_group', 'tenant', 'comments', 'tags',
        ]


class TunnelTerminationForm(NetBoxModelForm):
    tunnel = DynamicModelChoiceField(
        queryset=Tunnel.objects.all()
    )
    interface = DynamicModelChoiceField(
        label=_('Interface'),
        queryset=Interface.objects.all(),
        required=False,
        selector=True,
    )
    vminterface = DynamicModelChoiceField(
        queryset=VMInterface.objects.all(),
        required=False,
        selector=True,
        label=_('Interface'),
    )
    outside_ip = DynamicModelChoiceField(
        queryset=IPAddress.objects.all(),
        selector=True,
        label=_('Outside IP'),
    )

    class Meta:
        model = TunnelTermination
        fields = [
            'tunnel', 'role', 'outside_ip', 'tags',
        ]

    def __init__(self, *args, **kwargs):

        # Initialize helper selectors
        initial = kwargs.get('initial', {}).copy()
        if instance := kwargs.get('instance'):
            if type(instance.interface) is Interface:
                initial['interface'] = instance.interface
            elif type(instance.interface) is VMInterface:
                initial['vminterface'] = instance.interface
        kwargs['initial'] = initial

        super().__init__(*args, **kwargs)

    def clean(self):
        super().clean()

        # Handle interface assignment
        self.instance.interface = self.cleaned_data['interface'] or self.cleaned_data['interface'] or None


class IPSecProfileForm(NetBoxModelForm):
    comments = CommentField()

    fieldsets = (
        (_('Profile'), (
            'name', 'protocol', 'ike_version', 'description', 'tags',
        )),
        (_('Phase 1 Parameters'), (
            'phase1_encryption', 'phase1_authentication', 'phase1_group', 'phase1_sa_lifetime',
        )),
        (_('Phase 2 Parameters'), (
            'phase2_encryption', 'phase2_authentication', 'phase2_group', 'phase2_sa_lifetime',
            'phase2_sa_lifetime_data',
        )),
    )

    class Meta:
        model = IPSecProfile
        fields = [
            'name', 'protocol', 'ike_version', 'phase1_encryption', 'phase1_authentication', 'phase1_group',
            'phase1_sa_lifetime', 'phase2_encryption', 'phase2_authentication', 'phase2_group', 'phase2_sa_lifetime',
            'phase2_sa_lifetime_data', 'description', 'comments', 'tags',
        ]
