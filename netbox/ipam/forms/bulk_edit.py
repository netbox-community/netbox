from django import forms

from dcim.models import Region, Site, SiteGroup
from ipam.choices import *
from ipam.constants import *
from ipam.models import *
from ipam.models import ASN
from netbox.forms import NetBoxModelBulkEditForm
from tenancy.models import Tenant
from utilities.forms import (
    add_blank_choice, BulkEditNullBooleanSelect, DatePicker, DynamicModelChoiceField, NumericArrayField, StaticSelect,
    DynamicModelMultipleChoiceField,
)

__all__ = (
    'AggregateBulkEditForm',
    'ASNBulkEditForm',
    'FHRPGroupBulkEditForm',
    'IPAddressBulkEditForm',
    'IPRangeBulkEditForm',
    'PrefixBulkEditForm',
    'RIRBulkEditForm',
    'RoleBulkEditForm',
    'RouteTargetBulkEditForm',
    'ServiceBulkEditForm',
    'ServiceTemplateBulkEditForm',
    'VLANBulkEditForm',
    'VLANGroupBulkEditForm',
    'VRFBulkEditForm',
)


class VRFBulkEditForm(NetBoxModelBulkEditForm):
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False
    )
    enforce_unique = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect(),
        label='Enforce unique space'
    )
    description = forms.CharField(
        max_length=100,
        required=False
    )

    model = VRF
    nullable_fields = ('tenant', 'description')


class RouteTargetBulkEditForm(NetBoxModelBulkEditForm):
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False
    )
    description = forms.CharField(
        max_length=200,
        required=False
    )

    model = RouteTarget
    nullable_fields = ('tenant', 'description')


class RIRBulkEditForm(NetBoxModelBulkEditForm):
    is_private = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect
    )
    description = forms.CharField(
        max_length=200,
        required=False
    )

    model = RIR
    nullable_fields = ('is_private', 'description')


class ASNBulkEditForm(NetBoxModelBulkEditForm):
    sites = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False
    )
    rir = DynamicModelChoiceField(
        queryset=RIR.objects.all(),
        required=False,
        label='RIR'
    )
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False
    )
    description = forms.CharField(
        max_length=100,
        required=False
    )

    model = ASN
    nullable_fields = ('date_added', 'description')


class AggregateBulkEditForm(NetBoxModelBulkEditForm):
    rir = DynamicModelChoiceField(
        queryset=RIR.objects.all(),
        required=False,
        label='RIR'
    )
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False
    )
    date_added = forms.DateField(
        required=False
    )
    description = forms.CharField(
        max_length=100,
        required=False
    )

    model = Aggregate
    nullable_fields = ('date_added', 'description')


class RoleBulkEditForm(NetBoxModelBulkEditForm):
    weight = forms.IntegerField(
        required=False
    )
    description = forms.CharField(
        max_length=200,
        required=False
    )

    model = Role
    nullable_fields = ('description',)


class PrefixBulkEditForm(NetBoxModelBulkEditForm):
    region = DynamicModelChoiceField(
        queryset=Region.objects.all(),
        required=False
    )
    site_group = DynamicModelChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False
    )
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        query_params={
            'region_id': '$region',
            'group_id': '$site_group',
        }
    )
    vrf = DynamicModelChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label='VRF'
    )
    prefix_length = forms.IntegerField(
        min_value=PREFIX_LENGTH_MIN,
        max_value=PREFIX_LENGTH_MAX,
        required=False
    )
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False
    )
    status = forms.ChoiceField(
        choices=add_blank_choice(PrefixStatusChoices),
        required=False,
        widget=StaticSelect()
    )
    role = DynamicModelChoiceField(
        queryset=Role.objects.all(),
        required=False
    )
    is_pool = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect(),
        label='Is a pool'
    )
    mark_utilized = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect(),
        label='Treat as 100% utilized'
    )
    description = forms.CharField(
        max_length=100,
        required=False
    )

    model = Prefix
    nullable_fields = (
        'site', 'vrf', 'tenant', 'role', 'description',
    )


class IPRangeBulkEditForm(NetBoxModelBulkEditForm):
    vrf = DynamicModelChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label='VRF'
    )
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False
    )
    status = forms.ChoiceField(
        choices=add_blank_choice(IPRangeStatusChoices),
        required=False,
        widget=StaticSelect()
    )
    role = DynamicModelChoiceField(
        queryset=Role.objects.all(),
        required=False
    )
    description = forms.CharField(
        max_length=100,
        required=False
    )

    model = IPRange
    nullable_fields = (
        'vrf', 'tenant', 'role', 'description',
    )


class IPAddressBulkEditForm(NetBoxModelBulkEditForm):
    vrf = DynamicModelChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label='VRF'
    )
    mask_length = forms.IntegerField(
        min_value=IPADDRESS_MASK_LENGTH_MIN,
        max_value=IPADDRESS_MASK_LENGTH_MAX,
        required=False
    )
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False
    )
    status = forms.ChoiceField(
        choices=add_blank_choice(IPAddressStatusChoices),
        required=False,
        widget=StaticSelect()
    )
    role = forms.ChoiceField(
        choices=add_blank_choice(IPAddressRoleChoices),
        required=False,
        widget=StaticSelect()
    )
    dns_name = forms.CharField(
        max_length=255,
        required=False,
        label='DNS name'
    )
    description = forms.CharField(
        max_length=100,
        required=False
    )

    model = IPAddress
    nullable_fields = (
        'vrf', 'role', 'tenant', 'dns_name', 'description',
    )


class FHRPGroupBulkEditForm(NetBoxModelBulkEditForm):
    protocol = forms.ChoiceField(
        choices=add_blank_choice(FHRPGroupProtocolChoices),
        required=False,
        widget=StaticSelect()
    )
    group_id = forms.IntegerField(
        min_value=0,
        required=False,
        label='Group ID'
    )
    auth_type = forms.ChoiceField(
        choices=add_blank_choice(FHRPGroupAuthTypeChoices),
        required=False,
        widget=StaticSelect(),
        label='Authentication type'
    )
    auth_key = forms.CharField(
        max_length=255,
        required=False,
        label='Authentication key'
    )
    description = forms.CharField(
        max_length=200,
        required=False
    )

    model = FHRPGroup
    nullable_fields = ('auth_type', 'auth_key', 'description')


class VLANGroupBulkEditForm(NetBoxModelBulkEditForm):
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False
    )
    min_vid = forms.IntegerField(
        min_value=VLAN_VID_MIN,
        max_value=VLAN_VID_MAX,
        required=False,
        label='Minimum child VLAN VID'
    )
    max_vid = forms.IntegerField(
        min_value=VLAN_VID_MIN,
        max_value=VLAN_VID_MAX,
        required=False,
        label='Maximum child VLAN VID'
    )
    description = forms.CharField(
        max_length=200,
        required=False
    )

    model = VLANGroup
    nullable_fields = ('site', 'description')


class VLANBulkEditForm(NetBoxModelBulkEditForm):
    region = DynamicModelChoiceField(
        queryset=Region.objects.all(),
        required=False
    )
    site_group = DynamicModelChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False
    )
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        query_params={
            'region_id': '$region',
            'group_id': '$site_group',
        }
    )
    group = DynamicModelChoiceField(
        queryset=VLANGroup.objects.all(),
        required=False,
        query_params={
            'site_id': '$site'
        }
    )
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False
    )
    status = forms.ChoiceField(
        choices=add_blank_choice(VLANStatusChoices),
        required=False,
        widget=StaticSelect()
    )
    role = DynamicModelChoiceField(
        queryset=Role.objects.all(),
        required=False
    )
    description = forms.CharField(
        max_length=100,
        required=False
    )

    model = VLAN
    nullable_fields = (
        'site', 'group', 'tenant', 'role', 'description',
    )


class ServiceTemplateBulkEditForm(NetBoxModelBulkEditForm):
    protocol = forms.ChoiceField(
        choices=add_blank_choice(ServiceProtocolChoices),
        required=False,
        widget=StaticSelect()
    )
    ports = NumericArrayField(
        base_field=forms.IntegerField(
            min_value=SERVICE_PORT_MIN,
            max_value=SERVICE_PORT_MAX
        ),
        required=False
    )
    description = forms.CharField(
        max_length=100,
        required=False
    )

    model = ServiceTemplate
    nullable_fields = ('description',)


class ServiceBulkEditForm(ServiceTemplateBulkEditForm):
    model = Service
