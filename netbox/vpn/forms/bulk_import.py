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
    'IKEPolicyImportForm',
    'IKEProposalImportForm',
    'IPSecPolicyImportForm',
    'IPSecProfileImportForm',
    'IPSecProposalImportForm',
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
            'name', 'status', 'encapsulation', 'ipsec_profile', 'tenant', 'tunnel_id', 'description', 'comments',
            'tags',
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


class IKEProposalImportForm(NetBoxModelImportForm):
    authentication_method = CSVChoiceField(
        label=_('Authentication method'),
        choices=AuthenticationMethodChoices
    )
    encryption_algorithm = CSVChoiceField(
        label=_('Encryption algorithm'),
        choices=EncryptionAlgorithmChoices
    )
    authentication_algorithmn = CSVChoiceField(
        label=_('Authentication algorithm'),
        choices=AuthenticationAlgorithmChoices
    )
    group = CSVChoiceField(
        label=_('Group'),
        choices=DHGroupChoices
    )

    class Meta:
        model = IKEProposal
        fields = (
            'name', 'description', 'authentication_method', 'encryption_algorithm', 'authentication_algorithmn',
            'group', 'sa_lifetime', 'tags',
        )


class IKEPolicyImportForm(NetBoxModelImportForm):
    version = CSVChoiceField(
        label=_('Version'),
        choices=IKEVersionChoices
    )
    mode = CSVChoiceField(
        label=_('Mode'),
        choices=IKEModeChoices
    )
    # TODO: M2M field for proposals

    class Meta:
        model = IKEPolicy
        fields = (
            'name', 'description', 'version', 'mode', 'proposals', 'preshared_key', 'certificate', 'tags',
        )


class IPSecProposalImportForm(NetBoxModelImportForm):
    authentication_method = CSVChoiceField(
        label=_('Authentication method'),
        choices=AuthenticationMethodChoices
    )
    encryption_algorithm = CSVChoiceField(
        label=_('Encryption algorithm'),
        choices=EncryptionAlgorithmChoices
    )
    authentication_algorithmn = CSVChoiceField(
        label=_('Authentication algorithm'),
        choices=AuthenticationAlgorithmChoices
    )
    group = CSVChoiceField(
        label=_('Group'),
        choices=DHGroupChoices
    )

    class Meta:
        model = IPSecProposal
        fields = (
            'name', 'description', 'encryption_algorithm', 'authentication_algorithmn', 'sa_lifetime_seconds',
            'sa_lifetime_data', 'tags',
        )


class IPSecPolicyImportForm(NetBoxModelImportForm):
    pfs_group = CSVChoiceField(
        label=_('PFS group'),
        choices=DHGroupChoices
    )
    # TODO: M2M field for proposals

    class Meta:
        model = IPSecPolicy
        fields = (
            'name', 'description', 'proposals', 'pfs_group', 'tags',
        )


class IPSecProfileImportForm(NetBoxModelImportForm):
    mode = CSVChoiceField(
        label=_('Mode'),
        choices=IPSecModeChoices,
        help_text=_('IPSec protocol')
    )
    ike_policy = CSVModelChoiceField(
        label=_('IKE policy'),
        queryset=IKEPolicy.objects.all(),
        to_field_name='name'
    )
    ipsec_policy = CSVModelChoiceField(
        label=_('IPSec policy'),
        queryset=IPSecPolicy.objects.all(),
        to_field_name='name'
    )

    class Meta:
        model = IPSecProfile
        fields = (
            'name', 'ike_policy', 'ipsec_policy', 'description', 'comments', 'tags',
        )
