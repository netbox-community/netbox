from django import forms
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext as _

from dcim.models import Device, Region, Site
from ipam.models import RouteTarget, VLAN
from netbox.forms import NetBoxModelFilterSetForm
from tenancy.forms import TenancyFilterForm
from utilities.forms.fields import (
    ContentTypeMultipleChoiceField, DynamicModelChoiceField, DynamicModelMultipleChoiceField, TagFilterField,
)
from utilities.forms.utils import add_blank_choice
from virtualization.models import VirtualMachine
from vpn.choices import *
from vpn.constants import L2VPN_ASSIGNMENT_MODELS
from vpn.models import *

__all__ = (
    'IKEPolicyFilterForm',
    'IKEProposalFilterForm',
    'IPSecPolicyFilterForm',
    'IPSecProfileFilterForm',
    'IPSecProposalFilterForm',
    'L2VPNFilterForm',
    'L2VPNTerminationFilterForm',
    'TunnelFilterForm',
    'TunnelGroupFilterForm',
    'TunnelTerminationFilterForm',
)


class TunnelGroupFilterForm(NetBoxModelFilterSetForm):
    model = TunnelGroup
    tag = TagFilterField(model)


class TunnelFilterForm(TenancyFilterForm, NetBoxModelFilterSetForm):
    model = Tunnel
    fieldsets = (
        (None, ('q', 'filter_id', 'tag')),
        (_('Tunnel'), ('status', 'encapsulation', 'tunnel_id')),
        (_('Security'), ('ipsec_profile_id',)),
        (_('Tenancy'), ('tenant_group_id', 'tenant_id')),
    )
    status = forms.MultipleChoiceField(
        label=_('Status'),
        choices=TunnelStatusChoices,
        required=False
    )
    group_id = DynamicModelMultipleChoiceField(
        queryset=TunnelGroup.objects.all(),
        required=False,
        label=_('Tunnel group')
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
    tunnel_id = forms.IntegerField(
        required=False,
        label=_('Tunnel ID')
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


class IKEProposalFilterForm(NetBoxModelFilterSetForm):
    model = IKEProposal
    fieldsets = (
        (None, ('q', 'filter_id', 'tag')),
        (_('Parameters'), ('authentication_method', 'encryption_algorithm', 'authentication_algorithm', 'group')),
    )
    authentication_method = forms.MultipleChoiceField(
        label=_('Authentication method'),
        choices=AuthenticationMethodChoices,
        required=False
    )
    encryption_algorithm = forms.MultipleChoiceField(
        label=_('Encryption algorithm'),
        choices=EncryptionAlgorithmChoices,
        required=False
    )
    authentication_algorithm = forms.MultipleChoiceField(
        label=_('Authentication algorithm'),
        choices=AuthenticationAlgorithmChoices,
        required=False
    )
    group = forms.MultipleChoiceField(
        label=_('Group'),
        choices=DHGroupChoices,
        required=False
    )
    tag = TagFilterField(model)


class IKEPolicyFilterForm(NetBoxModelFilterSetForm):
    model = IKEPolicy
    fieldsets = (
        (None, ('q', 'filter_id', 'tag')),
        (_('Parameters'), ('version', 'mode', 'proposal_id')),
    )
    version = forms.MultipleChoiceField(
        label=_('IKE version'),
        choices=IKEVersionChoices,
        required=False
    )
    mode = forms.MultipleChoiceField(
        label=_('Mode'),
        choices=IKEModeChoices,
        required=False
    )
    proposal_id = DynamicModelMultipleChoiceField(
        queryset=IKEProposal.objects.all(),
        required=False,
        label=_('Proposal')
    )
    tag = TagFilterField(model)


class IPSecProposalFilterForm(NetBoxModelFilterSetForm):
    model = IPSecProposal
    fieldsets = (
        (None, ('q', 'filter_id', 'tag')),
        (_('Parameters'), ('encryption_algorithm', 'authentication_algorithm')),
    )
    encryption_algorithm = forms.MultipleChoiceField(
        label=_('Encryption algorithm'),
        choices=EncryptionAlgorithmChoices,
        required=False
    )
    authentication_algorithm = forms.MultipleChoiceField(
        label=_('Authentication algorithm'),
        choices=AuthenticationAlgorithmChoices,
        required=False
    )
    tag = TagFilterField(model)


class IPSecPolicyFilterForm(NetBoxModelFilterSetForm):
    model = IPSecPolicy
    fieldsets = (
        (None, ('q', 'filter_id', 'tag')),
        (_('Parameters'), ('proposal_id', 'pfs_group')),
    )
    proposal_id = DynamicModelMultipleChoiceField(
        queryset=IKEProposal.objects.all(),
        required=False,
        label=_('Proposal')
    )
    pfs_group = forms.MultipleChoiceField(
        label=_('Mode'),
        choices=DHGroupChoices,
        required=False
    )
    tag = TagFilterField(model)


class IPSecProfileFilterForm(NetBoxModelFilterSetForm):
    model = IPSecProfile
    fieldsets = (
        (None, ('q', 'filter_id', 'tag')),
        (_('Profile'), ('mode', 'ike_policy_id', 'ipsec_policy_id')),
    )
    mode = forms.MultipleChoiceField(
        label=_('Mode'),
        choices=IPSecModeChoices,
        required=False
    )
    ike_policy_id = DynamicModelMultipleChoiceField(
        queryset=IKEPolicy.objects.all(),
        required=False,
        label=_('IKE policy')
    )
    ipsec_policy_id = DynamicModelMultipleChoiceField(
        queryset=IPSecPolicy.objects.all(),
        required=False,
        label=_('IPSec policy')
    )
    tag = TagFilterField(model)


class L2VPNFilterForm(TenancyFilterForm, NetBoxModelFilterSetForm):
    model = L2VPN
    fieldsets = (
        (None, ('q', 'filter_id', 'tag')),
        (_('Attributes'), ('type', 'import_target_id', 'export_target_id')),
        (_('Tenant'), ('tenant_group_id', 'tenant_id')),
    )
    type = forms.ChoiceField(
        label=_('Type'),
        choices=add_blank_choice(L2VPNTypeChoices),
        required=False
    )
    import_target_id = DynamicModelMultipleChoiceField(
        queryset=RouteTarget.objects.all(),
        required=False,
        label=_('Import targets')
    )
    export_target_id = DynamicModelMultipleChoiceField(
        queryset=RouteTarget.objects.all(),
        required=False,
        label=_('Export targets')
    )
    tag = TagFilterField(model)


class L2VPNTerminationFilterForm(NetBoxModelFilterSetForm):
    model = L2VPNTermination
    fieldsets = (
        (None, ('filter_id', 'l2vpn_id',)),
        (_('Assigned Object'), (
            'assigned_object_type_id', 'region_id', 'site_id', 'device_id', 'virtual_machine_id', 'vlan_id',
        )),
    )
    l2vpn_id = DynamicModelChoiceField(
        queryset=L2VPN.objects.all(),
        required=False,
        label=_('L2VPN')
    )
    assigned_object_type_id = ContentTypeMultipleChoiceField(
        queryset=ContentType.objects.filter(L2VPN_ASSIGNMENT_MODELS),
        required=False,
        label=_('Assigned Object Type'),
        limit_choices_to=L2VPN_ASSIGNMENT_MODELS
    )
    region_id = DynamicModelMultipleChoiceField(
        queryset=Region.objects.all(),
        required=False,
        label=_('Region')
    )
    site_id = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        null_option='None',
        query_params={
            'region_id': '$region_id'
        },
        label=_('Site')
    )
    device_id = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        required=False,
        null_option='None',
        query_params={
            'site_id': '$site_id'
        },
        label=_('Device')
    )
    vlan_id = DynamicModelMultipleChoiceField(
        queryset=VLAN.objects.all(),
        required=False,
        null_option='None',
        query_params={
            'site_id': '$site_id'
        },
        label=_('VLAN')
    )
    virtual_machine_id = DynamicModelMultipleChoiceField(
        queryset=VirtualMachine.objects.all(),
        required=False,
        null_option='None',
        query_params={
            'site_id': '$site_id'
        },
        label=_('Virtual Machine')
    )
