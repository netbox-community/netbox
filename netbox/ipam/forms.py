from django import forms
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext as _

from dcim.models import Device, Interface, Location, Rack, Region, Site, SiteGroup
from extras.forms import (
    AddRemoveTagsForm, CustomFieldBulkEditForm, CustomFieldModelCSVForm, CustomFieldModelForm, CustomFieldFilterForm,
)
from extras.models import Tag
from tenancy.forms import TenancyFilterForm, TenancyForm
from tenancy.models import Tenant
from utilities.forms import (
    add_blank_choice, BootstrapMixin, BulkEditNullBooleanSelect, ContentTypeChoiceField, CSVChoiceField,
    CSVModelChoiceField, DatePicker, DynamicModelChoiceField, DynamicModelMultipleChoiceField, ExpandableIPAddressField,
    NumericArrayField, ReturnURLForm, SlugField, StaticSelect2, StaticSelect2Multiple, TagFilterField,
    BOOLEAN_WITH_BLANK_CHOICES,
)
from virtualization.models import Cluster, ClusterGroup, VirtualMachine, VMInterface
from .choices import *
from .constants import *
from .models import Aggregate, IPAddress, Prefix, RIR, Role, RouteTarget, Service, VLAN, VLANGroup, VRF

PREFIX_MASK_LENGTH_CHOICES = add_blank_choice([
    (i, i) for i in range(PREFIX_LENGTH_MIN, PREFIX_LENGTH_MAX + 1)
])

IPADDRESS_MASK_LENGTH_CHOICES = add_blank_choice([
    (i, i) for i in range(IPADDRESS_MASK_LENGTH_MIN, IPADDRESS_MASK_LENGTH_MAX + 1)
])


#
# VRFs
#

class VRFForm(BootstrapMixin, TenancyForm, CustomFieldModelForm):
    import_targets = DynamicModelMultipleChoiceField(
        queryset=RouteTarget.objects.all(),
        required=False
    )
    export_targets = DynamicModelMultipleChoiceField(
        queryset=RouteTarget.objects.all(),
        required=False
    )
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = VRF
        fields = [
            'name', 'rd', 'enforce_unique', 'description', 'import_targets', 'export_targets', 'tenant_group', 'tenant',
            'tags',
        ]
        fieldsets = (
            ('VRF', ('name', 'rd', 'enforce_unique', 'description', 'tags')),
            ('Route Targets', ('import_targets', 'export_targets')),
            ('Tenancy', ('tenant_group', 'tenant')),
        )
        labels = {
            'rd': "RD",
        }
        help_texts = {
            'rd': "Route distinguisher in any format",
        }


class VRFCSVForm(CustomFieldModelCSVForm):
    tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Assigned tenant'
    )

    class Meta:
        model = VRF
        fields = VRF.csv_headers


class VRFBulkEditForm(BootstrapMixin, AddRemoveTagsForm, CustomFieldBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=VRF.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
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

    class Meta:
        nullable_fields = [
            'tenant', 'description',
        ]


class VRFFilterForm(BootstrapMixin, TenancyFilterForm, CustomFieldFilterForm):
    model = VRF
    field_order = ['q', 'import_target_id', 'export_target_id', 'tenant_group_id', 'tenant_id']
    q = forms.CharField(
        required=False,
        label=_('Search')
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


#
# Route targets
#

class RouteTargetForm(BootstrapMixin, TenancyForm, CustomFieldModelForm):
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = RouteTarget
        fields = [
            'name', 'description', 'tenant_group', 'tenant', 'tags',
        ]


class RouteTargetCSVForm(CustomFieldModelCSVForm):
    tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Assigned tenant'
    )

    class Meta:
        model = RouteTarget
        fields = RouteTarget.csv_headers


class RouteTargetBulkEditForm(BootstrapMixin, AddRemoveTagsForm, CustomFieldBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=RouteTarget.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False
    )
    description = forms.CharField(
        max_length=200,
        required=False
    )

    class Meta:
        nullable_fields = [
            'tenant', 'description',
        ]


class RouteTargetFilterForm(BootstrapMixin, TenancyFilterForm, CustomFieldFilterForm):
    model = RouteTarget
    field_order = ['q', 'name', 'tenant_group_id', 'tenant_id', 'importing_vrfs', 'exporting_vrfs']
    q = forms.CharField(
        required=False,
        label=_('Search')
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


#
# RIRs
#

class RIRForm(BootstrapMixin, CustomFieldModelForm):
    slug = SlugField()

    class Meta:
        model = RIR
        fields = [
            'name', 'slug', 'is_private', 'description',
        ]


class RIRCSVForm(CustomFieldModelCSVForm):
    slug = SlugField()

    class Meta:
        model = RIR
        fields = RIR.csv_headers
        help_texts = {
            'name': 'RIR name',
        }


class RIRBulkEditForm(BootstrapMixin, CustomFieldBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=RIR.objects.all(),
        widget=forms.MultipleHiddenInput
    )
    is_private = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect
    )
    description = forms.CharField(
        max_length=200,
        required=False
    )

    class Meta:
        nullable_fields = ['is_private', 'description']


class RIRFilterForm(BootstrapMixin, forms.Form):
    is_private = forms.NullBooleanField(
        required=False,
        label=_('Private'),
        widget=StaticSelect2(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )


#
# Aggregates
#

class AggregateForm(BootstrapMixin, TenancyForm, CustomFieldModelForm):
    rir = DynamicModelChoiceField(
        queryset=RIR.objects.all(),
        label='RIR'
    )
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = Aggregate
        fields = [
            'prefix', 'rir', 'date_added', 'description', 'tenant_group', 'tenant', 'tags',
        ]
        fieldsets = (
            ('Aggregate', ('prefix', 'rir', 'date_added', 'description', 'tags')),
            ('Tenancy', ('tenant_group', 'tenant')),
        )
        help_texts = {
            'prefix': "IPv4 or IPv6 network",
            'rir': "Regional Internet Registry responsible for this prefix",
        }
        widgets = {
            'date_added': DatePicker(),
        }


class AggregateCSVForm(CustomFieldModelCSVForm):
    rir = CSVModelChoiceField(
        queryset=RIR.objects.all(),
        to_field_name='name',
        help_text='Assigned RIR'
    )
    tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Assigned tenant'
    )

    class Meta:
        model = Aggregate
        fields = Aggregate.csv_headers


class AggregateBulkEditForm(BootstrapMixin, AddRemoveTagsForm, CustomFieldBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=Aggregate.objects.all(),
        widget=forms.MultipleHiddenInput()
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
    date_added = forms.DateField(
        required=False
    )
    description = forms.CharField(
        max_length=100,
        required=False
    )

    class Meta:
        nullable_fields = [
            'date_added', 'description',
        ]
        widgets = {
            'date_added': DatePicker(),
        }


class AggregateFilterForm(BootstrapMixin, TenancyFilterForm, CustomFieldFilterForm):
    model = Aggregate
    field_order = ['q', 'family', 'rir', 'tenant_group_id', 'tenant_id']
    q = forms.CharField(
        required=False,
        label=_('Search')
    )
    family = forms.ChoiceField(
        required=False,
        choices=add_blank_choice(IPAddressFamilyChoices),
        label=_('Address family'),
        widget=StaticSelect2()
    )
    rir_id = DynamicModelMultipleChoiceField(
        queryset=RIR.objects.all(),
        required=False,
        label=_('RIR')
    )
    tag = TagFilterField(model)


#
# Roles
#

class RoleForm(BootstrapMixin, CustomFieldModelForm):
    slug = SlugField()

    class Meta:
        model = Role
        fields = [
            'name', 'slug', 'weight', 'description',
        ]


class RoleCSVForm(CustomFieldModelCSVForm):
    slug = SlugField()

    class Meta:
        model = Role
        fields = Role.csv_headers


class RoleBulkEditForm(BootstrapMixin, CustomFieldBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=Role.objects.all(),
        widget=forms.MultipleHiddenInput
    )
    weight = forms.IntegerField(
        required=False
    )
    description = forms.CharField(
        max_length=200,
        required=False
    )

    class Meta:
        nullable_fields = ['description']


#
# Prefixes
#

class PrefixForm(BootstrapMixin, TenancyForm, CustomFieldModelForm):
    vrf = DynamicModelChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label='VRF'
    )
    region = DynamicModelChoiceField(
        queryset=Region.objects.all(),
        required=False,
        initial_params={
            'sites': '$site'
        }
    )
    site_group = DynamicModelChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False,
        initial_params={
            'sites': '$site'
        }
    )
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        null_option='None',
        query_params={
            'region_id': '$region',
            'group_id': '$site_group',
        }
    )
    vlan_group = DynamicModelChoiceField(
        queryset=VLANGroup.objects.all(),
        required=False,
        label='VLAN group',
        null_option='None',
        query_params={
            'site_id': '$site'
        },
        initial_params={
            'vlans': '$vlan'
        }
    )
    vlan = DynamicModelChoiceField(
        queryset=VLAN.objects.all(),
        required=False,
        label='VLAN',
        query_params={
            'site_id': '$site',
            'group_id': '$vlan_group',
        }
    )
    role = DynamicModelChoiceField(
        queryset=Role.objects.all(),
        required=False
    )
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = Prefix
        fields = [
            'prefix', 'vrf', 'site', 'vlan', 'status', 'role', 'is_pool', 'description', 'tenant_group', 'tenant',
            'tags',
        ]
        fieldsets = (
            ('Prefix', ('prefix', 'status', 'vrf', 'role', 'is_pool', 'description', 'tags')),
            ('Site/VLAN Assignment', ('region', 'site_group', 'site', 'vlan_group', 'vlan')),
            ('Tenancy', ('tenant_group', 'tenant')),
        )
        widgets = {
            'status': StaticSelect2(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['vrf'].empty_label = 'Global'


class PrefixCSVForm(CustomFieldModelCSVForm):
    vrf = CSVModelChoiceField(
        queryset=VRF.objects.all(),
        to_field_name='name',
        required=False,
        help_text='Assigned VRF'
    )
    tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Assigned tenant'
    )
    site = CSVModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Assigned site'
    )
    vlan_group = CSVModelChoiceField(
        queryset=VLANGroup.objects.all(),
        required=False,
        to_field_name='name',
        help_text="VLAN's group (if any)"
    )
    vlan = CSVModelChoiceField(
        queryset=VLAN.objects.all(),
        required=False,
        to_field_name='vid',
        help_text="Assigned VLAN"
    )
    status = CSVChoiceField(
        choices=PrefixStatusChoices,
        help_text='Operational status'
    )
    role = CSVModelChoiceField(
        queryset=Role.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Functional role'
    )

    class Meta:
        model = Prefix
        fields = Prefix.csv_headers

    def __init__(self, data=None, *args, **kwargs):
        super().__init__(data, *args, **kwargs)

        if data:

            # Limit VLAN queryset by assigned site and/or group (if specified)
            params = {}
            if data.get('site'):
                params[f"site__{self.fields['site'].to_field_name}"] = data.get('site')
            if data.get('vlan_group'):
                params[f"group__{self.fields['vlan_group'].to_field_name}"] = data.get('vlan_group')
            if params:
                self.fields['vlan'].queryset = self.fields['vlan'].queryset.filter(**params)


class PrefixBulkEditForm(BootstrapMixin, AddRemoveTagsForm, CustomFieldBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=Prefix.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
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
        widget=StaticSelect2()
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
    description = forms.CharField(
        max_length=100,
        required=False
    )

    class Meta:
        nullable_fields = [
            'site', 'vrf', 'tenant', 'role', 'description',
        ]


class PrefixFilterForm(BootstrapMixin, TenancyFilterForm, CustomFieldFilterForm):
    model = Prefix
    field_order = [
        'q', 'within_include', 'family', 'mask_length', 'vrf_id', 'present_in_vrf_id', 'status', 'region_id',
        'site_group_id', 'site_id', 'role_id', 'tenant_group_id', 'tenant_id', 'is_pool',
    ]
    mask_length__lte = forms.IntegerField(
        widget=forms.HiddenInput()
    )
    q = forms.CharField(
        required=False,
        label=_('Search')
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
        widget=StaticSelect2()
    )
    mask_length = forms.ChoiceField(
        required=False,
        choices=PREFIX_MASK_LENGTH_CHOICES,
        label=_('Mask length'),
        widget=StaticSelect2()
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
        choices=PrefixStatusChoices,
        required=False,
        widget=StaticSelect2Multiple()
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
        widget=StaticSelect2(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    tag = TagFilterField(model)


#
# IP addresses
#

class IPAddressForm(BootstrapMixin, TenancyForm, ReturnURLForm, CustomFieldModelForm):
    device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        required=False,
        initial_params={
            'interfaces': '$interface'
        }
    )
    interface = DynamicModelChoiceField(
        queryset=Interface.objects.all(),
        required=False,
        query_params={
            'device_id': '$device'
        }
    )
    virtual_machine = DynamicModelChoiceField(
        queryset=VirtualMachine.objects.all(),
        required=False,
        initial_params={
            'interfaces': '$vminterface'
        }
    )
    vminterface = DynamicModelChoiceField(
        queryset=VMInterface.objects.all(),
        required=False,
        label='Interface',
        query_params={
            'virtual_machine_id': '$virtual_machine'
        }
    )
    vrf = DynamicModelChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label='VRF'
    )
    nat_region = DynamicModelChoiceField(
        queryset=Region.objects.all(),
        required=False,
        label='Region',
        initial_params={
            'sites': '$nat_site'
        }
    )
    nat_site_group = DynamicModelChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False,
        label='Site group',
        initial_params={
            'sites': '$nat_site'
        }
    )
    nat_site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        label='Site',
        query_params={
            'region_id': '$nat_region',
            'group_id': '$nat_site_group',
        }
    )
    nat_rack = DynamicModelChoiceField(
        queryset=Rack.objects.all(),
        required=False,
        label='Rack',
        null_option='None',
        query_params={
            'site_id': '$site'
        }
    )
    nat_device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        required=False,
        label='Device',
        query_params={
            'site_id': '$site',
            'rack_id': '$nat_rack',
        }
    )
    nat_cluster = DynamicModelChoiceField(
        queryset=Cluster.objects.all(),
        required=False,
        label='Cluster'
    )
    nat_virtual_machine = DynamicModelChoiceField(
        queryset=VirtualMachine.objects.all(),
        required=False,
        label='Virtual Machine',
        query_params={
            'cluster_id': '$nat_cluster',
        }
    )
    nat_vrf = DynamicModelChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label='VRF'
    )
    nat_inside = DynamicModelChoiceField(
        queryset=IPAddress.objects.all(),
        required=False,
        label='IP Address',
        query_params={
            'device_id': '$nat_device',
            'virtual_machine_id': '$nat_virtual_machine',
            'vrf_id': '$nat_vrf',
        }
    )
    primary_for_parent = forms.BooleanField(
        required=False,
        label='Make this the primary IP for the device/VM'
    )
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = IPAddress
        fields = [
            'address', 'vrf', 'status', 'role', 'dns_name', 'description', 'primary_for_parent', 'nat_site', 'nat_rack',
            'nat_device', 'nat_cluster', 'nat_virtual_machine', 'nat_vrf', 'nat_inside', 'tenant_group', 'tenant',
            'tags',
        ]
        widgets = {
            'status': StaticSelect2(),
            'role': StaticSelect2(),
        }

    def __init__(self, *args, **kwargs):

        # Initialize helper selectors
        instance = kwargs.get('instance')
        initial = kwargs.get('initial', {}).copy()
        if instance:
            if type(instance.assigned_object) is Interface:
                initial['interface'] = instance.assigned_object
            elif type(instance.assigned_object) is VMInterface:
                initial['vminterface'] = instance.assigned_object
            if instance.nat_inside:
                nat_inside_parent = instance.nat_inside.assigned_object
                if type(nat_inside_parent) is Interface:
                    initial['nat_site'] = nat_inside_parent.device.site.pk
                    if nat_inside_parent.device.rack:
                        initial['nat_rack'] = nat_inside_parent.device.rack.pk
                    initial['nat_device'] = nat_inside_parent.device.pk
                elif type(nat_inside_parent) is VMInterface:
                    initial['nat_cluster'] = nat_inside_parent.virtual_machine.cluster.pk
                    initial['nat_virtual_machine'] = nat_inside_parent.virtual_machine.pk
        kwargs['initial'] = initial

        super().__init__(*args, **kwargs)

        self.fields['vrf'].empty_label = 'Global'

        # Initialize primary_for_parent if IP address is already assigned
        if self.instance.pk and self.instance.assigned_object:
            parent = self.instance.assigned_object.parent_object
            if (
                self.instance.address.version == 4 and parent.primary_ip4_id == self.instance.pk or
                self.instance.address.version == 6 and parent.primary_ip6_id == self.instance.pk
            ):
                self.initial['primary_for_parent'] = True

    def clean(self):
        super().clean()

        # Cannot select both a device interface and a VM interface
        if self.cleaned_data.get('interface') and self.cleaned_data.get('vminterface'):
            raise forms.ValidationError("Cannot select both a device interface and a virtual machine interface")
        self.instance.assigned_object = self.cleaned_data.get('interface') or self.cleaned_data.get('vminterface')

        # Primary IP assignment is only available if an interface has been assigned.
        interface = self.cleaned_data.get('interface') or self.cleaned_data.get('vminterface')
        if self.cleaned_data.get('primary_for_parent') and not interface:
            self.add_error(
                'primary_for_parent', "Only IP addresses assigned to an interface can be designated as primary IPs."
            )

    def save(self, *args, **kwargs):
        ipaddress = super().save(*args, **kwargs)

        # Assign/clear this IPAddress as the primary for the associated Device/VirtualMachine.
        interface = self.instance.assigned_object
        if interface:
            parent = interface.parent_object
            if self.cleaned_data['primary_for_parent']:
                if ipaddress.address.version == 4:
                    parent.primary_ip4 = ipaddress
                else:
                    parent.primary_ip6 = ipaddress
                parent.save()
            elif ipaddress.address.version == 4 and parent.primary_ip4 == ipaddress:
                parent.primary_ip4 = None
                parent.save()
            elif ipaddress.address.version == 6 and parent.primary_ip6 == ipaddress:
                parent.primary_ip6 = None
                parent.save()

        return ipaddress


class IPAddressBulkCreateForm(BootstrapMixin, forms.Form):
    pattern = ExpandableIPAddressField(
        label='Address pattern'
    )


class IPAddressBulkAddForm(BootstrapMixin, TenancyForm, CustomFieldModelForm):
    vrf = DynamicModelChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label='VRF'
    )
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = IPAddress
        fields = [
            'address', 'vrf', 'status', 'role', 'dns_name', 'description', 'tenant_group', 'tenant', 'tags',
        ]
        widgets = {
            'status': StaticSelect2(),
            'role': StaticSelect2(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['vrf'].empty_label = 'Global'


class IPAddressCSVForm(CustomFieldModelCSVForm):
    vrf = CSVModelChoiceField(
        queryset=VRF.objects.all(),
        to_field_name='name',
        required=False,
        help_text='Assigned VRF'
    )
    tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        to_field_name='name',
        required=False,
        help_text='Assigned tenant'
    )
    status = CSVChoiceField(
        choices=IPAddressStatusChoices,
        required=False,
        help_text='Operational status'
    )
    role = CSVChoiceField(
        choices=IPAddressRoleChoices,
        required=False,
        help_text='Functional role'
    )
    device = CSVModelChoiceField(
        queryset=Device.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Parent device of assigned interface (if any)'
    )
    virtual_machine = CSVModelChoiceField(
        queryset=VirtualMachine.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Parent VM of assigned interface (if any)'
    )
    interface = CSVModelChoiceField(
        queryset=Interface.objects.none(),  # Can also refer to VMInterface
        required=False,
        to_field_name='name',
        help_text='Assigned interface'
    )
    is_primary = forms.BooleanField(
        help_text='Make this the primary IP for the assigned device',
        required=False
    )

    class Meta:
        model = IPAddress
        fields = [
            'address', 'vrf', 'tenant', 'status', 'role', 'device', 'virtual_machine', 'interface', 'is_primary',
            'dns_name', 'description',
        ]

    def __init__(self, data=None, *args, **kwargs):
        super().__init__(data, *args, **kwargs)

        if data:

            # Limit interface queryset by assigned device
            if data.get('device'):
                self.fields['interface'].queryset = Interface.objects.filter(
                    **{f"device__{self.fields['device'].to_field_name}": data['device']}
                )

            # Limit interface queryset by assigned device
            elif data.get('virtual_machine'):
                self.fields['interface'].queryset = VMInterface.objects.filter(
                    **{f"virtual_machine__{self.fields['virtual_machine'].to_field_name}": data['virtual_machine']}
                )

    def clean(self):
        super().clean()

        device = self.cleaned_data.get('device')
        virtual_machine = self.cleaned_data.get('virtual_machine')
        is_primary = self.cleaned_data.get('is_primary')

        # Validate is_primary
        if is_primary and not device and not virtual_machine:
            raise forms.ValidationError("No device or virtual machine specified; cannot set as primary IP")

    def save(self, *args, **kwargs):

        # Set interface assignment
        if self.cleaned_data['interface']:
            self.instance.assigned_object = self.cleaned_data['interface']

        ipaddress = super().save(*args, **kwargs)

        # Set as primary for device/VM
        if self.cleaned_data['is_primary']:
            parent = self.cleaned_data['device'] or self.cleaned_data['virtual_machine']
            if self.instance.address.version == 4:
                parent.primary_ip4 = ipaddress
            elif self.instance.address.version == 6:
                parent.primary_ip6 = ipaddress
            parent.save()

        return ipaddress


class IPAddressBulkEditForm(BootstrapMixin, AddRemoveTagsForm, CustomFieldBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=IPAddress.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
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
        widget=StaticSelect2()
    )
    role = forms.ChoiceField(
        choices=add_blank_choice(IPAddressRoleChoices),
        required=False,
        widget=StaticSelect2()
    )
    dns_name = forms.CharField(
        max_length=255,
        required=False
    )
    description = forms.CharField(
        max_length=100,
        required=False
    )

    class Meta:
        nullable_fields = [
            'vrf', 'role', 'tenant', 'dns_name', 'description',
        ]


class IPAddressAssignForm(BootstrapMixin, forms.Form):
    vrf_id = DynamicModelChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label='VRF',
        empty_label='Global'
    )
    q = forms.CharField(
        required=False,
        label='Search',
    )


class IPAddressFilterForm(BootstrapMixin, TenancyFilterForm, CustomFieldFilterForm):
    model = IPAddress
    field_order = [
        'q', 'parent', 'family', 'mask_length', 'vrf_id', 'present_in_vrf_id', 'status', 'role',
        'assigned_to_interface', 'tenant_group_id', 'tenant_id',
    ]
    q = forms.CharField(
        required=False,
        label=_('Search')
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
        widget=StaticSelect2()
    )
    mask_length = forms.ChoiceField(
        required=False,
        choices=IPADDRESS_MASK_LENGTH_CHOICES,
        label=_('Mask length'),
        widget=StaticSelect2()
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
        choices=IPAddressStatusChoices,
        required=False,
        widget=StaticSelect2Multiple()
    )
    role = forms.MultipleChoiceField(
        choices=IPAddressRoleChoices,
        required=False,
        widget=StaticSelect2Multiple()
    )
    assigned_to_interface = forms.NullBooleanField(
        required=False,
        label=_('Assigned to an interface'),
        widget=StaticSelect2(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    tag = TagFilterField(model)


#
# VLAN groups
#

class VLANGroupForm(BootstrapMixin, CustomFieldModelForm):
    scope_type = ContentTypeChoiceField(
        queryset=ContentType.objects.filter(model__in=VLANGROUP_SCOPE_TYPES),
        required=False,
        widget=StaticSelect2
    )
    region = DynamicModelChoiceField(
        queryset=Region.objects.all(),
        required=False,
        initial_params={
            'sites': '$site'
        }
    )
    sitegroup = DynamicModelChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False,
        initial_params={
            'sites': '$site'
        },
        label='Site group'
    )
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        initial_params={
            'locations': '$location'
        },
        query_params={
            'region_id': '$region',
            'group_id': '$sitegroup',
        }
    )
    location = DynamicModelChoiceField(
        queryset=Location.objects.all(),
        required=False,
        initial_params={
            'racks': '$rack'
        },
        query_params={
            'site_id': '$site',
        }
    )
    rack = DynamicModelChoiceField(
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
        initial_params={
            'clusters': '$cluster'
        },
        label='Cluster group'
    )
    cluster = DynamicModelChoiceField(
        queryset=Cluster.objects.all(),
        required=False,
        query_params={
            'group_id': '$clustergroup',
        }
    )
    slug = SlugField()

    class Meta:
        model = VLANGroup
        fields = [
            'name', 'slug', 'description', 'scope_type', 'region', 'sitegroup', 'site', 'location', 'rack',
            'clustergroup', 'cluster',
        ]
        widgets = {
            'scope_type': StaticSelect2,
        }

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        initial = kwargs.get('initial', {})

        if instance is not None and instance.scope:
            initial[instance.scope_type.model] = instance.scope

            kwargs['initial'] = initial

        super().__init__(*args, **kwargs)

    def clean(self):
        super().clean()

        # Assign scope based on scope_type
        if self.cleaned_data.get('scope_type'):
            scope_field = self.cleaned_data['scope_type'].model
            self.instance.scope = self.cleaned_data.get(scope_field)
        else:
            self.instance.scope_id = None


class VLANGroupCSVForm(CustomFieldModelCSVForm):
    site = CSVModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Assigned site'
    )
    slug = SlugField()

    class Meta:
        model = VLANGroup
        fields = VLANGroup.csv_headers


class VLANGroupBulkEditForm(BootstrapMixin, CustomFieldBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=VLANGroup.objects.all(),
        widget=forms.MultipleHiddenInput
    )
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False
    )
    description = forms.CharField(
        max_length=200,
        required=False
    )

    class Meta:
        nullable_fields = ['site', 'description']


class VLANGroupFilterForm(BootstrapMixin, forms.Form):
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


#
# VLANs
#

class VLANForm(BootstrapMixin, TenancyForm, CustomFieldModelForm):
    # VLANGroup assignment fields
    scope_type = forms.ChoiceField(
        choices=(
            ('', ''),
            ('dcim.region', 'Region'),
            ('dcim.sitegroup', 'Site group'),
            ('dcim.site', 'Site'),
            ('dcim.location', 'Location'),
            ('dcim.rack', 'Rack'),
            ('virtualization.clustergroup', 'Cluster group'),
            ('virtualization.cluster', 'Cluster'),
        ),
        required=False,
        widget=StaticSelect2,
        label='Group scope'
    )
    group = DynamicModelChoiceField(
        queryset=VLANGroup.objects.all(),
        required=False,
        query_params={
            'scope_type': '$scope_type',
        },
        label='VLAN Group'
    )

    # Site assignment fields
    region = DynamicModelChoiceField(
        queryset=Region.objects.all(),
        required=False,
        initial_params={
            'sites': '$site'
        },
        label='Region'
    )
    sitegroup = DynamicModelChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False,
        initial_params={
            'sites': '$site'
        },
        label='Site group'
    )
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        null_option='None',
        query_params={
            'region_id': '$region',
            'group_id': '$sitegroup',
        }
    )

    # Other fields
    role = DynamicModelChoiceField(
        queryset=Role.objects.all(),
        required=False
    )
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = VLAN
        fields = [
            'site', 'group', 'vid', 'name', 'status', 'role', 'description', 'tenant_group', 'tenant', 'tags',
        ]
        help_texts = {
            'site': "Leave blank if this VLAN spans multiple sites",
            'group': "VLAN group (optional)",
            'vid': "Configured VLAN ID",
            'name': "Configured VLAN name",
            'status': "Operational status of this VLAN",
            'role': "The primary function of this VLAN",
        }
        widgets = {
            'status': StaticSelect2(),
        }


class VLANCSVForm(CustomFieldModelCSVForm):
    site = CSVModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Assigned site'
    )
    group = CSVModelChoiceField(
        queryset=VLANGroup.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Assigned VLAN group'
    )
    tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        to_field_name='name',
        required=False,
        help_text='Assigned tenant'
    )
    status = CSVChoiceField(
        choices=VLANStatusChoices,
        help_text='Operational status'
    )
    role = CSVModelChoiceField(
        queryset=Role.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Functional role'
    )

    class Meta:
        model = VLAN
        fields = VLAN.csv_headers
        help_texts = {
            'vid': 'Numeric VLAN ID (1-4095)',
            'name': 'VLAN name',
        }


class VLANBulkEditForm(BootstrapMixin, AddRemoveTagsForm, CustomFieldBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=VLAN.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
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
        widget=StaticSelect2()
    )
    role = DynamicModelChoiceField(
        queryset=Role.objects.all(),
        required=False
    )
    description = forms.CharField(
        max_length=100,
        required=False
    )

    class Meta:
        nullable_fields = [
            'site', 'group', 'tenant', 'role', 'description',
        ]


class VLANFilterForm(BootstrapMixin, TenancyFilterForm, CustomFieldFilterForm):
    model = VLAN
    field_order = [
        'q', 'region_id', 'site_group_id', 'site_id', 'group_id', 'status', 'role_id', 'tenant_group_id', 'tenant_id',
    ]
    q = forms.CharField(
        required=False,
        label='Search'
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
    status = forms.MultipleChoiceField(
        choices=VLANStatusChoices,
        required=False,
        widget=StaticSelect2Multiple()
    )
    role_id = DynamicModelMultipleChoiceField(
        queryset=Role.objects.all(),
        required=False,
        null_option='None',
        label=_('Role')
    )
    tag = TagFilterField(model)


#
# Services
#

class ServiceForm(BootstrapMixin, CustomFieldModelForm):
    ports = NumericArrayField(
        base_field=forms.IntegerField(
            min_value=SERVICE_PORT_MIN,
            max_value=SERVICE_PORT_MAX
        ),
        help_text="Comma-separated list of one or more port numbers. A range may be specified using a hyphen."
    )
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = Service
        fields = [
            'name', 'protocol', 'ports', 'ipaddresses', 'description', 'tags',
        ]
        help_texts = {
            'ipaddresses': "IP address assignment is optional. If no IPs are selected, the service is assumed to be "
                           "reachable via all IPs assigned to the device.",
        }
        widgets = {
            'protocol': StaticSelect2(),
            'ipaddresses': StaticSelect2Multiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Limit IP address choices to those assigned to interfaces of the parent device/VM
        if self.instance.device:
            self.fields['ipaddresses'].queryset = IPAddress.objects.filter(
                interface__in=self.instance.device.vc_interfaces().values_list('id', flat=True)
            )
        elif self.instance.virtual_machine:
            self.fields['ipaddresses'].queryset = IPAddress.objects.filter(
                vminterface__in=self.instance.virtual_machine.interfaces.values_list('id', flat=True)
            )
        else:
            self.fields['ipaddresses'].choices = []


class ServiceFilterForm(BootstrapMixin, CustomFieldFilterForm):
    model = Service
    q = forms.CharField(
        required=False,
        label=_('Search')
    )
    protocol = forms.ChoiceField(
        choices=add_blank_choice(ServiceProtocolChoices),
        required=False,
        widget=StaticSelect2Multiple()
    )
    port = forms.IntegerField(
        required=False,
    )
    tag = TagFilterField(model)


class ServiceCSVForm(CustomFieldModelCSVForm):
    device = CSVModelChoiceField(
        queryset=Device.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Required if not assigned to a VM'
    )
    virtual_machine = CSVModelChoiceField(
        queryset=VirtualMachine.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Required if not assigned to a device'
    )
    protocol = CSVChoiceField(
        choices=ServiceProtocolChoices,
        help_text='IP protocol'
    )

    class Meta:
        model = Service
        fields = Service.csv_headers


class ServiceBulkEditForm(BootstrapMixin, AddRemoveTagsForm, CustomFieldBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=Service.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
    protocol = forms.ChoiceField(
        choices=add_blank_choice(ServiceProtocolChoices),
        required=False,
        widget=StaticSelect2()
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

    class Meta:
        nullable_fields = [
            'description',
        ]
