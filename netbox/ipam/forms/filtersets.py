from django import forms
from django.utils.translation import gettext_lazy as _

from dcim.models import Location, Rack, Region, Site, SiteGroup, Device
from ipam.choices import *
from ipam.constants import *
from ipam.filtersets import *
from ipam.models import *
from netbox.forms import NetBoxModelFilterSetForm, OrganizationalModelFilterSetForm, PrimaryModelFilterSetForm
from tenancy.forms import ContactModelFilterForm, TenancyFilterForm
from utilities.forms import BOOLEAN_WITH_BLANK_CHOICES, add_blank_choice
from utilities.forms.fields import DynamicModelChoiceField, DynamicModelMultipleChoiceField, TagFilterField
from utilities.forms.filterset_mappings import FILTERSET_MAPPINGS
from utilities.forms.mixins import FilterModifierMixin
from utilities.forms.rendering import FieldSet
from virtualization.models import VirtualMachine, ClusterGroup, Cluster
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
    'VLANTranslationPolicyFilterForm',
    'VLANTranslationRuleFilterForm',
    'VRFFilterForm',
)

PREFIX_MASK_LENGTH_CHOICES = add_blank_choice([
    (i, i) for i in range(PREFIX_LENGTH_MIN, PREFIX_LENGTH_MAX + 1)
])

IPADDRESS_MASK_LENGTH_CHOICES = add_blank_choice([
    (i, i) for i in range(IPADDRESS_MASK_LENGTH_MIN, IPADDRESS_MASK_LENGTH_MAX + 1)
])


class VRFFilterForm(FilterModifierMixin, TenancyFilterForm, PrimaryModelFilterSetForm):
    model = VRF
    fieldsets = (
        FieldSet('q', 'filter_id', 'tag', 'owner_id'),
        FieldSet('import_target_id', 'export_target_id', name=_('Route Targets')),
        FieldSet('tenant_group_id', 'tenant_id', name=_('Tenant')),
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


class RouteTargetFilterForm(FilterModifierMixin, TenancyFilterForm, PrimaryModelFilterSetForm):
    model = RouteTarget
    fieldsets = (
        FieldSet('q', 'filter_id', 'tag', 'owner_id'),
        FieldSet('importing_vrf_id', 'exporting_vrf_id', name=_('VRF')),
        FieldSet('tenant_group_id', 'tenant_id', name=_('Tenant')),
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


class RIRFilterForm(FilterModifierMixin, OrganizationalModelFilterSetForm):
    model = RIR
    fieldsets = (
        FieldSet('q', 'filter_id', 'tag', 'owner_id'),
        FieldSet('is_private', name=_('RIR')),
    )
    is_private = forms.NullBooleanField(
        required=False,
        label=_('Private'),
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    tag = TagFilterField(model)


class AggregateFilterForm(FilterModifierMixin, ContactModelFilterForm, TenancyFilterForm, PrimaryModelFilterSetForm):
    model = Aggregate
    fieldsets = (
        FieldSet('q', 'filter_id', 'tag', 'owner_id'),
        FieldSet('family', 'rir_id', name=_('Attributes')),
        FieldSet('tenant_group_id', 'tenant_id', name=_('Tenant')),
        FieldSet('contact', 'contact_role', 'contact_group', name=_('Contacts')),
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


class ASNRangeFilterForm(FilterModifierMixin, TenancyFilterForm, OrganizationalModelFilterSetForm):
    model = ASNRange
    fieldsets = (
        FieldSet('q', 'filter_id', 'tag', 'owner_id'),
        FieldSet('rir_id', 'start', 'end', name=_('Range')),
        FieldSet('tenant_group_id', 'tenant_id', name=_('Tenant')),
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


class ASNFilterForm(FilterModifierMixin, TenancyFilterForm, PrimaryModelFilterSetForm):
    model = ASN
    fieldsets = (
        FieldSet('q', 'filter_id', 'tag', 'owner_id'),
        FieldSet('rir_id', 'site_group_id', 'site_id', name=_('Assignment')),
        FieldSet('tenant_group_id', 'tenant_id', name=_('Tenant')),
    )
    rir_id = DynamicModelMultipleChoiceField(
        queryset=RIR.objects.all(),
        required=False,
        label=_('RIR')
    )
    site_group_id = DynamicModelMultipleChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False,
        label=_('Site group')
    )
    site_id = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        label=_('Site')
    )
    tag = TagFilterField(model)


class RoleFilterForm(FilterModifierMixin, OrganizationalModelFilterSetForm):
    model = Role
    fieldsets = (
        FieldSet('q', 'filter_id', 'tag', 'owner_id'),
    )
    tag = TagFilterField(model)


class PrefixFilterForm(FilterModifierMixin, ContactModelFilterForm, TenancyFilterForm, PrimaryModelFilterSetForm):
    model = Prefix
    fieldsets = (
        FieldSet('q', 'filter_id', 'tag', 'owner_id'),
        FieldSet(
            'within_include', 'family', 'status', 'role_id', 'mask_length', 'is_pool', 'mark_utilized',
            name=_('Addressing')
        ),
        FieldSet('vlan_group_id', 'vlan_id', name=_('VLAN Assignment')),
        FieldSet('vrf_id', 'present_in_vrf_id', name=_('VRF')),
        FieldSet('region_id', 'site_group_id', 'site_id', 'location_id', name=_('Scope')),
        FieldSet('tenant_group_id', 'tenant_id', name=_('Tenant')),
        FieldSet('contact', 'contact_role', 'contact_group', name=_('Contacts')),
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
        label=_('Site')
    )
    location_id = DynamicModelMultipleChoiceField(
        queryset=Location.objects.all(),
        required=False,
        label=_('Location')
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
    vlan_group_id = DynamicModelMultipleChoiceField(
        queryset=VLANGroup.objects.all(),
        required=False,
        label=_('VLAN Group'),
    )
    vlan_id = DynamicModelMultipleChoiceField(
        queryset=VLAN.objects.all(),
        required=False,
        label=_('VLAN'),
    )

    tag = TagFilterField(model)


class IPRangeFilterForm(FilterModifierMixin, ContactModelFilterForm, TenancyFilterForm, PrimaryModelFilterSetForm):
    model = IPRange
    fieldsets = (
        FieldSet('q', 'filter_id', 'tag', 'owner_id'),
        FieldSet('family', 'vrf_id', 'status', 'role_id', 'mark_populated', 'mark_utilized', name=_('Attributes')),
        FieldSet('tenant_group_id', 'tenant_id', name=_('Tenant')),
        FieldSet('contact', 'contact_role', 'contact_group', name=_('Contacts')),
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
    mark_populated = forms.NullBooleanField(
        required=False,
        label=_('Treat as populated'),
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


class IPAddressFilterForm(FilterModifierMixin, ContactModelFilterForm, TenancyFilterForm, PrimaryModelFilterSetForm):
    model = IPAddress
    fieldsets = (
        FieldSet('q', 'filter_id', 'tag', 'owner_id'),
        FieldSet(
            'parent', 'family', 'status', 'role', 'mask_length', 'assigned_to_interface', 'dns_name',
            name=_('Attributes')
        ),
        FieldSet('vrf_id', 'present_in_vrf_id', name=_('VRF')),
        FieldSet('tenant_group_id', 'tenant_id', name=_('Tenant')),
        FieldSet('device_id', 'virtual_machine_id', name=_('Device/VM')),
        FieldSet('contact', 'contact_role', 'contact_group', name=_('Contacts')),
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


class FHRPGroupFilterForm(FilterModifierMixin, PrimaryModelFilterSetForm):
    model = FHRPGroup
    fieldsets = (
        FieldSet('q', 'filter_id', 'tag', 'owner_id'),
        FieldSet('name', 'protocol', 'group_id', name=_('Attributes')),
        FieldSet('auth_type', 'auth_key', name=_('Authentication')),
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


class VLANGroupFilterForm(FilterModifierMixin, TenancyFilterForm, OrganizationalModelFilterSetForm):
    fieldsets = (
        FieldSet('q', 'filter_id', 'tag', 'owner_id'),
        FieldSet('region', 'site_group', 'site', 'location', 'rack', name=_('Location')),
        FieldSet('cluster_group', 'cluster', name=_('Cluster')),
        FieldSet('contains_vid', name=_('VLANs')),
        FieldSet('tenant_group_id', 'tenant_id', name=_('Tenant')),
    )
    model = VLANGroup
    region = DynamicModelMultipleChoiceField(
        queryset=Region.objects.all(),
        required=False,
        label=_('Region')
    )
    site_group = DynamicModelMultipleChoiceField(
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
    cluster = DynamicModelMultipleChoiceField(
        queryset=Cluster.objects.all(),
        required=False,
        label=_('Cluster')
    )
    cluster_group = DynamicModelMultipleChoiceField(
        queryset=ClusterGroup.objects.all(),
        required=False,
        label=_('Cluster group')
    )
    contains_vid = forms.IntegerField(
        min_value=0,
        required=False,
        label=_('Contains VLAN ID')
    )

    tag = TagFilterField(model)


class VLANTranslationPolicyFilterForm(FilterModifierMixin, PrimaryModelFilterSetForm):
    model = VLANTranslationPolicy
    fieldsets = (
        FieldSet('q', 'filter_id', 'tag', 'owner_id'),
        FieldSet('name', name=_('Attributes')),
    )
    name = forms.CharField(
        required=False,
        label=_('Name')
    )
    tag = TagFilterField(model)


class VLANTranslationRuleFilterForm(FilterModifierMixin, NetBoxModelFilterSetForm):
    model = VLANTranslationRule
    fieldsets = (
        FieldSet('q', 'filter_id', 'tag'),
        FieldSet('policy_id', 'local_vid', 'remote_vid', name=_('Attributes')),
    )
    tag = TagFilterField(model)
    policy_id = DynamicModelMultipleChoiceField(
        queryset=VLANTranslationPolicy.objects.all(),
        required=False,
        label=_('VLAN Translation Policy')
    )
    local_vid = forms.IntegerField(
        min_value=1,
        required=False,
        label=_('Local VLAN ID')
    )
    remote_vid = forms.IntegerField(
        min_value=1,
        required=False,
        label=_('Remote VLAN ID')
    )


class VLANFilterForm(FilterModifierMixin, TenancyFilterForm, PrimaryModelFilterSetForm):
    model = VLAN
    fieldsets = (
        FieldSet('q', 'filter_id', 'tag', 'owner_id'),
        FieldSet('region_id', 'site_group_id', 'site_id', name=_('Location')),
        FieldSet('group_id', 'status', 'role_id', 'vid', 'l2vpn_id', name=_('Attributes')),
        FieldSet('qinq_role', 'qinq_svlan_id', name=_('Q-in-Q/802.1ad')),
        FieldSet('tenant_group_id', 'tenant_id', name=_('Tenant')),
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
    qinq_role = forms.MultipleChoiceField(
        label=_('Q-in-Q role'),
        choices=VLANQinQRoleChoices,
        required=False
    )
    qinq_svlan_id = DynamicModelMultipleChoiceField(
        queryset=VLAN.objects.all(),
        required=False,
        null_option='None',
        label=_('Q-in-Q SVLAN')
    )
    l2vpn_id = DynamicModelMultipleChoiceField(
        queryset=L2VPN.objects.all(),
        required=False,
        label=_('L2VPN')
    )
    tag = TagFilterField(model)


class ServiceTemplateFilterForm(FilterModifierMixin, PrimaryModelFilterSetForm):
    model = ServiceTemplate
    fieldsets = (
        FieldSet('q', 'filter_id', 'tag', 'owner_id'),
        FieldSet('protocol', 'port', name=_('Attributes')),
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


class ServiceFilterForm(ContactModelFilterForm, ServiceTemplateFilterForm):
    model = Service
    fieldsets = (
        FieldSet('q', 'filter_id', 'tag', 'owner_id'),
        FieldSet('protocol', 'port', name=_('Attributes')),
        FieldSet('device_id', 'virtual_machine_id', 'fhrpgroup_id', name=_('Assignment')),
        FieldSet('contact', 'contact_role', 'contact_group', name=_('Contacts')),
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
    fhrpgroup_id = DynamicModelMultipleChoiceField(
        queryset=FHRPGroup.objects.all(),
        required=False,
        label=_('FHRP Group'),
    )
    tag = TagFilterField(model)


# Register FilterSet mappings for FilterModifierMixin lookup verification
FILTERSET_MAPPINGS[AggregateFilterForm] = AggregateFilterSet
FILTERSET_MAPPINGS[ASNFilterForm] = ASNFilterSet
FILTERSET_MAPPINGS[ASNRangeFilterForm] = ASNRangeFilterSet
FILTERSET_MAPPINGS[FHRPGroupFilterForm] = FHRPGroupFilterSet
FILTERSET_MAPPINGS[IPAddressFilterForm] = IPAddressFilterSet
FILTERSET_MAPPINGS[IPRangeFilterForm] = IPRangeFilterSet
FILTERSET_MAPPINGS[PrefixFilterForm] = PrefixFilterSet
FILTERSET_MAPPINGS[RIRFilterForm] = RIRFilterSet
FILTERSET_MAPPINGS[RoleFilterForm] = RoleFilterSet
FILTERSET_MAPPINGS[RouteTargetFilterForm] = RouteTargetFilterSet
FILTERSET_MAPPINGS[ServiceFilterForm] = ServiceFilterSet
FILTERSET_MAPPINGS[ServiceTemplateFilterForm] = ServiceTemplateFilterSet
FILTERSET_MAPPINGS[VLANFilterForm] = VLANFilterSet
FILTERSET_MAPPINGS[VLANGroupFilterForm] = VLANGroupFilterSet
FILTERSET_MAPPINGS[VLANTranslationPolicyFilterForm] = VLANTranslationPolicyFilterSet
FILTERSET_MAPPINGS[VLANTranslationRuleFilterForm] = VLANTranslationRuleFilterSet
FILTERSET_MAPPINGS[VRFFilterForm] = VRFFilterSet
