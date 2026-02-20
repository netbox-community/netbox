from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _

from dcim.forms.mixins import ScopedBulkEditForm
from dcim.models import Region, Site, SiteGroup
from ipam.choices import *
from ipam.constants import *
from ipam.models import *
from ipam.models import ASN
from netbox.forms import NetBoxModelBulkEditForm, OrganizationalModelBulkEditForm, PrimaryModelBulkEditForm
from tenancy.models import Tenant
from utilities.forms import add_blank_choice, get_field_value
from utilities.forms.fields import (
    ContentTypeChoiceField,
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
    NumericArrayField,
    NumericRangeArrayField,
)
from utilities.forms.rendering import FieldSet
from utilities.forms.widgets import BulkEditNullBooleanSelect, HTMXSelect
from utilities.templatetags.builtins.filters import bettertitle

__all__ = (
    'ASNBulkEditForm',
    'ASNRangeBulkEditForm',
    'AggregateBulkEditForm',
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
    'VLANTranslationPolicyBulkEditForm',
    'VLANTranslationRuleBulkEditForm',
    'VRFBulkEditForm',
)


class VRFBulkEditForm(PrimaryModelBulkEditForm):
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

    model = VRF
    fieldsets = (
        FieldSet('tenant', 'enforce_unique', 'description'),
    )
    nullable_fields = ('tenant', 'description', 'comments')


class RouteTargetBulkEditForm(PrimaryModelBulkEditForm):
    tenant = DynamicModelChoiceField(
        label=_('Tenant'),
        queryset=Tenant.objects.all(),
        required=False
    )

    model = RouteTarget
    fieldsets = (
        FieldSet('tenant', 'description'),
    )
    nullable_fields = ('tenant', 'description', 'comments')


class RIRBulkEditForm(OrganizationalModelBulkEditForm):
    is_private = forms.NullBooleanField(
        label=_('Is private'),
        required=False,
        widget=BulkEditNullBooleanSelect
    )

    model = RIR
    fieldsets = (
        FieldSet('is_private', 'description'),
    )
    nullable_fields = ('is_private', 'description', 'comments')


class ASNRangeBulkEditForm(OrganizationalModelBulkEditForm):
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

    model = ASNRange
    fieldsets = (
        FieldSet('rir', 'tenant', 'description'),
    )
    nullable_fields = ('description', 'comments')


class ASNBulkEditForm(PrimaryModelBulkEditForm):
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

    model = ASN
    fieldsets = (
        FieldSet('sites', 'rir', 'tenant', 'description'),
    )
    nullable_fields = ('tenant', 'description', 'comments')


class AggregateBulkEditForm(PrimaryModelBulkEditForm):
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

    model = Aggregate
    fieldsets = (
        FieldSet('rir', 'tenant', 'date_added', 'description'),
    )
    nullable_fields = ('date_added', 'description', 'comments')


class RoleBulkEditForm(OrganizationalModelBulkEditForm):
    weight = forms.IntegerField(
        label=_('Weight'),
        required=False
    )

    model = Role
    fieldsets = (
        FieldSet('weight', 'description'),
    )
    nullable_fields = ('description', 'comments')


class PrefixBulkEditForm(ScopedBulkEditForm, PrimaryModelBulkEditForm):
    vlan_group = DynamicModelChoiceField(
        queryset=VLANGroup.objects.all(),
        required=False,
        label=_('VLAN Group')
    )
    vlan = DynamicModelChoiceField(
        queryset=VLAN.objects.all(),
        required=False,
        label=_('VLAN'),
        query_params={
            'group_id': '$vlan_group',
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
        label=_('Treat as fully utilized')
    )

    model = Prefix
    fieldsets = (
        FieldSet('tenant', 'status', 'role', 'description'),
        FieldSet('vrf', 'prefix_length', 'is_pool', 'mark_utilized', name=_('Addressing')),
        FieldSet('scope_type', 'scope', name=_('Scope')),
        FieldSet('vlan_group', 'vlan', name=_('VLAN Assignment')),
    )
    nullable_fields = (
        'vlan', 'vrf', 'tenant', 'role', 'scope', 'description', 'comments',
    )


class IPRangeBulkEditForm(PrimaryModelBulkEditForm):
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
    mark_populated = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect(),
        label=_('Treat as populated')
    )
    mark_utilized = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect(),
        label=_('Treat as fully utilized')
    )

    model = IPRange
    fieldsets = (
        FieldSet('status', 'role', 'vrf', 'tenant', 'mark_utilized', 'description'),
    )
    nullable_fields = (
        'vrf', 'tenant', 'role', 'description', 'comments',
    )


class IPAddressBulkEditForm(PrimaryModelBulkEditForm):
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

    model = IPAddress
    fieldsets = (
        FieldSet('status', 'role', 'tenant', 'description'),
        FieldSet('vrf', 'mask_length', 'dns_name', name=_('Addressing')),
    )
    nullable_fields = (
        'vrf', 'role', 'tenant', 'dns_name', 'description', 'comments',
    )


class FHRPGroupBulkEditForm(PrimaryModelBulkEditForm):
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

    model = FHRPGroup
    fieldsets = (
        FieldSet('protocol', 'group_id', 'name', 'description'),
        FieldSet('auth_type', 'auth_key', name=_('Authentication')),
    )
    nullable_fields = ('auth_type', 'auth_key', 'name', 'description', 'comments')


class VLANGroupBulkEditForm(OrganizationalModelBulkEditForm):
    scope_type = ContentTypeChoiceField(
        queryset=ContentType.objects.filter(model__in=VLANGROUP_SCOPE_TYPES),
        widget=HTMXSelect(method='post', attrs={'hx-select': '#form_fields'}),
        required=False,
        label=_('Scope type')
    )
    scope = DynamicModelChoiceField(
        label=_('Scope'),
        queryset=Site.objects.none(),  # Initial queryset
        required=False,
        disabled=True,
        selector=True
    )
    vid_ranges = NumericRangeArrayField(
        label=_('VLAN ID ranges'),
        required=False
    )
    tenant = DynamicModelChoiceField(
        label=_('Tenant'),
        queryset=Tenant.objects.all(),
        required=False
    )

    model = VLANGroup
    fieldsets = (
        FieldSet('site', 'vid_ranges', 'description'),
        FieldSet('scope_type', 'scope', name=_('Scope')),
        FieldSet('tenant', name=_('Tenancy')),
    )
    nullable_fields = ('description', 'scope', 'comments')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if scope_type_id := get_field_value(self, 'scope_type'):
            try:
                scope_type = ContentType.objects.get(pk=scope_type_id)
                model = scope_type.model_class()
                self.fields['scope'].queryset = model.objects.all()
                self.fields['scope'].widget.attrs['selector'] = model._meta.label_lower
                self.fields['scope'].disabled = False
                self.fields['scope'].label = _(bettertitle(model._meta.verbose_name))
            except ObjectDoesNotExist:
                pass


class VLANBulkEditForm(PrimaryModelBulkEditForm):
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
    qinq_role = forms.ChoiceField(
        label=_('Q-in-Q role'),
        choices=add_blank_choice(VLANQinQRoleChoices),
        required=False
    )
    qinq_svlan = DynamicModelChoiceField(
        label=_('Q-in-Q SVLAN'),
        queryset=VLAN.objects.all(),
        required=False,
        query_params={
            'qinq_role': VLANQinQRoleChoices.ROLE_SERVICE,
        }
    )

    model = VLAN
    fieldsets = (
        FieldSet('status', 'role', 'tenant', 'description'),
        FieldSet('qinq_role', 'qinq_svlan', name=_('Q-in-Q')),
        FieldSet('region', 'site_group', 'site', 'group', name=_('Site & Group')),
    )
    nullable_fields = (
        'site', 'group', 'tenant', 'role', 'description', 'qinq_role', 'qinq_svlan', 'comments',
    )


class VLANTranslationPolicyBulkEditForm(PrimaryModelBulkEditForm):
    model = VLANTranslationPolicy
    fieldsets = (
        FieldSet('description'),
    )
    nullable_fields = ('description',)


class VLANTranslationRuleBulkEditForm(NetBoxModelBulkEditForm):
    policy = DynamicModelChoiceField(
        label=_('Policy'),
        queryset=VLANTranslationPolicy.objects.all(),
        selector=True
    )
    local_vid = forms.IntegerField(required=False)
    remote_vid = forms.IntegerField(required=False)

    model = VLANTranslationRule
    fieldsets = (
        FieldSet('policy', 'local_vid', 'remote_vid'),
    )
    fields = ('policy', 'local_vid', 'remote_vid')


class ServiceTemplateBulkEditForm(PrimaryModelBulkEditForm):
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

    model = ServiceTemplate
    fieldsets = (
        FieldSet('protocol', 'ports', 'description'),
    )
    nullable_fields = ('description', 'comments')


class ServiceBulkEditForm(ServiceTemplateBulkEditForm):
    model = Service
