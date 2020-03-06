import re

from django import forms
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.forms.array import SimpleArrayField
from django.core.exceptions import ObjectDoesNotExist
from mptt.forms import TreeNodeChoiceField
from netaddr import EUI
from netaddr.core import AddrFormatError
from taggit.forms import TagField
from timezone_field import TimeZoneFormField

from circuits.models import Circuit, Provider
from extras.forms import (
    AddRemoveTagsForm, CustomFieldBulkEditForm, CustomFieldModelCSVForm, CustomFieldFilterForm, CustomFieldModelForm,
    LocalConfigContextFilterForm,
)
from ipam.constants import BGP_ASN_MAX, BGP_ASN_MIN
from ipam.models import IPAddress, VLAN
from tenancy.forms import TenancyFilterForm, TenancyForm
from tenancy.models import Tenant, TenantGroup
from utilities.forms import (
    APISelect, APISelectMultiple, add_blank_choice, ArrayFieldSelectMultiple, BootstrapMixin, BulkEditForm,
    BulkEditNullBooleanSelect, ColorSelect, CommentField, ConfirmationForm, CSVChoiceField, DynamicModelChoiceField,
    DynamicModelMultipleChoiceField, ExpandableNameField, FlexibleModelChoiceField, JSONField, SelectWithPK,
    SmallTextarea, SlugField, StaticSelect2, StaticSelect2Multiple, TagFilterField, BOOLEAN_WITH_BLANK_CHOICES,
)
from virtualization.models import Cluster, ClusterGroup, VirtualMachine
from .choices import *
from .constants import *
from .models import (
    Cable, DeviceBay, DeviceBayTemplate, ConsolePort, ConsolePortTemplate, ConsoleServerPort, ConsoleServerPortTemplate,
    Device, DeviceRole, DeviceType, FrontPort, FrontPortTemplate, Interface, InterfaceTemplate, Manufacturer,
    InventoryItem, Platform, PowerFeed, PowerOutlet, PowerOutletTemplate, PowerPanel, PowerPort, PowerPortTemplate,
    Rack, RackGroup, RackReservation, RackRole, RearPort, RearPortTemplate, Region, Site, VirtualChassis,
)

DEVICE_BY_PK_RE = r'{\d+\}'

INTERFACE_MODE_HELP_TEXT = """
Access: One untagged VLAN<br />
Tagged: One untagged VLAN and/or one or more tagged VLANs<br />
Tagged (All): Implies all VLANs are available (w/optional untagged VLAN)
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


class DeviceComponentFilterForm(BootstrapMixin, forms.Form):

    field_order = [
        'q', 'region', 'site'
    ]
    q = forms.CharField(
        required=False,
        label='Search'
    )
    region = DynamicModelMultipleChoiceField(
        queryset=Region.objects.all(),
        to_field_name='slug',
        required=False,
        widget=APISelectMultiple(
            api_url='/api/dcim/regions/',
            value_field='slug',
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
            api_url="/api/dcim/sites/",
            value_field="slug",
            filter_for={
                'device_id': 'site',
            }
        )
    )
    device_id = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        required=False,
        label='Device',
        widget=APISelectMultiple(
            api_url='/api/dcim/devices/',
        )
    )


class InterfaceCommonForm:

    def clean(self):

        super().clean()

        # Validate VLAN assignments
        tagged_vlans = self.cleaned_data['tagged_vlans']

        # Untagged interfaces cannot be assigned tagged VLANs
        if self.cleaned_data['mode'] == InterfaceModeChoices.MODE_ACCESS and tagged_vlans:
            raise forms.ValidationError({
                'mode': "An access interface cannot have tagged VLANs assigned."
            })

        # Remove all tagged VLAN assignments from "tagged all" interfaces
        elif self.cleaned_data['mode'] == InterfaceModeChoices.MODE_TAGGED_ALL:
            self.cleaned_data['tagged_vlans'] = []

        # Validate tagged VLANs; must be a global VLAN or in the same site
        elif self.cleaned_data['mode'] == InterfaceModeChoices.MODE_TAGGED:
            valid_sites = [None, self.cleaned_data['device'].site]
            invalid_vlans = [str(v) for v in tagged_vlans if v.site not in valid_sites]

            if invalid_vlans:
                raise forms.ValidationError({
                    'tagged_vlans': "The tagged VLANs ({}) must belong to the same site as the interface's parent "
                                    "device/VM, or they must be global".format(', '.join(invalid_vlans))
                })


class BulkRenameForm(forms.Form):
    """
    An extendable form to be used for renaming device components in bulk.
    """
    find = forms.CharField()
    replace = forms.CharField()
    use_regex = forms.BooleanField(
        required=False,
        initial=True,
        label='Use regular expressions'
    )

    def clean(self):

        # Validate regular expression in "find" field
        if self.cleaned_data['use_regex']:
            try:
                re.compile(self.cleaned_data['find'])
            except re.error:
                raise forms.ValidationError({
                    'find': "Invalid regular expression"
                })


#
# Fields
#

class MACAddressField(forms.Field):
    widget = forms.CharField
    default_error_messages = {
        'invalid': 'MAC address must be in EUI-48 format',
    }

    def to_python(self, value):
        value = super().to_python(value)

        # Validate MAC address format
        try:
            value = EUI(value.strip())
        except AddrFormatError:
            raise forms.ValidationError(self.error_messages['invalid'], code='invalid')

        return value


#
# Regions
#

class RegionForm(BootstrapMixin, forms.ModelForm):
    parent = TreeNodeChoiceField(
        queryset=Region.objects.all(),
        required=False,
        widget=StaticSelect2()
    )
    slug = SlugField()

    class Meta:
        model = Region
        fields = (
            'parent', 'name', 'slug',
        )


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
    q = forms.CharField(
        required=False,
        label='Search'
    )


#
# Sites
#

class SiteForm(BootstrapMixin, TenancyForm, CustomFieldModelForm):
    region = TreeNodeChoiceField(
        queryset=Region.objects.all(),
        required=False,
        widget=StaticSelect2()
    )
    slug = SlugField()
    comments = CommentField()
    tags = TagField(
        required=False
    )

    class Meta:
        model = Site
        fields = [
            'name', 'slug', 'status', 'region', 'tenant_group', 'tenant', 'facility', 'asn', 'time_zone', 'description',
            'physical_address', 'shipping_address', 'latitude', 'longitude', 'contact_name', 'contact_phone',
            'contact_email', 'comments', 'tags',
        ]
        widgets = {
            'physical_address': SmallTextarea(
                attrs={
                    'rows': 3,
                }
            ),
            'shipping_address': SmallTextarea(
                attrs={
                    'rows': 3,
                }
            ),
            'status': StaticSelect2(),
            'time_zone': StaticSelect2(),
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


class SiteCSVForm(CustomFieldModelCSVForm):
    status = CSVChoiceField(
        choices=SiteStatusChoices,
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
        choices=add_blank_choice(SiteStatusChoices),
        required=False,
        initial='',
        widget=StaticSelect2()
    )
    region = TreeNodeChoiceField(
        queryset=Region.objects.all(),
        required=False,
        widget=StaticSelect2()
    )
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        widget=APISelect(
            api_url="/api/tenancy/tenants",
        )
    )
    asn = forms.IntegerField(
        min_value=BGP_ASN_MIN,
        max_value=BGP_ASN_MAX,
        required=False,
        label='ASN'
    )
    description = forms.CharField(
        max_length=100,
        required=False
    )
    time_zone = TimeZoneFormField(
        choices=add_blank_choice(TimeZoneFormField().choices),
        required=False,
        widget=StaticSelect2()
    )

    class Meta:
        nullable_fields = [
            'region', 'tenant', 'asn', 'description', 'time_zone',
        ]


class SiteFilterForm(BootstrapMixin, TenancyFilterForm, CustomFieldFilterForm):
    model = Site
    field_order = ['q', 'status', 'region', 'tenant_group', 'tenant']
    q = forms.CharField(
        required=False,
        label='Search'
    )
    status = forms.MultipleChoiceField(
        choices=SiteStatusChoices,
        required=False,
        widget=StaticSelect2Multiple()
    )
    region = DynamicModelMultipleChoiceField(
        queryset=Region.objects.all(),
        to_field_name='slug',
        required=False,
        widget=APISelectMultiple(
            api_url="/api/dcim/regions/",
            value_field="slug",
        )
    )
    tag = TagFilterField(model)


#
# Rack groups
#

class RackGroupForm(BootstrapMixin, forms.ModelForm):
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        widget=APISelect(
            api_url="/api/dcim/sites/"
        )
    )
    slug = SlugField()

    class Meta:
        model = RackGroup
        fields = (
            'site', 'name', 'slug',
        )


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
    region = DynamicModelMultipleChoiceField(
        queryset=Region.objects.all(),
        to_field_name='slug',
        required=False,
        widget=APISelectMultiple(
            api_url="/api/dcim/regions/",
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
            api_url="/api/dcim/sites/",
            value_field="slug",
        )
    )


#
# Rack roles
#

class RackRoleForm(BootstrapMixin, forms.ModelForm):
    slug = SlugField()

    class Meta:
        model = RackRole
        fields = [
            'name', 'slug', 'color', 'description',
        ]


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

class RackForm(BootstrapMixin, TenancyForm, CustomFieldModelForm):
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        widget=APISelect(
            api_url="/api/dcim/sites/",
            filter_for={
                'group': 'site_id',
            }
        )
    )
    group = DynamicModelChoiceField(
        queryset=RackGroup.objects.all(),
        required=False,
        widget=APISelect(
            api_url='/api/dcim/rack-groups/',
        )
    )
    role = DynamicModelChoiceField(
        queryset=RackRole.objects.all(),
        required=False,
        widget=APISelect(
            api_url='/api/dcim/rack-roles/',
        )
    )
    comments = CommentField()
    tags = TagField(
        required=False
    )

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
            'status': StaticSelect2(),
            'type': StaticSelect2(),
            'width': StaticSelect2(),
            'outer_unit': StaticSelect2(),
        }


class RackCSVForm(CustomFieldModelCSVForm):
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
        choices=RackStatusChoices,
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
        choices=RackTypeChoices,
        required=False,
        help_text='Rack type'
    )
    width = forms.ChoiceField(
        choices=RackWidthChoices,
        help_text='Rail-to-rail width (in inches)'
    )
    outer_unit = CSVChoiceField(
        choices=RackDimensionUnitChoices,
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

        super().clean()

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
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        widget=APISelect(
            api_url="/api/dcim/sites",
            filter_for={
                'group': 'site_id',
            }
        )
    )
    group = DynamicModelChoiceField(
        queryset=RackGroup.objects.all(),
        required=False,
        widget=APISelect(
            api_url="/api/dcim/rack-groups",
        )
    )
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        widget=APISelect(
            api_url="/api/tenancy/tenants",
        )
    )
    status = forms.ChoiceField(
        choices=add_blank_choice(RackStatusChoices),
        required=False,
        initial='',
        widget=StaticSelect2()
    )
    role = DynamicModelChoiceField(
        queryset=RackRole.objects.all(),
        required=False,
        widget=APISelect(
            api_url="/api/dcim/rack-roles",
        )
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
        choices=add_blank_choice(RackTypeChoices),
        required=False,
        widget=StaticSelect2()
    )
    width = forms.ChoiceField(
        choices=add_blank_choice(RackWidthChoices),
        required=False,
        widget=StaticSelect2()
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
        choices=add_blank_choice(RackDimensionUnitChoices),
        required=False,
        widget=StaticSelect2()
    )
    comments = CommentField(
        widget=SmallTextarea,
        label='Comments'
    )

    class Meta:
        nullable_fields = [
            'group', 'tenant', 'role', 'serial', 'asset_tag', 'outer_width', 'outer_depth', 'outer_unit', 'comments',
        ]


class RackFilterForm(BootstrapMixin, TenancyFilterForm, CustomFieldFilterForm):
    model = Rack
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
            api_url="/api/dcim/regions/",
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
            api_url="/api/dcim/sites/",
            value_field="slug",
            filter_for={
                'group_id': 'site'
            }
        )
    )
    group_id = DynamicModelMultipleChoiceField(
        queryset=RackGroup.objects.prefetch_related(
            'site'
        ),
        required=False,
        label='Rack group',
        widget=APISelectMultiple(
            api_url="/api/dcim/rack-groups/",
            null_option=True
        )
    )
    status = forms.MultipleChoiceField(
        choices=RackStatusChoices,
        required=False,
        widget=StaticSelect2Multiple()
    )
    role = DynamicModelMultipleChoiceField(
        queryset=RackRole.objects.all(),
        to_field_name='slug',
        required=False,
        widget=APISelectMultiple(
            api_url="/api/dcim/rack-roles/",
            value_field="slug",
            null_option=True,
        )
    )
    tag = TagFilterField(model)


#
# Rack elevations
#

class RackElevationFilterForm(RackFilterForm):
    field_order = ['q', 'region', 'site', 'group_id', 'id', 'status', 'role', 'tenant_group', 'tenant']
    id = DynamicModelMultipleChoiceField(
        queryset=Rack.objects.all(),
        label='Rack',
        required=False,
        widget=APISelectMultiple(
            api_url='/api/dcim/racks/',
            display_field='display_name',
        )
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Filter the rack field based on the site and group
        self.fields['site'].widget.add_filter_for('id', 'site')
        self.fields['group_id'].widget.add_filter_for('id', 'group_id')


#
# Rack reservations
#

class RackReservationForm(BootstrapMixin, TenancyForm, forms.ModelForm):
    units = SimpleArrayField(
        base_field=forms.IntegerField(),
        widget=ArrayFieldSelectMultiple(
            attrs={
                'size': 10,
            }
        )
    )
    user = forms.ModelChoiceField(
        queryset=User.objects.order_by(
            'username'
        ),
        widget=StaticSelect2()
    )

    class Meta:
        model = RackReservation
        fields = [
            'units', 'user', 'tenant_group', 'tenant', 'description',
        ]

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

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


class RackReservationBulkEditForm(BootstrapMixin, BulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=RackReservation.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
    user = forms.ModelChoiceField(
        queryset=User.objects.order_by(
            'username'
        ),
        required=False,
        widget=StaticSelect2()
    )
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        widget=APISelect(
            api_url="/api/tenancy/tenant",
        )
    )
    description = forms.CharField(
        max_length=100,
        required=False
    )

    class Meta:
        nullable_fields = []


class RackReservationFilterForm(BootstrapMixin, TenancyFilterForm):
    field_order = ['q', 'site', 'group_id', 'tenant_group', 'tenant']
    q = forms.CharField(
        required=False,
        label='Search'
    )
    site = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        to_field_name='slug',
        required=False,
        widget=APISelectMultiple(
            api_url="/api/dcim/sites/",
            value_field="slug",
        )
    )
    group_id = DynamicModelMultipleChoiceField(
        queryset=RackGroup.objects.prefetch_related('site'),
        required=False,
        label='Rack group',
        widget=APISelectMultiple(
            api_url="/api/dcim/rack-groups/",
            null_option=True,
        )
    )


#
# Manufacturers
#

class ManufacturerForm(BootstrapMixin, forms.ModelForm):
    slug = SlugField()

    class Meta:
        model = Manufacturer
        fields = [
            'name', 'slug',
        ]


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

class DeviceTypeForm(BootstrapMixin, CustomFieldModelForm):
    manufacturer = DynamicModelChoiceField(
        queryset=Manufacturer.objects.all(),
        widget=APISelect(
            api_url="/api/dcim/manufacturers/",
        )
    )
    slug = SlugField(
        slug_source='model'
    )
    comments = CommentField()
    tags = TagField(
        required=False
    )

    class Meta:
        model = DeviceType
        fields = [
            'manufacturer', 'model', 'slug', 'part_number', 'u_height', 'is_full_depth', 'subdevice_role',
            'front_image', 'rear_image', 'comments', 'tags',
        ]
        widgets = {
            'subdevice_role': StaticSelect2()
        }


class DeviceTypeImportForm(BootstrapMixin, forms.ModelForm):
    manufacturer = forms.ModelChoiceField(
        queryset=Manufacturer.objects.all(),
        to_field_name='name'
    )

    class Meta:
        model = DeviceType
        fields = [
            'manufacturer', 'model', 'slug', 'part_number', 'u_height', 'is_full_depth', 'subdevice_role',
        ]


class DeviceTypeBulkEditForm(BootstrapMixin, AddRemoveTagsForm, CustomFieldBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=DeviceType.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
    manufacturer = DynamicModelChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False,
        widget=APISelect(
            api_url="/api/dcim/manufacturers"
        )
    )
    u_height = forms.IntegerField(
        min_value=1,
        required=False
    )
    is_full_depth = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect(),
        label='Is full depth'
    )

    class Meta:
        nullable_fields = []


class DeviceTypeFilterForm(BootstrapMixin, CustomFieldFilterForm):
    model = DeviceType
    q = forms.CharField(
        required=False,
        label='Search'
    )
    manufacturer = DynamicModelMultipleChoiceField(
        queryset=Manufacturer.objects.all(),
        to_field_name='slug',
        required=False,
        widget=APISelectMultiple(
            api_url="/api/dcim/manufacturers/",
            value_field="slug",
        )
    )
    subdevice_role = forms.MultipleChoiceField(
        choices=add_blank_choice(SubdeviceRoleChoices),
        required=False,
        widget=StaticSelect2Multiple()
    )
    console_ports = forms.NullBooleanField(
        required=False,
        label='Has console ports',
        widget=StaticSelect2(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    console_server_ports = forms.NullBooleanField(
        required=False,
        label='Has console server ports',
        widget=StaticSelect2(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    power_ports = forms.NullBooleanField(
        required=False,
        label='Has power ports',
        widget=StaticSelect2(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    power_outlets = forms.NullBooleanField(
        required=False,
        label='Has power outlets',
        widget=StaticSelect2(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    interfaces = forms.NullBooleanField(
        required=False,
        label='Has interfaces',
        widget=StaticSelect2(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    pass_through_ports = forms.NullBooleanField(
        required=False,
        label='Has pass-through ports',
        widget=StaticSelect2(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    tag = TagFilterField(model)


#
# Device component templates
#

class ConsolePortTemplateForm(BootstrapMixin, forms.ModelForm):

    class Meta:
        model = ConsolePortTemplate
        fields = [
            'device_type', 'name', 'type',
        ]
        widgets = {
            'device_type': forms.HiddenInput(),
        }


class ConsolePortTemplateCreateForm(BootstrapMixin, forms.Form):
    device_type = DynamicModelChoiceField(
        queryset=DeviceType.objects.all(),
        widget=APISelect(
            api_url='/api/dcim/device-types/'
        )
    )
    name_pattern = ExpandableNameField(
        label='Name'
    )
    type = forms.ChoiceField(
        choices=add_blank_choice(ConsolePortTypeChoices),
        widget=StaticSelect2()
    )


class ConsolePortTemplateBulkEditForm(BootstrapMixin, BulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=ConsolePortTemplate.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
    type = forms.ChoiceField(
        choices=add_blank_choice(ConsolePortTypeChoices),
        required=False,
        widget=StaticSelect2()
    )

    class Meta:
        nullable_fields = ('type',)


class ConsoleServerPortTemplateForm(BootstrapMixin, forms.ModelForm):

    class Meta:
        model = ConsoleServerPortTemplate
        fields = [
            'device_type', 'name', 'type',
        ]
        widgets = {
            'device_type': forms.HiddenInput(),
        }


class ConsoleServerPortTemplateCreateForm(BootstrapMixin, forms.Form):
    device_type = DynamicModelChoiceField(
        queryset=DeviceType.objects.all(),
        widget=APISelect(
            api_url='/api/dcim/device-types/'
        )
    )
    name_pattern = ExpandableNameField(
        label='Name'
    )
    type = forms.ChoiceField(
        choices=add_blank_choice(ConsolePortTypeChoices),
        widget=StaticSelect2()
    )


class ConsoleServerPortTemplateBulkEditForm(BootstrapMixin, BulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=ConsoleServerPortTemplate.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
    type = forms.ChoiceField(
        choices=add_blank_choice(ConsolePortTypeChoices),
        required=False,
        widget=StaticSelect2()
    )

    class Meta:
        nullable_fields = ('type',)


class PowerPortTemplateForm(BootstrapMixin, forms.ModelForm):

    class Meta:
        model = PowerPortTemplate
        fields = [
            'device_type', 'name', 'type', 'maximum_draw', 'allocated_draw',
        ]
        widgets = {
            'device_type': forms.HiddenInput(),
        }


class PowerPortTemplateCreateForm(BootstrapMixin, forms.Form):
    device_type = DynamicModelChoiceField(
        queryset=DeviceType.objects.all(),
        widget=APISelect(
            api_url='/api/dcim/device-types/'
        )
    )
    name_pattern = ExpandableNameField(
        label='Name'
    )
    type = forms.ChoiceField(
        choices=add_blank_choice(PowerPortTypeChoices),
        required=False
    )
    maximum_draw = forms.IntegerField(
        min_value=1,
        required=False,
        help_text="Maximum power draw (watts)"
    )
    allocated_draw = forms.IntegerField(
        min_value=1,
        required=False,
        help_text="Allocated power draw (watts)"
    )


class PowerPortTemplateBulkEditForm(BootstrapMixin, BulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=PowerPortTemplate.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
    type = forms.ChoiceField(
        choices=add_blank_choice(PowerPortTypeChoices),
        required=False,
        widget=StaticSelect2()
    )
    maximum_draw = forms.IntegerField(
        min_value=1,
        required=False,
        help_text="Maximum power draw (watts)"
    )
    allocated_draw = forms.IntegerField(
        min_value=1,
        required=False,
        help_text="Allocated power draw (watts)"
    )

    class Meta:
        nullable_fields = ('type', 'maximum_draw', 'allocated_draw')


class PowerOutletTemplateForm(BootstrapMixin, forms.ModelForm):

    class Meta:
        model = PowerOutletTemplate
        fields = [
            'device_type', 'name', 'type', 'power_port', 'feed_leg',
        ]
        widgets = {
            'device_type': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        # Limit power_port choices to current DeviceType
        if hasattr(self.instance, 'device_type'):
            self.fields['power_port'].queryset = PowerPortTemplate.objects.filter(
                device_type=self.instance.device_type
            )


class PowerOutletTemplateCreateForm(BootstrapMixin, forms.Form):
    device_type = DynamicModelChoiceField(
        queryset=DeviceType.objects.all(),
        widget=APISelect(
            api_url='/api/dcim/device-types/'
        )
    )
    name_pattern = ExpandableNameField(
        label='Name'
    )
    type = forms.ChoiceField(
        choices=add_blank_choice(PowerOutletTypeChoices),
        required=False
    )
    power_port = forms.ModelChoiceField(
        queryset=PowerPortTemplate.objects.all(),
        required=False
    )
    feed_leg = forms.ChoiceField(
        choices=add_blank_choice(PowerOutletFeedLegChoices),
        required=False,
        widget=StaticSelect2()
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Limit power_port choices to current DeviceType
        device_type = DeviceType.objects.get(
            pk=self.initial.get('device_type') or self.data.get('device_type')
        )
        self.fields['power_port'].queryset = PowerPortTemplate.objects.filter(
            device_type=device_type
        )


class PowerOutletTemplateBulkEditForm(BootstrapMixin, BulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=PowerOutletTemplate.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
    type = forms.ChoiceField(
        choices=add_blank_choice(PowerOutletTypeChoices),
        required=False,
        widget=StaticSelect2()
    )
    feed_leg = forms.ChoiceField(
        choices=add_blank_choice(PowerOutletFeedLegChoices),
        required=False,
        widget=StaticSelect2()
    )

    class Meta:
        nullable_fields = ('type', 'feed_leg')


class InterfaceTemplateForm(BootstrapMixin, forms.ModelForm):

    class Meta:
        model = InterfaceTemplate
        fields = [
            'device_type', 'name', 'type', 'mgmt_only',
        ]
        widgets = {
            'device_type': forms.HiddenInput(),
            'type': StaticSelect2(),
        }


class InterfaceTemplateCreateForm(BootstrapMixin, forms.Form):
    device_type = DynamicModelChoiceField(
        queryset=DeviceType.objects.all(),
        widget=APISelect(
            api_url='/api/dcim/device-types/'
        )
    )
    name_pattern = ExpandableNameField(
        label='Name'
    )
    type = forms.ChoiceField(
        choices=InterfaceTypeChoices,
        widget=StaticSelect2()
    )
    mgmt_only = forms.BooleanField(
        required=False,
        label='Management only'
    )


class InterfaceTemplateBulkEditForm(BootstrapMixin, BulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=InterfaceTemplate.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
    type = forms.ChoiceField(
        choices=add_blank_choice(InterfaceTypeChoices),
        required=False,
        widget=StaticSelect2()
    )
    mgmt_only = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect,
        label='Management only'
    )

    class Meta:
        nullable_fields = []


class FrontPortTemplateForm(BootstrapMixin, forms.ModelForm):

    class Meta:
        model = FrontPortTemplate
        fields = [
            'device_type', 'name', 'type', 'rear_port', 'rear_port_position',
        ]
        widgets = {
            'device_type': forms.HiddenInput(),
            'rear_port': StaticSelect2(),
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        # Limit rear_port choices to current DeviceType
        if hasattr(self.instance, 'device_type'):
            self.fields['rear_port'].queryset = RearPortTemplate.objects.filter(
                device_type=self.instance.device_type
            )


class FrontPortTemplateCreateForm(BootstrapMixin, forms.Form):
    device_type = DynamicModelChoiceField(
        queryset=DeviceType.objects.all(),
        widget=APISelect(
            api_url='/api/dcim/device-types/'
        )
    )
    name_pattern = ExpandableNameField(
        label='Name'
    )
    type = forms.ChoiceField(
        choices=PortTypeChoices,
        widget=StaticSelect2()
    )
    rear_port_set = forms.MultipleChoiceField(
        choices=[],
        label='Rear ports',
        help_text='Select one rear port assignment for each front port being created.',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        device_type = DeviceType.objects.get(
            pk=self.initial.get('device_type') or self.data.get('device_type')
        )

        # Determine which rear port positions are occupied. These will be excluded from the list of available mappings.
        occupied_port_positions = [
            (front_port.rear_port_id, front_port.rear_port_position)
            for front_port in device_type.frontport_templates.all()
        ]

        # Populate rear port choices
        choices = []
        rear_ports = RearPortTemplate.objects.filter(device_type=device_type)
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


class FrontPortTemplateBulkEditForm(BootstrapMixin, BulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=FrontPortTemplate.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
    type = forms.ChoiceField(
        choices=add_blank_choice(PortTypeChoices),
        required=False,
        widget=StaticSelect2()
    )

    class Meta:
        nullable_fields = ()


class RearPortTemplateForm(BootstrapMixin, forms.ModelForm):

    class Meta:
        model = RearPortTemplate
        fields = [
            'device_type', 'name', 'type', 'positions',
        ]
        widgets = {
            'device_type': forms.HiddenInput(),
            'type': StaticSelect2(),
        }


class RearPortTemplateCreateForm(BootstrapMixin, forms.Form):
    device_type = DynamicModelChoiceField(
        queryset=DeviceType.objects.all(),
        widget=APISelect(
            api_url='/api/dcim/device-types/'
        )
    )
    name_pattern = ExpandableNameField(
        label='Name'
    )
    type = forms.ChoiceField(
        choices=PortTypeChoices,
        widget=StaticSelect2(),
    )
    positions = forms.IntegerField(
        min_value=REARPORT_POSITIONS_MIN,
        max_value=REARPORT_POSITIONS_MAX,
        initial=1,
        help_text='The number of front ports which may be mapped to each rear port'
    )


class RearPortTemplateBulkEditForm(BootstrapMixin, BulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=RearPortTemplate.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
    type = forms.ChoiceField(
        choices=add_blank_choice(PortTypeChoices),
        required=False,
        widget=StaticSelect2()
    )

    class Meta:
        nullable_fields = ()


class DeviceBayTemplateForm(BootstrapMixin, forms.ModelForm):

    class Meta:
        model = DeviceBayTemplate
        fields = [
            'device_type', 'name',
        ]
        widgets = {
            'device_type': forms.HiddenInput(),
        }


class DeviceBayTemplateCreateForm(BootstrapMixin, forms.Form):
    device_type = DynamicModelChoiceField(
        queryset=DeviceType.objects.all(),
        widget=APISelect(
            api_url='/api/dcim/device-types/'
        )
    )
    name_pattern = ExpandableNameField(
        label='Name'
    )


# TODO: DeviceBayTemplate has no fields suitable for bulk-editing yet
# class DeviceBayTemplateBulkEditForm(BootstrapMixin, BulkEditForm):
#     pk = forms.ModelMultipleChoiceField(
#         queryset=FrontPortTemplate.objects.all(),
#         widget=forms.MultipleHiddenInput()
#     )
#
#     class Meta:
#         nullable_fields = ()


#
# Component template import forms
#

class ComponentTemplateImportForm(BootstrapMixin, forms.ModelForm):

    def __init__(self, device_type, data=None, *args, **kwargs):

        # Must pass the parent DeviceType on form initialization
        data.update({
            'device_type': device_type.pk,
        })

        super().__init__(data, *args, **kwargs)

    def clean_device_type(self):

        data = self.cleaned_data['device_type']

        # Limit fields referencing other components to the parent DeviceType
        for field_name, field in self.fields.items():
            if isinstance(field, forms.ModelChoiceField) and field_name != 'device_type':
                field.queryset = field.queryset.filter(device_type=data)

        return data


class ConsolePortTemplateImportForm(ComponentTemplateImportForm):

    class Meta:
        model = ConsolePortTemplate
        fields = [
            'device_type', 'name', 'type',
        ]


class ConsoleServerPortTemplateImportForm(ComponentTemplateImportForm):

    class Meta:
        model = ConsoleServerPortTemplate
        fields = [
            'device_type', 'name', 'type',
        ]


class PowerPortTemplateImportForm(ComponentTemplateImportForm):

    class Meta:
        model = PowerPortTemplate
        fields = [
            'device_type', 'name', 'type', 'maximum_draw', 'allocated_draw',
        ]


class PowerOutletTemplateImportForm(ComponentTemplateImportForm):
    power_port = forms.ModelChoiceField(
        queryset=PowerPortTemplate.objects.all(),
        to_field_name='name',
        required=False
    )

    class Meta:
        model = PowerOutletTemplate
        fields = [
            'device_type', 'name', 'type', 'power_port', 'feed_leg',
        ]


class InterfaceTemplateImportForm(ComponentTemplateImportForm):
    type = forms.ChoiceField(
        choices=InterfaceTypeChoices.CHOICES
    )

    class Meta:
        model = InterfaceTemplate
        fields = [
            'device_type', 'name', 'type', 'mgmt_only',
        ]


class FrontPortTemplateImportForm(ComponentTemplateImportForm):
    type = forms.ChoiceField(
        choices=PortTypeChoices.CHOICES
    )
    rear_port = forms.ModelChoiceField(
        queryset=RearPortTemplate.objects.all(),
        to_field_name='name',
        required=False
    )

    class Meta:
        model = FrontPortTemplate
        fields = [
            'device_type', 'name', 'type', 'rear_port', 'rear_port_position',
        ]


class RearPortTemplateImportForm(ComponentTemplateImportForm):
    type = forms.ChoiceField(
        choices=PortTypeChoices.CHOICES
    )

    class Meta:
        model = RearPortTemplate
        fields = [
            'device_type', 'name', 'type', 'positions',
        ]


class DeviceBayTemplateImportForm(ComponentTemplateImportForm):

    class Meta:
        model = DeviceBayTemplate
        fields = [
            'device_type', 'name',
        ]


#
# Device roles
#

class DeviceRoleForm(BootstrapMixin, forms.ModelForm):
    slug = SlugField()

    class Meta:
        model = DeviceRole
        fields = [
            'name', 'slug', 'color', 'vm_role', 'description',
        ]


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
    manufacturer = DynamicModelChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False,
        widget=APISelect(
            api_url="/api/dcim/manufacturers/",
        )
    )
    slug = SlugField(
        max_length=64
    )

    class Meta:
        model = Platform
        fields = [
            'name', 'slug', 'manufacturer', 'napalm_driver', 'napalm_args',
        ]
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

class DeviceForm(BootstrapMixin, TenancyForm, CustomFieldModelForm):
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        widget=APISelect(
            api_url="/api/dcim/sites/",
            filter_for={
                'rack': 'site_id'
            }
        )
    )
    rack = DynamicModelChoiceField(
        queryset=Rack.objects.all(),
        required=False,
        widget=APISelect(
            api_url='/api/dcim/racks/',
            display_field='display_name'
        )
    )
    position = forms.TypedChoiceField(
        required=False,
        empty_value=None,
        help_text="The lowest-numbered unit occupied by the device",
        widget=APISelect(
            api_url='/api/dcim/racks/{{rack}}/elevation/',
            disabled_indicator='device'
        )
    )
    manufacturer = DynamicModelChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False,
        widget=APISelect(
            api_url="/api/dcim/manufacturers/",
            filter_for={
                'device_type': 'manufacturer_id',
                'platform': 'manufacturer_id'
            }
        )
    )
    device_type = DynamicModelChoiceField(
        queryset=DeviceType.objects.all(),
        widget=APISelect(
            api_url='/api/dcim/device-types/',
            display_field='model'
        )
    )
    device_role = DynamicModelChoiceField(
        queryset=DeviceRole.objects.all(),
        widget=APISelect(
            api_url='/api/dcim/device-roles/'
        )
    )
    platform = DynamicModelChoiceField(
        queryset=Platform.objects.all(),
        required=False,
        widget=APISelect(
            api_url="/api/dcim/platforms/",
            additional_query_params={
                "manufacturer_id": "null"
            }
        )
    )
    cluster_group = DynamicModelChoiceField(
        queryset=ClusterGroup.objects.all(),
        required=False,
        widget=APISelect(
            api_url="/api/virtualization/cluster-groups/",
            filter_for={
                'cluster': 'group_id'
            },
            attrs={
                'nullable': 'true'
            }
        )
    )
    cluster = DynamicModelChoiceField(
        queryset=Cluster.objects.all(),
        required=False,
        widget=APISelect(
            api_url='/api/virtualization/clusters/',
        )
    )
    comments = CommentField()
    tags = TagField(required=False)
    local_context_data = JSONField(
        required=False,
        label=''
    )

    class Meta:
        model = Device
        fields = [
            'name', 'device_role', 'device_type', 'serial', 'asset_tag', 'site', 'rack', 'position', 'face',
            'status', 'platform', 'primary_ip4', 'primary_ip6', 'cluster_group', 'cluster', 'tenant_group', 'tenant',
            'comments', 'tags', 'local_context_data'
        ]
        help_texts = {
            'device_role': "The function this device serves",
            'serial': "Chassis serial number",
            'local_context_data': "Local config context data overwrites all source contexts in the final rendered "
                                  "config context",
        }
        widgets = {
            'face': StaticSelect2(
                filter_for={
                    'position': 'face'
                }
            ),
            'status': StaticSelect2(),
            'primary_ip4': StaticSelect2(),
            'primary_ip6': StaticSelect2(),
        }

    def __init__(self, *args, **kwargs):

        # Initialize helper selectors
        instance = kwargs.get('instance')
        if 'initial' not in kwargs:
            kwargs['initial'] = {}
        # Using hasattr() instead of "is not None" to avoid RelatedObjectDoesNotExist on required field
        if instance and hasattr(instance, 'device_type'):
            kwargs['initial']['manufacturer'] = instance.device_type.manufacturer
        if instance and instance.cluster is not None:
            kwargs['initial']['cluster_group'] = instance.cluster.group

        if 'device_type' in kwargs['initial'] and 'manufacturer' not in kwargs['initial']:
            device_type_id = kwargs['initial']['device_type']
            manufacturer_id = DeviceType.objects.filter(pk=device_type_id).values_list('manufacturer__pk', flat=True).first()
            kwargs['initial']['manufacturer'] = manufacturer_id

        if 'cluster' in kwargs['initial'] and 'cluster_group' not in kwargs['initial']:
            cluster_id = kwargs['initial']['cluster']
            cluster_group_id = Cluster.objects.filter(pk=cluster_id).values_list('group__pk', flat=True).first()
            kwargs['initial']['cluster_group'] = cluster_group_id

        super().__init__(*args, **kwargs)

        if self.instance.pk:

            # Compile list of choices for primary IPv4 and IPv6 addresses
            for family in [4, 6]:
                ip_choices = [(None, '---------')]

                # Gather PKs of all interfaces belonging to this Device or a peer VirtualChassis member
                interface_ids = self.instance.vc_interfaces.values('pk')

                # Collect interface IPs
                interface_ips = IPAddress.objects.prefetch_related('interface').filter(
                    family=family, interface_id__in=interface_ids
                )
                if interface_ips:
                    ip_list = [(ip.id, '{} ({})'.format(ip.address, ip.interface)) for ip in interface_ips]
                    ip_choices.append(('Interface IPs', ip_list))
                # Collect NAT IPs
                nat_ips = IPAddress.objects.prefetch_related('nat_inside').filter(
                    family=family, nat_inside__interface__in=interface_ids
                )
                if nat_ips:
                    ip_list = [(ip.id, '{} ({})'.format(ip.address, ip.nat_inside.address)) for ip in nat_ips]
                    ip_choices.append(('NAT IPs', ip_list))
                self.fields['primary_ip{}'.format(family)].choices = ip_choices

            # If editing an existing device, exclude it from the list of occupied rack units. This ensures that a device
            # can be flipped from one face to another.
            self.fields['position'].widget.add_additional_query_param('exclude', self.instance.pk)

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


class BaseDeviceCSVForm(CustomFieldModelCSVForm):
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
        choices=DeviceStatusChoices,
        help_text='Operational status'
    )

    class Meta:
        fields = []
        model = Device
        help_texts = {
            'name': 'Device name',
        }

    def clean(self):

        super().clean()

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
        choices=DeviceFaceChoices,
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

        super().clean()

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

        super().clean()

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
    pk = forms.ModelMultipleChoiceField(
        queryset=Device.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
    device_type = DynamicModelChoiceField(
        queryset=DeviceType.objects.all(),
        required=False,
        widget=APISelect(
            api_url="/api/dcim/device-types/",
            display_field='display_name'
        )
    )
    device_role = DynamicModelChoiceField(
        queryset=DeviceRole.objects.all(),
        required=False,
        widget=APISelect(
            api_url="/api/dcim/device-roles/"
        )
    )
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        widget=APISelect(
            api_url="/api/tenancy/tenants/"
        )
    )
    platform = DynamicModelChoiceField(
        queryset=Platform.objects.all(),
        required=False,
        widget=APISelect(
            api_url="/api/dcim/platforms/"
        )
    )
    status = forms.ChoiceField(
        choices=add_blank_choice(DeviceStatusChoices),
        required=False,
        widget=StaticSelect2()
    )
    serial = forms.CharField(
        max_length=50,
        required=False,
        label='Serial Number'
    )

    class Meta:
        nullable_fields = [
            'tenant', 'platform', 'serial',
        ]


class DeviceFilterForm(BootstrapMixin, LocalConfigContextFilterForm, TenancyFilterForm, CustomFieldFilterForm):
    model = Device
    field_order = [
        'q', 'region', 'site', 'rack_group_id', 'rack_id', 'status', 'role', 'tenant_group', 'tenant',
        'manufacturer_id', 'device_type_id', 'mac_address', 'has_primary_ip',
    ]
    q = forms.CharField(
        required=False,
        label='Search'
    )
    region = DynamicModelMultipleChoiceField(
        queryset=Region.objects.all(),
        to_field_name='slug',
        required=False,
        widget=APISelectMultiple(
            api_url="/api/dcim/regions/",
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
            api_url="/api/dcim/sites/",
            value_field="slug",
            filter_for={
                'rack_group_id': 'site',
                'rack_id': 'site',
            }
        )
    )
    rack_group_id = DynamicModelMultipleChoiceField(
        queryset=RackGroup.objects.all(),
        required=False,
        label='Rack group',
        widget=APISelectMultiple(
            api_url="/api/dcim/rack-groups/",
            filter_for={
                'rack_id': 'group_id',
            }
        )
    )
    rack_id = DynamicModelMultipleChoiceField(
        queryset=Rack.objects.all(),
        required=False,
        label='Rack',
        widget=APISelectMultiple(
            api_url="/api/dcim/racks/",
            null_option=True,
        )
    )
    role = DynamicModelMultipleChoiceField(
        queryset=DeviceRole.objects.all(),
        to_field_name='slug',
        required=False,
        widget=APISelectMultiple(
            api_url="/api/dcim/device-roles/",
            value_field="slug",
        )
    )
    manufacturer_id = DynamicModelMultipleChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False,
        label='Manufacturer',
        widget=APISelectMultiple(
            api_url="/api/dcim/manufacturers/",
            filter_for={
                'device_type_id': 'manufacturer_id',
            }
        )
    )
    device_type_id = DynamicModelMultipleChoiceField(
        queryset=DeviceType.objects.all(),
        required=False,
        label='Model',
        widget=APISelectMultiple(
            api_url="/api/dcim/device-types/",
            display_field="model",
        )
    )
    platform = DynamicModelMultipleChoiceField(
        queryset=Platform.objects.all(),
        to_field_name='slug',
        required=False,
        widget=APISelectMultiple(
            api_url="/api/dcim/platforms/",
            value_field="slug",
            null_option=True,
        )
    )
    status = forms.MultipleChoiceField(
        choices=DeviceStatusChoices,
        required=False,
        widget=StaticSelect2Multiple()
    )
    mac_address = forms.CharField(
        required=False,
        label='MAC address'
    )
    has_primary_ip = forms.NullBooleanField(
        required=False,
        label='Has a primary IP',
        widget=StaticSelect2(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    virtual_chassis_member = forms.NullBooleanField(
        required=False,
        label='Virtual chassis member',
        widget=StaticSelect2(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    console_ports = forms.NullBooleanField(
        required=False,
        label='Has console ports',
        widget=StaticSelect2(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    console_server_ports = forms.NullBooleanField(
        required=False,
        label='Has console server ports',
        widget=StaticSelect2(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    power_ports = forms.NullBooleanField(
        required=False,
        label='Has power ports',
        widget=StaticSelect2(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    power_outlets = forms.NullBooleanField(
        required=False,
        label='Has power outlets',
        widget=StaticSelect2(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    interfaces = forms.NullBooleanField(
        required=False,
        label='Has interfaces',
        widget=StaticSelect2(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    pass_through_ports = forms.NullBooleanField(
        required=False,
        label='Has pass-through ports',
        widget=StaticSelect2(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    tag = TagFilterField(model)


#
# Bulk device component creation
#

class DeviceBulkAddComponentForm(BootstrapMixin, forms.Form):
    pk = forms.ModelMultipleChoiceField(
        queryset=Device.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
    name_pattern = ExpandableNameField(
        label='Name'
    )


class DeviceBulkAddInterfaceForm(DeviceBulkAddComponentForm):
    type = forms.ChoiceField(
        choices=InterfaceTypeChoices,
        widget=StaticSelect2()
    )
    enabled = forms.BooleanField(
        required=False,
        initial=True
    )
    mtu = forms.IntegerField(
        required=False,
        min_value=INTERFACE_MTU_MIN,
        max_value=INTERFACE_MTU_MAX,
        label='MTU'
    )
    mgmt_only = forms.BooleanField(
        required=False,
        label='Management only'
    )
    description = forms.CharField(
        max_length=100,
        required=False
    )


#
# Console ports
#


class ConsolePortFilterForm(DeviceComponentFilterForm):
    model = ConsolePort
    type = forms.MultipleChoiceField(
        choices=ConsolePortTypeChoices,
        required=False,
        widget=StaticSelect2Multiple()
    )
    tag = TagFilterField(model)


class ConsolePortForm(BootstrapMixin, forms.ModelForm):
    tags = TagField(
        required=False
    )

    class Meta:
        model = ConsolePort
        fields = [
            'device', 'name', 'type', 'description', 'tags',
        ]
        widgets = {
            'device': forms.HiddenInput(),
        }


class ConsolePortCreateForm(BootstrapMixin, forms.Form):
    device = DynamicModelChoiceField(
        queryset=Device.objects.prefetch_related('device_type__manufacturer'),
        widget=APISelect(
            api_url="/api/dcim/devices/",
        )
    )
    name_pattern = ExpandableNameField(
        label='Name'
    )
    type = forms.ChoiceField(
        choices=add_blank_choice(ConsolePortTypeChoices),
        required=False,
        widget=StaticSelect2()
    )
    description = forms.CharField(
        max_length=100,
        required=False
    )
    tags = TagField(
        required=False
    )


class ConsolePortBulkEditForm(BootstrapMixin, AddRemoveTagsForm, BulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=ConsolePort.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
    type = forms.ChoiceField(
        choices=add_blank_choice(ConsolePortTypeChoices),
        required=False,
        widget=StaticSelect2()
    )
    description = forms.CharField(
        max_length=100,
        required=False
    )

    class Meta:
        nullable_fields = (
            'description',
        )


class ConsolePortCSVForm(forms.ModelForm):
    device = FlexibleModelChoiceField(
        queryset=Device.objects.all(),
        to_field_name='name',
        help_text='Name or ID of device',
        error_messages={
            'invalid_choice': 'Device not found.',
        }
    )

    class Meta:
        model = ConsolePort
        fields = ConsolePort.csv_headers


#
# Console server ports
#


class ConsoleServerPortFilterForm(DeviceComponentFilterForm):
    model = ConsoleServerPort
    type = forms.MultipleChoiceField(
        choices=ConsolePortTypeChoices,
        required=False,
        widget=StaticSelect2Multiple()
    )
    tag = TagFilterField(model)


class ConsoleServerPortForm(BootstrapMixin, forms.ModelForm):
    tags = TagField(
        required=False
    )

    class Meta:
        model = ConsoleServerPort
        fields = [
            'device', 'name', 'type', 'description', 'tags',
        ]
        widgets = {
            'device': forms.HiddenInput(),
        }


class ConsoleServerPortCreateForm(BootstrapMixin, forms.Form):
    device = DynamicModelChoiceField(
        queryset=Device.objects.prefetch_related('device_type__manufacturer'),
        widget=APISelect(
            api_url="/api/dcim/devices/",
        )
    )
    name_pattern = ExpandableNameField(
        label='Name'
    )
    type = forms.ChoiceField(
        choices=add_blank_choice(ConsolePortTypeChoices),
        required=False,
        widget=StaticSelect2()
    )
    description = forms.CharField(
        max_length=100,
        required=False
    )
    tags = TagField(
        required=False
    )


class ConsoleServerPortBulkEditForm(BootstrapMixin, AddRemoveTagsForm, BulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=ConsoleServerPort.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
    type = forms.ChoiceField(
        choices=add_blank_choice(ConsolePortTypeChoices),
        required=False,
        widget=StaticSelect2()
    )
    description = forms.CharField(
        max_length=100,
        required=False
    )

    class Meta:
        nullable_fields = [
            'description',
        ]


class ConsoleServerPortBulkRenameForm(BulkRenameForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=ConsoleServerPort.objects.all(),
        widget=forms.MultipleHiddenInput()
    )


class ConsoleServerPortBulkDisconnectForm(ConfirmationForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=ConsoleServerPort.objects.all(),
        widget=forms.MultipleHiddenInput()
    )


class ConsoleServerPortCSVForm(forms.ModelForm):
    device = FlexibleModelChoiceField(
        queryset=Device.objects.all(),
        to_field_name='name',
        help_text='Name or ID of device',
        error_messages={
            'invalid_choice': 'Device not found.',
        }
    )

    class Meta:
        model = ConsoleServerPort
        fields = ConsoleServerPort.csv_headers


#
# Power ports
#


class PowerPortFilterForm(DeviceComponentFilterForm):
    model = PowerPort
    type = forms.MultipleChoiceField(
        choices=PowerPortTypeChoices,
        required=False,
        widget=StaticSelect2Multiple()
    )
    tag = TagFilterField(model)


class PowerPortForm(BootstrapMixin, forms.ModelForm):
    tags = TagField(
        required=False
    )

    class Meta:
        model = PowerPort
        fields = [
            'device', 'name', 'type', 'maximum_draw', 'allocated_draw', 'description', 'tags',
        ]
        widgets = {
            'device': forms.HiddenInput(),
        }


class PowerPortCreateForm(BootstrapMixin, forms.Form):
    device = DynamicModelChoiceField(
        queryset=Device.objects.prefetch_related('device_type__manufacturer'),
        widget=APISelect(
            api_url="/api/dcim/devices/",
        )
    )
    name_pattern = ExpandableNameField(
        label='Name'
    )
    type = forms.ChoiceField(
        choices=add_blank_choice(PowerPortTypeChoices),
        required=False,
        widget=StaticSelect2()
    )
    maximum_draw = forms.IntegerField(
        min_value=1,
        required=False,
        help_text="Maximum draw in watts"
    )
    allocated_draw = forms.IntegerField(
        min_value=1,
        required=False,
        help_text="Allocated draw in watts"
    )
    description = forms.CharField(
        max_length=100,
        required=False
    )
    tags = TagField(
        required=False
    )


class PowerPortBulkEditForm(BootstrapMixin, AddRemoveTagsForm, BulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=PowerPort.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
    type = forms.ChoiceField(
        choices=add_blank_choice(PowerPortTypeChoices),
        required=False,
        widget=StaticSelect2()
    )
    maximum_draw = forms.IntegerField(
        min_value=1,
        required=False,
        help_text="Maximum draw in watts"
    )
    allocated_draw = forms.IntegerField(
        min_value=1,
        required=False,
        help_text="Allocated draw in watts"
    )
    description = forms.CharField(
        max_length=100,
        required=False
    )

    class Meta:
        nullable_fields = (
            'description',
        )


class PowerPortCSVForm(forms.ModelForm):
    device = FlexibleModelChoiceField(
        queryset=Device.objects.all(),
        to_field_name='name',
        help_text='Name or ID of device',
        error_messages={
            'invalid_choice': 'Device not found.',
        }
    )

    class Meta:
        model = PowerPort
        fields = PowerPort.csv_headers


#
# Power outlets
#


class PowerOutletFilterForm(DeviceComponentFilterForm):
    model = PowerOutlet
    type = forms.MultipleChoiceField(
        choices=PowerOutletTypeChoices,
        required=False,
        widget=StaticSelect2Multiple()
    )
    tag = TagFilterField(model)


class PowerOutletForm(BootstrapMixin, forms.ModelForm):
    power_port = forms.ModelChoiceField(
        queryset=PowerPort.objects.all(),
        required=False
    )
    tags = TagField(
        required=False
    )

    class Meta:
        model = PowerOutlet
        fields = [
            'device', 'name', 'type', 'power_port', 'feed_leg', 'description', 'tags',
        ]
        widgets = {
            'device': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Limit power_port choices to the local device
        if hasattr(self.instance, 'device'):
            self.fields['power_port'].queryset = PowerPort.objects.filter(
                device=self.instance.device
            )


class PowerOutletCreateForm(BootstrapMixin, forms.Form):
    device = DynamicModelChoiceField(
        queryset=Device.objects.prefetch_related('device_type__manufacturer'),
        widget=APISelect(
            api_url="/api/dcim/devices/",
        )
    )
    name_pattern = ExpandableNameField(
        label='Name'
    )
    type = forms.ChoiceField(
        choices=add_blank_choice(PowerOutletTypeChoices),
        required=False,
        widget=StaticSelect2()
    )
    power_port = forms.ModelChoiceField(
        queryset=PowerPort.objects.all(),
        required=False
    )
    feed_leg = forms.ChoiceField(
        choices=add_blank_choice(PowerOutletFeedLegChoices),
        required=False
    )
    description = forms.CharField(
        max_length=100,
        required=False
    )
    tags = TagField(
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Limit power_port queryset to PowerPorts which belong to the parent Device
        device = Device.objects.get(
            pk=self.initial.get('device') or self.data.get('device')
        )
        self.fields['power_port'].queryset = PowerPort.objects.filter(device=device)


class PowerOutletCSVForm(forms.ModelForm):
    device = FlexibleModelChoiceField(
        queryset=Device.objects.all(),
        to_field_name='name',
        help_text='Name or ID of device',
        error_messages={
            'invalid_choice': 'Device not found.',
        }
    )
    power_port = FlexibleModelChoiceField(
        queryset=PowerPort.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Name or ID of Power Port',
        error_messages={
            'invalid_choice': 'Power Port not found.',
        }
    )
    feed_leg = CSVChoiceField(
        choices=PowerOutletFeedLegChoices,
        required=False,
    )

    class Meta:
        model = PowerOutlet
        fields = PowerOutlet.csv_headers

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Limit PowerPort choices to those belonging to this device (or VC master)
        if self.is_bound:
            try:
                device = self.fields['device'].to_python(self.data['device'])
            except forms.ValidationError:
                device = None
        else:
            try:
                device = self.instance.device
            except Device.DoesNotExist:
                device = None

        if device:
            self.fields['power_port'].queryset = PowerPort.objects.filter(
                device__in=[device, device.get_vc_master()]
            )
        else:
            self.fields['power_port'].queryset = PowerPort.objects.none()


class PowerOutletBulkEditForm(BootstrapMixin, AddRemoveTagsForm, BulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=PowerOutlet.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
    device = forms.ModelChoiceField(
        queryset=Device.objects.all(),
        required=False,
        disabled=True,
        widget=forms.HiddenInput()
    )
    type = forms.ChoiceField(
        choices=add_blank_choice(PowerOutletTypeChoices),
        required=False
    )
    feed_leg = forms.ChoiceField(
        choices=add_blank_choice(PowerOutletFeedLegChoices),
        required=False,
    )
    power_port = forms.ModelChoiceField(
        queryset=PowerPort.objects.all(),
        required=False
    )
    description = forms.CharField(
        max_length=100,
        required=False
    )

    class Meta:
        nullable_fields = [
            'type', 'feed_leg', 'power_port', 'description',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Limit power_port queryset to PowerPorts which belong to the parent Device
        if 'device' in self.initial:
            device = Device.objects.filter(pk=self.initial['device']).first()
            self.fields['power_port'].queryset = PowerPort.objects.filter(device=device)
        else:
            self.fields['power_port'].choices = ()
            self.fields['power_port'].widget.attrs['disabled'] = True


class PowerOutletBulkRenameForm(BulkRenameForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=PowerOutlet.objects.all(),
        widget=forms.MultipleHiddenInput
    )


class PowerOutletBulkDisconnectForm(ConfirmationForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=PowerOutlet.objects.all(),
        widget=forms.MultipleHiddenInput
    )


#
# Interfaces
#


class InterfaceFilterForm(DeviceComponentFilterForm):
    model = Interface
    type = forms.MultipleChoiceField(
        choices=InterfaceTypeChoices,
        required=False,
        widget=StaticSelect2Multiple()
    )
    enabled = forms.NullBooleanField(
        required=False,
        widget=StaticSelect2(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    tag = TagFilterField(model)


class InterfaceForm(InterfaceCommonForm, BootstrapMixin, forms.ModelForm):
    untagged_vlan = DynamicModelChoiceField(
        queryset=VLAN.objects.all(),
        required=False,
        label='Untagged VLAN',
        widget=APISelect(
            api_url="/api/ipam/vlans/",
            display_field='display_name',
            full=True,
            additional_query_params={
                'site_id': 'null',
            },
        )
    )
    tagged_vlans = DynamicModelMultipleChoiceField(
        queryset=VLAN.objects.all(),
        required=False,
        label='Tagged VLANs',
        widget=APISelectMultiple(
            api_url="/api/ipam/vlans/",
            display_field='display_name',
            full=True,
            additional_query_params={
                'site_id': 'null',
            },
        )
    )
    tags = TagField(
        required=False
    )

    class Meta:
        model = Interface
        fields = [
            'device', 'name', 'type', 'enabled', 'lag', 'mac_address', 'mtu', 'mgmt_only', 'description',
            'mode', 'untagged_vlan', 'tagged_vlans', 'tags',
        ]
        widgets = {
            'device': forms.HiddenInput(),
            'type': StaticSelect2(),
            'lag': StaticSelect2(),
            'mode': StaticSelect2(),
        }
        labels = {
            'mode': '802.1Q Mode',
        }
        help_texts = {
            'mode': INTERFACE_MODE_HELP_TEXT,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.is_bound:
            device = Device.objects.get(pk=self.data['device'])
        else:
            device = self.instance.device

        # Limit LAG choices to interfaces belonging to this device (or VC master)
        self.fields['lag'].queryset = Interface.objects.filter(
            device__in=[device, device.get_vc_master()],
            type=InterfaceTypeChoices.TYPE_LAG
        )

        # Add current site to VLANs query params
        self.fields['untagged_vlan'].widget.add_additional_query_param('site_id', device.site.pk)
        self.fields['tagged_vlans'].widget.add_additional_query_param('site_id', device.site.pk)


class InterfaceCreateForm(BootstrapMixin, InterfaceCommonForm, forms.Form):
    device = DynamicModelChoiceField(
        queryset=Device.objects.prefetch_related('device_type__manufacturer'),
        widget=APISelect(
            api_url="/api/dcim/devices/",
        )
    )
    name_pattern = ExpandableNameField(
        label='Name'
    )
    type = forms.ChoiceField(
        choices=InterfaceTypeChoices,
        widget=StaticSelect2(),
    )
    enabled = forms.BooleanField(
        required=False,
        initial=True
    )
    lag = forms.ModelChoiceField(
        queryset=Interface.objects.all(),
        required=False,
        label='Parent LAG',
        widget=StaticSelect2(),
    )
    mtu = forms.IntegerField(
        required=False,
        min_value=INTERFACE_MTU_MIN,
        max_value=INTERFACE_MTU_MAX,
        label='MTU'
    )
    mac_address = forms.CharField(
        required=False,
        label='MAC Address'
    )
    mgmt_only = forms.BooleanField(
        required=False,
        label='Management only',
        help_text='This interface is used only for out-of-band management'
    )
    description = forms.CharField(
        max_length=100,
        required=False
    )
    mode = forms.ChoiceField(
        choices=add_blank_choice(InterfaceModeChoices),
        required=False,
        widget=StaticSelect2(),
    )
    tags = TagField(
        required=False
    )
    untagged_vlan = DynamicModelChoiceField(
        queryset=VLAN.objects.all(),
        required=False,
        widget=APISelect(
            api_url="/api/ipam/vlans/",
            display_field='display_name',
            full=True,
            additional_query_params={
                'site_id': 'null',
            },
        )
    )
    tagged_vlans = DynamicModelMultipleChoiceField(
        queryset=VLAN.objects.all(),
        required=False,
        widget=APISelectMultiple(
            api_url="/api/ipam/vlans/",
            display_field='display_name',
            full=True,
            additional_query_params={
                'site_id': 'null',
            },
        )
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Limit LAG choices to interfaces which belong to the parent device (or VC master)
        device = Device.objects.get(
            pk=self.initial.get('device') or self.data.get('device')
        )
        self.fields['lag'].queryset = Interface.objects.filter(
            device__in=[device, device.get_vc_master()],
            type=InterfaceTypeChoices.TYPE_LAG
        )

        # Add current site to VLANs query params
        self.fields['untagged_vlan'].widget.add_additional_query_param('site_id', device.site.pk)
        self.fields['tagged_vlans'].widget.add_additional_query_param('site_id', device.site.pk)


class InterfaceCSVForm(forms.ModelForm):
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
    lag = FlexibleModelChoiceField(
        queryset=Interface.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Name or ID of LAG interface',
        error_messages={
            'invalid_choice': 'LAG interface not found.',
        }
    )
    type = CSVChoiceField(
        choices=InterfaceTypeChoices,
    )
    mode = CSVChoiceField(
        choices=InterfaceModeChoices,
        required=False,
    )

    class Meta:
        model = Interface
        fields = Interface.csv_headers

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Limit LAG choices to interfaces belonging to this device (or VC master)
        if self.is_bound and 'device' in self.data:
            try:
                device = self.fields['device'].to_python(self.data['device'])
            except forms.ValidationError:
                device = None
        else:
            device = self.instance.device

        if device:
            self.fields['lag'].queryset = Interface.objects.filter(
                device__in=[device, device.get_vc_master()], type=InterfaceTypeChoices.TYPE_LAG
            )
        else:
            self.fields['lag'].queryset = Interface.objects.none()

    def clean_enabled(self):
        # Make sure enabled is True when it's not included in the uploaded data
        if 'enabled' not in self.data:
            return True
        else:
            return self.cleaned_data['enabled']


class InterfaceBulkEditForm(BootstrapMixin, AddRemoveTagsForm, BulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=Interface.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
    device = forms.ModelChoiceField(
        queryset=Device.objects.all(),
        required=False,
        disabled=True,
        widget=forms.HiddenInput()
    )
    type = forms.ChoiceField(
        choices=add_blank_choice(InterfaceTypeChoices),
        required=False,
        widget=StaticSelect2()
    )
    enabled = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect()
    )
    lag = forms.ModelChoiceField(
        queryset=Interface.objects.all(),
        required=False,
        label='Parent LAG',
        widget=StaticSelect2()
    )
    mac_address = forms.CharField(
        required=False,
        label='MAC Address'
    )
    mtu = forms.IntegerField(
        required=False,
        min_value=INTERFACE_MTU_MIN,
        max_value=INTERFACE_MTU_MAX,
        label='MTU'
    )
    mgmt_only = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect(),
        label='Management only'
    )
    description = forms.CharField(
        max_length=100,
        required=False
    )
    mode = forms.ChoiceField(
        choices=add_blank_choice(InterfaceModeChoices),
        required=False,
        widget=StaticSelect2()
    )
    untagged_vlan = DynamicModelChoiceField(
        queryset=VLAN.objects.all(),
        required=False,
        widget=APISelect(
            api_url="/api/ipam/vlans/",
            display_field='display_name',
            full=True,
            additional_query_params={
                'site_id': 'null',
            },
        )
    )
    tagged_vlans = DynamicModelMultipleChoiceField(
        queryset=VLAN.objects.all(),
        required=False,
        widget=APISelectMultiple(
            api_url="/api/ipam/vlans/",
            display_field='display_name',
            full=True,
            additional_query_params={
                'site_id': 'null',
            },
        )
    )

    class Meta:
        nullable_fields = [
            'lag', 'mac_address', 'mtu', 'description', 'mode', 'untagged_vlan', 'tagged_vlans'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Limit LAG choices to interfaces which belong to the parent device (or VC master)
        if 'device' in self.initial:
            device = Device.objects.filter(pk=self.initial['device']).first()
            self.fields['lag'].queryset = Interface.objects.filter(
                device__in=[device, device.get_vc_master()],
                type=InterfaceTypeChoices.TYPE_LAG
            )

            # Add current site to VLANs query params
            self.fields['untagged_vlan'].widget.add_additional_query_param('site_id', device.site.pk)
            self.fields['tagged_vlans'].widget.add_additional_query_param('site_id', device.site.pk)
        else:
            self.fields['lag'].choices = ()
            self.fields['lag'].widget.attrs['disabled'] = True

    def clean(self):

        # Untagged interfaces cannot be assigned tagged VLANs
        if self.cleaned_data['mode'] == InterfaceModeChoices.MODE_ACCESS and self.cleaned_data['tagged_vlans']:
            raise forms.ValidationError({
                'mode': "An access interface cannot have tagged VLANs assigned."
            })

        # Remove all tagged VLAN assignments from "tagged all" interfaces
        elif self.cleaned_data['mode'] == InterfaceModeChoices.MODE_TAGGED_ALL:
            self.cleaned_data['tagged_vlans'] = []


class InterfaceBulkRenameForm(BulkRenameForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=Interface.objects.all(),
        widget=forms.MultipleHiddenInput()
    )


class InterfaceBulkDisconnectForm(ConfirmationForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=Interface.objects.all(),
        widget=forms.MultipleHiddenInput()
    )


#
# Front pass-through ports
#

class FrontPortFilterForm(DeviceComponentFilterForm):
    model = FrontPort
    type = forms.MultipleChoiceField(
        choices=PortTypeChoices,
        required=False,
        widget=StaticSelect2Multiple()
    )
    tag = TagFilterField(model)


class FrontPortForm(BootstrapMixin, forms.ModelForm):
    tags = TagField(
        required=False
    )

    class Meta:
        model = FrontPort
        fields = [
            'device', 'name', 'type', 'rear_port', 'rear_port_position', 'description', 'tags',
        ]
        widgets = {
            'device': forms.HiddenInput(),
            'type': StaticSelect2(),
            'rear_port': StaticSelect2(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Limit RearPort choices to the local device
        if hasattr(self.instance, 'device'):
            self.fields['rear_port'].queryset = self.fields['rear_port'].queryset.filter(
                device=self.instance.device
            )


# TODO: Merge with FrontPortTemplateCreateForm to remove duplicate logic
class FrontPortCreateForm(BootstrapMixin, forms.Form):
    device = DynamicModelChoiceField(
        queryset=Device.objects.prefetch_related('device_type__manufacturer'),
        widget=APISelect(
            api_url="/api/dcim/devices/",
        )
    )
    name_pattern = ExpandableNameField(
        label='Name'
    )
    type = forms.ChoiceField(
        choices=PortTypeChoices,
        widget=StaticSelect2(),
    )
    rear_port_set = forms.MultipleChoiceField(
        choices=[],
        label='Rear ports',
        help_text='Select one rear port assignment for each front port being created.',
    )
    description = forms.CharField(
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        device = Device.objects.get(
            pk=self.initial.get('device') or self.data.get('device')
        )

        # Determine which rear port positions are occupied. These will be excluded from the list of available
        # mappings.
        occupied_port_positions = [
            (front_port.rear_port_id, front_port.rear_port_position)
            for front_port in device.frontports.all()
        ]

        # Populate rear port choices
        choices = []
        rear_ports = RearPort.objects.filter(device=device)
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


class FrontPortCSVForm(forms.ModelForm):
    device = FlexibleModelChoiceField(
        queryset=Device.objects.all(),
        to_field_name='name',
        help_text='Name or ID of device',
        error_messages={
            'invalid_choice': 'Device not found.',
        }
    )
    rear_port = FlexibleModelChoiceField(
        queryset=RearPort.objects.all(),
        to_field_name='name',
        help_text='Name or ID of Rear Port',
        error_messages={
            'invalid_choice': 'Rear Port not found.',
        }
    )
    type = CSVChoiceField(
        choices=PortTypeChoices,
    )

    class Meta:
        model = FrontPort
        fields = FrontPort.csv_headers

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Limit RearPort choices to those belonging to this device (or VC master)
        if self.is_bound:
            try:
                device = self.fields['device'].to_python(self.data['device'])
            except forms.ValidationError:
                device = None
        else:
            try:
                device = self.instance.device
            except Device.DoesNotExist:
                device = None

        if device:
            self.fields['rear_port'].queryset = RearPort.objects.filter(
                device__in=[device, device.get_vc_master()]
            )
        else:
            self.fields['rear_port'].queryset = RearPort.objects.none()


class FrontPortBulkEditForm(BootstrapMixin, AddRemoveTagsForm, BulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=FrontPort.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
    type = forms.ChoiceField(
        choices=add_blank_choice(PortTypeChoices),
        required=False,
        widget=StaticSelect2()
    )
    description = forms.CharField(
        max_length=100,
        required=False
    )

    class Meta:
        nullable_fields = [
            'description',
        ]


class FrontPortBulkRenameForm(BulkRenameForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=FrontPort.objects.all(),
        widget=forms.MultipleHiddenInput
    )


class FrontPortBulkDisconnectForm(ConfirmationForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=FrontPort.objects.all(),
        widget=forms.MultipleHiddenInput
    )


#
# Rear pass-through ports
#

class RearPortFilterForm(DeviceComponentFilterForm):
    model = RearPort
    type = forms.MultipleChoiceField(
        choices=PortTypeChoices,
        required=False,
        widget=StaticSelect2Multiple()
    )
    tag = TagFilterField(model)


class RearPortForm(BootstrapMixin, forms.ModelForm):
    tags = TagField(
        required=False
    )

    class Meta:
        model = RearPort
        fields = [
            'device', 'name', 'type', 'positions', 'description', 'tags',
        ]
        widgets = {
            'device': forms.HiddenInput(),
            'type': StaticSelect2(),
        }


class RearPortCreateForm(BootstrapMixin, forms.Form):
    device = DynamicModelChoiceField(
        queryset=Device.objects.prefetch_related('device_type__manufacturer'),
        widget=APISelect(
            api_url="/api/dcim/devices/",
        )
    )
    name_pattern = ExpandableNameField(
        label='Name'
    )
    type = forms.ChoiceField(
        choices=PortTypeChoices,
        widget=StaticSelect2(),
    )
    positions = forms.IntegerField(
        min_value=REARPORT_POSITIONS_MIN,
        max_value=REARPORT_POSITIONS_MAX,
        initial=1,
        help_text='The number of front ports which may be mapped to each rear port'
    )
    description = forms.CharField(
        required=False
    )


class RearPortCSVForm(forms.ModelForm):
    device = FlexibleModelChoiceField(
        queryset=Device.objects.all(),
        to_field_name='name',
        help_text='Name or ID of device',
        error_messages={
            'invalid_choice': 'Device not found.',
        }
    )
    type = CSVChoiceField(
        choices=PortTypeChoices,
    )

    class Meta:
        model = RearPort
        fields = RearPort.csv_headers


class RearPortBulkEditForm(BootstrapMixin, AddRemoveTagsForm, BulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=RearPort.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
    type = forms.ChoiceField(
        choices=add_blank_choice(PortTypeChoices),
        required=False,
        widget=StaticSelect2()
    )
    description = forms.CharField(
        max_length=100,
        required=False
    )

    class Meta:
        nullable_fields = [
            'description',
        ]


class RearPortBulkRenameForm(BulkRenameForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=RearPort.objects.all(),
        widget=forms.MultipleHiddenInput
    )


class RearPortBulkDisconnectForm(ConfirmationForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=RearPort.objects.all(),
        widget=forms.MultipleHiddenInput
    )


#
# Cables
#

class ConnectCableToDeviceForm(BootstrapMixin, forms.ModelForm):
    """
    Base form for connecting a Cable to a Device component
    """
    termination_b_site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        label='Site',
        required=False,
        widget=APISelect(
            api_url='/api/dcim/sites/',
            filter_for={
                'termination_b_rack': 'site_id',
                'termination_b_device': 'site_id',
            }
        )
    )
    termination_b_rack = DynamicModelChoiceField(
        queryset=Rack.objects.all(),
        label='Rack',
        required=False,
        widget=APISelect(
            api_url='/api/dcim/racks/',
            filter_for={
                'termination_b_device': 'rack_id',
            },
            attrs={
                'nullable': 'true',
            }
        )
    )
    termination_b_device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        label='Device',
        required=False,
        widget=APISelect(
            api_url='/api/dcim/devices/',
            display_field='display_name',
            filter_for={
                'termination_b_id': 'device_id',
            }
        )
    )

    class Meta:
        model = Cable
        fields = [
            'termination_b_site', 'termination_b_rack', 'termination_b_device', 'termination_b_id', 'type', 'status',
            'label', 'color', 'length', 'length_unit',
        ]
        widgets = {
            'status': StaticSelect2,
            'type': StaticSelect2,
            'length_unit': StaticSelect2,
        }


class ConnectCableToConsolePortForm(ConnectCableToDeviceForm):
    termination_b_id = forms.IntegerField(
        label='Name',
        widget=APISelect(
            api_url='/api/dcim/console-ports/',
            disabled_indicator='cable',
        )
    )


class ConnectCableToConsoleServerPortForm(ConnectCableToDeviceForm):
    termination_b_id = forms.IntegerField(
        label='Name',
        widget=APISelect(
            api_url='/api/dcim/console-server-ports/',
            disabled_indicator='cable',
        )
    )


class ConnectCableToPowerPortForm(ConnectCableToDeviceForm):
    termination_b_id = forms.IntegerField(
        label='Name',
        widget=APISelect(
            api_url='/api/dcim/power-ports/',
            disabled_indicator='cable',
        )
    )


class ConnectCableToPowerOutletForm(ConnectCableToDeviceForm):
    termination_b_id = forms.IntegerField(
        label='Name',
        widget=APISelect(
            api_url='/api/dcim/power-outlets/',
            disabled_indicator='cable',
        )
    )


class ConnectCableToInterfaceForm(ConnectCableToDeviceForm):
    termination_b_id = forms.IntegerField(
        label='Name',
        widget=APISelect(
            api_url='/api/dcim/interfaces/',
            disabled_indicator='cable',
            additional_query_params={
                'kind': 'physical',
            }
        )
    )


class ConnectCableToFrontPortForm(ConnectCableToDeviceForm):
    termination_b_id = forms.IntegerField(
        label='Name',
        widget=APISelect(
            api_url='/api/dcim/front-ports/',
            disabled_indicator='cable',
        )
    )


class ConnectCableToRearPortForm(ConnectCableToDeviceForm):
    termination_b_id = forms.IntegerField(
        label='Name',
        widget=APISelect(
            api_url='/api/dcim/rear-ports/',
            disabled_indicator='cable',
        )
    )


class ConnectCableToCircuitTerminationForm(BootstrapMixin, forms.ModelForm):
    termination_b_provider = DynamicModelChoiceField(
        queryset=Provider.objects.all(),
        label='Provider',
        required=False,
        widget=APISelect(
            api_url='/api/circuits/providers/',
            filter_for={
                'termination_b_circuit': 'provider_id',
            }
        )
    )
    termination_b_site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        label='Site',
        required=False,
        widget=APISelect(
            api_url='/api/dcim/sites/',
            filter_for={
                'termination_b_circuit': 'site_id',
            }
        )
    )
    termination_b_circuit = DynamicModelChoiceField(
        queryset=Circuit.objects.all(),
        label='Circuit',
        widget=APISelect(
            api_url='/api/circuits/circuits/',
            display_field='cid',
            filter_for={
                'termination_b_id': 'circuit_id',
            }
        )
    )
    termination_b_id = forms.IntegerField(
        label='Side',
        widget=APISelect(
            api_url='/api/circuits/circuit-terminations/',
            disabled_indicator='cable',
            display_field='term_side',
            full=True
        )
    )

    class Meta:
        model = Cable
        fields = [
            'termination_b_provider', 'termination_b_site', 'termination_b_circuit', 'termination_b_id', 'type',
            'status', 'label', 'color', 'length', 'length_unit',
        ]


class ConnectCableToPowerFeedForm(BootstrapMixin, forms.ModelForm):
    termination_b_site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        label='Site',
        required=False,
        widget=APISelect(
            api_url='/api/dcim/sites/',
            display_field='cid',
            filter_for={
                'termination_b_rackgroup': 'site_id',
                'termination_b_powerpanel': 'site_id',
            }
        )
    )
    termination_b_rackgroup = DynamicModelChoiceField(
        queryset=RackGroup.objects.all(),
        label='Rack Group',
        required=False,
        widget=APISelect(
            api_url='/api/dcim/rack-groups/',
            display_field='cid',
            filter_for={
                'termination_b_powerpanel': 'rackgroup_id',
            }
        )
    )
    termination_b_powerpanel = DynamicModelChoiceField(
        queryset=PowerPanel.objects.all(),
        label='Power Panel',
        required=False,
        widget=APISelect(
            api_url='/api/dcim/power-panels/',
            filter_for={
                'termination_b_id': 'power_panel_id',
            }
        )
    )
    termination_b_id = forms.IntegerField(
        label='Name',
        widget=APISelect(
            api_url='/api/dcim/power-feeds/',
        )
    )

    class Meta:
        model = Cable
        fields = [
            'termination_b_rackgroup', 'termination_b_powerpanel', 'termination_b_id', 'type', 'status', 'label',
            'color', 'length', 'length_unit',
        ]


class CableForm(BootstrapMixin, forms.ModelForm):

    class Meta:
        model = Cable
        fields = [
            'type', 'status', 'label', 'color', 'length', 'length_unit',
        ]
        widgets = {
            'status': StaticSelect2,
            'type': StaticSelect2,
            'length_unit': StaticSelect2,
        }


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
        limit_choices_to=CABLE_TERMINATION_MODELS,
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
        limit_choices_to=CABLE_TERMINATION_MODELS,
        to_field_name='model',
        help_text='Side B type'
    )
    side_b_name = forms.CharField(
        help_text='Side B component'
    )

    # Cable attributes
    status = CSVChoiceField(
        choices=CableStatusChoices,
        required=False,
        help_text='Connection status'
    )
    type = CSVChoiceField(
        choices=CableTypeChoices,
        required=False,
        help_text='Cable type'
    )
    length_unit = CSVChoiceField(
        choices=CableLengthUnitChoices,
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

    def clean_length_unit(self):
        # Avoid trying to save as NULL
        length_unit = self.cleaned_data.get('length_unit', None)
        return length_unit if length_unit is not None else ''


class CableBulkEditForm(BootstrapMixin, BulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=Cable.objects.all(),
        widget=forms.MultipleHiddenInput
    )
    type = forms.ChoiceField(
        choices=add_blank_choice(CableTypeChoices),
        required=False,
        initial='',
        widget=StaticSelect2()
    )
    status = forms.ChoiceField(
        choices=add_blank_choice(CableStatusChoices),
        required=False,
        widget=StaticSelect2(),
        initial=''
    )
    label = forms.CharField(
        max_length=100,
        required=False
    )
    color = forms.CharField(
        max_length=6,  # RGB color code
        required=False,
        widget=ColorSelect()
    )
    length = forms.IntegerField(
        min_value=1,
        required=False
    )
    length_unit = forms.ChoiceField(
        choices=add_blank_choice(CableLengthUnitChoices),
        required=False,
        initial='',
        widget=StaticSelect2()
    )

    class Meta:
        nullable_fields = [
            'type', 'status', 'label', 'color', 'length',
        ]

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
    q = forms.CharField(
        required=False,
        label='Search'
    )
    site = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        to_field_name='slug',
        required=False,
        widget=APISelectMultiple(
            api_url="/api/dcim/sites/",
            value_field="slug",
            filter_for={
                'rack_id': 'site',
                'device_id': 'site',
            }
        )
    )
    tenant = DynamicModelMultipleChoiceField(
        queryset=Tenant.objects.all(),
        to_field_name='slug',
        required=False,
        widget=APISelectMultiple(
            api_url="/api/tenancy/tenants/",
            value_field='slug',
            filter_for={
                'device_id': 'tenant',
            }
        )
    )
    rack_id = DynamicModelMultipleChoiceField(
        queryset=Rack.objects.all(),
        required=False,
        label='Rack',
        widget=APISelectMultiple(
            api_url="/api/dcim/racks/",
            null_option=True,
            filter_for={
                'device_id': 'rack_id',
            }
        )
    )
    type = forms.MultipleChoiceField(
        choices=add_blank_choice(CableTypeChoices),
        required=False,
        widget=StaticSelect2()
    )
    status = forms.ChoiceField(
        required=False,
        choices=add_blank_choice(CableStatusChoices),
        widget=StaticSelect2()
    )
    color = forms.CharField(
        max_length=6,  # RGB color code
        required=False,
        widget=ColorSelect()
    )
    device_id = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        required=False,
        label='Device',
        widget=APISelectMultiple(
            api_url='/api/dcim/devices/',
        )
    )


#
# Device bays
#

class DeviceBayFilterForm(DeviceComponentFilterForm):
    model = DeviceBay
    tag = TagFilterField(model)


class DeviceBayForm(BootstrapMixin, forms.ModelForm):
    tags = TagField(
        required=False
    )

    class Meta:
        model = DeviceBay
        fields = [
            'device', 'name', 'description', 'tags',
        ]
        widgets = {
            'device': forms.HiddenInput(),
        }


class DeviceBayCreateForm(BootstrapMixin, forms.Form):
    device = DynamicModelChoiceField(
        queryset=Device.objects.prefetch_related('device_type__manufacturer'),
        widget=APISelect(
            api_url="/api/dcim/devices/",
        )
    )
    name_pattern = ExpandableNameField(
        label='Name'
    )
    tags = TagField(
        required=False
    )


class PopulateDeviceBayForm(BootstrapMixin, forms.Form):
    installed_device = forms.ModelChoiceField(
        queryset=Device.objects.all(),
        label='Child Device',
        help_text="Child devices must first be created and assigned to the site/rack of the parent device.",
        widget=StaticSelect2(),
    )

    def __init__(self, device_bay, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields['installed_device'].queryset = Device.objects.filter(
            site=device_bay.device.site,
            rack=device_bay.device.rack,
            parent_bay__isnull=True,
            device_type__u_height=0,
            device_type__subdevice_role=SubdeviceRoleChoices.ROLE_CHILD
        ).exclude(pk=device_bay.device.pk)


class DeviceBayCSVForm(forms.ModelForm):
    device = FlexibleModelChoiceField(
        queryset=Device.objects.all(),
        to_field_name='name',
        help_text='Name or ID of device',
        error_messages={
            'invalid_choice': 'Device not found.',
        }
    )
    installed_device = FlexibleModelChoiceField(
        queryset=Device.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Name or ID of device',
        error_messages={
            'invalid_choice': 'Child device not found.',
        }
    )

    class Meta:
        model = DeviceBay
        fields = DeviceBay.csv_headers

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Limit installed device choices to devices of the correct type and location
        if self.is_bound:
            try:
                device = self.fields['device'].to_python(self.data['device'])
            except forms.ValidationError:
                device = None
        else:
            try:
                device = self.instance.device
            except Device.DoesNotExist:
                device = None

        if device:
            self.fields['installed_device'].queryset = Device.objects.filter(
                site=device.site,
                rack=device.rack,
                parent_bay__isnull=True,
                device_type__u_height=0,
                device_type__subdevice_role=SubdeviceRoleChoices.ROLE_CHILD
            ).exclude(pk=device.pk)
        else:
            self.fields['installed_device'].queryset = Interface.objects.none()


class DeviceBayBulkRenameForm(BulkRenameForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=DeviceBay.objects.all(),
        widget=forms.MultipleHiddenInput()
    )


#
# Connections
#

class ConsoleConnectionFilterForm(BootstrapMixin, forms.Form):
    site = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        to_field_name='slug',
        required=False,
        widget=APISelectMultiple(
            api_url="/api/dcim/sites/",
            value_field="slug",
            filter_for={
                'device_id': 'site',
            }
        )
    )
    device_id = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        required=False,
        label='Device',
        widget=APISelectMultiple(
            api_url='/api/dcim/devices/',
        )
    )


class PowerConnectionFilterForm(BootstrapMixin, forms.Form):
    site = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        to_field_name='slug',
        required=False,
        widget=APISelectMultiple(
            api_url="/api/dcim/sites/",
            value_field="slug",
            filter_for={
                'device_id': 'site',
            }
        )
    )
    device_id = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        required=False,
        label='Device',
        widget=APISelectMultiple(
            api_url='/api/dcim/devices/',
        )
    )


class InterfaceConnectionFilterForm(BootstrapMixin, forms.Form):
    site = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        to_field_name='slug',
        required=False,
        widget=APISelectMultiple(
            api_url="/api/dcim/sites/",
            value_field="slug",
            filter_for={
                'device_id': 'site',
            }
        )
    )
    device_id = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        required=False,
        label='Device',
        widget=APISelectMultiple(
            api_url='/api/dcim/devices/',
        )
    )


#
# Inventory items
#

class InventoryItemForm(BootstrapMixin, forms.ModelForm):
    device = DynamicModelChoiceField(
        queryset=Device.objects.prefetch_related('device_type__manufacturer'),
        widget=APISelect(
            api_url="/api/dcim/devices/"
        )
    )
    manufacturer = DynamicModelChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False,
        widget=APISelect(
            api_url="/api/dcim/manufacturers/"
        )
    )
    tags = TagField(
        required=False
    )

    class Meta:
        model = InventoryItem
        fields = [
            'name', 'device', 'manufacturer', 'part_id', 'serial', 'asset_tag', 'description', 'tags',
        ]


class InventoryItemCreateForm(BootstrapMixin, forms.Form):
    device = DynamicModelChoiceField(
        queryset=Device.objects.prefetch_related('device_type__manufacturer'),
        widget=APISelect(
            api_url="/api/dcim/devices/",
        )
    )
    name_pattern = ExpandableNameField(
        label='Name'
    )
    manufacturer = DynamicModelChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False,
        widget=APISelect(
            api_url="/api/dcim/manufacturers/"
        )
    )
    part_id = forms.CharField(
        max_length=50,
        required=False,
        label='Part ID'
    )
    serial = forms.CharField(
        max_length=50,
        required=False,
    )
    asset_tag = forms.CharField(
        max_length=50,
        required=False,
    )
    description = forms.CharField(
        max_length=100,
        required=False
    )


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
    pk = forms.ModelMultipleChoiceField(
        queryset=InventoryItem.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
    device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        required=False,
        widget=APISelect(
            api_url="/api/dcim/devices/"
        )
    )
    manufacturer = DynamicModelChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False,
        widget=APISelect(
            api_url="/api/dcim/manufacturers/"
        )
    )
    part_id = forms.CharField(
        max_length=50,
        required=False,
        label='Part ID'
    )
    description = forms.CharField(
        max_length=100,
        required=False
    )

    class Meta:
        nullable_fields = [
            'manufacturer', 'part_id', 'description',
        ]


class InventoryItemFilterForm(BootstrapMixin, forms.Form):
    model = InventoryItem
    q = forms.CharField(
        required=False,
        label='Search'
    )
    region = DynamicModelMultipleChoiceField(
        queryset=Region.objects.all(),
        to_field_name='slug',
        required=False,
        widget=APISelectMultiple(
            api_url="/api/dcim/regions/",
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
            api_url="/api/dcim/sites/",
            value_field="slug",
            filter_for={
                'device_id': 'site'
            }
        )
    )
    device_id = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        required=False,
        label='Device',
        widget=APISelect(
            api_url='/api/dcim/devices/',
        )
    )
    manufacturer = DynamicModelMultipleChoiceField(
        queryset=Manufacturer.objects.all(),
        to_field_name='slug',
        required=False,
        widget=APISelect(
            api_url="/api/dcim/manufacturers/",
            value_field="slug",
        )
    )
    discovered = forms.NullBooleanField(
        required=False,
        widget=StaticSelect2(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    tag = TagFilterField(model)


#
# Virtual chassis
#

class DeviceSelectionForm(forms.Form):
    pk = forms.ModelMultipleChoiceField(
        queryset=Device.objects.all(),
        widget=forms.MultipleHiddenInput()
    )


class VirtualChassisForm(BootstrapMixin, forms.ModelForm):
    tags = TagField(
        required=False
    )

    class Meta:
        model = VirtualChassis
        fields = [
            'master', 'domain', 'tags',
        ]
        widgets = {
            'master': SelectWithPK(),
        }


class BaseVCMemberFormSet(forms.BaseModelFormSet):

    def clean(self):
        super().clean()

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
        fields = [
            'vc_position', 'vc_priority',
        ]
        labels = {
            'vc_position': 'Position',
            'vc_priority': 'Priority',
        }

    def __init__(self, validate_vc_position=False, *args, **kwargs):
        super().__init__(*args, **kwargs)

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


class VCMemberSelectForm(BootstrapMixin, forms.Form):
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        widget=APISelect(
            api_url="/api/dcim/sites/",
            filter_for={
                'rack': 'site_id',
                'device': 'site_id',
            }
        )
    )
    rack = DynamicModelChoiceField(
        queryset=Rack.objects.all(),
        required=False,
        widget=APISelect(
            api_url='/api/dcim/racks/',
            filter_for={
                'device': 'rack_id'
            },
            attrs={
                'nullable': 'true',
            }
        )
    )
    device = DynamicModelChoiceField(
        queryset=Device.objects.filter(
            virtual_chassis__isnull=True
        ),
        widget=APISelect(
            api_url='/api/dcim/devices/',
            display_field='display_name',
            disabled_indicator='virtual_chassis'
        )
    )

    def clean_device(self):
        device = self.cleaned_data['device']
        if device.virtual_chassis is not None:
            raise forms.ValidationError(
                "Device {} is already assigned to a virtual chassis.".format(device)
            )
        return device


class VirtualChassisFilterForm(BootstrapMixin, CustomFieldFilterForm):
    model = VirtualChassis
    q = forms.CharField(
        required=False,
        label='Search'
    )
    region = DynamicModelMultipleChoiceField(
        queryset=Region.objects.all(),
        to_field_name='slug',
        required=False,
        widget=APISelectMultiple(
            api_url="/api/dcim/regions/",
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
            api_url="/api/dcim/sites/",
            value_field="slug",
        )
    )
    tenant_group = DynamicModelMultipleChoiceField(
        queryset=TenantGroup.objects.all(),
        to_field_name='slug',
        required=False,
        widget=APISelectMultiple(
            api_url="/api/tenancy/tenant-groups/",
            value_field="slug",
            null_option=True,
            filter_for={
                'tenant': 'group'
            }
        )
    )
    tenant = DynamicModelMultipleChoiceField(
        queryset=Tenant.objects.all(),
        to_field_name='slug',
        required=False,
        widget=APISelectMultiple(
            api_url="/api/tenancy/tenants/",
            value_field="slug",
            null_option=True,
        )
    )
    tag = TagFilterField(model)


#
# Power panels
#

class PowerPanelForm(BootstrapMixin, forms.ModelForm):
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        widget=APISelect(
            api_url="/api/dcim/sites/",
            filter_for={
                'rack_group': 'site_id',
            }
        )
    )
    rack_group = DynamicModelChoiceField(
        queryset=RackGroup.objects.all(),
        required=False,
        widget=APISelect(
            api_url='/api/dcim/rack-groups/',
        )
    )

    class Meta:
        model = PowerPanel
        fields = [
            'site', 'rack_group', 'name',
        ]


class PowerPanelCSVForm(forms.ModelForm):
    site = forms.ModelChoiceField(
        queryset=Site.objects.all(),
        to_field_name='name',
        help_text='Name of parent site',
        error_messages={
            'invalid_choice': 'Site not found.',
        }
    )
    rack_group_name = forms.CharField(
        required=False,
        help_text="Rack group name (optional)"
    )

    class Meta:
        model = PowerPanel
        fields = PowerPanel.csv_headers

    def clean(self):

        super().clean()

        site = self.cleaned_data.get('site')
        rack_group_name = self.cleaned_data.get('rack_group_name')

        # Validate rack group
        if rack_group_name:
            try:
                self.instance.rack_group = RackGroup.objects.get(site=site, name=rack_group_name)
            except RackGroup.DoesNotExist:
                raise forms.ValidationError(
                    "Rack group {} not found in site {}".format(rack_group_name, site)
                )


class PowerPanelFilterForm(BootstrapMixin, CustomFieldFilterForm):
    model = PowerPanel
    q = forms.CharField(
        required=False,
        label='Search'
    )
    region = DynamicModelMultipleChoiceField(
        queryset=Region.objects.all(),
        to_field_name='slug',
        required=False,
        widget=APISelectMultiple(
            api_url="/api/dcim/regions/",
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
            api_url="/api/dcim/sites/",
            value_field="slug",
            filter_for={
                'rack_group_id': 'site',
            }
        )
    )
    rack_group_id = DynamicModelMultipleChoiceField(
        queryset=RackGroup.objects.all(),
        required=False,
        label='Rack group (ID)',
        widget=APISelectMultiple(
            api_url="/api/dcim/rack-groups/",
            null_option=True,
        )
    )


#
# Power feeds
#

class PowerFeedForm(BootstrapMixin, CustomFieldModelForm):
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        widget=APISelect(
            api_url='/api/dcim/sites/',
            filter_for={
                'power_panel': 'site_id',
                'rack': 'site_id',
            }
        )
    )
    power_panel = DynamicModelChoiceField(
        queryset=PowerPanel.objects.all(),
        widget=APISelect(
            api_url="/api/dcim/power-panels/"
        )
    )
    rack = DynamicModelChoiceField(
        queryset=Rack.objects.all(),
        required=False,
        widget=APISelect(
            api_url="/api/dcim/racks/"
        )
    )
    comments = CommentField()
    tags = TagField(
        required=False
    )

    class Meta:
        model = PowerFeed
        fields = [
            'site', 'power_panel', 'rack', 'name', 'status', 'type', 'supply', 'phase', 'voltage', 'amperage',
            'max_utilization', 'comments', 'tags',
        ]
        widgets = {
            'status': StaticSelect2(),
            'type': StaticSelect2(),
            'supply': StaticSelect2(),
            'phase': StaticSelect2(),
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        # Initialize site field
        if self.instance and hasattr(self.instance, 'power_panel'):
            self.initial['site'] = self.instance.power_panel.site


class PowerFeedCSVForm(CustomFieldModelCSVForm):
    site = forms.ModelChoiceField(
        queryset=Site.objects.all(),
        to_field_name='name',
        help_text='Name of parent site',
        error_messages={
            'invalid_choice': 'Site not found.',
        }
    )
    panel_name = forms.ModelChoiceField(
        queryset=PowerPanel.objects.all(),
        to_field_name='name',
        help_text='Name of upstream power panel',
        error_messages={
            'invalid_choice': 'Power panel not found.',
        }
    )
    rack_group = forms.CharField(
        required=False,
        help_text="Rack group name (optional)"
    )
    rack_name = forms.CharField(
        required=False,
        help_text="Rack name (optional)"
    )
    status = CSVChoiceField(
        choices=PowerFeedStatusChoices,
        required=False,
        help_text='Operational status'
    )
    type = CSVChoiceField(
        choices=PowerFeedTypeChoices,
        required=False,
        help_text='Primary or redundant'
    )
    supply = CSVChoiceField(
        choices=PowerFeedSupplyChoices,
        required=False,
        help_text='AC/DC'
    )
    phase = CSVChoiceField(
        choices=PowerFeedPhaseChoices,
        required=False,
        help_text='Single or three-phase'
    )

    class Meta:
        model = PowerFeed
        fields = PowerFeed.csv_headers

    def clean(self):

        super().clean()

        site = self.cleaned_data.get('site')
        panel_name = self.cleaned_data.get('panel_name')
        rack_group = self.cleaned_data.get('rack_group')
        rack_name = self.cleaned_data.get('rack_name')

        # Validate power panel
        if panel_name:
            try:
                self.instance.power_panel = PowerPanel.objects.get(site=site, name=panel_name)
            except Rack.DoesNotExist:
                raise forms.ValidationError(
                    "Power panel {} not found in site {}".format(panel_name, site)
                )

        # Validate rack
        if rack_name:
            try:
                self.instance.rack = Rack.objects.get(site=site, group__name=rack_group, name=rack_name)
            except Rack.DoesNotExist:
                raise forms.ValidationError(
                    "Rack {} not found in site {}, group {}".format(rack_name, site, rack_group)
                )


class PowerFeedBulkEditForm(BootstrapMixin, AddRemoveTagsForm, CustomFieldBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=PowerFeed.objects.all(),
        widget=forms.MultipleHiddenInput
    )
    power_panel = DynamicModelChoiceField(
        queryset=PowerPanel.objects.all(),
        required=False,
        widget=APISelect(
            api_url="/api/dcim/power-panels/",
            filter_for={
                'rackgroup': 'site_id',
            }
        )
    )
    rack = DynamicModelChoiceField(
        queryset=Rack.objects.all(),
        required=False,
        widget=APISelect(
            api_url="/api/dcim/racks",
        )
    )
    status = forms.ChoiceField(
        choices=add_blank_choice(PowerFeedStatusChoices),
        required=False,
        initial='',
        widget=StaticSelect2()
    )
    type = forms.ChoiceField(
        choices=add_blank_choice(PowerFeedTypeChoices),
        required=False,
        initial='',
        widget=StaticSelect2()
    )
    supply = forms.ChoiceField(
        choices=add_blank_choice(PowerFeedSupplyChoices),
        required=False,
        initial='',
        widget=StaticSelect2()
    )
    phase = forms.ChoiceField(
        choices=add_blank_choice(PowerFeedPhaseChoices),
        required=False,
        initial='',
        widget=StaticSelect2()
    )
    voltage = forms.IntegerField(
        required=False
    )
    amperage = forms.IntegerField(
        required=False
    )
    max_utilization = forms.IntegerField(
        required=False
    )
    comments = CommentField(
        widget=SmallTextarea,
        label='Comments'
    )

    class Meta:
        nullable_fields = [
            'rackgroup', 'comments',
        ]


class PowerFeedFilterForm(BootstrapMixin, CustomFieldFilterForm):
    model = PowerFeed
    q = forms.CharField(
        required=False,
        label='Search'
    )
    region = DynamicModelMultipleChoiceField(
        queryset=Region.objects.all(),
        to_field_name='slug',
        required=False,
        widget=APISelectMultiple(
            api_url="/api/dcim/regions/",
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
            api_url="/api/dcim/sites/",
            value_field="slug",
            filter_for={
                'power_panel_id': 'site',
                'rack_id': 'site',
            }
        )
    )
    power_panel_id = DynamicModelMultipleChoiceField(
        queryset=PowerPanel.objects.all(),
        required=False,
        label='Power panel',
        widget=APISelectMultiple(
            api_url="/api/dcim/power-panels/",
            null_option=True,
        )
    )
    rack_id = DynamicModelMultipleChoiceField(
        queryset=Rack.objects.all(),
        required=False,
        label='Rack',
        widget=APISelectMultiple(
            api_url="/api/dcim/racks/",
            null_option=True,
        )
    )
    status = forms.MultipleChoiceField(
        choices=PowerFeedStatusChoices,
        required=False,
        widget=StaticSelect2Multiple()
    )
    type = forms.ChoiceField(
        choices=add_blank_choice(PowerFeedTypeChoices),
        required=False,
        widget=StaticSelect2()
    )
    supply = forms.ChoiceField(
        choices=add_blank_choice(PowerFeedSupplyChoices),
        required=False,
        widget=StaticSelect2()
    )
    phase = forms.ChoiceField(
        choices=add_blank_choice(PowerFeedPhaseChoices),
        required=False,
        widget=StaticSelect2()
    )
    voltage = forms.IntegerField(
        required=False
    )
    amperage = forms.IntegerField(
        required=False
    )
    max_utilization = forms.IntegerField(
        required=False
    )
    tag = TagFilterField(model)
