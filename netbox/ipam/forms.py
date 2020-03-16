from django import forms
from django.core.exceptions import MultipleObjectsReturned
from django.core.validators import MaxValueValidator, MinValueValidator
from taggit.forms import TagField

from dcim.models import Device, Interface, Rack, Region, Site
from extras.forms import (
    AddRemoveTagsForm, CustomFieldBulkEditForm, CustomFieldModelCSVForm, CustomFieldModelForm, CustomFieldFilterForm,
)
from tenancy.forms import TenancyFilterForm, TenancyForm
from tenancy.models import Tenant
from utilities.forms import (
    add_blank_choice, APISelect, APISelectMultiple, BootstrapMixin, BulkEditNullBooleanSelect, CSVChoiceField,
    DatePicker, DynamicModelChoiceField, DynamicModelMultipleChoiceField, ExpandableIPAddressField,
    FlexibleModelChoiceField, ReturnURLForm, SlugField, StaticSelect2, StaticSelect2Multiple, TagFilterField,
    BOOLEAN_WITH_BLANK_CHOICES,
)
from virtualization.models import VirtualMachine
from .constants import *
from .choices import *
from .models import Aggregate, IPAddress, Prefix, RIR, Role, Service, VLAN, VLANGroup, VRF


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
    tags = TagField(
        required=False
    )

    class Meta:
        model = VRF
        fields = [
            'name', 'rd', 'enforce_unique', 'description', 'tenant_group', 'tenant', 'tags',
        ]
        labels = {
            'rd': "RD",
        }
        help_texts = {
            'rd': "Route distinguisher in any format",
        }


class VRFCSVForm(CustomFieldModelCSVForm):
    tenant = forms.ModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Name of assigned tenant',
        error_messages={
            'invalid_choice': 'Tenant not found.',
        }
    )

    class Meta:
        model = VRF
        fields = VRF.csv_headers
        help_texts = {
            'name': 'VRF name',
        }


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
    field_order = ['q', 'tenant_group', 'tenant']
    q = forms.CharField(
        required=False,
        label='Search'
    )
    tag = TagFilterField(model)


#
# RIRs
#

class RIRForm(BootstrapMixin, forms.ModelForm):
    slug = SlugField()

    class Meta:
        model = RIR
        fields = [
            'name', 'slug', 'is_private',
        ]


class RIRCSVForm(forms.ModelForm):
    slug = SlugField()

    class Meta:
        model = RIR
        fields = RIR.csv_headers
        help_texts = {
            'name': 'RIR name',
        }


class RIRFilterForm(BootstrapMixin, forms.Form):
    is_private = forms.NullBooleanField(
        required=False,
        label='Private',
        widget=StaticSelect2(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )


#
# Aggregates
#

class AggregateForm(BootstrapMixin, CustomFieldModelForm):
    rir = DynamicModelChoiceField(
        queryset=RIR.objects.all()
    )
    tags = TagField(
        required=False
    )

    class Meta:
        model = Aggregate
        fields = [
            'prefix', 'rir', 'date_added', 'description', 'tags',
        ]
        help_texts = {
            'prefix': "IPv4 or IPv6 network",
            'rir': "Regional Internet Registry responsible for this prefix",
        }
        widgets = {
            'date_added': DatePicker(),
        }


class AggregateCSVForm(CustomFieldModelCSVForm):
    rir = forms.ModelChoiceField(
        queryset=RIR.objects.all(),
        to_field_name='name',
        help_text='Name of parent RIR',
        error_messages={
            'invalid_choice': 'RIR not found.',
        }
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


class AggregateFilterForm(BootstrapMixin, CustomFieldFilterForm):
    model = Aggregate
    q = forms.CharField(
        required=False,
        label='Search'
    )
    family = forms.ChoiceField(
        required=False,
        choices=add_blank_choice(IPAddressFamilyChoices),
        label='Address family',
        widget=StaticSelect2()
    )
    rir = DynamicModelMultipleChoiceField(
        queryset=RIR.objects.all(),
        to_field_name='slug',
        required=False,
        label='RIR',
        widget=APISelectMultiple(
            value_field="slug",
        )
    )
    tag = TagFilterField(model)


#
# Roles
#

class RoleForm(BootstrapMixin, forms.ModelForm):
    slug = SlugField()

    class Meta:
        model = Role
        fields = [
            'name', 'slug', 'weight', 'description',
        ]


class RoleCSVForm(forms.ModelForm):
    slug = SlugField()

    class Meta:
        model = Role
        fields = Role.csv_headers
        help_texts = {
            'name': 'Role name',
        }


#
# Prefixes
#

class PrefixForm(BootstrapMixin, TenancyForm, CustomFieldModelForm):
    vrf = DynamicModelChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label='VRF'
    )
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        widget=APISelect(
            filter_for={
                'vlan_group': 'site_id',
                'vlan': 'site_id',
            },
            attrs={
                'nullable': 'true',
            }
        )
    )
    vlan_group = DynamicModelChoiceField(
        queryset=VLANGroup.objects.all(),
        required=False,
        label='VLAN group',
        widget=APISelect(
            filter_for={
                'vlan': 'group_id'
            },
            attrs={
                'nullable': 'true',
            }
        )
    )
    vlan = DynamicModelChoiceField(
        queryset=VLAN.objects.all(),
        required=False,
        label='VLAN',
        widget=APISelect(
            display_field='display_name'
        )
    )
    role = DynamicModelChoiceField(
        queryset=Role.objects.all(),
        required=False
    )
    tags = TagField(required=False)

    class Meta:
        model = Prefix
        fields = [
            'prefix', 'vrf', 'site', 'vlan', 'status', 'role', 'is_pool', 'description', 'tenant_group', 'tenant',
            'tags',
        ]
        widgets = {
            'status': StaticSelect2(),
        }

    def __init__(self, *args, **kwargs):

        # Initialize helper selectors
        instance = kwargs.get('instance')
        initial = kwargs.get('initial', {}).copy()
        if instance and instance.vlan is not None:
            initial['vlan_group'] = instance.vlan.group
        kwargs['initial'] = initial

        super().__init__(*args, **kwargs)

        self.fields['vrf'].empty_label = 'Global'


class PrefixCSVForm(CustomFieldModelCSVForm):
    vrf = FlexibleModelChoiceField(
        queryset=VRF.objects.all(),
        to_field_name='rd',
        required=False,
        help_text='Route distinguisher of parent VRF (or {ID})',
        error_messages={
            'invalid_choice': 'VRF not found.',
        }
    )
    tenant = forms.ModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Name of assigned tenant',
        error_messages={
            'invalid_choice': 'Tenant not found.',
        }
    )
    site = forms.ModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Name of parent site',
        error_messages={
            'invalid_choice': 'Site not found.',
        }
    )
    vlan_group = forms.CharField(
        help_text='Group name of assigned VLAN',
        required=False
    )
    vlan_vid = forms.IntegerField(
        help_text='Numeric ID of assigned VLAN',
        required=False
    )
    status = CSVChoiceField(
        choices=PrefixStatusChoices,
        help_text='Operational status'
    )
    role = forms.ModelChoiceField(
        queryset=Role.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Functional role',
        error_messages={
            'invalid_choice': 'Invalid role.',
        }
    )

    class Meta:
        model = Prefix
        fields = Prefix.csv_headers

    def clean(self):

        super().clean()

        site = self.cleaned_data.get('site')
        vlan_group = self.cleaned_data.get('vlan_group')
        vlan_vid = self.cleaned_data.get('vlan_vid')

        # Validate VLAN
        if vlan_group and vlan_vid:
            try:
                self.instance.vlan = VLAN.objects.get(site=site, group__name=vlan_group, vid=vlan_vid)
            except VLAN.DoesNotExist:
                if site:
                    raise forms.ValidationError("VLAN {} not found in site {} group {}".format(
                        vlan_vid, site, vlan_group
                    ))
                else:
                    raise forms.ValidationError("Global VLAN {} not found in group {}".format(vlan_vid, vlan_group))
            except MultipleObjectsReturned:
                raise forms.ValidationError(
                    "Multiple VLANs with VID {} found in group {}".format(vlan_vid, vlan_group)
                )
        elif vlan_vid:
            try:
                self.instance.vlan = VLAN.objects.get(site=site, group__isnull=True, vid=vlan_vid)
            except VLAN.DoesNotExist:
                if site:
                    raise forms.ValidationError("VLAN {} not found in site {}".format(vlan_vid, site))
                else:
                    raise forms.ValidationError("Global VLAN {} not found".format(vlan_vid))
            except MultipleObjectsReturned:
                raise forms.ValidationError("Multiple VLANs with VID {} found".format(vlan_vid))


class PrefixBulkEditForm(BootstrapMixin, AddRemoveTagsForm, CustomFieldBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=Prefix.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False
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
        'q', 'within_include', 'family', 'mask_length', 'vrf_id', 'status', 'region', 'site', 'role', 'tenant_group',
        'tenant', 'is_pool', 'expand',
    ]
    q = forms.CharField(
        required=False,
        label='Search'
    )
    within_include = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Prefix',
            }
        ),
        label='Search within'
    )
    family = forms.ChoiceField(
        required=False,
        choices=add_blank_choice(IPAddressFamilyChoices),
        label='Address family',
        widget=StaticSelect2()
    )
    mask_length = forms.ChoiceField(
        required=False,
        choices=PREFIX_MASK_LENGTH_CHOICES,
        label='Mask length',
        widget=StaticSelect2()
    )
    vrf_id = DynamicModelMultipleChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label='VRF',
        widget=APISelectMultiple(
            null_option=True,
        )
    )
    status = forms.MultipleChoiceField(
        choices=PrefixStatusChoices,
        required=False,
        widget=StaticSelect2Multiple()
    )
    region = DynamicModelMultipleChoiceField(
        queryset=Region.objects.all(),
        to_field_name='slug',
        required=False,
        widget=APISelectMultiple(
            value_field="slug",
            filter_for={
                'site': 'region'
            }
        )
    )
    site = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        to_field_name='slug',
        required=False,
        widget=APISelectMultiple(
            value_field="slug",
            null_option=True,
        )
    )
    role = DynamicModelMultipleChoiceField(
        queryset=Role.objects.all(),
        to_field_name='slug',
        required=False,
        widget=APISelectMultiple(
            value_field="slug",
            null_option=True,
        )
    )
    is_pool = forms.NullBooleanField(
        required=False,
        label='Is a pool',
        widget=StaticSelect2(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    expand = forms.BooleanField(
        required=False,
        label='Expand prefix hierarchy'
    )
    tag = TagFilterField(model)


#
# IP addresses
#

class IPAddressForm(BootstrapMixin, TenancyForm, ReturnURLForm, CustomFieldModelForm):
    interface = forms.ModelChoiceField(
        queryset=Interface.objects.all(),
        required=False
    )
    vrf = DynamicModelChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label='VRF'
    )
    nat_site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        label='Site',
        widget=APISelect(
            filter_for={
                'nat_rack': 'site_id',
                'nat_device': 'site_id'
            }
        )
    )
    nat_rack = DynamicModelChoiceField(
        queryset=Rack.objects.all(),
        required=False,
        label='Rack',
        widget=APISelect(
            display_field='display_name',
            filter_for={
                'nat_device': 'rack_id'
            },
            attrs={
                'nullable': 'true'
            }
        )
    )
    nat_device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        required=False,
        label='Device',
        widget=APISelect(
            display_field='display_name',
            filter_for={
                'nat_inside': 'device_id'
            }
        )
    )
    nat_vrf = DynamicModelChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label='VRF',
        widget=APISelect(
            filter_for={
                'nat_inside': 'vrf_id'
            }
        )
    )
    nat_inside = DynamicModelChoiceField(
        queryset=IPAddress.objects.all(),
        required=False,
        label='IP Address',
        widget=APISelect(
            display_field='address'
        )
    )
    primary_for_parent = forms.BooleanField(
        required=False,
        label='Make this the primary IP for the device/VM'
    )
    tags = TagField(
        required=False
    )

    class Meta:
        model = IPAddress
        fields = [
            'address', 'vrf', 'status', 'role', 'dns_name', 'description', 'interface', 'primary_for_parent',
            'nat_site', 'nat_rack', 'nat_inside', 'tenant_group', 'tenant', 'tags',
        ]
        widgets = {
            'status': StaticSelect2(),
            'role': StaticSelect2(),
        }

    def __init__(self, *args, **kwargs):

        # Initialize helper selectors
        instance = kwargs.get('instance')
        initial = kwargs.get('initial', {}).copy()
        if instance and instance.nat_inside and instance.nat_inside.device is not None:
            initial['nat_site'] = instance.nat_inside.device.site
            initial['nat_rack'] = instance.nat_inside.device.rack
            initial['nat_device'] = instance.nat_inside.device
        kwargs['initial'] = initial

        super().__init__(*args, **kwargs)

        self.fields['vrf'].empty_label = 'Global'

        # Limit interface selections to those belonging to the parent device/VM
        if self.instance and self.instance.interface:
            self.fields['interface'].queryset = Interface.objects.filter(
                device=self.instance.interface.device, virtual_machine=self.instance.interface.virtual_machine
            )
        else:
            self.fields['interface'].choices = []

        # Initialize primary_for_parent if IP address is already assigned
        if self.instance.pk and self.instance.interface is not None:
            parent = self.instance.interface.parent
            if (
                self.instance.address.version == 4 and parent.primary_ip4_id == self.instance.pk or
                self.instance.address.version == 6 and parent.primary_ip6_id == self.instance.pk
            ):
                self.initial['primary_for_parent'] = True

    def clean(self):
        super().clean()

        # Primary IP assignment is only available if an interface has been assigned.
        if self.cleaned_data.get('primary_for_parent') and not self.cleaned_data.get('interface'):
            self.add_error(
                'primary_for_parent', "Only IP addresses assigned to an interface can be designated as primary IPs."
            )

    def save(self, *args, **kwargs):

        ipaddress = super().save(*args, **kwargs)

        # Assign/clear this IPAddress as the primary for the associated Device/VirtualMachine.
        if self.cleaned_data['primary_for_parent']:
            parent = self.cleaned_data['interface'].parent
            if ipaddress.address.version == 4:
                parent.primary_ip4 = ipaddress
            else:
                parent.primary_ip6 = ipaddress
            parent.save()
        elif self.cleaned_data['interface']:
            parent = self.cleaned_data['interface'].parent
            if ipaddress.address.version == 4 and parent.primary_ip4 == ipaddress:
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

    class Meta:
        model = IPAddress
        fields = [
            'address', 'vrf', 'status', 'role', 'dns_name', 'description', 'tenant_group', 'tenant',
        ]
        widgets = {
            'status': StaticSelect2(),
            'role': StaticSelect2(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['vrf'].empty_label = 'Global'


class IPAddressCSVForm(CustomFieldModelCSVForm):
    vrf = FlexibleModelChoiceField(
        queryset=VRF.objects.all(),
        to_field_name='rd',
        required=False,
        help_text='Route distinguisher of parent VRF (or {ID})',
        error_messages={
            'invalid_choice': 'VRF not found.',
        }
    )
    tenant = forms.ModelChoiceField(
        queryset=Tenant.objects.all(),
        to_field_name='name',
        required=False,
        help_text='Name of the assigned tenant',
        error_messages={
            'invalid_choice': 'Tenant not found.',
        }
    )
    status = CSVChoiceField(
        choices=IPAddressStatusChoices,
        help_text='Operational status'
    )
    role = CSVChoiceField(
        choices=IPAddressRoleChoices,
        required=False,
        help_text='Functional role'
    )
    device = FlexibleModelChoiceField(
        queryset=Device.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Name or ID of assigned device',
        error_messages={
            'invalid_choice': 'Device not found.',
        }
    )
    virtual_machine = forms.ModelChoiceField(
        queryset=VirtualMachine.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Name of assigned virtual machine',
        error_messages={
            'invalid_choice': 'Virtual machine not found.',
        }
    )
    interface_name = forms.CharField(
        help_text='Name of assigned interface',
        required=False
    )
    is_primary = forms.BooleanField(
        help_text='Make this the primary IP for the assigned device',
        required=False
    )

    class Meta:
        model = IPAddress
        fields = IPAddress.csv_headers

    def clean(self):
        super().clean()

        device = self.cleaned_data.get('device')
        virtual_machine = self.cleaned_data.get('virtual_machine')
        interface_name = self.cleaned_data.get('interface_name')
        is_primary = self.cleaned_data.get('is_primary')

        # Validate interface
        if interface_name and device:
            try:
                self.instance.interface = Interface.objects.get(device=device, name=interface_name)
            except Interface.DoesNotExist:
                raise forms.ValidationError("Invalid interface {} for device {}".format(
                    interface_name, device
                ))
        elif interface_name and virtual_machine:
            try:
                self.instance.interface = Interface.objects.get(virtual_machine=virtual_machine, name=interface_name)
            except Interface.DoesNotExist:
                raise forms.ValidationError("Invalid interface {} for virtual machine {}".format(
                    interface_name, virtual_machine
                ))
        elif interface_name:
            raise forms.ValidationError("Interface given ({}) but parent device/virtual machine not specified".format(
                interface_name
            ))
        elif device:
            raise forms.ValidationError("Device specified ({}) but interface missing".format(device))
        elif virtual_machine:
            raise forms.ValidationError("Virtual machine specified ({}) but interface missing".format(virtual_machine))

        # Validate is_primary
        if is_primary and not device and not virtual_machine:
            raise forms.ValidationError("No device or virtual machine specified; cannot set as primary IP")

    def save(self, *args, **kwargs):

        # Set interface
        if self.cleaned_data['device'] and self.cleaned_data['interface_name']:
            self.instance.interface = Interface.objects.get(
                device=self.cleaned_data['device'],
                name=self.cleaned_data['interface_name']
            )
        elif self.cleaned_data['virtual_machine'] and self.cleaned_data['interface_name']:
            self.instance.interface = Interface.objects.get(
                virtual_machine=self.cleaned_data['virtual_machine'],
                name=self.cleaned_data['interface_name']
            )

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
        'q', 'parent', 'family', 'mask_length', 'vrf_id', 'status', 'role', 'assigned_to_interface', 'tenant_group',
        'tenant',
    ]
    q = forms.CharField(
        required=False,
        label='Search'
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
        label='Address family',
        widget=StaticSelect2()
    )
    mask_length = forms.ChoiceField(
        required=False,
        choices=IPADDRESS_MASK_LENGTH_CHOICES,
        label='Mask length',
        widget=StaticSelect2()
    )
    vrf_id = DynamicModelMultipleChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label='VRF',
        widget=APISelectMultiple(
            null_option=True,
        )
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
        label='Assigned to an interface',
        widget=StaticSelect2(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    tag = TagFilterField(model)


#
# VLAN groups
#

class VLANGroupForm(BootstrapMixin, forms.ModelForm):
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False
    )
    slug = SlugField()

    class Meta:
        model = VLANGroup
        fields = [
            'site', 'name', 'slug',
        ]


class VLANGroupCSVForm(forms.ModelForm):
    site = forms.ModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Name of parent site',
        error_messages={
            'invalid_choice': 'Site not found.',
        }
    )
    slug = SlugField()

    class Meta:
        model = VLANGroup
        fields = VLANGroup.csv_headers
        help_texts = {
            'name': 'Name of VLAN group',
        }


class VLANGroupFilterForm(BootstrapMixin, forms.Form):
    region = DynamicModelMultipleChoiceField(
        queryset=Region.objects.all(),
        to_field_name='slug',
        required=False,
        widget=APISelectMultiple(
            value_field="slug",
            filter_for={
                'site': 'region',
            }
        )
    )
    site = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        to_field_name='slug',
        required=False,
        widget=APISelectMultiple(
            value_field="slug",
            null_option=True,
        )
    )


#
# VLANs
#

class VLANForm(BootstrapMixin, TenancyForm, CustomFieldModelForm):
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        widget=APISelect(
            filter_for={
                'group': 'site_id'
            },
            attrs={
                'nullable': 'true',
            }
        )
    )
    group = DynamicModelChoiceField(
        queryset=VLANGroup.objects.all(),
        required=False
    )
    role = DynamicModelChoiceField(
        queryset=Role.objects.all(),
        required=False
    )
    tags = TagField(required=False)

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
    site = forms.ModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Name of parent site',
        error_messages={
            'invalid_choice': 'Site not found.',
        }
    )
    group_name = forms.CharField(
        help_text='Name of VLAN group',
        required=False
    )
    tenant = forms.ModelChoiceField(
        queryset=Tenant.objects.all(),
        to_field_name='name',
        required=False,
        help_text='Name of assigned tenant',
        error_messages={
            'invalid_choice': 'Tenant not found.',
        }
    )
    status = CSVChoiceField(
        choices=VLANStatusChoices,
        help_text='Operational status'
    )
    role = forms.ModelChoiceField(
        queryset=Role.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Functional role',
        error_messages={
            'invalid_choice': 'Invalid role.',
        }
    )

    class Meta:
        model = VLAN
        fields = VLAN.csv_headers
        help_texts = {
            'vid': 'Numeric VLAN ID (1-4095)',
            'name': 'VLAN name',
        }

    def clean(self):
        super().clean()

        site = self.cleaned_data.get('site')
        group_name = self.cleaned_data.get('group_name')

        # Validate VLAN group
        if group_name:
            try:
                self.instance.group = VLANGroup.objects.get(site=site, name=group_name)
            except VLANGroup.DoesNotExist:
                if site:
                    raise forms.ValidationError(
                        "VLAN group {} not found for site {}".format(group_name, site)
                    )
                else:
                    raise forms.ValidationError(
                        "Global VLAN group {} not found".format(group_name)
                    )


class VLANBulkEditForm(BootstrapMixin, AddRemoveTagsForm, CustomFieldBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=VLAN.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False
    )
    group = DynamicModelChoiceField(
        queryset=VLANGroup.objects.all(),
        required=False
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
    field_order = ['q', 'region', 'site', 'group_id', 'status', 'role', 'tenant_group', 'tenant']
    q = forms.CharField(
        required=False,
        label='Search'
    )
    region = DynamicModelMultipleChoiceField(
        queryset=Region.objects.all(),
        to_field_name='slug',
        required=False,
        widget=APISelectMultiple(
            value_field="slug",
            filter_for={
                'site': 'region',
                'group_id': 'region'
            }
        )
    )
    site = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        to_field_name='slug',
        required=False,
        widget=APISelectMultiple(
            value_field="slug",
            null_option=True,
        )
    )
    group_id = DynamicModelMultipleChoiceField(
        queryset=VLANGroup.objects.all(),
        required=False,
        label='VLAN group',
        widget=APISelectMultiple(
            null_option=True,
        )
    )
    status = forms.MultipleChoiceField(
        choices=VLANStatusChoices,
        required=False,
        widget=StaticSelect2Multiple()
    )
    role = DynamicModelMultipleChoiceField(
        queryset=Role.objects.all(),
        to_field_name='slug',
        required=False,
        widget=APISelectMultiple(
            value_field="slug",
            null_option=True,
        )
    )
    tag = TagFilterField(model)


#
# Services
#

class ServiceForm(BootstrapMixin, CustomFieldModelForm):
    port = forms.IntegerField(
        min_value=SERVICE_PORT_MIN,
        max_value=SERVICE_PORT_MAX
    )
    tags = TagField(
        required=False
    )

    class Meta:
        model = Service
        fields = [
            'name', 'protocol', 'port', 'ipaddresses', 'description', 'tags',
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
            vc_interface_ids = [i['id'] for i in self.instance.device.vc_interfaces.values('id')]
            self.fields['ipaddresses'].queryset = IPAddress.objects.filter(
                interface_id__in=vc_interface_ids
            )
        elif self.instance.virtual_machine:
            self.fields['ipaddresses'].queryset = IPAddress.objects.filter(
                interface__virtual_machine=self.instance.virtual_machine
            )
        else:
            self.fields['ipaddresses'].choices = []


class ServiceFilterForm(BootstrapMixin, CustomFieldFilterForm):
    model = Service
    q = forms.CharField(
        required=False,
        label='Search'
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
    device = FlexibleModelChoiceField(
        queryset=Device.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Name or ID of device',
        error_messages={
            'invalid_choice': 'Device not found.',
        }
    )
    virtual_machine = FlexibleModelChoiceField(
        queryset=VirtualMachine.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Name or ID of virtual machine',
        error_messages={
            'invalid_choice': 'Virtual machine not found.',
        }
    )
    protocol = CSVChoiceField(
        choices=ServiceProtocolChoices,
        help_text='IP protocol'
    )

    class Meta:
        model = Service
        fields = Service.csv_headers
        help_texts = {
        }


class ServiceBulkEditForm(BootstrapMixin, CustomFieldBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=Service.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
    protocol = forms.ChoiceField(
        choices=add_blank_choice(ServiceProtocolChoices),
        required=False,
        widget=StaticSelect2()
    )
    port = forms.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(65535),
        ],
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
