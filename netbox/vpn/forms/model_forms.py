from django import forms
from django.utils.translation import gettext_lazy as _

from dcim.models import Device, Interface
from ipam.models import IPAddress
from netbox.forms import NetBoxModelForm
from tenancy.forms import TenancyForm
from utilities.forms.fields import CommentField, DynamicModelChoiceField, DynamicModelMultipleChoiceField
from utilities.forms.utils import add_blank_choice
from utilities.forms.widgets import HTMXSelect
from virtualization.models import VirtualMachine, VMInterface
from vpn.choices import *
from vpn.models import *

__all__ = (
    'IKEPolicyForm',
    'IKEProposalForm',
    'IPSecPolicyForm',
    'IPSecProfileForm',
    'IPSecProposalForm',
    'TunnelCreateForm',
    'TunnelForm',
    'TunnelTerminationForm',
)


class TunnelForm(TenancyForm, NetBoxModelForm):
    ipsec_profile = DynamicModelChoiceField(
        queryset=IPSecProfile.objects.all(),
        label=_('IPSec Profile'),
        required=False
    )
    comments = CommentField()

    fieldsets = (
        (_('Tunnel'), ('name', 'status', 'encapsulation', 'description', 'tunnel_id', 'tags')),
        (_('Security'), ('ipsec_profile',)),
        (_('Tenancy'), ('tenant_group', 'tenant')),
    )

    class Meta:
        model = Tunnel
        fields = [
            'name', 'status', 'encapsulation', 'description', 'tunnel_id', 'ipsec_profile', 'tenant_group', 'tenant',
            'comments', 'tags',
        ]


class TunnelCreateForm(TunnelForm):
    # First termination
    termination1_role = forms.ChoiceField(
        choices=add_blank_choice(TunnelTerminationRoleChoices),
        required=False,
        label=_('Role')
    )
    termination1_type = forms.ChoiceField(
        choices=TunnelTerminationTypeChoices,
        required=False,
        widget=HTMXSelect(),
        label=_('Type')
    )
    termination1_parent = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        required=False,
        selector=True,
        label=_('Device')
    )
    termination1_interface = DynamicModelChoiceField(
        queryset=Interface.objects.all(),
        required=False,
        label=_('Interface'),
        query_params={
            'device_id': '$termination1_parent',
        }
    )
    termination1_outside_ip = DynamicModelChoiceField(
        queryset=IPAddress.objects.all(),
        label=_('Outside IP'),
        required=False,
        query_params={
            'device_id': '$termination1_parent',
        }
    )

    # Second termination
    termination2_role = forms.ChoiceField(
        choices=add_blank_choice(TunnelTerminationRoleChoices),
        required=False,
        label=_('Role')
    )
    termination2_type = forms.ChoiceField(
        choices=TunnelTerminationTypeChoices,
        required=False,
        widget=HTMXSelect(),
        label=_('Type')
    )
    termination2_parent = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        required=False,
        selector=True,
        label=_('Device')
    )
    termination2_interface = DynamicModelChoiceField(
        queryset=Interface.objects.all(),
        required=False,
        label=_('Interface'),
        query_params={
            'device_id': '$termination2_parent',
        }
    )
    termination2_outside_ip = DynamicModelChoiceField(
        queryset=IPAddress.objects.all(),
        required=False,
        label=_('Outside IP'),
        query_params={
            'device_id': '$termination2_parent',
        }
    )

    fieldsets = (
        (_('Tunnel'), ('name', 'status', 'encapsulation', 'description', 'tunnel_id', 'tags')),
        (_('Security'), ('ipsec_profile',)),
        (_('Tenancy'), ('tenant_group', 'tenant')),
        (_('First Termination'), (
            'termination1_role', 'termination1_type', 'termination1_parent', 'termination1_interface',
            'termination1_outside_ip',
        )),
        (_('Second Termination'), (
            'termination2_role', 'termination2_type', 'termination2_parent', 'termination2_interface',
            'termination2_outside_ip',
        )),
    )

    def __init__(self, *args, initial=None, **kwargs):
        super().__init__(*args, initial=initial, **kwargs)

        if initial and initial.get('termination1_type') == TunnelTerminationTypeChoices.TYPE_VIRUTALMACHINE:
            self.fields['termination1_parent'].label = _('Virtual Machine')
            self.fields['termination1_parent'].queryset = VirtualMachine.objects.all()
            self.fields['termination1_interface'].queryset = VMInterface.objects.all()
            self.fields['termination1_interface'].widget.add_query_params({
                'virtual_machine_id': '$termination1_parent',
            })
            self.fields['termination1_outside_ip'].widget.add_query_params({
                'virtual_machine_id': '$termination1_parent',
            })

        if initial and initial.get('termination2_type') == TunnelTerminationTypeChoices.TYPE_VIRUTALMACHINE:
            self.fields['termination2_parent'].label = _('Virtual Machine')
            self.fields['termination2_parent'].queryset = VirtualMachine.objects.all()
            self.fields['termination2_interface'].queryset = VMInterface.objects.all()
            self.fields['termination2_interface'].widget.add_query_params({
                'virtual_machine_id': '$termination2_parent',
            })
            self.fields['termination2_outside_ip'].widget.add_query_params({
                'virtual_machine_id': '$termination2_parent',
            })

    def clean(self):
        super().clean()

        # Validate attributes for each termination (if any)
        for term in ('termination1', 'termination2'):
            required_parameters = (
                f'{term}_role', f'{term}_parent', f'{term}_interface',
            )
            parameters = (
                *required_parameters,
                f'{term}_outside_ip',
            )
        if any([self.cleaned_data[param] for param in parameters]):
            for param in required_parameters:
                if not self.cleaned_data[param]:
                    raise forms.ValidationError({
                        param: _("This parameter is required when defining a termination.")
                    })

    def save(self, *args, **kwargs):
        instance = super().save(*args, **kwargs)

        # Create first termination
        if self.cleaned_data['termination1_interface']:
            TunnelTermination.objects.create(
                tunnel=instance,
                role=self.cleaned_data['termination1_role'],
                interface=self.cleaned_data['termination1_interface'],
                outside_ip=self.cleaned_data['termination1_outside_ip'],
            )

        # Create second termination, if defined
        if self.cleaned_data['termination2_interface']:
            TunnelTermination.objects.create(
                tunnel=instance,
                role=self.cleaned_data['termination2_role'],
                interface=self.cleaned_data['termination2_interface'],
                outside_ip=self.cleaned_data.get('termination1_outside_ip'),
            )

        return instance


class TunnelTerminationForm(NetBoxModelForm):
    tunnel = DynamicModelChoiceField(
        queryset=Tunnel.objects.all()
    )
    type = forms.ChoiceField(
        choices=TunnelTerminationTypeChoices,
        widget=HTMXSelect(),
        label=_('Type')
    )
    parent = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        selector=True,
        label=_('Device')
    )
    interface = DynamicModelChoiceField(
        queryset=Interface.objects.all(),
        label=_('Interface'),
        query_params={
            'device_id': '$parent',
        }
    )
    outside_ip = DynamicModelChoiceField(
        queryset=IPAddress.objects.all(),
        label=_('Outside IP'),
        required=False,
        query_params={
            'device_id': '$parent',
        }
    )

    fieldsets = (
        (None, ('tunnel', 'role', 'type', 'parent', 'interface', 'outside_ip', 'tags')),
    )

    class Meta:
        model = TunnelTermination
        fields = [
            'tunnel', 'role', 'interface', 'outside_ip', 'tags',
        ]

    def __init__(self, *args, initial=None, **kwargs):
        super().__init__(*args, initial=initial, **kwargs)

        if initial and initial.get('type') == TunnelTerminationTypeChoices.TYPE_VIRUTALMACHINE:
            self.fields['parent'].label = _('Virtual Machine')
            self.fields['parent'].queryset = VirtualMachine.objects.all()
            self.fields['interface'].queryset = VMInterface.objects.all()
            self.fields['interface'].widget.add_query_params({
                'virtual_machine_id': '$parent',
            })
            self.fields['outside_ip'].widget.add_query_params({
                'virtual_machine_id': '$parent',
            })

        if self.instance.pk:
            self.fields['parent'].initial = self.instance.interface.parent_object
            self.fields['interface'].initial = self.instance.interface

    def clean(self):
        super().clean()

        # Assign the interface
        self.instance.interface = self.cleaned_data.get('interface')


class IKEProposalForm(NetBoxModelForm):

    fieldsets = (
        (_('Proposal'), ('name', 'description', 'tags')),
        (_('Parameters'), (
            'authentication_method', 'encryption_algorithm', 'authentication_algorithm', 'group', 'sa_lifetime',
        )),
    )

    class Meta:
        model = IKEProposal
        fields = [
            'name', 'description', 'authentication_method', 'encryption_algorithm', 'authentication_algorithm', 'group',
            'sa_lifetime', 'tags',
        ]


class IKEPolicyForm(NetBoxModelForm):
    proposals = DynamicModelMultipleChoiceField(
        queryset=IKEProposal.objects.all(),
        label=_('Proposals')
    )

    fieldsets = (
        (_('Policy'), ('name', 'description', 'tags')),
        (_('Parameters'), ('version', 'mode', 'proposals')),
        (_('Authentication'), ('preshared_key', 'certificate')),
    )

    class Meta:
        model = IKEPolicy
        fields = [
            'name', 'description', 'version', 'mode', 'proposals', 'preshared_key', 'certificate', 'tags',
        ]


class IPSecProposalForm(NetBoxModelForm):

    fieldsets = (
        (_('Proposal'), ('name', 'description', 'tags')),
        (_('Parameters'), (
            'encryption_algorithm', 'authentication_algorithm', 'sa_lifetime_seconds', 'sa_lifetime_data',
        )),
    )

    class Meta:
        model = IPSecProposal
        fields = [
            'name', 'description', 'encryption_algorithm', 'authentication_algorithm', 'sa_lifetime_seconds',
            'sa_lifetime_data', 'tags',
        ]


class IPSecPolicyForm(NetBoxModelForm):
    proposals = DynamicModelMultipleChoiceField(
        queryset=IPSecProposal.objects.all(),
        label=_('Proposals')
    )

    fieldsets = (
        (_('Policy'), ('name', 'description', 'tags')),
        (_('Parameters'), ('proposals', 'pfs_group')),
    )

    class Meta:
        model = IPSecPolicy
        fields = [
            'name', 'description', 'proposals', 'pfs_group', 'tags',
        ]


class IPSecProfileForm(NetBoxModelForm):
    ike_policy = DynamicModelChoiceField(
        queryset=IKEPolicy.objects.all(),
        label=_('IKE policy')
    )
    ipsec_policy = DynamicModelChoiceField(
        queryset=IPSecPolicy.objects.all(),
        label=_('IPSec policy')
    )
    comments = CommentField()

    fieldsets = (
        (_('Profile'), ('name', 'description', 'tags')),
        (_('Parameters'), ('mode', 'ike_policy', 'ipsec_policy')),
    )

    class Meta:
        model = IPSecProfile
        fields = [
            'name', 'description', 'mode', 'ike_policy', 'ipsec_policy', 'description', 'comments', 'tags',
        ]
