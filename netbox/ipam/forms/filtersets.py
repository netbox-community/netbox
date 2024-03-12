from django import forms
from django.utils.translation import gettext_lazy as _

from dcim.models import Location, Rack, Region, Site, SiteGroup, Device
from ipam.choices import *
from ipam.constants import *
from ipam.models import *
from netbox.forms import NetBoxModelFilterSetForm
from tenancy.forms import TenancyFilterForm
from utilities.forms import BOOLEAN_WITH_BLANK_CHOICES, add_blank_choice
from utilities.forms.fields import DynamicModelChoiceField, DynamicModelMultipleChoiceField, TagFilterField
from virtualization.models import VirtualMachine
from vpn.models import L2VPN

__all__ = (
    'AggregateFilterForm',
    'ASNFilterForm',
    'ASNRangeFilterForm',
    'FHRPGroupFilterForm',
    'IPAddressFilterForm',
    'IPRangeFilterForm',
    'PrefixFilterForm',
    'RIRFilterForm',
    'RoleFilterForm',
    'RouteTargetFilterForm',
    'ServiceFilterForm',
    'ServiceTemplateFilterForm',
    'VLANFilterForm',
    'VLANGroupFilterForm',
    'VRFFilterForm',
)

PREFIX_MASK_LENGTH_CHOICES = add_blank_choice([
    (i, i) for i in range(PREFIX_LENGTH_MIN, PREFIX_LENGTH_MAX + 1)
])

IPADDRESS_MASK_LENGTH_CHOICES = add_blank_choice([
    (i, i) for i in range(IPADDRESS_MASK_LENGTH_MIN, IPADDRESS_MASK_LENGTH_MAX + 1)
])


class VRFFilterForm(TenancyFilterForm, NetBoxModelFilterSetForm):
    model = VRF
    fieldsets = (
        (None, ('q', 'filter_id', 'tag')),
        (_('Route Targets'), ('import_target_id', 'export_target_id')),
        (_('Tenant'), ('tenant_group_id', 'tenant_id')),
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


class RouteTargetFilterForm(TenancyFilterForm, NetBoxModelFilterSetForm):
    model = RouteTarget
    fieldsets = (
        (None, ('q', 'filter_id', 'tag')),
        (_('VRF'), ('importing_vrf_id', 'exporting_vrf_id')),
        (_('Tenant'), ('tenant_group_id', 'tenant_id')),
    )
    importing_vrf_id = DynamicModelMultipleChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label=_('Imported by VRF')
    )
    exporting_vrf_id = DynamicModelMultipleChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label=_('Exported by VRF')
    )
    tag = TagFilterField(model)


class RIRFilterForm(NetBoxModelFilterSetForm):
    model = RIR
    is_private = forms.NullBooleanField(
        required=False,
        label=_('Private'),
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    tag = TagFilterField(model)


class AggregateFilterForm(TenancyFilterForm, NetBoxModelFilterSetForm):
    model = Aggregate
    fieldsets = (
        (None, ('q', 'filter_id', 'tag')),
        (_('Attributes'), ('family', 'rir_id')),
        (_('Tenant'), ('tenant_group_id', 'tenant_id')),
    )
    family = forms.ChoiceField(
        required=False,
        choices=add_blank_choice(IPAddressFamilyChoices),
        label=_('Address family')
    )
    rir_id = DynamicModelMultipleChoiceField(
        queryset=RIR.objects.all(),
        required=False,
        label=_('RIR')
    )
    tag = TagFilterField(model)


class ASNRangeFilterForm(TenancyFilterForm, NetBoxModelFilterSetForm):
    model = ASNRange
    fieldsets = (
        (None, ('q', 'filter_id', 'tag')),
        (_('Range'), ('rir_id', 'start', 'end')),
        (_('Tenant'), ('tenant_group_id', 'tenant_id')),
    )
    rir_id = DynamicModelMultipleChoiceField(
        queryset=RIR.objects.all(),
        required=False,
        label=_('RIR')
    )
    start = forms.IntegerField(
        label=_('Start'),
        required=False
    )
    end = forms.IntegerField(
        label=_('End'),
        required=False
    )
    tag = TagFilterField(model)


class ASNFilterForm(TenancyFilterForm, NetBoxModelFilterSetForm):
    model = ASN
    fieldsets = (
        (None, ('q', 'filter_id', 'tag')),
        (_('Assignment'), ('rir_id', 'site_id')),
        (_('Tenant'), ('tenant_group_id', 'tenant_id')),
    )
    rir_id = DynamicModelMultipleChoiceField(
        queryset=RIR.objects.all(),
        required=False,
        label=_('RIR')
    )
    site_id = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        label=_('Site')
    )
    tag = TagFilterField(model)


class RoleFilterForm(NetBoxModelFilterSetForm):
    model = Role
    tag = TagFilterField(model)


class PrefixFilterForm(TenancyFilterForm, NetBoxModelFilterSetForm):
    model = Prefix
    fieldsets = (
        (None, ('q', 'filter_id', 'tag')),
        (_('Addressing'), ('within_include', 'family', 'status', 'role_id', 'mask_length', 'is_pool', 'mark_utilized')),
        (_('VRF'), ('vrf_id', 'present_in_vrf_id')),
        (_('Location'), ('region_id', 'site_group_id', 'site_id')),
        (_('Tenant'), ('tenant_group_id', 'tenant_id')),
    )
    mask_length__lte = forms.IntegerField(
        widget=forms.HiddenInput()
    )
    within_include = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Prefix',
            }
        ),
        label=_('Search within')
    )
    family = forms.ChoiceField(
        required=False,
        choices=add_blank_choice(IPAddressFamilyChoices),
        label=_('Address family')
    )
    mask_length = forms.MultipleChoiceField(
        required=False,
        choices=PREFIX_MASK_LENGTH_CHOICES,
        label=_('Mask length')
    )
    vrf_id = DynamicModelMultipleChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label=_('Assigned VRF'),
        null_option='Global'
    )
    present_in_vrf_id = DynamicModelChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label=_('Present in VRF')
    )
    status = forms.MultipleChoiceField(
        label=_('Status'),
        choices=PrefixStatusChoices,
        required=False
    )
    region_id = DynamicModelMultipleChoiceField(
        queryset=Region.objects.all(),
        required=False,
        label=_('Region')
    )
    site_group_id = DynamicModelMultipleChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False,
        label=_('Site group')
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
    role_id = DynamicModelMultipleChoiceField(
        queryset=Role.objects.all(),
        required=False,
        null_option='None',
        label=_('Role')
    )
    is_pool = forms.NullBooleanField(
        required=False,
        label=_('Is a pool'),
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    mark_utilized = forms.NullBooleanField(
        required=False,
        label=_('Treat as fully utilized'),
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    tag = TagFilterField(model)


class IPRangeFilterForm(TenancyFilterForm, NetBoxModelFilterSetForm):
    model = IPRange
    fieldsets = (
        (None, ('q', 'filter_id', 'tag')),
        (_('Attributes'), ('family', 'vrf_id', 'status', 'role_id', 'mark_utilized')),
        (_('Tenant'), ('tenant_group_id', 'tenant_id')),
    )
    family = forms.ChoiceField(
        required=False,
        choices=add_blank_choice(IPAddressFamilyChoices),
        label=_('Address family')
    )
    vrf_id = DynamicModelMultipleChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label=_('Assigned VRF'),
        null_option='Global'
    )
    status = forms.MultipleChoiceField(
        label=_('Status'),
        choices=IPRangeStatusChoices,
        required=False
    )
    role_id = DynamicModelMultipleChoiceField(
        queryset=Role.objects.all(),
        required=False,
        null_option='None',
        label=_('Role')
    )
    mark_utilized = forms.NullBooleanField(
        required=False,
        label=_('Treat as fully utilized'),
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    tag = TagFilterField(model)


class IPAddressFilterForm(TenancyFilterForm, NetBoxModelFilterSetForm):
    model = IPAddress
    fieldsets = (
        (None, ('q', 'filter_id', 'tag')),
        (_('Attributes'), ('parent', 'family', 'status', 'role', 'mask_length', 'assigned_to_interface', 'dns_name')),
        (_('VRF'), ('vrf_id', 'present_in_vrf_id')),
        (_('Tenant'), ('tenant_group_id', 'tenant_id')),
        (_('Device/VM'), ('device_id', 'virtual_machine_id')),
    )
    selector_fields = ('filter_id', 'q', 'region_id', 'group_id', 'parent', 'status', 'role')
    parent = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Prefix',
            }
        ),
        label=_('Parent Prefix')
    )
    family = forms.ChoiceField(
        required=False,
        choices=add_blank_choice(IPAddressFamilyChoices),
        label=_('Address family')
    )
    mask_length = forms.ChoiceField(
        required=False,
        choices=IPADDRESS_MASK_LENGTH_CHOICES,
        label=_('Mask length')
    )
    vrf_id = DynamicModelMultipleChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label=_('Assigned VRF'),
        null_option='Global'
    )
    present_in_vrf_id = DynamicModelChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label=_('Present in VRF')
    )
    device_id = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        required=False,
        label=_('Assigned Device'),
    )
    virtual_machine_id = DynamicModelMultipleChoiceField(
        queryset=VirtualMachine.objects.all(),
        required=False,
        label=_('Assigned VM'),
    )
    status = forms.MultipleChoiceField(
        label=_('Status'),
        choices=IPAddressStatusChoices,
        required=False
    )
    role = forms.MultipleChoiceField(
        label=_('Role'),
        choices=IPAddressRoleChoices,
        required=False
    )
    assigned_to_interface = forms.NullBooleanField(
        required=False,
        label=_('Assigned to an interface'),
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    dns_name = forms.CharField(
        required=False,
        label=_('DNS Name')
    )
    tag = TagFilterField(model)


class FHRPGroupFilterForm(NetBoxModelFilterSetForm):
    model = FHRPGroup
    fieldsets = (
        (None, ('q', 'filter_id', 'tag')),
        (_('Attributes'), ('name', 'protocol', 'group_id')),
        (_('Authentication'), ('auth_type', 'auth_key')),
    )
    name = forms.CharField(
        label=_('Name'),
        required=False
    )
    protocol = forms.MultipleChoiceField(
        label=_('Protocol'),
        choices=FHRPGroupProtocolChoices,
        required=False
    )
    group_id = forms.IntegerField(
        min_value=0,
        required=False,
        label=_('Group ID')
    )
    auth_type = forms.MultipleChoiceField(
        choices=FHRPGroupAuthTypeChoices,
        required=False,
        label=_('Authentication type')
    )
    auth_key = forms.CharField(
        required=False,
        label=_('Authentication key')
    )
    tag = TagFilterField(model)


class VLANGroupFilterForm(NetBoxModelFilterSetForm):
    fieldsets = (
        (None, ('q', 'filter_id', 'tag')),
        (_('Location'), ('region', 'sitegroup', 'site', 'location', 'rack')),
        (_('VLAN ID'), ('min_vid', 'max_vid')),
    )
    model = VLANGroup
    region = DynamicModelMultipleChoiceField(
        queryset=Region.objects.all(),
        required=False,
        label=_('Region')
    )
    sitegroup = DynamicModelMultipleChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False,
        label=_('Site group')
    )
    site = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        label=_('Site')
    )
    location = DynamicModelMultipleChoiceField(
        queryset=Location.objects.all(),
        required=False,
        label=_('Location')
    )
    rack = DynamicModelMultipleChoiceField(
        queryset=Rack.objects.all(),
        required=False,
        label=_('Rack')
    )
    min_vid = forms.IntegerField(
        required=False,
        min_value=VLAN_VID_MIN,
        max_value=VLAN_VID_MAX,
        label=_('Minimum VID')
    )
    max_vid = forms.IntegerField(
        required=False,
        min_value=VLAN_VID_MIN,
        max_value=VLAN_VID_MAX,
        label=_('Maximum VID')
    )
    tag = TagFilterField(model)


class VLANFilterForm(TenancyFilterForm, NetBoxModelFilterSetForm):
    model = VLAN
    fieldsets = (
        (None, ('q', 'filter_id', 'tag')),
        (_('Location'), ('region_id', 'site_group_id', 'site_id')),
        (_('Attributes'), ('group_id', 'status', 'role_id', 'vid', 'l2vpn_id')),
        (_('Tenant'), ('tenant_group_id', 'tenant_id')),
    )
    selector_fields = ('filter_id', 'q', 'site_id')
    region_id = DynamicModelMultipleChoiceField(
        queryset=Region.objects.all(),
        required=False,
        label=_('Region')
    )
    site_group_id = DynamicModelMultipleChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False,
        label=_('Site group')
    )
    site_id = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        null_option='None',
        query_params={
            'region': '$region'
        },
        label=_('Site')
    )
    group_id = DynamicModelMultipleChoiceField(
        queryset=VLANGroup.objects.all(),
        required=False,
        null_option='None',
        query_params={
            'region': '$region'
        },
        label=_('VLAN group')
    )
    status = forms.MultipleChoiceField(
        label=_('Status'),
        choices=VLANStatusChoices,
        required=False
    )
    role_id = DynamicModelMultipleChoiceField(
        queryset=Role.objects.all(),
        required=False,
        null_option='None',
        label=_('Role')
    )
    vid = forms.IntegerField(
        required=False,
        label=_('VLAN ID')
    )
    l2vpn_id = DynamicModelMultipleChoiceField(
        queryset=L2VPN.objects.all(),
        required=False,
        label=_('L2VPN')
    )
    tag = TagFilterField(model)


class ServiceTemplateFilterForm(NetBoxModelFilterSetForm):
    model = ServiceTemplate
    fieldsets = (
        (None, ('q', 'filter_id', 'tag')),
        (_('Attributes'), ('protocol', 'port')),
    )
    protocol = forms.ChoiceField(
        label=_('Protocol'),
        choices=add_blank_choice(ServiceProtocolChoices),
        required=False
    )
    port = forms.IntegerField(
        label=_('Port'),
        required=False,
    )
    tag = TagFilterField(model)


class ServiceFilterForm(ServiceTemplateFilterForm):
    model = Service
    fieldsets = (
        (None, ('q', 'filter_id', 'tag')),
        (_('Attributes'), ('protocol', 'port')),
        (_('Assignment'), ('device_id', 'virtual_machine_id')),
    )
    device_id = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        required=False,
        label=_('Device'),
    )
    virtual_machine_id = DynamicModelMultipleChoiceField(
        queryset=VirtualMachine.objects.all(),
        required=False,
        label=_('Virtual Machine'),
    )
    tag = TagFilterField(model)
