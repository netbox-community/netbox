from django import forms
from django.utils.translation import gettext as _

from dcim.models import Location, Rack, Region, Site, SiteGroup, Device
from virtualization.models import VirtualMachine
from ipam.choices import *
from ipam.constants import *
from ipam.models import *
from ipam.models import ASN
from netbox.forms import NetBoxModelFilterSetForm
from tenancy.forms import TenancyFilterForm
from utilities.forms import (
    add_blank_choice, DynamicModelChoiceField, DynamicModelMultipleChoiceField, MultipleChoiceField, StaticSelect,
    TagFilterField, BOOLEAN_WITH_BLANK_CHOICES,
)

__all__ = (
    'AggregateFilterForm',
    'ASNFilterForm',
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
        (None, ('q', 'tag')),
        ('Route Targets', ('import_target_id', 'export_target_id')),
        ('Tenant', ('tenant_group_id', 'tenant_id')),
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
        (None, ('q', 'tag')),
        ('VRF', ('importing_vrf_id', 'exporting_vrf_id')),
        ('Tenant', ('tenant_group_id', 'tenant_id')),
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
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    tag = TagFilterField(model)


class AggregateFilterForm(TenancyFilterForm, NetBoxModelFilterSetForm):
    model = Aggregate
    fieldsets = (
        (None, ('q', 'tag')),
        ('Attributes', ('family', 'rir_id')),
        ('Tenant', ('tenant_group_id', 'tenant_id')),
    )
    family = forms.ChoiceField(
        required=False,
        choices=add_blank_choice(IPAddressFamilyChoices),
        label=_('Address family'),
        widget=StaticSelect()
    )
    rir_id = DynamicModelMultipleChoiceField(
        queryset=RIR.objects.all(),
        required=False,
        label=_('RIR')
    )
    tag = TagFilterField(model)


class ASNFilterForm(TenancyFilterForm, NetBoxModelFilterSetForm):
    model = ASN
    fieldsets = (
        (None, ('q', 'tag')),
        ('Assignment', ('rir_id', 'site_id')),
        ('Tenant', ('tenant_group_id', 'tenant_id')),
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
        (None, ('q', 'tag')),
        ('Addressing', ('within_include', 'family', 'status', 'role_id', 'mask_length', 'is_pool', 'mark_utilized')),
        ('VRF', ('vrf_id', 'present_in_vrf_id')),
        ('Location', ('region_id', 'site_group_id', 'site_id')),
        ('Tenant', ('tenant_group_id', 'tenant_id')),
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
        label=_('Address family'),
        widget=StaticSelect()
    )
    mask_length = MultipleChoiceField(
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
    status = MultipleChoiceField(
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
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    mark_utilized = forms.NullBooleanField(
        required=False,
        label=_('Marked as 100% utilized'),
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    tag = TagFilterField(model)


class IPRangeFilterForm(TenancyFilterForm, NetBoxModelFilterSetForm):
    model = IPRange
    fieldsets = (
        (None, ('q', 'tag')),
        ('Attriubtes', ('family', 'vrf_id', 'status', 'role_id')),
        ('Tenant', ('tenant_group_id', 'tenant_id')),
    )
    family = forms.ChoiceField(
        required=False,
        choices=add_blank_choice(IPAddressFamilyChoices),
        label=_('Address family'),
        widget=StaticSelect()
    )
    vrf_id = DynamicModelMultipleChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label=_('Assigned VRF'),
        null_option='Global'
    )
    status = MultipleChoiceField(
        choices=PrefixStatusChoices,
        required=False
    )
    role_id = DynamicModelMultipleChoiceField(
        queryset=Role.objects.all(),
        required=False,
        null_option='None',
        label=_('Role')
    )
    tag = TagFilterField(model)


class IPAddressFilterForm(TenancyFilterForm, NetBoxModelFilterSetForm):
    model = IPAddress
    fieldsets = (
        (None, ('q', 'tag')),
        ('Attributes', ('parent', 'family', 'status', 'role', 'mask_length', 'assigned_to_interface')),
        ('VRF', ('vrf_id', 'present_in_vrf_id')),
        ('Tenant', ('tenant_group_id', 'tenant_id')),
        ('Device/VM', ('device_id', 'virtual_machine_id')),
    )
    parent = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Prefix',
            }
        ),
        label='Parent Prefix'
    )
    family = forms.ChoiceField(
        required=False,
        choices=add_blank_choice(IPAddressFamilyChoices),
        label=_('Address family'),
        widget=StaticSelect()
    )
    mask_length = forms.ChoiceField(
        required=False,
        choices=IPADDRESS_MASK_LENGTH_CHOICES,
        label=_('Mask length'),
        widget=StaticSelect()
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
    status = MultipleChoiceField(
        choices=IPAddressStatusChoices,
        required=False
    )
    role = MultipleChoiceField(
        choices=IPAddressRoleChoices,
        required=False
    )
    assigned_to_interface = forms.NullBooleanField(
        required=False,
        label=_('Assigned to an interface'),
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    tag = TagFilterField(model)


class FHRPGroupFilterForm(NetBoxModelFilterSetForm):
    model = FHRPGroup
    fieldsets = (
        (None, ('q', 'tag')),
        ('Attributes', ('protocol', 'group_id')),
        ('Authentication', ('auth_type', 'auth_key')),
    )
    protocol = MultipleChoiceField(
        choices=FHRPGroupProtocolChoices,
        required=False
    )
    group_id = forms.IntegerField(
        min_value=0,
        required=False,
        label='Group ID'
    )
    auth_type = MultipleChoiceField(
        choices=FHRPGroupAuthTypeChoices,
        required=False,
        label='Authentication type'
    )
    auth_key = forms.CharField(
        required=False,
        label='Authentication key'
    )
    tag = TagFilterField(model)


class VLANGroupFilterForm(NetBoxModelFilterSetForm):
    fieldsets = (
        (None, ('q', 'tag')),
        ('Location', ('region', 'sitegroup', 'site', 'location', 'rack')),
        ('VLAN ID', ('min_vid', 'max_vid')),
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
        label='Minimum VID'
    )
    max_vid = forms.IntegerField(
        required=False,
        min_value=VLAN_VID_MIN,
        max_value=VLAN_VID_MAX,
        label='Maximum VID'
    )
    tag = TagFilterField(model)


class VLANFilterForm(TenancyFilterForm, NetBoxModelFilterSetForm):
    model = VLAN
    fieldsets = (
        (None, ('q', 'tag')),
        ('Location', ('region_id', 'site_group_id', 'site_id')),
        ('Attributes', ('group_id', 'status', 'role_id', 'vid')),
        ('Tenant', ('tenant_group_id', 'tenant_id')),
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
    status = MultipleChoiceField(
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
        label='VLAN ID'
    )
    tag = TagFilterField(model)


class ServiceTemplateFilterForm(NetBoxModelFilterSetForm):
    model = ServiceTemplate
    fieldsets = (
        (None, ('q', 'tag')),
        ('Attributes', ('protocol', 'port')),
    )
    protocol = forms.ChoiceField(
        choices=add_blank_choice(ServiceProtocolChoices),
        required=False,
        widget=StaticSelect()
    )
    port = forms.IntegerField(
        required=False,
    )
    tag = TagFilterField(model)


class ServiceFilterForm(ServiceTemplateFilterForm):
    model = Service
