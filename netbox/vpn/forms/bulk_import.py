from django.utils.translation import gettext_lazy as _

from dcim.models import Device, Interface
from ipam.models import IPAddress
from netbox.forms import NetBoxModelImportForm
from tenancy.models import Tenant
from utilities.forms.fields import CSVChoiceField, CSVModelChoiceField
from virtualization.models import VirtualMachine, VMInterface
from vpn.choices import *
from vpn.models import *

__all__ = (
    'IPSecProfileImportForm',
    'TunnelImportForm',
    'TunnelTerminationImportForm',
)


class TunnelImportForm(NetBoxModelImportForm):
    status = CSVChoiceField(
        label=_('Status'),
        choices=TunnelStatusChoices,
        help_text=_('Operational status')
    )
    encapsulation = CSVChoiceField(
        label=_('Encapsulation'),
        choices=TunnelEncapsulationChoices,
        help_text=_('Tunnel encapsulation')
    )
    ipsec_profile = CSVModelChoiceField(
        label=_('IPSec profile'),
        queryset=IPSecProfile.objects.all(),
        to_field_name='name'
    )
    tenant = CSVModelChoiceField(
        label=_('Tenant'),
        queryset=Tenant.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Assigned tenant')
    )

    class Meta:
        model = Tunnel
        fields = (
            'name', 'status', 'encapsulation', 'ipsec_profile', 'tenant', 'preshared_key', 'tunnel_id', 'description',
            'comments', 'tags',
        )


class TunnelTerminationImportForm(NetBoxModelImportForm):
    tunnel = CSVModelChoiceField(
        label=_('Tunnel'),
        queryset=Tunnel.objects.all(),
        to_field_name='name'
    )
    role = CSVChoiceField(
        label=_('Role'),
        choices=TunnelTerminationRoleChoices,
        help_text=_('Operational role')
    )
    device = CSVModelChoiceField(
        label=_('Device'),
        queryset=Device.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Parent device of assigned interface')
    )
    virtual_machine = CSVModelChoiceField(
        label=_('Virtual machine'),
        queryset=VirtualMachine.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Parent VM of assigned interface')
    )
    interface = CSVModelChoiceField(
        label=_('Interface'),
        queryset=Interface.objects.none(),  # Can also refer to VMInterface
        required=False,
        to_field_name='name',
        help_text=_('Assigned interface')
    )
    outside_ip = CSVModelChoiceField(
        label=_('Outside IP'),
        queryset=IPAddress.objects.all(),
        to_field_name='name'
    )

    class Meta:
        model = TunnelTermination
        fields = (
            'tunnel', 'role', 'outside_ip', 'tags',
        )

    def __init__(self, data=None, *args, **kwargs):
        super().__init__(data, *args, **kwargs)

        if data:

            # Limit interface queryset by assigned device/VM
            if data.get('device'):
                self.fields['interface'].queryset = Interface.objects.filter(
                    **{f"device__{self.fields['device'].to_field_name}": data['device']}
                )
            elif data.get('virtual_machine'):
                self.fields['interface'].queryset = VMInterface.objects.filter(
                    **{f"virtual_machine__{self.fields['virtual_machine'].to_field_name}": data['virtual_machine']}
                )


class IPSecProfileImportForm(NetBoxModelImportForm):
    protocol = CSVChoiceField(
        label=_('Protocol'),
        choices=IPSecProtocolChoices,
        help_text=_('IPSec protocol')
    )
    ike_version = CSVChoiceField(
        label=_('IKE version'),
        choices=IKEVersionChoices,
        help_text=_('IKE version')
    )
    phase1_encryption = CSVChoiceField(
        label=_('Phase 1 Encryption'),
        choices=EncryptionChoices
    )
    phase1_authentication = CSVChoiceField(
        label=_('Phase 1 Authentication'),
        choices=AuthenticationChoices
    )
    phase1_group = CSVChoiceField(
        label=_('Phase 1 Group'),
        choices=DHGroupChoices
    )
    phase2_encryption = CSVChoiceField(
        label=_('Phase 2 Encryption'),
        choices=EncryptionChoices
    )
    phase2_authentication = CSVChoiceField(
        label=_('Phase 2 Authentication'),
        choices=AuthenticationChoices
    )
    phase2_group = CSVChoiceField(
        label=_('Phase 2 Group'),
        choices=DHGroupChoices
    )

    class Meta:
        model = IPSecProfile
        fields = (
            'name', 'protocol', 'ike_version', 'phase1_encryption', 'phase1_authentication', 'phase1_group',
            'phase1_sa_lifetime', 'phase1_encryption', 'phase1_authentication', 'phase1_group', 'phase1_sa_lifetime',
            'description', 'comments', 'tags',
        )
