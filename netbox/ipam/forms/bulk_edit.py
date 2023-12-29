from django import forms
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _

from dcim.models import Location, Rack, Region, Site, SiteGroup
from ipam.choices import *
from ipam.constants import *
from ipam.models import *
from ipam.models import ASN
from netbox.forms import NetBoxModelBulkEditForm
from tenancy.models import Tenant
from utilities.forms import add_blank_choice
from utilities.forms.fields import (
    CommentField, ContentTypeChoiceField, DynamicModelChoiceField, DynamicModelMultipleChoiceField, NumericArrayField,
)
from utilities.forms.widgets import BulkEditNullBooleanSelect
from virtualization.models import Cluster, ClusterGroup

__all__ = (
    'AggregateBulkEditForm',
    'ASNBulkEditForm',
    'ASNRangeBulkEditForm',
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
        label=_('Tenant'),
        queryset=Tenant.objects.all(),
        required=False
    )
    enforce_unique = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect(),
        label=_('Enforce unique space')
    )
    description = forms.CharField(
        label=_('Description'),
        max_length=200,
        required=False
    )
    comments = CommentField()

    model = VRF
    fieldsets = (
        (None, ('tenant', 'enforce_unique', 'description')),
    )
    nullable_fields = ('tenant', 'description', 'comments')


class RouteTargetBulkEditForm(NetBoxModelBulkEditForm):
    tenant = DynamicModelChoiceField(
        label=_('Tenant'),
        queryset=Tenant.objects.all(),
        required=False
    )
    description = forms.CharField(
        label=_('Description'),
        max_length=200,
        required=False
    )
    comments = CommentField()

    model = RouteTarget
    fieldsets = (
        (None, ('tenant', 'description')),
    )
    nullable_fields = ('tenant', 'description', 'comments')


class RIRBulkEditForm(NetBoxModelBulkEditForm):
    is_private = forms.NullBooleanField(
        label=_('Is private'),
        required=False,
        widget=BulkEditNullBooleanSelect
    )
    description = forms.CharField(
        label=_('Description'),
        max_length=200,
        required=False
    )

    model = RIR
    fieldsets = (
        (None, ('is_private', 'description')),
    )
    nullable_fields = ('is_private', 'description')


class ASNRangeBulkEditForm(NetBoxModelBulkEditForm):
    rir = DynamicModelChoiceField(
        queryset=RIR.objects.all(),
        required=False,
        label=_('RIR')
    )
    tenant = DynamicModelChoiceField(
        label=_('Tenant'),
        queryset=Tenant.objects.all(),
        required=False
    )
    description = forms.CharField(
        label=_('Description'),
        max_length=200,
        required=False
    )

    model = ASNRange
    fieldsets = (
        (None, ('rir', 'tenant', 'description')),
    )
    nullable_fields = ('description',)


class ASNBulkEditForm(NetBoxModelBulkEditForm):
    sites = DynamicModelMultipleChoiceField(
        label=_('Sites'),
        queryset=Site.objects.all(),
        required=False
    )
    rir = DynamicModelChoiceField(
        queryset=RIR.objects.all(),
        required=False,
        label=_('RIR')
    )
    tenant = DynamicModelChoiceField(
        label=_('Tenant'),
        queryset=Tenant.objects.all(),
        required=False
    )
    description = forms.CharField(
        label=_('Description'),
        max_length=200,
        required=False
    )
    comments = CommentField()

    model = ASN
    fieldsets = (
        (None, ('sites', 'rir', 'tenant', 'description')),
    )
    nullable_fields = ('tenant', 'description', 'comments')


class AggregateBulkEditForm(NetBoxModelBulkEditForm):
    rir = DynamicModelChoiceField(
        queryset=RIR.objects.all(),
        required=False,
        label=_('RIR')
    )
    tenant = DynamicModelChoiceField(
        label=_('Tenant'),
        queryset=Tenant.objects.all(),
        required=False
    )
    date_added = forms.DateField(
        label=_('Date added'),
        required=False
    )
    description = forms.CharField(
        label=_('Description'),
        max_length=200,
        required=False
    )
    comments = CommentField()

    model = Aggregate
    fieldsets = (
        (None, ('rir', 'tenant', 'date_added', 'description')),
    )
    nullable_fields = ('date_added', 'description', 'comments')


class RoleBulkEditForm(NetBoxModelBulkEditForm):
    weight = forms.IntegerField(
        label=_('Weight'),
        required=False
    )
    description = forms.CharField(
        label=_('Description'),
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
        label=_('Region'),
        queryset=Region.objects.all(),
        required=False
    )
    site_group = DynamicModelChoiceField(
        label=_('Site group'),
        queryset=SiteGroup.objects.all(),
        required=False
    )
    site = DynamicModelChoiceField(
        label=_('Site'),
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
        label=_('Prefix length'),
        min_value=PREFIX_LENGTH_MIN,
        max_value=PREFIX_LENGTH_MAX,
        required=False
    )
    tenant = DynamicModelChoiceField(
        label=_('Tenant'),
        queryset=Tenant.objects.all(),
        required=False
    )
    status = forms.ChoiceField(
        label=_('Status'),
        choices=add_blank_choice(PrefixStatusChoices),
        required=False
    )
    role = DynamicModelChoiceField(
        label=_('Role'),
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
        label=_('Description'),
        max_length=200,
        required=False
    )
    comments = CommentField()

    model = Prefix
    fieldsets = (
        (None, ('tenant', 'status', 'role', 'description')),
        (_('Site'), ('region', 'site_group', 'site')),
        (_('Addressing'), ('vrf', 'prefix_length', 'is_pool', 'mark_utilized')),
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
        label=_('Tenant'),
        queryset=Tenant.objects.all(),
        required=False
    )
    status = forms.ChoiceField(
        label=_('Status'),
        choices=add_blank_choice(IPRangeStatusChoices),
        required=False
    )
    role = DynamicModelChoiceField(
        label=_('Role'),
        queryset=Role.objects.all(),
        required=False
    )
    mark_utilized = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect(),
        label=_('Treat as 100% utilized')
    )
    description = forms.CharField(
        label=_('Description'),
        max_length=200,
        required=False
    )
    comments = CommentField()

    model = IPRange
    fieldsets = (
        (None, ('status', 'role', 'vrf', 'tenant', 'mark_utilized', 'description')),
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
        label=_('Mask length'),
        min_value=IPADDRESS_MASK_LENGTH_MIN,
        max_value=IPADDRESS_MASK_LENGTH_MAX,
        required=False
    )
    tenant = DynamicModelChoiceField(
        label=_('Tenant'),
        queryset=Tenant.objects.all(),
        required=False
    )
    status = forms.ChoiceField(
        label=_('Status'),
        choices=add_blank_choice(IPAddressStatusChoices),
        required=False
    )
    role = forms.ChoiceField(
        label=_('Role'),
        choices=add_blank_choice(IPAddressRoleChoices),
        required=False
    )
    dns_name = forms.CharField(
        max_length=255,
        required=False,
        label=_('DNS name')
    )
    description = forms.CharField(
        label=_('Description'),
        max_length=200,
        required=False
    )
    comments = CommentField()

    model = IPAddress
    fieldsets = (
        (None, ('status', 'role', 'tenant', 'description')),
        (_('Addressing'), ('vrf', 'mask_length', 'dns_name')),
    )
    nullable_fields = (
        'vrf', 'role', 'tenant', 'dns_name', 'description', 'comments',
    )


class FHRPGroupBulkEditForm(NetBoxModelBulkEditForm):
    protocol = forms.ChoiceField(
        label=_('Protocol'),
        choices=add_blank_choice(FHRPGroupProtocolChoices),
        required=False
    )
    group_id = forms.IntegerField(
        min_value=0,
        required=False,
        label=_('Group ID')
    )
    auth_type = forms.ChoiceField(
        choices=add_blank_choice(FHRPGroupAuthTypeChoices),
        required=False,
        label=_('Authentication type')
    )
    auth_key = forms.CharField(
        max_length=255,
        required=False,
        label=_('Authentication key')
    )
    name = forms.CharField(
        label=_('Name'),
        max_length=100,
        required=False
    )
    description = forms.CharField(
        label=_('Description'),
        max_length=200,
        required=False
    )
    comments = CommentField()

    model = FHRPGroup
    fieldsets = (
        (None, ('protocol', 'group_id', 'name', 'description')),
        (_('Authentication'), ('auth_type', 'auth_key')),
    )
    nullable_fields = ('auth_type', 'auth_key', 'name', 'description', 'comments')


class VLANGroupBulkEditForm(NetBoxModelBulkEditForm):
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
        label=_('Description'),
        max_length=200,
        required=False
    )
    scope_type = ContentTypeChoiceField(
        label=_('Scope type'),
        queryset=ContentType.objects.filter(model__in=VLANGROUP_SCOPE_TYPES),
        required=False
    )
    scope_id = forms.IntegerField(
        required=False,
        widget=forms.HiddenInput()
    )
    region = DynamicModelChoiceField(
        label=_('Region'),
        queryset=Region.objects.all(),
        required=False
    )
    sitegroup = DynamicModelChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False,
        label=_('Site group')
    )
    site = DynamicModelChoiceField(
        label=_('Site'),
        queryset=Site.objects.all(),
        required=False,
        query_params={
            'region_id': '$region',
            'group_id': '$sitegroup',
        }
    )
    location = DynamicModelChoiceField(
        label=_('Location'),
        queryset=Location.objects.all(),
        required=False,
        query_params={
            'site_id': '$site',
        }
    )
    rack = DynamicModelChoiceField(
        label=_('Rack'),
        queryset=Rack.objects.all(),
        required=False,
        query_params={
            'site_id': '$site',
            'location_id': '$location',
        }
    )
    clustergroup = DynamicModelChoiceField(
        queryset=ClusterGroup.objects.all(),
        required=False,
        label=_('Cluster group')
    )
    cluster = DynamicModelChoiceField(
        label=_('Cluster'),
        queryset=Cluster.objects.all(),
        required=False,
        query_params={
            'group_id': '$clustergroup',
        }
    )

    model = VLANGroup
    fieldsets = (
        (None, ('site', 'min_vid', 'max_vid', 'description')),
        (_('Scope'), ('scope_type', 'region', 'sitegroup', 'site', 'location', 'rack', 'clustergroup', 'cluster')),
    )
    nullable_fields = ('description',)

    def clean(self):
        super().clean()

        # Assign scope based on scope_type
        if self.cleaned_data.get('scope_type'):
            scope_field = self.cleaned_data['scope_type'].model
            if scope_obj := self.cleaned_data.get(scope_field):
                self.cleaned_data['scope_id'] = scope_obj.pk
                self.changed_data.append('scope_id')
            else:
                self.cleaned_data.pop('scope_type')
                self.changed_data.remove('scope_type')


class VLANBulkEditForm(NetBoxModelBulkEditForm):
    region = DynamicModelChoiceField(
        label=_('Region'),
        queryset=Region.objects.all(),
        required=False
    )
    site_group = DynamicModelChoiceField(
        label=_('Site group'),
        queryset=SiteGroup.objects.all(),
        required=False
    )
    site = DynamicModelChoiceField(
        label=_('Site'),
        queryset=Site.objects.all(),
        required=False,
        query_params={
            'region_id': '$region',
            'group_id': '$site_group',
        }
    )
    group = DynamicModelChoiceField(
        label=_('Group'),
        queryset=VLANGroup.objects.all(),
        required=False,
        query_params={
            'site_id': '$site'
        }
    )
    tenant = DynamicModelChoiceField(
        label=_('Tenant'),
        queryset=Tenant.objects.all(),
        required=False
    )
    status = forms.ChoiceField(
        label=_('Status'),
        choices=add_blank_choice(VLANStatusChoices),
        required=False
    )
    role = DynamicModelChoiceField(
        label=_('Role'),
        queryset=Role.objects.all(),
        required=False
    )
    description = forms.CharField(
        label=_('Description'),
        max_length=200,
        required=False
    )
    comments = CommentField()

    model = VLAN
    fieldsets = (
        (None, ('status', 'role', 'tenant', 'description')),
        (_('Site & Group'), ('region', 'site_group', 'site', 'group')),
    )
    nullable_fields = (
        'site', 'group', 'tenant', 'role', 'description', 'comments',
    )


class ServiceTemplateBulkEditForm(NetBoxModelBulkEditForm):
    protocol = forms.ChoiceField(
        label=_('Protocol'),
        choices=add_blank_choice(ServiceProtocolChoices),
        required=False
    )
    ports = NumericArrayField(
        label=_('Ports'),
        base_field=forms.IntegerField(
            min_value=SERVICE_PORT_MIN,
            max_value=SERVICE_PORT_MAX
        ),
        required=False
    )
    description = forms.CharField(
        label=_('Description'),
        max_length=200,
        required=False
    )
    comments = CommentField()

    model = ServiceTemplate
    fieldsets = (
        (None, ('protocol', 'ports', 'description')),
    )
    nullable_fields = ('description', 'comments')


class ServiceBulkEditForm(ServiceTemplateBulkEditForm):
    model = Service
