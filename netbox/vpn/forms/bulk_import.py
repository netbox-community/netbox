from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from dcim.models import Device, Interface
from ipam.models import IPAddress, VLAN
from netbox.forms import NetBoxModelImportForm
from tenancy.models import Tenant
from utilities.forms.fields import CSVChoiceField, CSVModelChoiceField, CSVModelMultipleChoiceField, SlugField
from virtualization.models import VirtualMachine, VMInterface
from vpn.choices import *
from vpn.models import *

__all__ = (
    'IKEPolicyImportForm',
    'IKEProposalImportForm',
    'IPSecPolicyImportForm',
    'IPSecProfileImportForm',
    'IPSecProposalImportForm',
    'L2VPNImportForm',
    'L2VPNTerminationImportForm',
    'TunnelImportForm',
    'TunnelGroupImportForm',
    'TunnelTerminationImportForm',
)


class TunnelGroupImportForm(NetBoxModelImportForm):
    slug = SlugField()

    class Meta:
        model = TunnelGroup
        fields = ('name', 'slug', 'description', 'tags')


class TunnelImportForm(NetBoxModelImportForm):
    status = CSVChoiceField(
        label=_('Status'),
        choices=TunnelStatusChoices,
        help_text=_('Operational status')
    )
    group = CSVModelChoiceField(
        label=_('Tunnel group'),
        queryset=TunnelGroup.objects.all(),
        required=False,
        to_field_name='name'
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
            'name', 'status', 'group', 'encapsulation', 'ipsec_profile', 'tenant', 'tunnel_id', 'description',
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
            'group', 'sa_lifetime', 'comments', 'tags',
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
            'name', 'description', 'version', 'mode', 'proposals', 'preshared_key', 'comments', 'tags',
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
            'sa_lifetime_data', 'comments', 'tags',
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
            'name', 'description', 'proposals', 'pfs_group', 'comments', 'tags',
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


class L2VPNImportForm(NetBoxModelImportForm):
    tenant = CSVModelChoiceField(
        label=_('Tenant'),
        queryset=Tenant.objects.all(),
        required=False,
        to_field_name='name',
    )
    type = CSVChoiceField(
        label=_('Type'),
        choices=L2VPNTypeChoices,
        help_text=_('L2VPN type')
    )

    class Meta:
        model = L2VPN
        fields = ('identifier', 'name', 'slug', 'tenant', 'type', 'description',
                  'comments', 'tags')


class L2VPNTerminationImportForm(NetBoxModelImportForm):
    l2vpn = CSVModelChoiceField(
        queryset=L2VPN.objects.all(),
        required=True,
        to_field_name='name',
        label=_('L2VPN'),
    )
    device = CSVModelChoiceField(
        label=_('Device'),
        queryset=Device.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Parent device (for interface)')
    )
    virtual_machine = CSVModelChoiceField(
        label=_('Virtual machine'),
        queryset=VirtualMachine.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Parent virtual machine (for interface)')
    )
    interface = CSVModelChoiceField(
        label=_('Interface'),
        queryset=Interface.objects.none(),  # Can also refer to VMInterface
        required=False,
        to_field_name='name',
        help_text=_('Assigned interface (device or VM)')
    )
    vlan = CSVModelChoiceField(
        label=_('VLAN'),
        queryset=VLAN.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Assigned VLAN')
    )

    class Meta:
        model = L2VPNTermination
        fields = ('l2vpn', 'device', 'virtual_machine', 'interface', 'vlan', 'tags')

    def __init__(self, data=None, *args, **kwargs):
        super().__init__(data, *args, **kwargs)

        if data:

            # Limit interface queryset by device or VM
            if data.get('device'):
                self.fields['interface'].queryset = Interface.objects.filter(
                    **{f"device__{self.fields['device'].to_field_name}": data['device']}
                )
            elif data.get('virtual_machine'):
                self.fields['interface'].queryset = VMInterface.objects.filter(
                    **{f"virtual_machine__{self.fields['virtual_machine'].to_field_name}": data['virtual_machine']}
                )

    def clean(self):
        super().clean()

        if self.cleaned_data.get('device') and self.cleaned_data.get('virtual_machine'):
            raise ValidationError(_('Cannot import device and VM interface terminations simultaneously.'))
        if not self.instance and not (self.cleaned_data.get('interface') or self.cleaned_data.get('vlan')):
            raise ValidationError(_('Each termination must specify either an interface or a VLAN.'))
        if self.cleaned_data.get('interface') and self.cleaned_data.get('vlan'):
            raise ValidationError(_('Cannot assign both an interface and a VLAN.'))

        # if this is an update we might not have interface or vlan in the form data
        if self.cleaned_data.get('interface') or self.cleaned_data.get('vlan'):
            self.instance.assigned_object = self.cleaned_data.get('interface') or self.cleaned_data.get('vlan')
