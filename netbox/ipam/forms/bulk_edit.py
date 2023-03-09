from django import forms
from django.utils.translation import gettext as _

from dcim.models import Region, Site, SiteGroup
from ipam.choices import *
from ipam.constants import *
from ipam.models import *
from ipam.models import ASN
from netbox.forms import NetBoxModelBulkEditForm
from tenancy.models import Tenant
from utilities.forms import (
    add_blank_choice, BulkEditNullBooleanSelect, CommentField, DynamicModelChoiceField, NumericArrayField,
    StaticSelect, DynamicModelMultipleChoiceField
)

__all__ = (
    'AggregateBulkEditForm',
    'ASNBulkEditForm',
    'FHRPGroupBulkEditForm',
    'IPAddressBulkEditForm',
    'IPRangeBulkEditForm',
    'L2VPNBulkEditForm',
    'L2VPNTerminationBulkEditForm',
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
        label=_('Enforce unique space')
    )
    description = forms.CharField(
        max_length=200,
        required=False
    )
    comments = CommentField(
        label='Comments'
    )

    model = VRF
    fieldsets = (
        (None, ('tenant', 'enforce_unique', 'description')),
    )
    nullable_fields = ('tenant', 'description', 'comments')


class RouteTargetBulkEditForm(NetBoxModelBulkEditForm):
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False
    )
    description = forms.CharField(
        max_length=200,
        required=False
    )
    comments = CommentField(
        label='Comments'
    )

    model = RouteTarget
    fieldsets = (
        (None, ('tenant', 'description')),
    )
    nullable_fields = ('tenant', 'description', 'comments')


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
    fieldsets = (
        (None, ('is_private', 'description')),
    )
    nullable_fields = ('is_private', 'description')


class ASNBulkEditForm(NetBoxModelBulkEditForm):
    sites = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False
    )
    rir = DynamicModelChoiceField(
        queryset=RIR.objects.all(),
        required=False,
        label=_('RIR')
    )
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False
    )
    description = forms.CharField(
        max_length=200,
        required=False
    )
    comments = CommentField(
        label='Comments'
    )

    model = ASN
    fieldsets = (
        (None, ('sites', 'rir', 'tenant', 'description')),
    )
    nullable_fields = ('date_added', 'description', 'comments')


class AggregateBulkEditForm(NetBoxModelBulkEditForm):
    rir = DynamicModelChoiceField(
        queryset=RIR.objects.all(),
        required=False,
        label=_('RIR')
    )
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False
    )
    date_added = forms.DateField(
        required=False
    )
    description = forms.CharField(
        max_length=200,
        required=False
    )
    comments = CommentField(
        label='Comments'
    )

    model = Aggregate
    fieldsets = (
        (None, ('rir', 'tenant', 'date_added', 'description')),
    )
    nullable_fields = ('date_added', 'description', 'comments')


class RoleBulkEditForm(NetBoxModelBulkEditForm):
    weight = forms.IntegerField(
        required=False
    )
    description = forms.CharField(
        max_length=200,
        required=False
    )

    model = Role
    fieldsets = (
        (None, ('weight', 'description')),
    )
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
        label=_('VRF')
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
        label=_('Is a pool')
    )
    mark_utilized = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect(),
        label=_('Treat as 100% utilized')
    )
    description = forms.CharField(
        max_length=200,
        required=False
    )
    comments = CommentField(
        label='Comments'
    )

    model = Prefix
    fieldsets = (
        (None, ('tenant', 'status', 'role', 'description')),
        ('Site', ('region', 'site_group', 'site')),
        ('Addressing', ('vrf', 'prefix_length', 'is_pool', 'mark_utilized')),
    )
    nullable_fields = (
        'site', 'vrf', 'tenant', 'role', 'description', 'comments',
    )


class IPRangeBulkEditForm(NetBoxModelBulkEditForm):
    vrf = DynamicModelChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label=_('VRF')
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
        max_length=200,
        required=False
    )
    comments = CommentField(
        label='Comments'
    )

    model = IPRange
    fieldsets = (
        (None, ('status', 'role', 'vrf', 'tenant', 'description')),
    )
    nullable_fields = (
        'vrf', 'tenant', 'role', 'description', 'comments',
    )


class IPAddressBulkEditForm(NetBoxModelBulkEditForm):
    vrf = DynamicModelChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label=_('VRF')
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
        label=_('DNS name')
    )
    description = forms.CharField(
        max_length=200,
        required=False
    )
    comments = CommentField(
        label='Comments'
    )

    model = IPAddress
    fieldsets = (
        (None, ('status', 'role', 'tenant', 'description')),
        ('Addressing', ('vrf', 'mask_length', 'dns_name')),
    )
    nullable_fields = (
        'vrf', 'role', 'tenant', 'dns_name', 'description', 'comments',
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
        label=_('Group ID')
    )
    auth_type = forms.ChoiceField(
        choices=add_blank_choice(FHRPGroupAuthTypeChoices),
        required=False,
        widget=StaticSelect(),
        label=_('Authentication type')
    )
    auth_key = forms.CharField(
        max_length=255,
        required=False,
        label=_('Authentication key')
    )
    name = forms.CharField(
        max_length=100,
        required=False
    )
    description = forms.CharField(
        max_length=200,
        required=False
    )
    comments = CommentField(
        label='Comments'
    )

    model = FHRPGroup
    fieldsets = (
        (None, ('protocol', 'group_id', 'name', 'description')),
        ('Authentication', ('auth_type', 'auth_key')),
    )
    nullable_fields = ('auth_type', 'auth_key', 'name', 'description', 'comments')


class VLANGroupBulkEditForm(NetBoxModelBulkEditForm):
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False
    )
    min_vid = forms.IntegerField(
        min_value=VLAN_VID_MIN,
        max_value=VLAN_VID_MAX,
        required=False,
        label=_('Minimum child VLAN VID')
    )
    max_vid = forms.IntegerField(
        min_value=VLAN_VID_MIN,
        max_value=VLAN_VID_MAX,
        required=False,
        label=_('Maximum child VLAN VID')
    )
    description = forms.CharField(
        max_length=200,
        required=False
    )

    model = VLANGroup
    fieldsets = (
        (None, ('site', 'min_vid', 'max_vid', 'description')),
    )
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
        max_length=200,
        required=False
    )
    comments = CommentField(
        label='Comments'
    )

    model = VLAN
    fieldsets = (
        (None, ('status', 'role', 'tenant', 'description')),
        ('Site & Group', ('region', 'site_group', 'site', 'group')),
    )
    nullable_fields = (
        'site', 'group', 'tenant', 'role', 'description', 'comments',
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
        max_length=200,
        required=False
    )
    comments = CommentField(
        label='Comments'
    )

    model = ServiceTemplate
    fieldsets = (
        (None, ('protocol', 'ports', 'description')),
    )
    nullable_fields = ('description', 'comments')


class ServiceBulkEditForm(ServiceTemplateBulkEditForm):
    model = Service


class L2VPNBulkEditForm(NetBoxModelBulkEditForm):
    type = forms.ChoiceField(
        choices=add_blank_choice(L2VPNTypeChoices),
        required=False,
        widget=StaticSelect()
    )
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False
    )
    description = forms.CharField(
        max_length=200,
        required=False
    )
    comments = CommentField(
        label='Comments'
    )

    model = L2VPN
    fieldsets = (
        (None, ('type', 'tenant', 'description')),
    )
    nullable_fields = ('tenant', 'description', 'comments')


class L2VPNTerminationBulkEditForm(NetBoxModelBulkEditForm):
    model = L2VPN
