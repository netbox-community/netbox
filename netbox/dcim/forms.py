import re
from operator import attrgetter

from django import forms
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.forms.array import SimpleArrayField
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, Q
from mptt.forms import TreeNodeChoiceField
from natsort import natsorted
from taggit.forms import TagField
from timezone_field import TimeZoneFormField

from extras.forms import AddRemoveTagsForm, CustomFieldForm, CustomFieldBulkEditForm, CustomFieldFilterForm
from ipam.models import IPAddress, VLAN, VLANGroup
from tenancy.forms import TenancyForm
from tenancy.models import Tenant
from utilities.forms import (
    AnnotatedMultipleChoiceField, APISelect, add_blank_choice, ArrayFieldSelectMultiple, BootstrapMixin, BulkEditForm,
    BulkEditNullBooleanSelect, ChainedFieldsMixin, ChainedModelChoiceField, ColorSelect, CommentField, ComponentForm,
    ConfirmationForm, ContentTypeSelect, CSVChoiceField, ExpandableNameField, FilterChoiceField,
    FilterTreeNodeMultipleChoiceField, FlexibleModelChoiceField, JSONField, Livesearch, SelectWithPK, SmallTextarea,
    SlugField, COLOR_CHOICES,

)
from virtualization.models import Cluster
from .constants import *
from .models import (
    Cable, DeviceBay, DeviceBayTemplate, ConsolePort, ConsolePortTemplate, ConsoleServerPort, ConsoleServerPortTemplate,
    Device, DeviceRole, DeviceType, FrontPort, FrontPortTemplate, Interface, InterfaceTemplate, Manufacturer,
    InventoryItem, Platform, PowerOutlet, PowerOutletTemplate, PowerPort, PowerPortTemplate, Rack, RackGroup,
    RackReservation, RackRole, RearPort, RearPortTemplate, Region, Site, VirtualChassis,
)

DEVICE_BY_PK_RE = r'{\d+\}'

INTERFACE_MODE_HELP_TEXT = """
Access: One untagged VLAN<br />
Tagged: One untagged VLAN and/or one or more tagged VLANs<br />
Tagged All: Implies all VLANs are available (w/optional untagged VLAN)
"""


def get_device_by_name_or_pk(name):
    """
    Attempt to retrieve a device by either its name or primary key ('{pk}').
    """
    if re.match(DEVICE_BY_PK_RE, name):
        pk = name.strip('{}')
        device = Device.objects.get(pk=pk)
    else:
        device = Device.objects.get(name=name)
    return device


class BulkRenameForm(forms.Form):
    """
    An extendable form to be used for renaming device components in bulk.
    """
    find = forms.CharField()
    replace = forms.CharField()


#
# Regions
#

class RegionForm(BootstrapMixin, forms.ModelForm):
    slug = SlugField()

    class Meta:
        model = Region
        fields = ['parent', 'name', 'slug']


class RegionCSVForm(forms.ModelForm):
    parent = forms.ModelChoiceField(
        queryset=Region.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Name of parent region',
        error_messages={
            'invalid_choice': 'Region not found.',
        }
    )

    class Meta:
        model = Region
        fields = Region.csv_headers
        help_texts = {
            'name': 'Region name',
            'slug': 'URL-friendly slug',
        }


class RegionFilterForm(BootstrapMixin, forms.Form):
    model = Site
    q = forms.CharField(required=False, label='Search')


#
# Sites
#

class SiteForm(BootstrapMixin, TenancyForm, CustomFieldForm):
    region = TreeNodeChoiceField(queryset=Region.objects.all(), required=False)
    slug = SlugField()
    comments = CommentField()
    tags = TagField(required=False)

    class Meta:
        model = Site
        fields = [
            'name', 'slug', 'status', 'region', 'tenant_group', 'tenant', 'facility', 'asn', 'time_zone', 'description',
            'physical_address', 'shipping_address', 'latitude', 'longitude', 'contact_name', 'contact_phone',
            'contact_email', 'comments', 'tags',
        ]
        widgets = {
            'physical_address': SmallTextarea(attrs={'rows': 3}),
            'shipping_address': SmallTextarea(attrs={'rows': 3}),
        }
        help_texts = {
            'name': "Full name of the site",
            'facility': "Data center provider and facility (e.g. Equinix NY7)",
            'asn': "BGP autonomous system number",
            'time_zone': "Local time zone",
            'description': "Short description (will appear in sites list)",
            'physical_address': "Physical location of the building (e.g. for GPS)",
            'shipping_address': "If different from the physical address",
            'latitude': "Latitude in decimal format (xx.yyyyyy)",
            'longitude': "Longitude in decimal format (xx.yyyyyy)"
        }


class SiteCSVForm(forms.ModelForm):
    status = CSVChoiceField(
        choices=SITE_STATUS_CHOICES,
        required=False,
        help_text='Operational status'
    )
    region = forms.ModelChoiceField(
        queryset=Region.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Name of assigned region',
        error_messages={
            'invalid_choice': 'Region not found.',
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

    class Meta:
        model = Site
        fields = Site.csv_headers
        help_texts = {
            'name': 'Site name',
            'slug': 'URL-friendly slug',
            'asn': '32-bit autonomous system number',
        }


class SiteBulkEditForm(BootstrapMixin, AddRemoveTagsForm, CustomFieldBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=Site.objects.all(),
        widget=forms.MultipleHiddenInput
    )
    status = forms.ChoiceField(
        choices=add_blank_choice(SITE_STATUS_CHOICES),
        required=False,
        initial=''
    )
    region = TreeNodeChoiceField(
        queryset=Region.objects.all(),
        required=False
    )
    tenant = forms.ModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False
    )
    asn = forms.IntegerField(
        min_value=1,
        max_value=4294967295,
        required=False,
        label='ASN'
    )
    description = forms.CharField(
        max_length=100,
        required=False
    )
    time_zone = TimeZoneFormField(
        choices=add_blank_choice(TimeZoneFormField().choices),
        required=False
    )

    class Meta:
        nullable_fields = ['region', 'tenant', 'asn', 'description', 'time_zone']


class SiteFilterForm(BootstrapMixin, CustomFieldFilterForm):
    model = Site
    q = forms.CharField(required=False, label='Search')
    status = AnnotatedMultipleChoiceField(
        choices=SITE_STATUS_CHOICES,
        annotate=Site.objects.all(),
        annotate_field='status',
        required=False
    )
    region = FilterTreeNodeMultipleChoiceField(
        queryset=Region.objects.annotate(filter_count=Count('sites')),
        to_field_name='slug',
        required=False,
    )
    tenant = FilterChoiceField(
        queryset=Tenant.objects.annotate(filter_count=Count('sites')),
        to_field_name='slug',
        null_label='-- None --'
    )


#
# Rack groups
#

class RackGroupForm(BootstrapMixin, forms.ModelForm):
    slug = SlugField()

    class Meta:
        model = RackGroup
        fields = ['site', 'name', 'slug']


class RackGroupCSVForm(forms.ModelForm):
    site = forms.ModelChoiceField(
        queryset=Site.objects.all(),
        to_field_name='name',
        help_text='Name of parent site',
        error_messages={
            'invalid_choice': 'Site not found.',
        }
    )

    class Meta:
        model = RackGroup
        fields = RackGroup.csv_headers
        help_texts = {
            'name': 'Name of rack group',
            'slug': 'URL-friendly slug',
        }


class RackGroupFilterForm(BootstrapMixin, forms.Form):
    site = FilterChoiceField(queryset=Site.objects.annotate(filter_count=Count('rack_groups')), to_field_name='slug')


#
# Rack roles
#

class RackRoleForm(BootstrapMixin, forms.ModelForm):
    slug = SlugField()

    class Meta:
        model = RackRole
        fields = ['name', 'slug', 'color']


class RackRoleCSVForm(forms.ModelForm):
    slug = SlugField()

    class Meta:
        model = RackRole
        fields = RackRole.csv_headers
        help_texts = {
            'name': 'Name of rack role',
            'color': 'RGB color in hexadecimal (e.g. 00ff00)'
        }


#
# Racks
#

class RackForm(BootstrapMixin, TenancyForm, CustomFieldForm):
    group = ChainedModelChoiceField(
        queryset=RackGroup.objects.all(),
        chains=(
            ('site', 'site'),
        ),
        required=False,
        widget=APISelect(
            api_url='/api/dcim/rack-groups/?site_id={{site}}',
        )
    )
    comments = CommentField()
    tags = TagField(required=False)

    class Meta:
        model = Rack
        fields = [
            'site', 'group', 'name', 'facility_id', 'tenant_group', 'tenant', 'status', 'role', 'serial', 'asset_tag',
            'type', 'width', 'u_height', 'desc_units', 'outer_width', 'outer_depth', 'outer_unit', 'comments', 'tags',
        ]
        help_texts = {
            'site': "The site at which the rack exists",
            'name': "Organizational rack name",
            'facility_id': "The unique rack ID assigned by the facility",
            'u_height': "Height in rack units",
        }
        widgets = {
            'site': forms.Select(attrs={'filter-for': 'group'}),
        }


class RackCSVForm(forms.ModelForm):
    site = forms.ModelChoiceField(
        queryset=Site.objects.all(),
        to_field_name='name',
        help_text='Name of parent site',
        error_messages={
            'invalid_choice': 'Site not found.',
        }
    )
    group_name = forms.CharField(
        help_text='Name of rack group',
        required=False
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
    status = CSVChoiceField(
        choices=RACK_STATUS_CHOICES,
        required=False,
        help_text='Operational status'
    )
    role = forms.ModelChoiceField(
        queryset=RackRole.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Name of assigned role',
        error_messages={
            'invalid_choice': 'Role not found.',
        }
    )
    type = CSVChoiceField(
        choices=RACK_TYPE_CHOICES,
        required=False,
        help_text='Rack type'
    )
    width = forms.ChoiceField(
        choices=(
            (RACK_WIDTH_19IN, '19'),
            (RACK_WIDTH_23IN, '23'),
        ),
        help_text='Rail-to-rail width (in inches)'
    )
    outer_unit = CSVChoiceField(
        choices=RACK_DIMENSION_UNIT_CHOICES,
        required=False,
        help_text='Unit for outer dimensions'
    )

    class Meta:
        model = Rack
        fields = Rack.csv_headers
        help_texts = {
            'name': 'Rack name',
            'u_height': 'Height in rack units',
        }

    def clean(self):

        super(RackCSVForm, self).clean()

        site = self.cleaned_data.get('site')
        group_name = self.cleaned_data.get('group_name')
        name = self.cleaned_data.get('name')
        facility_id = self.cleaned_data.get('facility_id')

        # Validate rack group
        if group_name:
            try:
                self.instance.group = RackGroup.objects.get(site=site, name=group_name)
            except RackGroup.DoesNotExist:
                raise forms.ValidationError("Rack group {} not found for site {}".format(group_name, site))

            # Validate uniqueness of rack name within group
            if Rack.objects.filter(group=self.instance.group, name=name).exists():
                raise forms.ValidationError(
                    "A rack named {} already exists within group {}".format(name, group_name)
                )

            # Validate uniqueness of facility ID within group
            if facility_id and Rack.objects.filter(group=self.instance.group, facility_id=facility_id).exists():
                raise forms.ValidationError(
                    "A rack with the facility ID {} already exists within group {}".format(facility_id, group_name)
                )


class RackBulkEditForm(BootstrapMixin, AddRemoveTagsForm, CustomFieldBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=Rack.objects.all(),
        widget=forms.MultipleHiddenInput
    )
    site = forms.ModelChoiceField(
        queryset=Site.objects.all(),
        required=False
    )
    group = forms.ModelChoiceField(
        queryset=RackGroup.objects.all(),
        required=False
    )
    tenant = forms.ModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False
    )
    status = forms.ChoiceField(
        choices=add_blank_choice(RACK_STATUS_CHOICES),
        required=False,
        initial=''
    )
    role = forms.ModelChoiceField(
        queryset=RackRole.objects.all(),
        required=False
    )
    serial = forms.CharField(
        max_length=50,
        required=False,
        label='Serial Number'
    )
    asset_tag = forms.CharField(
        max_length=50,
        required=False
    )
    type = forms.ChoiceField(
        choices=add_blank_choice(RACK_TYPE_CHOICES),
        required=False
    )
    width = forms.ChoiceField(
        choices=add_blank_choice(RACK_WIDTH_CHOICES),
        required=False
    )
    u_height = forms.IntegerField(
        required=False,
        label='Height (U)'
    )
    desc_units = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect,
        label='Descending units'
    )
    outer_width = forms.IntegerField(
        required=False,
        min_value=1
    )
    outer_depth = forms.IntegerField(
        required=False,
        min_value=1
    )
    outer_unit = forms.ChoiceField(
        choices=add_blank_choice(RACK_DIMENSION_UNIT_CHOICES),
        required=False
    )
    comments = CommentField(
        widget=SmallTextarea
    )

    class Meta:
        nullable_fields = [
            'group', 'tenant', 'role', 'serial', 'asset_tag', 'outer_width', 'outer_depth', 'outer_unit', 'comments',
        ]


class RackFilterForm(BootstrapMixin, CustomFieldFilterForm):
    model = Rack
    q = forms.CharField(required=False, label='Search')
    site = FilterChoiceField(
        queryset=Site.objects.annotate(filter_count=Count('racks')),
        to_field_name='slug'
    )
    group_id = FilterChoiceField(
        queryset=RackGroup.objects.select_related('site').annotate(filter_count=Count('racks')),
        label='Rack group',
        null_label='-- None --'
    )
    tenant = FilterChoiceField(
        queryset=Tenant.objects.annotate(filter_count=Count('racks')),
        to_field_name='slug',
        null_label='-- None --'
    )
    status = AnnotatedMultipleChoiceField(
        choices=RACK_STATUS_CHOICES,
        annotate=Rack.objects.all(),
        annotate_field='status',
        required=False
    )
    role = FilterChoiceField(
        queryset=RackRole.objects.annotate(filter_count=Count('racks')),
        to_field_name='slug',
        null_label='-- None --'
    )


#
# Rack reservations
#

class RackReservationForm(BootstrapMixin, TenancyForm, forms.ModelForm):
    units = SimpleArrayField(forms.IntegerField(), widget=ArrayFieldSelectMultiple(attrs={'size': 10}))
    user = forms.ModelChoiceField(queryset=User.objects.order_by('username'))

    class Meta:
        model = RackReservation
        fields = ['units', 'user', 'tenant_group', 'tenant', 'description']

    def __init__(self, *args, **kwargs):

        super(RackReservationForm, self).__init__(*args, **kwargs)

        # Populate rack unit choices
        self.fields['units'].widget.choices = self._get_unit_choices()

    def _get_unit_choices(self):
        rack = self.instance.rack
        reserved_units = []
        for resv in rack.reservations.exclude(pk=self.instance.pk):
            for u in resv.units:
                reserved_units.append(u)
        unit_choices = [(u, {'label': str(u), 'disabled': u in reserved_units}) for u in rack.units]
        return unit_choices


class RackReservationFilterForm(BootstrapMixin, forms.Form):
    q = forms.CharField(required=False, label='Search')
    site = FilterChoiceField(
        queryset=Site.objects.annotate(filter_count=Count('racks__reservations')),
        to_field_name='slug'
    )
    group_id = FilterChoiceField(
        queryset=RackGroup.objects.select_related('site').annotate(filter_count=Count('racks__reservations')),
        label='Rack group',
        null_label='-- None --'
    )
    tenant = FilterChoiceField(
        queryset=Tenant.objects.annotate(filter_count=Count('rackreservations')),
        to_field_name='slug',
        null_label='-- None --'
    )


class RackReservationBulkEditForm(BootstrapMixin, BulkEditForm):
    pk = forms.ModelMultipleChoiceField(queryset=RackReservation.objects.all(), widget=forms.MultipleHiddenInput)
    user = forms.ModelChoiceField(queryset=User.objects.order_by('username'), required=False)
    tenant = forms.ModelChoiceField(queryset=Tenant.objects.all(), required=False)
    description = forms.CharField(max_length=100, required=False)

    class Meta:
        nullable_fields = []


#
# Manufacturers
#

class ManufacturerForm(BootstrapMixin, forms.ModelForm):
    slug = SlugField()

    class Meta:
        model = Manufacturer
        fields = ['name', 'slug']


class ManufacturerCSVForm(forms.ModelForm):
    class Meta:
        model = Manufacturer
        fields = Manufacturer.csv_headers
        help_texts = {
            'name': 'Manufacturer name',
            'slug': 'URL-friendly slug',
        }


#
# Device types
#

class DeviceTypeForm(BootstrapMixin, CustomFieldForm):
    slug = SlugField(slug_source='model')
    tags = TagField(required=False)

    class Meta:
        model = DeviceType
        fields = [
            'manufacturer', 'model', 'slug', 'part_number', 'u_height', 'is_full_depth', 'subdevice_role',
            'interface_ordering', 'comments', 'tags',
        ]
        labels = {
            'interface_ordering': 'Order interfaces by',
        }


class DeviceTypeCSVForm(forms.ModelForm):
    manufacturer = forms.ModelChoiceField(
        queryset=Manufacturer.objects.all(),
        required=True,
        to_field_name='name',
        help_text='Manufacturer name',
        error_messages={
            'invalid_choice': 'Manufacturer not found.',
        }
    )
    subdevice_role = CSVChoiceField(
        choices=SUBDEVICE_ROLE_CHOICES,
        required=False,
        help_text='Parent/child status'
    )
    interface_ordering = CSVChoiceField(
        choices=IFACE_ORDERING_CHOICES,
        required=False,
        help_text='Interface ordering'
    )

    class Meta:
        model = DeviceType
        fields = DeviceType.csv_headers
        help_texts = {
            'model': 'Model name',
            'slug': 'URL-friendly slug',
        }


class DeviceTypeBulkEditForm(BootstrapMixin, AddRemoveTagsForm, CustomFieldBulkEditForm):
    pk = forms.ModelMultipleChoiceField(queryset=DeviceType.objects.all(), widget=forms.MultipleHiddenInput)
    manufacturer = forms.ModelChoiceField(queryset=Manufacturer.objects.all(), required=False)
    u_height = forms.IntegerField(min_value=1, required=False)
    is_full_depth = forms.NullBooleanField(required=False, widget=BulkEditNullBooleanSelect, label='Is full depth')
    interface_ordering = forms.ChoiceField(choices=add_blank_choice(IFACE_ORDERING_CHOICES), required=False)

    class Meta:
        nullable_fields = []


class DeviceTypeFilterForm(BootstrapMixin, CustomFieldFilterForm):
    model = DeviceType
    q = forms.CharField(required=False, label='Search')
    manufacturer = FilterChoiceField(
        queryset=Manufacturer.objects.annotate(filter_count=Count('device_types')),
        to_field_name='slug'
    )
    console_ports = forms.BooleanField(
        required=False,
        label='Has console ports'
    )
    console_server_ports = forms.BooleanField(
        required=False,
        label='Has console server ports'
    )
    power_ports = forms.BooleanField(
        required=False,
        label='Has power ports'
    )
    power_outlets = forms.BooleanField(
        required=False,
        label='Has power outlets'
    )
    interfaces = forms.BooleanField(
        required=False,
        label='Has interfaces'
    )
    pass_through_ports = forms.BooleanField(
        required=False,
        label='Has pass-through ports'
    )
    subdevice_role = forms.NullBooleanField(
        required=False,
        label='Subdevice role',
        widget=forms.Select(choices=add_blank_choice(SUBDEVICE_ROLE_CHOICES))
    )


#
# Device component templates
#

class ConsolePortTemplateForm(BootstrapMixin, forms.ModelForm):

    class Meta:
        model = ConsolePortTemplate
        fields = ['device_type', 'name']
        widgets = {
            'device_type': forms.HiddenInput(),
        }


class ConsolePortTemplateCreateForm(ComponentForm):
    name_pattern = ExpandableNameField(label='Name')


class ConsoleServerPortTemplateForm(BootstrapMixin, forms.ModelForm):

    class Meta:
        model = ConsoleServerPortTemplate
        fields = ['device_type', 'name']
        widgets = {
            'device_type': forms.HiddenInput(),
        }


class ConsoleServerPortTemplateCreateForm(ComponentForm):
    name_pattern = ExpandableNameField(label='Name')


class PowerPortTemplateForm(BootstrapMixin, forms.ModelForm):

    class Meta:
        model = PowerPortTemplate
        fields = ['device_type', 'name']
        widgets = {
            'device_type': forms.HiddenInput(),
        }


class PowerPortTemplateCreateForm(ComponentForm):
    name_pattern = ExpandableNameField(label='Name')


class PowerOutletTemplateForm(BootstrapMixin, forms.ModelForm):

    class Meta:
        model = PowerOutletTemplate
        fields = ['device_type', 'name']
        widgets = {
            'device_type': forms.HiddenInput(),
        }


class PowerOutletTemplateCreateForm(ComponentForm):
    name_pattern = ExpandableNameField(label='Name')


class InterfaceTemplateForm(BootstrapMixin, forms.ModelForm):

    class Meta:
        model = InterfaceTemplate
        fields = ['device_type', 'name', 'form_factor', 'mgmt_only']
        widgets = {
            'device_type': forms.HiddenInput(),
        }


class InterfaceTemplateCreateForm(ComponentForm):
    name_pattern = ExpandableNameField(label='Name')
    form_factor = forms.ChoiceField(choices=IFACE_FF_CHOICES)
    mgmt_only = forms.BooleanField(required=False, label='OOB Management')


class InterfaceTemplateBulkEditForm(BootstrapMixin, BulkEditForm):
    pk = forms.ModelMultipleChoiceField(queryset=InterfaceTemplate.objects.all(), widget=forms.MultipleHiddenInput)
    form_factor = forms.ChoiceField(choices=add_blank_choice(IFACE_FF_CHOICES), required=False)
    mgmt_only = forms.NullBooleanField(required=False, widget=BulkEditNullBooleanSelect, label='Management only')

    class Meta:
        nullable_fields = []


class FrontPortTemplateForm(BootstrapMixin, forms.ModelForm):

    class Meta:
        model = FrontPortTemplate
        fields = ['device_type', 'name', 'type', 'rear_port', 'rear_port_position']
        widgets = {
            'device_type': forms.HiddenInput(),
        }


class FrontPortTemplateCreateForm(ComponentForm):
    name_pattern = ExpandableNameField(
        label='Name'
    )
    type = forms.ChoiceField(
        choices=PORT_TYPE_CHOICES
    )
    rear_port_set = forms.MultipleChoiceField(
        choices=[],
        label='Rear ports',
        help_text='Select one rear port assignment for each front port being created.'
    )

    def __init__(self, *args, **kwargs):

        super(FrontPortTemplateCreateForm, self).__init__(*args, **kwargs)

        # Determine which rear port positions are occupied. These will be excluded from the list of available mappings.
        occupied_port_positions = [
            (front_port.rear_port_id, front_port.rear_port_position)
            for front_port in self.parent.frontport_templates.all()
        ]

        # Populate rear port choices
        choices = []
        rear_ports = natsorted(RearPortTemplate.objects.filter(device_type=self.parent), key=attrgetter('name'))
        for rear_port in rear_ports:
            for i in range(1, rear_port.positions + 1):
                if (rear_port.pk, i) not in occupied_port_positions:
                    choices.append(
                        ('{}:{}'.format(rear_port.pk, i), '{}:{}'.format(rear_port.name, i))
                    )
        self.fields['rear_port_set'].choices = choices

    def clean(self):

        # Validate that the number of ports being created equals the number of selected (rear port, position) tuples
        front_port_count = len(self.cleaned_data['name_pattern'])
        rear_port_count = len(self.cleaned_data['rear_port_set'])
        if front_port_count != rear_port_count:
            raise forms.ValidationError({
                'rear_port_set': 'The provided name pattern will create {} ports, however {} rear port assignments '
                                 'were selected. These counts must match.'.format(front_port_count, rear_port_count)
            })

    def get_iterative_data(self, iteration):

        # Assign rear port and position from selected set
        rear_port, position = self.cleaned_data['rear_port_set'][iteration].split(':')

        return {
            'rear_port': int(rear_port),
            'rear_port_position': int(position),
        }


class RearPortTemplateForm(BootstrapMixin, forms.ModelForm):

    class Meta:
        model = RearPortTemplate
        fields = ['device_type', 'name', 'type', 'positions']
        widgets = {
            'device_type': forms.HiddenInput(),
        }


class RearPortTemplateCreateForm(ComponentForm):
    name_pattern = ExpandableNameField(
        label='Name'
    )
    type = forms.ChoiceField(
        choices=PORT_TYPE_CHOICES
    )
    positions = forms.IntegerField(
        min_value=1,
        max_value=64,
        initial=1,
        help_text='The number of front ports which may be mapped to each rear port'
    )


class DeviceBayTemplateForm(BootstrapMixin, forms.ModelForm):

    class Meta:
        model = DeviceBayTemplate
        fields = ['device_type', 'name']
        widgets = {
            'device_type': forms.HiddenInput(),
        }


class DeviceBayTemplateCreateForm(ComponentForm):
    name_pattern = ExpandableNameField(label='Name')


#
# Device roles
#

class DeviceRoleForm(BootstrapMixin, forms.ModelForm):
    slug = SlugField()

    class Meta:
        model = DeviceRole
        fields = ['name', 'slug', 'color', 'vm_role']


class DeviceRoleCSVForm(forms.ModelForm):
    slug = SlugField()

    class Meta:
        model = DeviceRole
        fields = DeviceRole.csv_headers
        help_texts = {
            'name': 'Name of device role',
            'color': 'RGB color in hexadecimal (e.g. 00ff00)'
        }


#
# Platforms
#

class PlatformForm(BootstrapMixin, forms.ModelForm):
    slug = SlugField()

    class Meta:
        model = Platform
        fields = ['name', 'slug', 'manufacturer', 'napalm_driver', 'napalm_args']
        widgets = {
            'napalm_args': SmallTextarea(),
        }


class PlatformCSVForm(forms.ModelForm):
    slug = SlugField()
    manufacturer = forms.ModelChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Manufacturer name',
        error_messages={
            'invalid_choice': 'Manufacturer not found.',
        }
    )

    class Meta:
        model = Platform
        fields = Platform.csv_headers
        help_texts = {
            'name': 'Platform name',
        }


#
# Devices
#

class DeviceForm(BootstrapMixin, TenancyForm, CustomFieldForm):
    site = forms.ModelChoiceField(
        queryset=Site.objects.all(),
        widget=forms.Select(
            attrs={'filter-for': 'rack'}
        )
    )
    rack = ChainedModelChoiceField(
        queryset=Rack.objects.all(),
        chains=(
            ('site', 'site'),
        ),
        required=False,
        widget=APISelect(
            api_url='/api/dcim/racks/?site_id={{site}}',
            display_field='display_name',
            attrs={'filter-for': 'position'}
        )
    )
    position = forms.TypedChoiceField(
        required=False,
        empty_value=None,
        help_text="The lowest-numbered unit occupied by the device",
        widget=APISelect(
            api_url='/api/dcim/racks/{{rack}}/units/?face={{face}}',
            disabled_indicator='device'
        )
    )
    manufacturer = forms.ModelChoiceField(
        queryset=Manufacturer.objects.all(),
        widget=forms.Select(
            attrs={'filter-for': 'device_type'}
        )
    )
    device_type = ChainedModelChoiceField(
        queryset=DeviceType.objects.all(),
        chains=(
            ('manufacturer', 'manufacturer'),
        ),
        label='Device type',
        widget=APISelect(
            api_url='/api/dcim/device-types/?manufacturer_id={{manufacturer}}',
            display_field='model'
        )
    )
    comments = CommentField()
    tags = TagField(required=False)
    local_context_data = JSONField(required=False)

    class Meta:
        model = Device
        fields = [
            'name', 'device_role', 'device_type', 'serial', 'asset_tag', 'site', 'rack', 'position', 'face',
            'status', 'platform', 'primary_ip4', 'primary_ip6', 'tenant_group', 'tenant', 'comments', 'tags',
            'local_context_data'
        ]
        help_texts = {
            'device_role': "The function this device serves",
            'serial': "Chassis serial number",
            'local_context_data': "Local config context data overwrites all sources contexts in the final rendered config context"
        }
        widgets = {
            'face': forms.Select(attrs={'filter-for': 'position'}),
        }

    def __init__(self, *args, **kwargs):

        # Initialize helper selectors
        instance = kwargs.get('instance')
        # Using hasattr() instead of "is not None" to avoid RelatedObjectDoesNotExist on required field
        if instance and hasattr(instance, 'device_type'):
            initial = kwargs.get('initial', {}).copy()
            initial['manufacturer'] = instance.device_type.manufacturer
            kwargs['initial'] = initial

        super(DeviceForm, self).__init__(*args, **kwargs)

        if self.instance.pk:

            # Compile list of choices for primary IPv4 and IPv6 addresses
            for family in [4, 6]:
                ip_choices = [(None, '---------')]

                # Gather PKs of all interfaces belonging to this Device or a peer VirtualChassis member
                interface_ids = self.instance.vc_interfaces.values('pk')

                # Collect interface IPs
                interface_ips = IPAddress.objects.select_related('interface').filter(
                    family=family, interface_id__in=interface_ids
                )
                if interface_ips:
                    ip_list = [(ip.id, '{} ({})'.format(ip.address, ip.interface)) for ip in interface_ips]
                    ip_choices.append(('Interface IPs', ip_list))
                # Collect NAT IPs
                nat_ips = IPAddress.objects.select_related('nat_inside').filter(
                    family=family, nat_inside__interface__in=interface_ids
                )
                if nat_ips:
                    ip_list = [(ip.id, '{} ({})'.format(ip.address, ip.nat_inside.address)) for ip in nat_ips]
                    ip_choices.append(('NAT IPs', ip_list))
                self.fields['primary_ip{}'.format(family)].choices = ip_choices

            # If editing an existing device, exclude it from the list of occupied rack units. This ensures that a device
            # can be flipped from one face to another.
            self.fields['position'].widget.attrs['api-url'] += '&exclude={}'.format(self.instance.pk)

            # Limit platform by manufacturer
            self.fields['platform'].queryset = Platform.objects.filter(
                Q(manufacturer__isnull=True) | Q(manufacturer=self.instance.device_type.manufacturer)
            )

        else:

            # An object that doesn't exist yet can't have any IPs assigned to it
            self.fields['primary_ip4'].choices = []
            self.fields['primary_ip4'].widget.attrs['readonly'] = True
            self.fields['primary_ip6'].choices = []
            self.fields['primary_ip6'].widget.attrs['readonly'] = True

        # Rack position
        pk = self.instance.pk if self.instance.pk else None
        try:
            if self.is_bound and self.data.get('rack') and str(self.data.get('face')):
                position_choices = Rack.objects.get(pk=self.data['rack']) \
                    .get_rack_units(face=self.data.get('face'), exclude=pk)
            elif self.initial.get('rack') and str(self.initial.get('face')):
                position_choices = Rack.objects.get(pk=self.initial['rack']) \
                    .get_rack_units(face=self.initial.get('face'), exclude=pk)
            else:
                position_choices = []
        except Rack.DoesNotExist:
            position_choices = []
        self.fields['position'].choices = [('', '---------')] + [
            (p['id'], {
                'label': p['name'],
                'disabled': bool(p['device'] and p['id'] != self.initial.get('position')),
            }) for p in position_choices
        ]

        # Disable rack assignment if this is a child device installed in a parent device
        if pk and self.instance.device_type.is_child_device and hasattr(self.instance, 'parent_bay'):
            self.fields['site'].disabled = True
            self.fields['rack'].disabled = True
            self.initial['site'] = self.instance.parent_bay.device.site_id
            self.initial['rack'] = self.instance.parent_bay.device.rack_id


class BaseDeviceCSVForm(forms.ModelForm):
    device_role = forms.ModelChoiceField(
        queryset=DeviceRole.objects.all(),
        to_field_name='name',
        help_text='Name of assigned role',
        error_messages={
            'invalid_choice': 'Invalid device role.',
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
    manufacturer = forms.ModelChoiceField(
        queryset=Manufacturer.objects.all(),
        to_field_name='name',
        help_text='Device type manufacturer',
        error_messages={
            'invalid_choice': 'Invalid manufacturer.',
        }
    )
    model_name = forms.CharField(
        help_text='Device type model name'
    )
    platform = forms.ModelChoiceField(
        queryset=Platform.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Name of assigned platform',
        error_messages={
            'invalid_choice': 'Invalid platform.',
        }
    )
    status = CSVChoiceField(
        choices=DEVICE_STATUS_CHOICES,
        help_text='Operational status'
    )

    class Meta:
        fields = []
        model = Device
        help_texts = {
            'name': 'Device name',
        }

    def clean(self):

        super(BaseDeviceCSVForm, self).clean()

        manufacturer = self.cleaned_data.get('manufacturer')
        model_name = self.cleaned_data.get('model_name')

        # Validate device type
        if manufacturer and model_name:
            try:
                self.instance.device_type = DeviceType.objects.get(manufacturer=manufacturer, model=model_name)
            except DeviceType.DoesNotExist:
                raise forms.ValidationError("Device type {} {} not found".format(manufacturer, model_name))


class DeviceCSVForm(BaseDeviceCSVForm):
    site = forms.ModelChoiceField(
        queryset=Site.objects.all(),
        to_field_name='name',
        help_text='Name of parent site',
        error_messages={
            'invalid_choice': 'Invalid site name.',
        }
    )
    rack_group = forms.CharField(
        required=False,
        help_text='Parent rack\'s group (if any)'
    )
    rack_name = forms.CharField(
        required=False,
        help_text='Name of parent rack'
    )
    face = CSVChoiceField(
        choices=RACK_FACE_CHOICES,
        required=False,
        help_text='Mounted rack face'
    )
    cluster = forms.ModelChoiceField(
        queryset=Cluster.objects.all(),
        to_field_name='name',
        required=False,
        help_text='Virtualization cluster',
        error_messages={
            'invalid_choice': 'Invalid cluster name.',
        }
    )

    class Meta(BaseDeviceCSVForm.Meta):
        fields = [
            'name', 'device_role', 'tenant', 'manufacturer', 'model_name', 'platform', 'serial', 'asset_tag', 'status',
            'site', 'rack_group', 'rack_name', 'position', 'face', 'cluster', 'comments',
        ]

    def clean(self):

        super(DeviceCSVForm, self).clean()

        site = self.cleaned_data.get('site')
        rack_group = self.cleaned_data.get('rack_group')
        rack_name = self.cleaned_data.get('rack_name')

        # Validate rack
        if site and rack_group and rack_name:
            try:
                self.instance.rack = Rack.objects.get(site=site, group__name=rack_group, name=rack_name)
            except Rack.DoesNotExist:
                raise forms.ValidationError("Rack {} not found in site {} group {}".format(rack_name, site, rack_group))
        elif site and rack_name:
            try:
                self.instance.rack = Rack.objects.get(site=site, group__isnull=True, name=rack_name)
            except Rack.DoesNotExist:
                raise forms.ValidationError("Rack {} not found in site {} (no group)".format(rack_name, site))


class ChildDeviceCSVForm(BaseDeviceCSVForm):
    parent = FlexibleModelChoiceField(
        queryset=Device.objects.all(),
        to_field_name='name',
        help_text='Name or ID of parent device',
        error_messages={
            'invalid_choice': 'Parent device not found.',
        }
    )
    device_bay_name = forms.CharField(
        help_text='Name of device bay',
    )
    cluster = forms.ModelChoiceField(
        queryset=Cluster.objects.all(),
        to_field_name='name',
        required=False,
        help_text='Virtualization cluster',
        error_messages={
            'invalid_choice': 'Invalid cluster name.',
        }
    )

    class Meta(BaseDeviceCSVForm.Meta):
        fields = [
            'name', 'device_role', 'tenant', 'manufacturer', 'model_name', 'platform', 'serial', 'asset_tag', 'status',
            'parent', 'device_bay_name', 'cluster', 'comments',
        ]

    def clean(self):

        super(ChildDeviceCSVForm, self).clean()

        parent = self.cleaned_data.get('parent')
        device_bay_name = self.cleaned_data.get('device_bay_name')

        # Validate device bay
        if parent and device_bay_name:
            try:
                self.instance.parent_bay = DeviceBay.objects.get(device=parent, name=device_bay_name)
                # Inherit site and rack from parent device
                self.instance.site = parent.site
                self.instance.rack = parent.rack
            except DeviceBay.DoesNotExist:
                raise forms.ValidationError("Parent device/bay ({} {}) not found".format(parent, device_bay_name))


class DeviceBulkEditForm(BootstrapMixin, AddRemoveTagsForm, CustomFieldBulkEditForm):
    pk = forms.ModelMultipleChoiceField(queryset=Device.objects.all(), widget=forms.MultipleHiddenInput)
    device_type = forms.ModelChoiceField(queryset=DeviceType.objects.all(), required=False, label='Type')
    device_role = forms.ModelChoiceField(queryset=DeviceRole.objects.all(), required=False, label='Role')
    tenant = forms.ModelChoiceField(queryset=Tenant.objects.all(), required=False)
    platform = forms.ModelChoiceField(queryset=Platform.objects.all(), required=False)
    status = forms.ChoiceField(choices=add_blank_choice(DEVICE_STATUS_CHOICES), required=False, initial='')
    serial = forms.CharField(max_length=50, required=False, label='Serial Number')

    class Meta:
        nullable_fields = ['tenant', 'platform', 'serial']


class DeviceFilterForm(BootstrapMixin, CustomFieldFilterForm):
    model = Device
    q = forms.CharField(required=False, label='Search')
    site = FilterChoiceField(
        queryset=Site.objects.annotate(filter_count=Count('devices')),
        to_field_name='slug',
    )
    rack_group_id = FilterChoiceField(
        queryset=RackGroup.objects.select_related('site').annotate(filter_count=Count('racks__devices')),
        label='Rack group',
    )
    rack_id = FilterChoiceField(
        queryset=Rack.objects.annotate(filter_count=Count('devices')),
        label='Rack',
        null_label='-- None --',
    )
    role = FilterChoiceField(
        queryset=DeviceRole.objects.annotate(filter_count=Count('devices')),
        to_field_name='slug',
    )
    tenant = FilterChoiceField(
        queryset=Tenant.objects.annotate(filter_count=Count('devices')),
        to_field_name='slug',
        null_label='-- None --',
    )
    manufacturer_id = FilterChoiceField(queryset=Manufacturer.objects.all(), label='Manufacturer')
    device_type_id = FilterChoiceField(
        queryset=DeviceType.objects.select_related('manufacturer').order_by('model').annotate(
            filter_count=Count('instances'),
        ),
        label='Model',
    )
    platform = FilterChoiceField(
        queryset=Platform.objects.annotate(filter_count=Count('devices')),
        to_field_name='slug',
        null_label='-- None --',
    )
    status = AnnotatedMultipleChoiceField(
        choices=DEVICE_STATUS_CHOICES,
        annotate=Device.objects.all(),
        annotate_field='status',
        required=False
    )
    mac_address = forms.CharField(required=False, label='MAC address')
    has_primary_ip = forms.NullBooleanField(
        required=False,
        label='Has a primary IP',
        widget=forms.Select(choices=[
            ('', '---------'),
            ('True', 'Yes'),
            ('False', 'No'),
        ])
    )


#
# Bulk device component creation
#

class DeviceBulkAddComponentForm(BootstrapMixin, forms.Form):
    pk = forms.ModelMultipleChoiceField(queryset=Device.objects.all(), widget=forms.MultipleHiddenInput)
    name_pattern = ExpandableNameField(label='Name')


class DeviceBulkAddInterfaceForm(DeviceBulkAddComponentForm):
    form_factor = forms.ChoiceField(choices=IFACE_FF_CHOICES)
    enabled = forms.BooleanField(required=False, initial=True)
    mtu = forms.IntegerField(required=False, min_value=1, max_value=32767, label='MTU')
    mgmt_only = forms.BooleanField(required=False, label='OOB Management')
    description = forms.CharField(max_length=100, required=False)


#
# Console ports
#

class ConsolePortForm(BootstrapMixin, forms.ModelForm):
    tags = TagField(required=False)

    class Meta:
        model = ConsolePort
        fields = ['device', 'name', 'tags']
        widgets = {
            'device': forms.HiddenInput(),
        }


class ConsolePortCreateForm(ComponentForm):
    name_pattern = ExpandableNameField(label='Name')
    tags = TagField(required=False)


#
# Console server ports
#

class ConsoleServerPortForm(BootstrapMixin, forms.ModelForm):
    tags = TagField(required=False)

    class Meta:
        model = ConsoleServerPort
        fields = ['device', 'name', 'tags']
        widgets = {
            'device': forms.HiddenInput(),
        }


class ConsoleServerPortCreateForm(ComponentForm):
    name_pattern = ExpandableNameField(label='Name')
    tags = TagField(required=False)


class ConsoleServerPortBulkRenameForm(BulkRenameForm):
    pk = forms.ModelMultipleChoiceField(queryset=ConsoleServerPort.objects.all(), widget=forms.MultipleHiddenInput)


class ConsoleServerPortBulkDisconnectForm(ConfirmationForm):
    pk = forms.ModelMultipleChoiceField(queryset=ConsoleServerPort.objects.all(), widget=forms.MultipleHiddenInput)


#
# Power ports
#

class PowerPortForm(BootstrapMixin, forms.ModelForm):
    tags = TagField(required=False)

    class Meta:
        model = PowerPort
        fields = ['device', 'name', 'tags']
        widgets = {
            'device': forms.HiddenInput(),
        }


class PowerPortCreateForm(ComponentForm):
    name_pattern = ExpandableNameField(label='Name')
    tags = TagField(required=False)


#
# Power outlets
#

class PowerOutletForm(BootstrapMixin, forms.ModelForm):
    tags = TagField(required=False)

    class Meta:
        model = PowerOutlet
        fields = ['device', 'name', 'tags']
        widgets = {
            'device': forms.HiddenInput(),
        }


class PowerOutletCreateForm(ComponentForm):
    name_pattern = ExpandableNameField(label='Name')
    tags = TagField(required=False)


class PowerOutletBulkRenameForm(BulkRenameForm):
    pk = forms.ModelMultipleChoiceField(queryset=PowerOutlet.objects.all(), widget=forms.MultipleHiddenInput)


class PowerOutletBulkDisconnectForm(ConfirmationForm):
    pk = forms.ModelMultipleChoiceField(queryset=PowerOutlet.objects.all(), widget=forms.MultipleHiddenInput)


#
# Interfaces
#

class InterfaceForm(BootstrapMixin, forms.ModelForm):
    tags = TagField(required=False)

    class Meta:
        model = Interface
        fields = [
            'device', 'name', 'form_factor', 'enabled', 'lag', 'mac_address', 'mtu', 'mgmt_only', 'description',
            'mode', 'untagged_vlan', 'tagged_vlans', 'tags',
        ]
        widgets = {
            'device': forms.HiddenInput(),
        }
        labels = {
            'mode': '802.1Q Mode',
        }
        help_texts = {
            'mode': INTERFACE_MODE_HELP_TEXT,
        }

    def __init__(self, *args, **kwargs):
        super(InterfaceForm, self).__init__(*args, **kwargs)

        # Limit LAG choices to interfaces belonging to this device (or VC master)
        if self.is_bound:
            device = Device.objects.get(pk=self.data['device'])
            self.fields['lag'].queryset = Interface.objects.order_naturally().filter(
                device__in=[device, device.get_vc_master()], form_factor=IFACE_FF_LAG
            )
        else:
            device = self.instance.device
            self.fields['lag'].queryset = Interface.objects.order_naturally().filter(
                device__in=[self.instance.device, self.instance.device.get_vc_master()], form_factor=IFACE_FF_LAG
            )

    def clean(self):

        super(InterfaceForm, self).clean()

        # Validate VLAN assignments
        tagged_vlans = self.cleaned_data['tagged_vlans']

        # Untagged interfaces cannot be assigned tagged VLANs
        if self.cleaned_data['mode'] == IFACE_MODE_ACCESS and tagged_vlans:
            raise forms.ValidationError({
                'mode': "An access interface cannot have tagged VLANs assigned."
            })

        # Remove all tagged VLAN assignments from "tagged all" interfaces
        elif self.cleaned_data['mode'] == IFACE_MODE_TAGGED_ALL:
            self.cleaned_data['tagged_vlans'] = []


class InterfaceAssignVLANsForm(BootstrapMixin, forms.ModelForm):
    vlans = forms.MultipleChoiceField(
        choices=[],
        label='VLANs',
        widget=forms.SelectMultiple(attrs={'size': 20})
    )
    tagged = forms.BooleanField(
        required=False,
        initial=True
    )

    class Meta:
        model = Interface
        fields = []

    def __init__(self, *args, **kwargs):

        super(InterfaceAssignVLANsForm, self).__init__(*args, **kwargs)

        if self.instance.mode == IFACE_MODE_ACCESS:
            self.initial['tagged'] = False

        # Find all VLANs already assigned to the interface for exclusion from the list
        assigned_vlans = [v.pk for v in self.instance.tagged_vlans.all()]
        if self.instance.untagged_vlan is not None:
            assigned_vlans.append(self.instance.untagged_vlan.pk)

        # Compile VLAN choices
        vlan_choices = []

        # Add non-grouped global VLANs
        global_vlans = VLAN.objects.filter(site=None, group=None).exclude(pk__in=assigned_vlans)
        vlan_choices.append((
            'Global', [(vlan.pk, vlan) for vlan in global_vlans])
        )

        # Add grouped global VLANs
        for group in VLANGroup.objects.filter(site=None):
            global_group_vlans = VLAN.objects.filter(group=group).exclude(pk__in=assigned_vlans)
            vlan_choices.append(
                (group.name, [(vlan.pk, vlan) for vlan in global_group_vlans])
            )

        site = getattr(self.instance.parent, 'site', None)
        if site is not None:

            # Add non-grouped site VLANs
            site_vlans = VLAN.objects.filter(site=site, group=None).exclude(pk__in=assigned_vlans)
            vlan_choices.append((site.name, [(vlan.pk, vlan) for vlan in site_vlans]))

            # Add grouped site VLANs
            for group in VLANGroup.objects.filter(site=site):
                site_group_vlans = VLAN.objects.filter(group=group).exclude(pk__in=assigned_vlans)
                vlan_choices.append((
                    '{} / {}'.format(group.site.name, group.name),
                    [(vlan.pk, vlan) for vlan in site_group_vlans]
                ))

        self.fields['vlans'].choices = vlan_choices

    def clean(self):

        super(InterfaceAssignVLANsForm, self).clean()

        # Only untagged VLANs permitted on an access interface
        if self.instance.mode == IFACE_MODE_ACCESS and len(self.cleaned_data['vlans']) > 1:
            raise forms.ValidationError("Only one VLAN may be assigned to an access interface.")

        # 'tagged' is required if more than one VLAN is selected
        if not self.cleaned_data['tagged'] and len(self.cleaned_data['vlans']) > 1:
            raise forms.ValidationError("Only one untagged VLAN may be selected.")

    def save(self, *args, **kwargs):

        if self.cleaned_data['tagged']:
            for vlan in self.cleaned_data['vlans']:
                self.instance.tagged_vlans.add(vlan)
        else:
            self.instance.untagged_vlan_id = self.cleaned_data['vlans'][0]

        return super(InterfaceAssignVLANsForm, self).save(*args, **kwargs)


class InterfaceCreateForm(ComponentForm, forms.Form):
    name_pattern = ExpandableNameField(label='Name')
    form_factor = forms.ChoiceField(choices=IFACE_FF_CHOICES)
    enabled = forms.BooleanField(required=False)
    lag = forms.ModelChoiceField(queryset=Interface.objects.all(), required=False, label='Parent LAG')
    mtu = forms.IntegerField(required=False, min_value=1, max_value=32767, label='MTU')
    mac_address = forms.CharField(required=False, label='MAC Address')
    mgmt_only = forms.BooleanField(
        required=False,
        label='OOB Management',
        help_text='This interface is used only for out-of-band management'
    )
    description = forms.CharField(max_length=100, required=False)
    mode = forms.ChoiceField(choices=add_blank_choice(IFACE_MODE_CHOICES), required=False)
    tags = TagField(required=False)

    def __init__(self, *args, **kwargs):

        # Set interfaces enabled by default
        kwargs['initial'] = kwargs.get('initial', {}).copy()
        kwargs['initial'].update({'enabled': True})

        super(InterfaceCreateForm, self).__init__(*args, **kwargs)

        # Limit LAG choices to interfaces belonging to this device (or its VC master)
        if self.parent is not None:
            self.fields['lag'].queryset = Interface.objects.order_naturally().filter(
                device__in=[self.parent, self.parent.get_vc_master()], form_factor=IFACE_FF_LAG
            )
        else:
            self.fields['lag'].queryset = Interface.objects.none()


class InterfaceBulkEditForm(BootstrapMixin, AddRemoveTagsForm, BulkEditForm):
    pk = forms.ModelMultipleChoiceField(queryset=Interface.objects.all(), widget=forms.MultipleHiddenInput)
    form_factor = forms.ChoiceField(choices=add_blank_choice(IFACE_FF_CHOICES), required=False)
    enabled = forms.NullBooleanField(required=False, widget=BulkEditNullBooleanSelect)
    lag = forms.ModelChoiceField(queryset=Interface.objects.all(), required=False, label='Parent LAG')
    mtu = forms.IntegerField(required=False, min_value=1, max_value=32767, label='MTU')
    mgmt_only = forms.NullBooleanField(required=False, widget=BulkEditNullBooleanSelect, label='Management only')
    description = forms.CharField(max_length=100, required=False)
    mode = forms.ChoiceField(choices=add_blank_choice(IFACE_MODE_CHOICES), required=False)

    class Meta:
        nullable_fields = ['lag', 'mtu', 'description', 'mode']

    def __init__(self, *args, **kwargs):
        super(InterfaceBulkEditForm, self).__init__(*args, **kwargs)

        # Limit LAG choices to interfaces which belong to the parent device (or VC master)
        device = self.parent_obj
        if device is not None:
            interface_ordering = device.device_type.interface_ordering
            self.fields['lag'].queryset = Interface.objects.order_naturally(method=interface_ordering).filter(
                device__in=[device, device.get_vc_master()], form_factor=IFACE_FF_LAG
            )
        else:
            self.fields['lag'].choices = []


class InterfaceBulkRenameForm(BulkRenameForm):
    pk = forms.ModelMultipleChoiceField(queryset=Interface.objects.all(), widget=forms.MultipleHiddenInput)


class InterfaceBulkDisconnectForm(ConfirmationForm):
    pk = forms.ModelMultipleChoiceField(queryset=Interface.objects.all(), widget=forms.MultipleHiddenInput)


#
# Front pass-through ports
#

class FrontPortForm(BootstrapMixin, forms.ModelForm):
    tags = TagField(required=False)

    class Meta:
        model = FrontPort
        fields = ['device', 'name', 'type', 'rear_port', 'rear_port_position', 'tags']
        widgets = {
            'device': forms.HiddenInput(),
        }


# TODO: Merge with  FrontPortTemplateCreateForm to remove duplicate logic
class FrontPortCreateForm(ComponentForm):
    name_pattern = ExpandableNameField(
        label='Name'
    )
    type = forms.ChoiceField(
        choices=PORT_TYPE_CHOICES
    )
    rear_port_set = forms.MultipleChoiceField(
        choices=[],
        label='Rear ports',
        help_text='Select one rear port assignment for each front port being created.'
    )

    def __init__(self, *args, **kwargs):

        super(FrontPortCreateForm, self).__init__(*args, **kwargs)

        # Determine which rear port positions are occupied. These will be excluded from the list of available mappings.
        occupied_port_positions = [
            (front_port.rear_port_id, front_port.rear_port_position)
            for front_port in self.parent.frontports.all()
        ]

        # Populate rear port choices
        choices = []
        rear_ports = natsorted(RearPort.objects.filter(device=self.parent), key=attrgetter('name'))
        for rear_port in rear_ports:
            for i in range(1, rear_port.positions + 1):
                if (rear_port.pk, i) not in occupied_port_positions:
                    choices.append(
                        ('{}:{}'.format(rear_port.pk, i), '{}:{}'.format(rear_port.name, i))
                    )
        self.fields['rear_port_set'].choices = choices

    def clean(self):

        # Validate that the number of ports being created equals the number of selected (rear port, position) tuples
        front_port_count = len(self.cleaned_data['name_pattern'])
        rear_port_count = len(self.cleaned_data['rear_port_set'])
        if front_port_count != rear_port_count:
            raise forms.ValidationError({
                'rear_port_set': 'The provided name pattern will create {} ports, however {} rear port assignments '
                                 'were selected. These counts must match.'.format(front_port_count, rear_port_count)
            })

    def get_iterative_data(self, iteration):

        # Assign rear port and position from selected set
        rear_port, position = self.cleaned_data['rear_port_set'][iteration].split(':')

        return {
            'rear_port': int(rear_port),
            'rear_port_position': int(position),
        }


class FrontPortBulkRenameForm(BulkRenameForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=FrontPort.objects.all(),
        widget=forms.MultipleHiddenInput
    )


#
# Rear pass-through ports
#

class RearPortForm(BootstrapMixin, forms.ModelForm):
    tags = TagField(required=False)

    class Meta:
        model = RearPort
        fields = ['device', 'name', 'type', 'positions', 'tags']
        widgets = {
            'device': forms.HiddenInput(),
        }


class RearPortCreateForm(ComponentForm):
    name_pattern = ExpandableNameField(
        label='Name'
    )
    type = forms.ChoiceField(
        choices=PORT_TYPE_CHOICES
    )
    positions = forms.IntegerField(
        min_value=1,
        max_value=64,
        initial=1,
        help_text='The number of front ports which may be mapped to each rear port'
    )


class RearPortBulkRenameForm(BulkRenameForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=RearPort.objects.all(),
        widget=forms.MultipleHiddenInput
    )


#
# Cables
#

class CableCreateForm(BootstrapMixin, ChainedFieldsMixin, forms.ModelForm):
    termination_b_site = forms.ModelChoiceField(
        queryset=Site.objects.all(),
        label='Site',
        required=False,
        widget=forms.Select(
            attrs={'filter-for': 'termination_b_rack'}
        )
    )
    termination_b_rack = ChainedModelChoiceField(
        queryset=Rack.objects.all(),
        chains=(
            ('site', 'termination_b_site'),
        ),
        label='Rack',
        required=False,
        widget=APISelect(
            api_url='/api/dcim/racks/?site_id={{termination_b_site}}',
            attrs={'filter-for': 'termination_b_device', 'nullable': 'true'}
        )
    )
    termination_b_device = ChainedModelChoiceField(
        queryset=Device.objects.all(),
        chains=(
            ('site', 'termination_b_site'),
            ('rack', 'termination_b_rack'),
        ),
        label='Device',
        required=False,
        widget=APISelect(
            api_url='/api/dcim/devices/?site_id={{termination_b_site}}&rack_id={{termination_b_rack}}',
            display_field='display_name',
            attrs={'filter-for': 'termination_b_id'}
        )
    )
    livesearch = forms.CharField(
        required=False,
        label='Device',
        widget=Livesearch(
            query_key='q',
            query_url='dcim-api:device-list',
            field_to_update='termination_b_device'
        )
    )
    termination_b_type = forms.ModelChoiceField(
        queryset=ContentType.objects.all(),
        label='Type',
        widget=ContentTypeSelect(
            attrs={'filter-for': 'termination_b_id'}
        )
    )
    termination_b_id = forms.IntegerField(
        label='Name',
        widget=APISelect(
            api_url='/api/dcim/{{termination_b_type}}s/?device_id={{termination_b_device}}',
            disabled_indicator='cable'
        )
    )

    class Meta:
        model = Cable
        fields = [
            'termination_b_site', 'termination_b_rack', 'termination_b_device', 'livesearch', 'termination_b_type',
            'termination_b_id', 'type', 'status', 'label', 'color', 'length', 'length_unit',
        ]

    def __init__(self, *args, **kwargs):
        super(CableCreateForm, self).__init__(*args, **kwargs)

        # Define available types for endpoint B based on the type of endpoint A
        termination_a_type = self.instance.termination_a._meta.model_name
        self.fields['termination_b_type'].queryset = ContentType.objects.filter(
            model__in=COMPATIBLE_TERMINATION_TYPES.get(termination_a_type)
        )


class CableForm(BootstrapMixin, forms.ModelForm):

    class Meta:
        model = Cable
        fields = ('type', 'status', 'label', 'color', 'length', 'length_unit')


class CableCSVForm(forms.ModelForm):

    # Termination A
    side_a_device = FlexibleModelChoiceField(
        queryset=Device.objects.all(),
        to_field_name='name',
        help_text='Side A device name or ID',
        error_messages={
            'invalid_choice': 'Side A device not found',
        }
    )
    side_a_type = forms.ModelChoiceField(
        queryset=ContentType.objects.all(),
        limit_choices_to={'model__in': CABLE_TERMINATION_TYPES},
        to_field_name='model',
        help_text='Side A type'
    )
    side_a_name = forms.CharField(
        help_text='Side A component'
    )

    # Termination B
    side_b_device = FlexibleModelChoiceField(
        queryset=Device.objects.all(),
        to_field_name='name',
        help_text='Side B device name or ID',
        error_messages={
            'invalid_choice': 'Side B device not found',
        }
    )
    side_b_type = forms.ModelChoiceField(
        queryset=ContentType.objects.all(),
        limit_choices_to={'model__in': CABLE_TERMINATION_TYPES},
        to_field_name='model',
        help_text='Side B type'
    )
    side_b_name = forms.CharField(
        help_text='Side B component'
    )

    # Cable attributes
    status = CSVChoiceField(
        choices=CONNECTION_STATUS_CHOICES,
        required=False,
        help_text='Connection status'
    )
    type = CSVChoiceField(
        choices=CABLE_TYPE_CHOICES,
        required=False,
        help_text='Cable type'
    )
    length_unit = CSVChoiceField(
        choices=CABLE_LENGTH_UNIT_CHOICES,
        required=False,
        help_text='Length unit'
    )

    class Meta:
        model = Cable
        fields = [
            'side_a_device', 'side_a_type', 'side_a_name', 'side_b_device', 'side_b_type', 'side_b_name', 'type',
            'status', 'label', 'color', 'length', 'length_unit',
        ]
        help_texts = {
            'color': 'RGB color in hexadecimal (e.g. 00ff00)'
        }

    # TODO: Merge the clean() methods for either end
    def clean_side_a_name(self):

        device = self.cleaned_data.get('side_a_device')
        content_type = self.cleaned_data.get('side_a_type')
        name = self.cleaned_data.get('side_a_name')
        if not device or not content_type or not name:
            return None

        model = content_type.model_class()
        try:
            termination_object = model.objects.get(
                device=device,
                name=name
            )
            if termination_object.cable is not None:
                raise forms.ValidationError(
                    "Side A: {} {} is already connected".format(device, termination_object)
                )
        except ObjectDoesNotExist:
            raise forms.ValidationError(
                "A side termination not found: {} {}".format(device, name)
            )

        self.instance.termination_a = termination_object
        return termination_object

    def clean_side_b_name(self):

        device = self.cleaned_data.get('side_b_device')
        content_type = self.cleaned_data.get('side_b_type')
        name = self.cleaned_data.get('side_b_name')
        if not device or not content_type or not name:
            return None

        model = content_type.model_class()
        try:
            termination_object = model.objects.get(
                device=device,
                name=name
            )
            if termination_object.cable is not None:
                raise forms.ValidationError(
                    "Side B: {} {} is already connected".format(device, termination_object)
                )
        except ObjectDoesNotExist:
            raise forms.ValidationError(
                "B side termination not found: {} {}".format(device, name)
            )

        self.instance.termination_b = termination_object
        return termination_object


class CableBulkEditForm(BootstrapMixin, BulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=Cable.objects.all(),
        widget=forms.MultipleHiddenInput
    )
    type = forms.ChoiceField(
        choices=add_blank_choice(CABLE_TYPE_CHOICES),
        required=False,
        initial=''
    )
    status = forms.ChoiceField(
        choices=add_blank_choice(CONNECTION_STATUS_CHOICES),
        required=False,
        initial=''
    )
    label = forms.CharField(
        max_length=100,
        required=False
    )
    color = forms.CharField(
        max_length=6,
        required=False,
        widget=ColorSelect()
    )
    length = forms.IntegerField(
        min_value=1,
        required=False
    )
    length_unit = forms.ChoiceField(
        choices=add_blank_choice(CABLE_LENGTH_UNIT_CHOICES),
        required=False,
        initial=''
    )

    class Meta:
        nullable_fields = ['type', 'status', 'label', 'color', 'length']

    def clean(self):

        # Validate length/unit
        length = self.cleaned_data.get('length')
        length_unit = self.cleaned_data.get('length_unit')
        if length and not length_unit:
            raise forms.ValidationError({
                'length_unit': "Must specify a unit when setting length"
            })


class CableFilterForm(BootstrapMixin, forms.Form):
    model = Cable
    q = forms.CharField(required=False, label='Search')
    type = AnnotatedMultipleChoiceField(
        choices=CABLE_TYPE_CHOICES,
        annotate=Cable.objects.all(),
        annotate_field='type',
        required=False
    )
    color = forms.ChoiceField(
        choices=add_blank_choice(COLOR_CHOICES),
        widget=ColorSelect(),
        required=False
    )


#
# Device bays
#

class DeviceBayForm(BootstrapMixin, forms.ModelForm):
    tags = TagField(required=False)

    class Meta:
        model = DeviceBay
        fields = ['device', 'name', 'tags']
        widgets = {
            'device': forms.HiddenInput(),
        }


class DeviceBayCreateForm(ComponentForm):
    name_pattern = ExpandableNameField(label='Name')
    tags = TagField(required=False)


class PopulateDeviceBayForm(BootstrapMixin, forms.Form):
    installed_device = forms.ModelChoiceField(
        queryset=Device.objects.all(),
        label='Child Device',
        help_text="Child devices must first be created and assigned to the site/rack of the parent device."
    )

    def __init__(self, device_bay, *args, **kwargs):

        super(PopulateDeviceBayForm, self).__init__(*args, **kwargs)

        self.fields['installed_device'].queryset = Device.objects.filter(
            site=device_bay.device.site,
            rack=device_bay.device.rack,
            parent_bay__isnull=True,
            device_type__u_height=0,
            device_type__subdevice_role=SUBDEVICE_ROLE_CHILD
        ).exclude(pk=device_bay.device.pk)


class DeviceBayBulkRenameForm(BulkRenameForm):
    pk = forms.ModelMultipleChoiceField(queryset=DeviceBay.objects.all(), widget=forms.MultipleHiddenInput)


#
# Connections
#

class ConsoleConnectionFilterForm(BootstrapMixin, forms.Form):
    site = forms.ModelChoiceField(required=False, queryset=Site.objects.all(), to_field_name='slug')
    device = forms.CharField(required=False, label='Device name')


class PowerConnectionFilterForm(BootstrapMixin, forms.Form):
    site = forms.ModelChoiceField(required=False, queryset=Site.objects.all(), to_field_name='slug')
    device = forms.CharField(required=False, label='Device name')


class InterfaceConnectionFilterForm(BootstrapMixin, forms.Form):
    site = forms.ModelChoiceField(required=False, queryset=Site.objects.all(), to_field_name='slug')
    device = forms.CharField(required=False, label='Device name')


#
# Inventory items
#

class InventoryItemForm(BootstrapMixin, forms.ModelForm):
    tags = TagField(required=False)

    class Meta:
        model = InventoryItem
        fields = ['name', 'manufacturer', 'part_id', 'serial', 'asset_tag', 'description', 'tags']


class InventoryItemCSVForm(forms.ModelForm):
    device = FlexibleModelChoiceField(
        queryset=Device.objects.all(),
        to_field_name='name',
        help_text='Device name or ID',
        error_messages={
            'invalid_choice': 'Device not found.',
        }
    )
    manufacturer = forms.ModelChoiceField(
        queryset=Manufacturer.objects.all(),
        to_field_name='name',
        required=False,
        help_text='Manufacturer name',
        error_messages={
            'invalid_choice': 'Invalid manufacturer.',
        }
    )

    class Meta:
        model = InventoryItem
        fields = InventoryItem.csv_headers


class InventoryItemBulkEditForm(BootstrapMixin, BulkEditForm):
    pk = forms.ModelMultipleChoiceField(queryset=InventoryItem.objects.all(), widget=forms.MultipleHiddenInput)
    manufacturer = forms.ModelChoiceField(queryset=Manufacturer.objects.all(), required=False)
    part_id = forms.CharField(max_length=50, required=False, label='Part ID')
    description = forms.CharField(max_length=100, required=False)

    class Meta:
        nullable_fields = ['manufacturer', 'part_id', 'description']


class InventoryItemFilterForm(BootstrapMixin, forms.Form):
    model = InventoryItem
    q = forms.CharField(required=False, label='Search')
    manufacturer = FilterChoiceField(
        queryset=Manufacturer.objects.annotate(filter_count=Count('inventory_items')),
        to_field_name='slug',
        null_label='-- None --'
    )


#
# Virtual chassis
#

class DeviceSelectionForm(forms.Form):
    pk = forms.ModelMultipleChoiceField(queryset=Device.objects.all(), widget=forms.MultipleHiddenInput)


class VirtualChassisForm(BootstrapMixin, forms.ModelForm):
    tags = TagField(required=False)

    class Meta:
        model = VirtualChassis
        fields = ['master', 'domain', 'tags']
        widgets = {
            'master': SelectWithPK,
        }


class BaseVCMemberFormSet(forms.BaseModelFormSet):

    def clean(self):
        super(BaseVCMemberFormSet, self).clean()

        # Check for duplicate VC position values
        vc_position_list = []
        for form in self.forms:
            vc_position = form.cleaned_data.get('vc_position')
            if vc_position:
                if vc_position in vc_position_list:
                    error_msg = 'A virtual chassis member already exists in position {}.'.format(vc_position)
                    form.add_error('vc_position', error_msg)
                vc_position_list.append(vc_position)


class DeviceVCMembershipForm(forms.ModelForm):

    class Meta:
        model = Device
        fields = ['vc_position', 'vc_priority']
        labels = {
            'vc_position': 'Position',
            'vc_priority': 'Priority',
        }

    def __init__(self, validate_vc_position=False, *args, **kwargs):
        super(DeviceVCMembershipForm, self).__init__(*args, **kwargs)

        # Require VC position (only required when the Device is a VirtualChassis member)
        self.fields['vc_position'].required = True

        # Validation of vc_position is optional. This is only required when adding a new member to an existing
        # VirtualChassis. Otherwise, vc_position validation is handled by BaseVCMemberFormSet.
        self.validate_vc_position = validate_vc_position

    def clean_vc_position(self):
        vc_position = self.cleaned_data['vc_position']

        if self.validate_vc_position:
            conflicting_members = Device.objects.filter(
                virtual_chassis=self.instance.virtual_chassis,
                vc_position=vc_position
            )
            if conflicting_members.exists():
                raise forms.ValidationError(
                    'A virtual chassis member already exists in position {}.'.format(vc_position)
                )

        return vc_position


class VCMemberSelectForm(BootstrapMixin, ChainedFieldsMixin, forms.Form):
    site = forms.ModelChoiceField(
        queryset=Site.objects.all(),
        label='Site',
        required=False,
        widget=forms.Select(
            attrs={'filter-for': 'rack'}
        )
    )
    rack = ChainedModelChoiceField(
        queryset=Rack.objects.all(),
        chains=(
            ('site', 'site'),
        ),
        label='Rack',
        required=False,
        widget=APISelect(
            api_url='/api/dcim/racks/?site_id={{site}}',
            attrs={'filter-for': 'device', 'nullable': 'true'}
        )
    )
    device = ChainedModelChoiceField(
        queryset=Device.objects.filter(virtual_chassis__isnull=True),
        chains=(
            ('site', 'site'),
            ('rack', 'rack'),
        ),
        label='Device',
        widget=APISelect(
            api_url='/api/dcim/devices/?site_id={{site}}&rack_id={{rack}}',
            display_field='display_name',
            disabled_indicator='virtual_chassis'
        )
    )

    def clean_device(self):
        device = self.cleaned_data['device']
        if device.virtual_chassis is not None:
            raise forms.ValidationError("Device {} is already assigned to a virtual chassis.".format(device))
        return device


class VirtualChassisFilterForm(BootstrapMixin, CustomFieldFilterForm):
    model = VirtualChassis
    q = forms.CharField(required=False, label='Search')
    site = FilterChoiceField(
        queryset=Site.objects.all(),
        to_field_name='slug',
    )
    tenant = FilterChoiceField(
        queryset=Tenant.objects.all(),
        to_field_name='slug',
        null_label='-- None --',
    )
