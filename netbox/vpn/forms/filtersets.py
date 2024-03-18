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
from utilities.forms.rendering import FieldSet
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
        FieldSet('q', 'filter_id', 'tag'),
        FieldSet('status', 'encapsulation', 'tunnel_id', name=_('Tunnel')),
        FieldSet('ipsec_profile_id', name=_('Security')),
        FieldSet('tenant_group_id', 'tenant_id', name=_('Tenancy')),
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
        FieldSet('q', 'filter_id', 'tag'),
        FieldSet('tunnel_id', 'role', name=_('Termination')),
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
        FieldSet('q', 'filter_id', 'tag'),
        FieldSet(
            'authentication_method', 'encryption_algorithm', 'authentication_algorithm', 'group', name=_('Parameters')
        ),
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
        FieldSet('q', 'filter_id', 'tag'),
        FieldSet('version', 'mode', 'proposal_id', name=_('Parameters')),
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
        FieldSet('q', 'filter_id', 'tag'),
        FieldSet('encryption_algorithm', 'authentication_algorithm', name=_('Parameters')),
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
        FieldSet('q', 'filter_id', 'tag'),
        FieldSet('proposal_id', 'pfs_group', name=_('Parameters')),
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
        FieldSet('q', 'filter_id', 'tag'),
        FieldSet('mode', 'ike_policy_id', 'ipsec_policy_id', name=_('Profile')),
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
        FieldSet('q', 'filter_id', 'tag'),
        FieldSet('type', 'import_target_id', 'export_target_id', name=_('Attributes')),
        FieldSet('tenant_group_id', 'tenant_id', name=_('Tenant')),
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
        FieldSet('filter_id', 'l2vpn_id',),
        FieldSet(
            'assigned_object_type_id', 'region_id', 'site_id', 'device_id', 'virtual_machine_id', 'vlan_id',
            name=_('Assigned Object')
        ),
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
