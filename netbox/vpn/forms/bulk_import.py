from django.utils.translation import gettext_lazy as _

from dcim.models import Device, Interface
from ipam.models import IPAddress
from netbox.forms import NetBoxModelImportForm
from tenancy.models import Tenant
from utilities.forms.fields import CSVChoiceField, CSVModelChoiceField, CSVModelMultipleChoiceField
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
        required=False,
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
    termination = CSVModelChoiceField(
        label=_('Termination'),
        queryset=Interface.objects.none(),  # Can also refer to VMInterface
        required=False,
        to_field_name='name',
        help_text=_('Device or virtual machine interface')
    )
    outside_ip = CSVModelChoiceField(
        label=_('Outside IP'),
        queryset=IPAddress.objects.all(),
        required=False,
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

            # Limit termination queryset by assigned device/VM
            if data.get('device'):
                self.fields['termination'].queryset = Interface.objects.filter(
                    **{f"device__{self.fields['device'].to_field_name}": data['device']}
                )
            elif data.get('virtual_machine'):
                self.fields['termination'].queryset = VMInterface.objects.filter(
                    **{f"virtual_machine__{self.fields['virtual_machine'].to_field_name}": data['virtual_machine']}
                )

    def save(self, *args, **kwargs):

        # Assign termination object
        if self.cleaned_data.get('termination'):
            self.instance.termination = self.cleaned_data['termination']

        return super().save(*args, **kwargs)


class IKEProposalImportForm(NetBoxModelImportForm):
    authentication_method = CSVChoiceField(
        label=_('Authentication method'),
        choices=AuthenticationMethodChoices
    )
    encryption_algorithm = CSVChoiceField(
        label=_('Encryption algorithm'),
        choices=EncryptionAlgorithmChoices
    )
    authentication_algorithm = CSVChoiceField(
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
            'name', 'description', 'authentication_method', 'encryption_algorithm', 'authentication_algorithm',
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
    proposals = CSVModelMultipleChoiceField(
        queryset=IKEProposal.objects.all(),
        to_field_name='name',
        help_text=_('IKE proposal(s)'),
    )

    class Meta:
        model = IKEPolicy
        fields = (
            'name', 'description', 'version', 'mode', 'proposals', 'preshared_key', 'tags',
        )


class IPSecProposalImportForm(NetBoxModelImportForm):
    encryption_algorithm = CSVChoiceField(
        label=_('Encryption algorithm'),
        choices=EncryptionAlgorithmChoices
    )
    authentication_algorithm = CSVChoiceField(
        label=_('Authentication algorithm'),
        choices=AuthenticationAlgorithmChoices
    )

    class Meta:
        model = IPSecProposal
        fields = (
            'name', 'description', 'encryption_algorithm', 'authentication_algorithm', 'sa_lifetime_seconds',
            'sa_lifetime_data', 'tags',
        )


class IPSecPolicyImportForm(NetBoxModelImportForm):
    pfs_group = CSVChoiceField(
        label=_('Diffie-Hellman group for Perfect Forward Secrecy'),
        choices=DHGroupChoices
    )
    proposals = CSVModelMultipleChoiceField(
        queryset=IPSecProposal.objects.all(),
        to_field_name='name',
        help_text=_('IPSec proposal(s)'),
    )

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
            'name', 'mode', 'ike_policy', 'ipsec_policy', 'description', 'comments', 'tags',
        )
