from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from dcim.models import Device, Interface
from ipam.models import IPAddress, RouteTarget, VLAN
from netbox.forms import NetBoxModelForm
from tenancy.forms import TenancyForm
from utilities.forms.fields import CommentField, DynamicModelChoiceField, DynamicModelMultipleChoiceField, SlugField
from utilities.forms.utils import add_blank_choice, get_field_value
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
    'L2VPNForm',
    'L2VPNTerminationForm',
    'TunnelCreateForm',
    'TunnelForm',
    'TunnelGroupForm',
    'TunnelTerminationForm',
)


class TunnelGroupForm(NetBoxModelForm):
    slug = SlugField()

    fieldsets = (
        (_('Tunnel Group'), ('name', 'slug', 'description', 'tags')),
    )

    class Meta:
        model = TunnelGroup
        fields = [
            'name', 'slug', 'description', 'tags',
        ]


class TunnelForm(TenancyForm, NetBoxModelForm):
    group = DynamicModelChoiceField(
        queryset=TunnelGroup.objects.all(),
        label=_('Tunnel Group'),
        required=False
    )
    ipsec_profile = DynamicModelChoiceField(
        queryset=IPSecProfile.objects.all(),
        label=_('IPSec Profile'),
        required=False
    )
    comments = CommentField()

    fieldsets = (
        (_('Tunnel'), ('name', 'status', 'group', 'encapsulation', 'description', 'tunnel_id', 'tags')),
        (_('Security'), ('ipsec_profile',)),
        (_('Tenancy'), ('tenant_group', 'tenant')),
    )

    class Meta:
        model = Tunnel
        fields = [
            'name', 'status', 'group', 'encapsulation', 'description', 'tunnel_id', 'ipsec_profile', 'tenant_group',
            'tenant', 'comments', 'tags',
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
    termination1_termination = DynamicModelChoiceField(
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
    termination2_termination = DynamicModelChoiceField(
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
        (_('Tunnel'), ('name', 'status', 'group', 'encapsulation', 'description', 'tunnel_id', 'tags')),
        (_('Security'), ('ipsec_profile',)),
        (_('Tenancy'), ('tenant_group', 'tenant')),
        (_('First Termination'), (
            'termination1_role', 'termination1_type', 'termination1_parent', 'termination1_termination',
            'termination1_outside_ip',
        )),
        (_('Second Termination'), (
            'termination2_role', 'termination2_type', 'termination2_parent', 'termination2_termination',
            'termination2_outside_ip',
        )),
    )

    def __init__(self, *args, initial=None, **kwargs):
        super().__init__(*args, initial=initial, **kwargs)

        if get_field_value(self, 'termination1_type') == TunnelTerminationTypeChoices.TYPE_VIRTUALMACHINE:
            self.fields['termination1_parent'].label = _('Virtual Machine')
            self.fields['termination1_parent'].queryset = VirtualMachine.objects.all()
            self.fields['termination1_termination'].queryset = VMInterface.objects.all()
            self.fields['termination1_termination'].widget.add_query_params({
                'virtual_machine_id': '$termination1_parent',
            })
            self.fields['termination1_outside_ip'].widget.add_query_params({
                'virtual_machine_id': '$termination1_parent',
            })

        if get_field_value(self, 'termination2_type') == TunnelTerminationTypeChoices.TYPE_VIRTUALMACHINE:
            self.fields['termination2_parent'].label = _('Virtual Machine')
            self.fields['termination2_parent'].queryset = VirtualMachine.objects.all()
            self.fields['termination2_termination'].queryset = VMInterface.objects.all()
            self.fields['termination2_termination'].widget.add_query_params({
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
                f'{term}_role', f'{term}_parent', f'{term}_termination',
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
        if self.cleaned_data['termination1_termination']:
            TunnelTermination.objects.create(
                tunnel=instance,
                role=self.cleaned_data['termination1_role'],
                termination=self.cleaned_data['termination1_termination'],
                outside_ip=self.cleaned_data['termination1_outside_ip'],
            )

        # Create second termination, if defined
        if self.cleaned_data['termination2_termination']:
            TunnelTermination.objects.create(
                tunnel=instance,
                role=self.cleaned_data['termination2_role'],
                termination=self.cleaned_data['termination2_termination'],
                outside_ip=self.cleaned_data.get('termination2_outside_ip'),
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
    termination = DynamicModelChoiceField(
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
        (None, ('tunnel', 'role', 'type', 'parent', 'termination', 'outside_ip', 'tags')),
    )

    class Meta:
        model = TunnelTermination
        fields = [
            'tunnel', 'role', 'termination', 'outside_ip', 'tags',
        ]

    def __init__(self, *args, initial=None, **kwargs):
        super().__init__(*args, initial=initial, **kwargs)

        if (get_field_value(self, 'type') is None and
                self.instance.pk and isinstance(self.instance.termination.parent_object, VirtualMachine)):
            self.fields['type'].initial = TunnelTerminationTypeChoices.TYPE_VIRTUALMACHINE

        # If initial or self.data is set and the type is a VIRTUALMACHINE type, swap the field querysets.
        if get_field_value(self, 'type') == TunnelTerminationTypeChoices.TYPE_VIRTUALMACHINE:
            self.fields['parent'].label = _('Virtual Machine')
            self.fields['parent'].queryset = VirtualMachine.objects.all()
            self.fields['parent'].widget.attrs['selector'] = 'virtualization.virtualmachine'
            self.fields['termination'].queryset = VMInterface.objects.all()
            self.fields['termination'].widget.add_query_params({
                'virtual_machine_id': '$parent',
            })
            self.fields['outside_ip'].widget.add_query_params({
                'virtual_machine_id': '$parent',
            })

        if self.instance.pk:
            self.fields['parent'].initial = self.instance.termination.parent_object
            self.fields['termination'].initial = self.instance.termination

    def clean(self):
        super().clean()

        # Set the terminated object
        self.instance.termination = self.cleaned_data.get('termination')


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
            'sa_lifetime', 'comments', 'tags',
        ]


class IKEPolicyForm(NetBoxModelForm):
    proposals = DynamicModelMultipleChoiceField(
        queryset=IKEProposal.objects.all(),
        label=_('Proposals')
    )

    fieldsets = (
        (_('Policy'), ('name', 'description', 'tags')),
        (_('Parameters'), ('version', 'mode', 'proposals', 'preshared_key')),
    )

    class Meta:
        model = IKEPolicy
        fields = [
            'name', 'description', 'version', 'mode', 'proposals', 'preshared_key', 'comments', 'tags',
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
            'sa_lifetime_data', 'comments', 'tags',
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
            'name', 'description', 'proposals', 'pfs_group', 'comments', 'tags',
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


#
# L2VPN
#

class L2VPNForm(TenancyForm, NetBoxModelForm):
    slug = SlugField()
    import_targets = DynamicModelMultipleChoiceField(
        label=_('Import targets'),
        queryset=RouteTarget.objects.all(),
        required=False
    )
    export_targets = DynamicModelMultipleChoiceField(
        label=_('Export targets'),
        queryset=RouteTarget.objects.all(),
        required=False
    )
    comments = CommentField()

    fieldsets = (
        (_('L2VPN'), ('name', 'slug', 'type', 'identifier', 'description', 'tags')),
        (_('Route Targets'), ('import_targets', 'export_targets')),
        (_('Tenancy'), ('tenant_group', 'tenant')),
    )

    class Meta:
        model = L2VPN
        fields = (
            'name', 'slug', 'type', 'identifier', 'import_targets', 'export_targets', 'tenant', 'description',
            'comments', 'tags'
        )


class L2VPNTerminationForm(NetBoxModelForm):
    l2vpn = DynamicModelChoiceField(
        queryset=L2VPN.objects.all(),
        required=True,
        query_params={},
        label=_('L2VPN'),
        fetch_trigger='open'
    )
    vlan = DynamicModelChoiceField(
        queryset=VLAN.objects.all(),
        required=False,
        selector=True,
        label=_('VLAN')
    )
    interface = DynamicModelChoiceField(
        label=_('Interface'),
        queryset=Interface.objects.all(),
        required=False,
        selector=True
    )
    vminterface = DynamicModelChoiceField(
        queryset=VMInterface.objects.all(),
        required=False,
        selector=True,
        label=_('Interface')
    )

    class Meta:
        model = L2VPNTermination
        fields = ('l2vpn', 'tags')

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        initial = kwargs.get('initial', {}).copy()

        if instance:
            if type(instance.assigned_object) is Interface:
                initial['interface'] = instance.assigned_object
            elif type(instance.assigned_object) is VLAN:
                initial['vlan'] = instance.assigned_object
            elif type(instance.assigned_object) is VMInterface:
                initial['vminterface'] = instance.assigned_object
            kwargs['initial'] = initial

        super().__init__(*args, **kwargs)

    def clean(self):
        super().clean()

        interface = self.cleaned_data.get('interface')
        vminterface = self.cleaned_data.get('vminterface')
        vlan = self.cleaned_data.get('vlan')

        if not (interface or vminterface or vlan):
            raise ValidationError(_('A termination must specify an interface or VLAN.'))
        if len([x for x in (interface, vminterface, vlan) if x]) > 1:
            raise ValidationError(_('A termination can only have one terminating object (an interface or VLAN).'))

        self.instance.assigned_object = interface or vminterface or vlan
