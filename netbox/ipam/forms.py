from __future__ import unicode_literals

from django import forms
from django.core.exceptions import MultipleObjectsReturned
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import Count
from taggit.forms import TagField

from dcim.models import Site, Rack, Device, Interface
from extras.forms import AddRemoveTagsForm, CustomFieldForm, CustomFieldBulkEditForm, CustomFieldFilterForm
from tenancy.forms import TenancyForm
from tenancy.models import Tenant
from utilities.forms import (
    AnnotatedMultipleChoiceField, APISelect, BootstrapMixin, BulkEditNullBooleanSelect, ChainedModelChoiceField,
    CSVChoiceField, ExpandableIPAddressField, FilterChoiceField, FlexibleModelChoiceField, Livesearch, ReturnURLForm,
    SlugField, add_blank_choice,
)
from virtualization.models import VirtualMachine
from .constants import (
    IP_PROTOCOL_CHOICES, IPADDRESS_ROLE_CHOICES, IPADDRESS_STATUS_CHOICES, PREFIX_STATUS_CHOICES, VLAN_STATUS_CHOICES,
)
from .models import Aggregate, IPAddress, Prefix, RIR, Role, Service, VLAN, VLANGroup, VRF

IP_FAMILY_CHOICES = [
    ('', 'All'),
    (4, 'IPv4'),
    (6, 'IPv6'),
]

PREFIX_MASK_LENGTH_CHOICES = add_blank_choice([(i, i) for i in range(1, 128)])
IPADDRESS_MASK_LENGTH_CHOICES = add_blank_choice([(i, i) for i in range(1, 129)])


#
# VRFs
#

class VRFForm(BootstrapMixin, TenancyForm, CustomFieldForm):
    tags = TagField(required=False)

    class Meta:
        model = VRF
        fields = ['name', 'rd', 'enforce_unique', 'description', 'tenant_group', 'tenant', 'tags']
        labels = {
            'rd': "RD",
        }
        help_texts = {
            'rd': "Route distinguisher in any format",
        }


class VRFCSVForm(forms.ModelForm):
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
    pk = forms.ModelMultipleChoiceField(queryset=VRF.objects.all(), widget=forms.MultipleHiddenInput)
    tenant = forms.ModelChoiceField(queryset=Tenant.objects.all(), required=False)
    enforce_unique = forms.NullBooleanField(
        required=False, widget=BulkEditNullBooleanSelect, label='Enforce unique space'
    )
    description = forms.CharField(max_length=100, required=False)

    class Meta:
        nullable_fields = ['tenant', 'description']


class VRFFilterForm(BootstrapMixin, CustomFieldFilterForm):
    model = VRF
    q = forms.CharField(required=False, label='Search')
    tenant = FilterChoiceField(
        queryset=Tenant.objects.annotate(filter_count=Count('vrfs')),
        to_field_name='slug',
        null_label='-- None --'
    )


#
# RIRs
#

class RIRForm(BootstrapMixin, forms.ModelForm):
    slug = SlugField()

    class Meta:
        model = RIR
        fields = ['name', 'slug', 'is_private']


class RIRCSVForm(forms.ModelForm):
    slug = SlugField()

    class Meta:
        model = RIR
        fields = RIR.csv_headers
        help_texts = {
            'name': 'RIR name',
        }


class RIRFilterForm(BootstrapMixin, forms.Form):
    is_private = forms.NullBooleanField(required=False, label='Private', widget=forms.Select(choices=[
        ('', '---------'),
        ('True', 'Yes'),
        ('False', 'No'),
    ]))


#
# Aggregates
#

class AggregateForm(BootstrapMixin, CustomFieldForm):
    tags = TagField(required=False)

    class Meta:
        model = Aggregate
        fields = ['prefix', 'rir', 'date_added', 'description', 'tags']
        help_texts = {
            'prefix': "IPv4 or IPv6 network",
            'rir': "Regional Internet Registry responsible for this prefix",
            'date_added': "Format: YYYY-MM-DD",
        }


class AggregateCSVForm(forms.ModelForm):
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
    pk = forms.ModelMultipleChoiceField(queryset=Aggregate.objects.all(), widget=forms.MultipleHiddenInput)
    rir = forms.ModelChoiceField(queryset=RIR.objects.all(), required=False, label='RIR')
    date_added = forms.DateField(required=False)
    description = forms.CharField(max_length=100, required=False)

    class Meta:
        nullable_fields = ['date_added', 'description']


class AggregateFilterForm(BootstrapMixin, CustomFieldFilterForm):
    model = Aggregate
    q = forms.CharField(required=False, label='Search')
    family = forms.ChoiceField(required=False, choices=IP_FAMILY_CHOICES, label='Address Family')
    rir = FilterChoiceField(
        queryset=RIR.objects.annotate(filter_count=Count('aggregates')),
        to_field_name='slug',
        label='RIR'
    )


#
# Roles
#

class RoleForm(BootstrapMixin, forms.ModelForm):
    slug = SlugField()

    class Meta:
        model = Role
        fields = ['name', 'slug']


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

class PrefixForm(BootstrapMixin, TenancyForm, CustomFieldForm):
    site = forms.ModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        label='Site',
        widget=forms.Select(
            attrs={'filter-for': 'vlan_group', 'nullable': 'true'}
        )
    )
    vlan_group = ChainedModelChoiceField(
        queryset=VLANGroup.objects.all(),
        chains=(
            ('site', 'site'),
        ),
        required=False,
        label='VLAN group',
        widget=APISelect(
            api_url='/api/ipam/vlan-groups/?site_id={{site}}',
            attrs={'filter-for': 'vlan', 'nullable': 'true'}
        )
    )
    vlan = ChainedModelChoiceField(
        queryset=VLAN.objects.all(),
        chains=(
            ('site', 'site'),
            ('group', 'vlan_group'),
        ),
        required=False,
        label='VLAN',
        widget=APISelect(
            api_url='/api/ipam/vlans/?site_id={{site}}&group_id={{vlan_group}}', display_field='display_name'
        )
    )
    tags = TagField(required=False)

    class Meta:
        model = Prefix
        fields = [
            'prefix', 'vrf', 'site', 'vlan', 'status', 'role', 'is_pool', 'description', 'tenant_group', 'tenant',
            'tags',
        ]

    def __init__(self, *args, **kwargs):

        # Initialize helper selectors
        instance = kwargs.get('instance')
        initial = kwargs.get('initial', {}).copy()
        if instance and instance.vlan is not None:
            initial['vlan_group'] = instance.vlan.group
        kwargs['initial'] = initial

        super(PrefixForm, self).__init__(*args, **kwargs)

        self.fields['vrf'].empty_label = 'Global'


class PrefixCSVForm(forms.ModelForm):
    vrf = forms.ModelChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        to_field_name='rd',
        help_text='Route distinguisher of parent VRF',
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
        choices=PREFIX_STATUS_CHOICES,
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

        super(PrefixCSVForm, self).clean()

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
    pk = forms.ModelMultipleChoiceField(queryset=Prefix.objects.all(), widget=forms.MultipleHiddenInput)
    site = forms.ModelChoiceField(queryset=Site.objects.all(), required=False)
    vrf = forms.ModelChoiceField(queryset=VRF.objects.all(), required=False, label='VRF')
    tenant = forms.ModelChoiceField(queryset=Tenant.objects.all(), required=False)
    status = forms.ChoiceField(choices=add_blank_choice(PREFIX_STATUS_CHOICES), required=False)
    role = forms.ModelChoiceField(queryset=Role.objects.all(), required=False)
    is_pool = forms.NullBooleanField(required=False, widget=BulkEditNullBooleanSelect, label='Is a pool')
    description = forms.CharField(max_length=100, required=False)

    class Meta:
        nullable_fields = ['site', 'vrf', 'tenant', 'role', 'description']


class PrefixFilterForm(BootstrapMixin, CustomFieldFilterForm):
    model = Prefix
    q = forms.CharField(required=False, label='Search')
    within_include = forms.CharField(required=False, label='Search within', widget=forms.TextInput(attrs={
        'placeholder': 'Prefix',
    }))
    family = forms.ChoiceField(required=False, choices=IP_FAMILY_CHOICES, label='Address family')
    mask_length = forms.ChoiceField(required=False, choices=PREFIX_MASK_LENGTH_CHOICES, label='Mask length')
    vrf = FilterChoiceField(
        queryset=VRF.objects.annotate(filter_count=Count('prefixes')),
        to_field_name='rd',
        label='VRF',
        null_label='-- Global --'
    )
    tenant = FilterChoiceField(
        queryset=Tenant.objects.annotate(filter_count=Count('prefixes')),
        to_field_name='slug',
        null_label='-- None --'
    )
    status = AnnotatedMultipleChoiceField(
        choices=PREFIX_STATUS_CHOICES,
        annotate=Prefix.objects.all(),
        annotate_field='status',
        required=False
    )
    site = FilterChoiceField(
        queryset=Site.objects.annotate(filter_count=Count('prefixes')),
        to_field_name='slug',
        null_label='-- None --'
    )
    role = FilterChoiceField(
        queryset=Role.objects.annotate(filter_count=Count('prefixes')),
        to_field_name='slug',
        null_label='-- None --'
    )
    expand = forms.BooleanField(required=False, label='Expand prefix hierarchy')


#
# IP addresses
#

class IPAddressForm(BootstrapMixin, TenancyForm, ReturnURLForm, CustomFieldForm):
    interface = forms.ModelChoiceField(
        queryset=Interface.objects.all(),
        required=False
    )
    nat_site = forms.ModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        label='Site',
        widget=forms.Select(
            attrs={'filter-for': 'nat_rack'}
        )
    )
    nat_rack = ChainedModelChoiceField(
        queryset=Rack.objects.all(),
        chains=(
            ('site', 'nat_site'),
        ),
        required=False,
        label='Rack',
        widget=APISelect(
            api_url='/api/dcim/racks/?site_id={{nat_site}}',
            display_field='display_name',
            attrs={'filter-for': 'nat_device', 'nullable': 'true'}
        )
    )
    nat_device = ChainedModelChoiceField(
        queryset=Device.objects.all(),
        chains=(
            ('site', 'nat_site'),
            ('rack', 'nat_rack'),
        ),
        required=False,
        label='Device',
        widget=APISelect(
            api_url='/api/dcim/devices/?site_id={{nat_site}}&rack_id={{nat_rack}}',
            display_field='display_name',
            attrs={'filter-for': 'nat_inside'}
        )
    )
    nat_inside = ChainedModelChoiceField(
        queryset=IPAddress.objects.all(),
        chains=(
            ('interface__device', 'nat_device'),
        ),
        required=False,
        label='IP Address',
        widget=APISelect(
            api_url='/api/ipam/ip-addresses/?device_id={{nat_device}}',
            display_field='address'
        )
    )
    livesearch = forms.CharField(
        required=False,
        label='Search',
        widget=Livesearch(
            query_key='q',
            query_url='ipam-api:ipaddress-list',
            field_to_update='nat_inside',
            obj_label='address'
        )
    )
    primary_for_parent = forms.BooleanField(required=False, label='Make this the primary IP for the device/VM')
    tags = TagField(required=False)

    class Meta:
        model = IPAddress
        fields = [
            'address', 'vrf', 'status', 'role', 'description', 'interface', 'primary_for_parent', 'nat_site',
            'nat_rack', 'nat_inside', 'tenant_group', 'tenant', 'tags',
        ]

    def __init__(self, *args, **kwargs):

        # Initialize helper selectors
        instance = kwargs.get('instance')
        initial = kwargs.get('initial', {}).copy()
        if instance and instance.nat_inside and instance.nat_inside.device is not None:
            initial['nat_site'] = instance.nat_inside.device.site
            initial['nat_rack'] = instance.nat_inside.device.rack
            initial['nat_device'] = instance.nat_inside.device
        kwargs['initial'] = initial

        super(IPAddressForm, self).__init__(*args, **kwargs)

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
        super(IPAddressForm, self).clean()

        # Primary IP assignment is only available if an interface has been assigned.
        if self.cleaned_data.get('primary_for_parent') and not self.cleaned_data.get('interface'):
            self.add_error(
                'primary_for_parent', "Only IP addresses assigned to an interface can be designated as primary IPs."
            )

    def save(self, *args, **kwargs):

        ipaddress = super(IPAddressForm, self).save(*args, **kwargs)

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
    pattern = ExpandableIPAddressField(label='Address pattern')


class IPAddressBulkAddForm(BootstrapMixin, TenancyForm, CustomFieldForm):

    class Meta:
        model = IPAddress
        fields = ['address', 'vrf', 'status', 'role', 'description', 'tenant_group', 'tenant']

    def __init__(self, *args, **kwargs):
        super(IPAddressBulkAddForm, self).__init__(*args, **kwargs)
        self.fields['vrf'].empty_label = 'Global'


class IPAddressCSVForm(forms.ModelForm):
    vrf = forms.ModelChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        to_field_name='rd',
        help_text='Route distinguisher of the assigned VRF',
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
        choices=IPADDRESS_STATUS_CHOICES,
        help_text='Operational status'
    )
    role = CSVChoiceField(
        choices=IPADDRESS_ROLE_CHOICES,
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

        super(IPAddressCSVForm, self).clean()

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

        ipaddress = super(IPAddressCSVForm, self).save(*args, **kwargs)

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
    pk = forms.ModelMultipleChoiceField(queryset=IPAddress.objects.all(), widget=forms.MultipleHiddenInput)
    vrf = forms.ModelChoiceField(queryset=VRF.objects.all(), required=False, label='VRF')
    tenant = forms.ModelChoiceField(queryset=Tenant.objects.all(), required=False)
    status = forms.ChoiceField(choices=add_blank_choice(IPADDRESS_STATUS_CHOICES), required=False)
    role = forms.ChoiceField(choices=add_blank_choice(IPADDRESS_ROLE_CHOICES), required=False)
    description = forms.CharField(max_length=100, required=False)

    class Meta:
        nullable_fields = ['vrf', 'role', 'tenant', 'description']


class IPAddressAssignForm(BootstrapMixin, forms.Form):
    vrf = forms.ModelChoiceField(queryset=VRF.objects.all(), required=False, label='VRF', empty_label='Global')
    address = forms.CharField(label='IP Address')


class IPAddressFilterForm(BootstrapMixin, CustomFieldFilterForm):
    model = IPAddress
    q = forms.CharField(required=False, label='Search')
    parent = forms.CharField(required=False, label='Parent Prefix', widget=forms.TextInput(attrs={
        'placeholder': 'Prefix',
    }))
    family = forms.ChoiceField(required=False, choices=IP_FAMILY_CHOICES, label='Address family')
    mask_length = forms.ChoiceField(required=False, choices=IPADDRESS_MASK_LENGTH_CHOICES, label='Mask length')
    vrf = FilterChoiceField(
        queryset=VRF.objects.annotate(filter_count=Count('ip_addresses')),
        to_field_name='rd',
        label='VRF',
        null_label='-- Global --'
    )
    tenant = FilterChoiceField(
        queryset=Tenant.objects.annotate(filter_count=Count('ip_addresses')),
        to_field_name='slug',
        null_label='-- None --'
    )
    status = AnnotatedMultipleChoiceField(
        choices=IPADDRESS_STATUS_CHOICES,
        annotate=IPAddress.objects.all(),
        annotate_field='status',
        required=False
    )
    role = AnnotatedMultipleChoiceField(
        choices=IPADDRESS_ROLE_CHOICES,
        annotate=IPAddress.objects.all(),
        annotate_field='role',
        required=False
    )


#
# VLAN groups
#

class VLANGroupForm(BootstrapMixin, forms.ModelForm):
    slug = SlugField()

    class Meta:
        model = VLANGroup
        fields = ['site', 'name', 'slug']


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
    site = FilterChoiceField(
        queryset=Site.objects.annotate(filter_count=Count('vlan_groups')),
        to_field_name='slug',
        null_label='-- Global --'
    )


#
# VLANs
#

class VLANForm(BootstrapMixin, TenancyForm, CustomFieldForm):
    site = forms.ModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        widget=forms.Select(
            attrs={'filter-for': 'group', 'nullable': 'true'}
        )
    )
    group = ChainedModelChoiceField(
        queryset=VLANGroup.objects.all(),
        chains=(
            ('site', 'site'),
        ),
        required=False,
        label='Group',
        widget=APISelect(
            api_url='/api/ipam/vlan-groups/?site_id={{site}}',
        )
    )
    tags = TagField(required=False)

    class Meta:
        model = VLAN
        fields = ['site', 'group', 'vid', 'name', 'status', 'role', 'description', 'tenant_group', 'tenant', 'tags']
        help_texts = {
            'site': "Leave blank if this VLAN spans multiple sites",
            'group': "VLAN group (optional)",
            'vid': "Configured VLAN ID",
            'name': "Configured VLAN name",
            'status': "Operational status of this VLAN",
            'role': "The primary function of this VLAN",
        }


class VLANCSVForm(forms.ModelForm):
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
        choices=VLAN_STATUS_CHOICES,
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

        super(VLANCSVForm, self).clean()

        site = self.cleaned_data.get('site')
        group_name = self.cleaned_data.get('group_name')

        # Validate VLAN group
        if group_name:
            try:
                self.instance.group = VLANGroup.objects.get(site=site, name=group_name)
            except VLANGroup.DoesNotExist:
                if site:
                    raise forms.ValidationError("VLAN group {} not found for site {}".format(group_name, site))
                else:
                    raise forms.ValidationError("Global VLAN group {} not found".format(group_name))


class VLANBulkEditForm(BootstrapMixin, AddRemoveTagsForm, CustomFieldBulkEditForm):
    pk = forms.ModelMultipleChoiceField(queryset=VLAN.objects.all(), widget=forms.MultipleHiddenInput)
    site = forms.ModelChoiceField(queryset=Site.objects.all(), required=False)
    group = forms.ModelChoiceField(queryset=VLANGroup.objects.all(), required=False)
    tenant = forms.ModelChoiceField(queryset=Tenant.objects.all(), required=False)
    status = forms.ChoiceField(choices=add_blank_choice(VLAN_STATUS_CHOICES), required=False)
    role = forms.ModelChoiceField(queryset=Role.objects.all(), required=False)
    description = forms.CharField(max_length=100, required=False)

    class Meta:
        nullable_fields = ['site', 'group', 'tenant', 'role', 'description']


class VLANFilterForm(BootstrapMixin, CustomFieldFilterForm):
    model = VLAN
    q = forms.CharField(required=False, label='Search')
    site = FilterChoiceField(
        queryset=Site.objects.annotate(filter_count=Count('vlans')),
        to_field_name='slug',
        null_label='-- Global --'
    )
    group_id = FilterChoiceField(
        queryset=VLANGroup.objects.annotate(filter_count=Count('vlans')),
        label='VLAN group',
        null_label='-- None --'
    )
    tenant = FilterChoiceField(
        queryset=Tenant.objects.annotate(filter_count=Count('vlans')),
        to_field_name='slug',
        null_label='-- None --'
    )
    status = AnnotatedMultipleChoiceField(
        choices=VLAN_STATUS_CHOICES,
        annotate=VLAN.objects.all(),
        annotate_field='status',
        required=False
    )
    role = FilterChoiceField(
        queryset=Role.objects.annotate(filter_count=Count('vlans')),
        to_field_name='slug',
        null_label='-- None --'
    )


#
# Services
#

class ServiceForm(BootstrapMixin, CustomFieldForm):
    tags = TagField(required=False)

    class Meta:
        model = Service
        fields = ['name', 'protocol', 'port', 'ipaddresses', 'description', 'tags']
        help_texts = {
            'ipaddresses': "IP address assignment is optional. If no IPs are selected, the service is assumed to be "
                           "reachable via all IPs assigned to the device.",
        }

    def __init__(self, *args, **kwargs):

        super(ServiceForm, self).__init__(*args, **kwargs)

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
        choices=add_blank_choice(IP_PROTOCOL_CHOICES),
        required=False
    )
    port = forms.IntegerField(
        required=False
    )


class ServiceBulkEditForm(BootstrapMixin, CustomFieldBulkEditForm):
    pk = forms.ModelMultipleChoiceField(queryset=Service.objects.all(), widget=forms.MultipleHiddenInput)
    protocol = forms.ChoiceField(choices=add_blank_choice(IP_PROTOCOL_CHOICES), required=False)
    port = forms.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(65535)], required=False)
    description = forms.CharField(max_length=100, required=False)

    class Meta:
        nullable_fields = ['site', 'group', 'tenant', 'role', 'description']
