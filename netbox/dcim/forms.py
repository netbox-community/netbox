import re

from django import forms
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.forms.array import SimpleArrayField
from django.core.exceptions import ObjectDoesNotExist
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from netaddr import EUI
from netaddr.core import AddrFormatError
from timezone_field import TimeZoneFormField

from circuits.models import Circuit, CircuitTermination, Provider
from extras.forms import (
    AddRemoveTagsForm, CustomFieldModelBulkEditForm, CustomFieldModelCSVForm, CustomFieldModelFilterForm, CustomFieldModelForm,
    CustomFieldsMixin, LocalConfigContextFilterForm,
)
from extras.models import Tag
from ipam.constants import BGP_ASN_MAX, BGP_ASN_MIN
from ipam.models import IPAddress, VLAN, VLANGroup
from tenancy.forms import TenancyFilterForm, TenancyForm
from tenancy.models import Tenant
from utilities.forms import (
    APISelect, APISelectMultiple, add_blank_choice, BootstrapMixin, BulkEditForm, BulkEditNullBooleanSelect,
    ColorField, CommentField, CSVChoiceField, CSVContentTypeField, CSVModelChoiceField, CSVTypedChoiceField,
    DynamicModelChoiceField, DynamicModelMultipleChoiceField, ExpandableNameField, form_from_model, JSONField,
    NumericArrayField, SelectWithPK, SmallTextarea, SlugField, StaticSelect, StaticSelectMultiple, TagFilterField,
    BOOLEAN_WITH_BLANK_CHOICES,
)
from virtualization.models import Cluster, ClusterGroup
from .choices import *
from .constants import *
from .models import *

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


class DeviceComponentFilterForm(BootstrapMixin, CustomFieldModelFilterForm):
    field_order = [
        'q', 'name', 'label', 'region_id', 'site_group_id', 'site_id',
    ]
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': _('All Fields')}),
        label=_('Search')
    )
    name = forms.CharField(
        required=False
    )
    label = forms.CharField(
        required=False
    )
    region_id = DynamicModelMultipleChoiceField(
        queryset=Region.objects.all(),
        required=False,
        label=_('Region'),
        fetch_trigger='open'
    )
    site_group_id = DynamicModelMultipleChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False,
        label=_('Site group'),
        fetch_trigger='open'
    )
    site_id = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        query_params={
            'region_id': '$region_id',
            'group_id': '$site_group_id',
        },
        label=_('Site'),
        fetch_trigger='open'
    )
    location_id = DynamicModelMultipleChoiceField(
        queryset=Location.objects.all(),
        required=False,
        query_params={
            'site_id': '$site_id',
        },
        label=_('Location'),
        fetch_trigger='open'
    )
    device_id = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        required=False,
        query_params={
            'site_id': '$site_id',
            'location_id': '$location_id',
        },
        label=_('Device'),
        fetch_trigger='open'
    )


class InterfaceCommonForm(forms.Form):
    mac_address = forms.CharField(
        empty_value=None,
        required=False,
        label='MAC address'
    )
    mtu = forms.IntegerField(
        required=False,
        min_value=INTERFACE_MTU_MIN,
        max_value=INTERFACE_MTU_MAX,
        label='MTU'
    )

    def clean(self):
        super().clean()

        parent_field = 'device' if 'device' in self.cleaned_data else 'virtual_machine'
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
            valid_sites = [None, self.cleaned_data[parent_field].site]
            invalid_vlans = [str(v) for v in tagged_vlans if v.site not in valid_sites]

            if invalid_vlans:
                raise forms.ValidationError({
                    'tagged_vlans': f"The tagged VLANs ({', '.join(invalid_vlans)}) must belong to the same site as "
                                    f"the interface's parent device/VM, or they must be global"
                })


class ComponentForm(forms.Form):
    """
    Subclass this form when facilitating the creation of one or more device component or component templates based on
    a name pattern.
    """
    name_pattern = ExpandableNameField(
        label='Name'
    )
    label_pattern = ExpandableNameField(
        label='Label',
        required=False,
        help_text='Alphanumeric ranges are supported. (Must match the number of names being created.)'
    )

    def clean(self):
        super().clean()

        # Validate that the number of components being created from both the name_pattern and label_pattern are equal
        if self.cleaned_data['label_pattern']:
            name_pattern_count = len(self.cleaned_data['name_pattern'])
            label_pattern_count = len(self.cleaned_data['label_pattern'])
            if name_pattern_count != label_pattern_count:
                raise forms.ValidationError({
                    'label_pattern': f'The provided name pattern will create {name_pattern_count} components, however '
                                     f'{label_pattern_count} labels will be generated. These counts must match.'
                }, code='label_pattern_mismatch')


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

class RegionForm(BootstrapMixin, CustomFieldModelForm):
    parent = DynamicModelChoiceField(
        queryset=Region.objects.all(),
        required=False
    )
    slug = SlugField()

    class Meta:
        model = Region
        fields = (
            'parent', 'name', 'slug', 'description',
        )


class RegionCSVForm(CustomFieldModelCSVForm):
    parent = CSVModelChoiceField(
        queryset=Region.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Name of parent region'
    )

    class Meta:
        model = Region
        fields = ('name', 'slug', 'parent', 'description')


class RegionBulkEditForm(BootstrapMixin, CustomFieldModelBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=Region.objects.all(),
        widget=forms.MultipleHiddenInput
    )
    parent = DynamicModelChoiceField(
        queryset=Region.objects.all(),
        required=False
    )
    description = forms.CharField(
        max_length=200,
        required=False
    )

    class Meta:
        nullable_fields = ['parent', 'description']


class RegionFilterForm(BootstrapMixin, CustomFieldModelFilterForm):
    model = Region
    field_groups = [
        ['q'],
        ['parent_id'],
    ]
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': _('All Fields')}),
        label=_('Search')
    )
    parent_id = DynamicModelMultipleChoiceField(
        queryset=Region.objects.all(),
        required=False,
        label=_('Parent region'),
        fetch_trigger='open'
    )


#
# Site groups
#

class SiteGroupForm(BootstrapMixin, CustomFieldModelForm):
    parent = DynamicModelChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False
    )
    slug = SlugField()

    class Meta:
        model = SiteGroup
        fields = (
            'parent', 'name', 'slug', 'description',
        )


class SiteGroupCSVForm(CustomFieldModelCSVForm):
    parent = CSVModelChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Name of parent site group'
    )

    class Meta:
        model = SiteGroup
        fields = ('name', 'slug', 'parent', 'description')


class SiteGroupBulkEditForm(BootstrapMixin, CustomFieldModelBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=SiteGroup.objects.all(),
        widget=forms.MultipleHiddenInput
    )
    parent = DynamicModelChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False
    )
    description = forms.CharField(
        max_length=200,
        required=False
    )

    class Meta:
        nullable_fields = ['parent', 'description']


class SiteGroupFilterForm(BootstrapMixin, CustomFieldModelFilterForm):
    model = SiteGroup
    field_groups = [
        ['q'],
        ['parent_id'],
    ]
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': _('All Fields')}),
        label=_('Search')
    )
    parent_id = DynamicModelMultipleChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False,
        label=_('Parent group'),
        fetch_trigger='open'
    )


#
# Sites
#

class SiteForm(BootstrapMixin, TenancyForm, CustomFieldModelForm):
    region = DynamicModelChoiceField(
        queryset=Region.objects.all(),
        required=False
    )
    group = DynamicModelChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False
    )
    slug = SlugField()
    time_zone = TimeZoneFormField(
        choices=add_blank_choice(TimeZoneFormField().choices),
        required=False,
        widget=StaticSelect()
    )
    comments = CommentField()
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = Site
        fields = [
            'name', 'slug', 'status', 'region', 'group', 'tenant_group', 'tenant', 'facility', 'asn', 'time_zone',
            'description', 'physical_address', 'shipping_address', 'latitude', 'longitude', 'contact_name',
            'contact_phone', 'contact_email', 'comments', 'tags',
        ]
        fieldsets = (
            ('Site', (
                'name', 'slug', 'status', 'region', 'group', 'facility', 'asn', 'time_zone', 'description', 'tags',
            )),
            ('Tenancy', ('tenant_group', 'tenant')),
            ('Contact Info', (
                'physical_address', 'shipping_address', 'latitude', 'longitude', 'contact_name', 'contact_phone',
                'contact_email',
            )),
        )
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
            'status': StaticSelect(),
            'time_zone': StaticSelect(),
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
    region = CSVModelChoiceField(
        queryset=Region.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Assigned region'
    )
    group = CSVModelChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Assigned group'
    )
    tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Assigned tenant'
    )

    class Meta:
        model = Site
        fields = (
            'name', 'slug', 'status', 'region', 'group', 'tenant', 'facility', 'asn', 'time_zone', 'description',
            'physical_address', 'shipping_address', 'latitude', 'longitude', 'contact_name', 'contact_phone',
            'contact_email', 'comments',
        )
        help_texts = {
            'time_zone': mark_safe(
                'Time zone (<a href="https://en.wikipedia.org/wiki/List_of_tz_database_time_zones">available options</a>)'
            )
        }


class SiteBulkEditForm(BootstrapMixin, AddRemoveTagsForm, CustomFieldModelBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=Site.objects.all(),
        widget=forms.MultipleHiddenInput
    )
    status = forms.ChoiceField(
        choices=add_blank_choice(SiteStatusChoices),
        required=False,
        initial='',
        widget=StaticSelect()
    )
    region = DynamicModelChoiceField(
        queryset=Region.objects.all(),
        required=False
    )
    group = DynamicModelChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False
    )
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False
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
        widget=StaticSelect()
    )

    class Meta:
        nullable_fields = [
            'region', 'group', 'tenant', 'asn', 'description', 'time_zone',
        ]


class SiteFilterForm(BootstrapMixin, TenancyFilterForm, CustomFieldModelFilterForm):
    model = Site
    field_order = ['q', 'status', 'region_id', 'tenant_group_id', 'tenant_id']
    field_groups = [
        ['q', 'tag'],
        ['status', 'region_id', 'group_id'],
        ['tenant_group_id', 'tenant_id'],
    ]
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': _('All Fields')}),
        label=_('Search')
    )
    status = forms.MultipleChoiceField(
        choices=SiteStatusChoices,
        required=False,
        widget=StaticSelectMultiple(),
    )
    region_id = DynamicModelMultipleChoiceField(
        queryset=Region.objects.all(),
        required=False,
        label=_('Region'),
        fetch_trigger='open'
    )
    group_id = DynamicModelMultipleChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False,
        label=_('Site group'),
        fetch_trigger='open'
    )
    tag = TagFilterField(model)


#
# Locations
#

class LocationForm(BootstrapMixin, CustomFieldModelForm):
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
        query_params={
            'region_id': '$region',
            'group_id': '$site_group',
        }
    )
    parent = DynamicModelChoiceField(
        queryset=Location.objects.all(),
        required=False,
        query_params={
            'site_id': '$site'
        }
    )
    slug = SlugField()

    class Meta:
        model = Location
        fields = (
            'region', 'site_group', 'site', 'parent', 'name', 'slug', 'description',
        )


class LocationCSVForm(CustomFieldModelCSVForm):
    site = CSVModelChoiceField(
        queryset=Site.objects.all(),
        to_field_name='name',
        help_text='Assigned site'
    )
    parent = CSVModelChoiceField(
        queryset=Location.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Parent location',
        error_messages={
            'invalid_choice': 'Location not found.',
        }
    )

    class Meta:
        model = Location
        fields = ('site', 'parent', 'name', 'slug', 'description')


class LocationBulkEditForm(BootstrapMixin, CustomFieldModelBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=Location.objects.all(),
        widget=forms.MultipleHiddenInput
    )
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False
    )
    parent = DynamicModelChoiceField(
        queryset=Location.objects.all(),
        required=False,
        query_params={
            'site_id': '$site'
        }
    )
    description = forms.CharField(
        max_length=200,
        required=False
    )

    class Meta:
        nullable_fields = ['parent', 'description']


class LocationFilterForm(BootstrapMixin, CustomFieldModelFilterForm):
    model = Location
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': _('All Fields')}),
        label=_('Search')
    )
    region_id = DynamicModelMultipleChoiceField(
        queryset=Region.objects.all(),
        required=False,
        label=_('Region'),
        fetch_trigger='open'
    )
    site_group_id = DynamicModelMultipleChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False,
        label=_('Site group'),
        fetch_trigger='open'
    )
    site_id = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        query_params={
            'region_id': '$region_id',
            'group_id': '$site_group_id',
        },
        label=_('Site'),
        fetch_trigger='open'
    )
    parent_id = DynamicModelMultipleChoiceField(
        queryset=Location.objects.all(),
        required=False,
        query_params={
            'region_id': '$region_id',
            'site_id': '$site_id',
        },
        label=_('Parent'),
        fetch_trigger='open'
    )


#
# Rack roles
#

class RackRoleForm(BootstrapMixin, CustomFieldModelForm):
    slug = SlugField()

    class Meta:
        model = RackRole
        fields = [
            'name', 'slug', 'color', 'description',
        ]


class RackRoleCSVForm(CustomFieldModelCSVForm):
    slug = SlugField()

    class Meta:
        model = RackRole
        fields = ('name', 'slug', 'color', 'description')
        help_texts = {
            'color': mark_safe('RGB color in hexadecimal (e.g. <code>00ff00</code>)'),
        }


class RackRoleBulkEditForm(BootstrapMixin, CustomFieldModelBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=RackRole.objects.all(),
        widget=forms.MultipleHiddenInput
    )
    color = ColorField(
        required=False
    )
    description = forms.CharField(
        max_length=200,
        required=False
    )

    class Meta:
        nullable_fields = ['color', 'description']


#
# Racks
#

class RackForm(BootstrapMixin, TenancyForm, CustomFieldModelForm):
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
        query_params={
            'region_id': '$region',
            'group_id': '$site_group',
        }
    )
    location = DynamicModelChoiceField(
        queryset=Location.objects.all(),
        required=False,
        query_params={
            'site_id': '$site'
        }
    )
    role = DynamicModelChoiceField(
        queryset=RackRole.objects.all(),
        required=False
    )
    comments = CommentField()
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = Rack
        fields = [
            'region', 'site_group', 'site', 'location', 'name', 'facility_id', 'tenant_group', 'tenant', 'status',
            'role', 'serial', 'asset_tag', 'type', 'width', 'u_height', 'desc_units', 'outer_width', 'outer_depth',
            'outer_unit', 'comments', 'tags',
        ]
        help_texts = {
            'site': "The site at which the rack exists",
            'name': "Organizational rack name",
            'facility_id': "The unique rack ID assigned by the facility",
            'u_height': "Height in rack units",
        }
        widgets = {
            'status': StaticSelect(),
            'type': StaticSelect(),
            'width': StaticSelect(),
            'outer_unit': StaticSelect(),
        }


class RackCSVForm(CustomFieldModelCSVForm):
    site = CSVModelChoiceField(
        queryset=Site.objects.all(),
        to_field_name='name'
    )
    location = CSVModelChoiceField(
        queryset=Location.objects.all(),
        required=False,
        to_field_name='name'
    )
    tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Name of assigned tenant'
    )
    status = CSVChoiceField(
        choices=RackStatusChoices,
        required=False,
        help_text='Operational status'
    )
    role = CSVModelChoiceField(
        queryset=RackRole.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Name of assigned role'
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
        fields = (
            'site', 'location', 'name', 'facility_id', 'tenant', 'status', 'role', 'type', 'serial', 'asset_tag',
            'width', 'u_height', 'desc_units', 'outer_width', 'outer_depth', 'outer_unit', 'comments',
        )

    def __init__(self, data=None, *args, **kwargs):
        super().__init__(data, *args, **kwargs)

        if data:

            # Limit location queryset by assigned site
            params = {f"site__{self.fields['site'].to_field_name}": data.get('site')}
            self.fields['location'].queryset = self.fields['location'].queryset.filter(**params)


class RackBulkEditForm(BootstrapMixin, AddRemoveTagsForm, CustomFieldModelBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=Rack.objects.all(),
        widget=forms.MultipleHiddenInput
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
        query_params={
            'region_id': '$region',
            'group_id': '$site_group',
        }
    )
    location = DynamicModelChoiceField(
        queryset=Location.objects.all(),
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
        choices=add_blank_choice(RackStatusChoices),
        required=False,
        initial='',
        widget=StaticSelect()
    )
    role = DynamicModelChoiceField(
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
        choices=add_blank_choice(RackTypeChoices),
        required=False,
        widget=StaticSelect()
    )
    width = forms.ChoiceField(
        choices=add_blank_choice(RackWidthChoices),
        required=False,
        widget=StaticSelect()
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
        widget=StaticSelect()
    )
    comments = CommentField(
        widget=SmallTextarea,
        label='Comments'
    )

    class Meta:
        nullable_fields = [
            'location', 'tenant', 'role', 'serial', 'asset_tag', 'outer_width', 'outer_depth', 'outer_unit', 'comments',
        ]


class RackFilterForm(BootstrapMixin, TenancyFilterForm, CustomFieldModelFilterForm):
    model = Rack
    field_order = ['q', 'region_id', 'site_id', 'location_id', 'status', 'role_id', 'tenant_group_id', 'tenant_id']
    field_groups = [
        ['q', 'tag'],
        ['region_id', 'site_id', 'location_id'],
        ['status', 'role_id'],
        ['type', 'width', 'asset_tag'],
        ['tenant_group_id', 'tenant_id'],
    ]
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': _('All Fields')}),
        label=_('Search')
    )
    region_id = DynamicModelMultipleChoiceField(
        queryset=Region.objects.all(),
        required=False,
        label=_('Region'),
        fetch_trigger='open'
    )
    site_id = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        query_params={
            'region_id': '$region_id'
        },
        label=_('Site'),
        fetch_trigger='open'
    )
    location_id = DynamicModelMultipleChoiceField(
        queryset=Location.objects.all(),
        required=False,
        null_option='None',
        query_params={
            'site_id': '$site_id'
        },
        label=_('Location'),
        fetch_trigger='open'
    )
    status = forms.MultipleChoiceField(
        choices=RackStatusChoices,
        required=False,
        widget=StaticSelectMultiple()
    )
    type = forms.MultipleChoiceField(
        choices=RackTypeChoices,
        required=False,
        widget=StaticSelectMultiple()
    )
    width = forms.MultipleChoiceField(
        choices=RackWidthChoices,
        required=False,
        widget=StaticSelectMultiple()
    )
    role_id = DynamicModelMultipleChoiceField(
        queryset=RackRole.objects.all(),
        required=False,
        null_option='None',
        label=_('Role'),
        fetch_trigger='open'
    )
    asset_tag = forms.CharField(
        required=False
    )
    tag = TagFilterField(model)


#
# Rack elevations
#

class RackElevationFilterForm(RackFilterForm):
    field_order = [
        'q', 'region_id', 'site_id', 'location_id', 'id', 'status', 'role_id', 'tenant_group_id',
        'tenant_id',
    ]
    id = DynamicModelMultipleChoiceField(
        queryset=Rack.objects.all(),
        label=_('Rack'),
        required=False,
        query_params={
            'site_id': '$site_id',
            'location_id': '$location_id',
        },
        fetch_trigger='open'
    )


#
# Rack reservations
#

class RackReservationForm(BootstrapMixin, TenancyForm, CustomFieldModelForm):
    region = DynamicModelChoiceField(
        queryset=Region.objects.all(),
        required=False,
        initial_params={
            'sites': '$site'
        },
        fetch_trigger='open'
    )
    site_group = DynamicModelChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False,
        initial_params={
            'sites': '$site'
        },
        fetch_trigger='open'
    )
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        query_params={
            'region_id': '$region',
            'group_id': '$site_group',
        },
        fetch_trigger='open'
    )
    location = DynamicModelChoiceField(
        queryset=Location.objects.all(),
        required=False,
        query_params={
            'site_id': '$site'
        },
        fetch_trigger='open'
    )
    rack = DynamicModelChoiceField(
        queryset=Rack.objects.all(),
        query_params={
            'site_id': '$site',
            'location_id': '$location',
        },
        fetch_trigger='open'
    )
    units = NumericArrayField(
        base_field=forms.IntegerField(),
        help_text="Comma-separated list of numeric unit IDs. A range may be specified using a hyphen."
    )
    user = forms.ModelChoiceField(
        queryset=User.objects.order_by(
            'username'
        ),
        widget=StaticSelect()
    )
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        fetch_trigger='open'
    )

    class Meta:
        model = RackReservation
        fields = [
            'region', 'site_group', 'site', 'location', 'rack', 'units', 'user', 'tenant_group', 'tenant',
            'description', 'tags',
        ]
        fieldsets = (
            ('Reservation', ('region', 'site', 'location', 'rack', 'units', 'user', 'description', 'tags')),
            ('Tenancy', ('tenant_group', 'tenant')),
        )


class RackReservationCSVForm(CustomFieldModelCSVForm):
    site = CSVModelChoiceField(
        queryset=Site.objects.all(),
        to_field_name='name',
        help_text='Parent site'
    )
    location = CSVModelChoiceField(
        queryset=Location.objects.all(),
        to_field_name='name',
        required=False,
        help_text="Rack's location (if any)"
    )
    rack = CSVModelChoiceField(
        queryset=Rack.objects.all(),
        to_field_name='name',
        help_text='Rack'
    )
    units = SimpleArrayField(
        base_field=forms.IntegerField(),
        required=True,
        help_text='Comma-separated list of individual unit numbers'
    )
    tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Assigned tenant'
    )

    class Meta:
        model = RackReservation
        fields = ('site', 'location', 'rack', 'units', 'tenant', 'description')

    def __init__(self, data=None, *args, **kwargs):
        super().__init__(data, *args, **kwargs)

        if data:

            # Limit location queryset by assigned site
            params = {f"site__{self.fields['site'].to_field_name}": data.get('site')}
            self.fields['location'].queryset = self.fields['location'].queryset.filter(**params)

            # Limit rack queryset by assigned site and group
            params = {
                f"site__{self.fields['site'].to_field_name}": data.get('site'),
                f"location__{self.fields['location'].to_field_name}": data.get('location'),
            }
            self.fields['rack'].queryset = self.fields['rack'].queryset.filter(**params)


class RackReservationBulkEditForm(BootstrapMixin, AddRemoveTagsForm, CustomFieldModelBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=RackReservation.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
    user = forms.ModelChoiceField(
        queryset=User.objects.order_by(
            'username'
        ),
        required=False,
        widget=StaticSelect()
    )
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False
    )
    description = forms.CharField(
        max_length=100,
        required=False
    )

    class Meta:
        nullable_fields = []


class RackReservationFilterForm(BootstrapMixin, TenancyFilterForm, CustomFieldModelFilterForm):
    model = RackReservation
    field_order = ['q', 'region_id', 'site_id', 'location_id', 'user_id', 'tenant_group_id', 'tenant_id']
    field_groups = [
        ['q', 'tag'],
        ['user_id'],
        ['region_id', 'site_id', 'location_id'],
        ['tenant_group_id', 'tenant_id'],
    ]
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': _('All Fields')}),
        label=_('Search')
    )
    region_id = DynamicModelMultipleChoiceField(
        queryset=Region.objects.all(),
        required=False,
        label=_('Region'),
        fetch_trigger='open'
    )
    site_id = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        query_params={
            'region_id': '$region_id'
        },
        label=_('Site'),
        fetch_trigger='open'
    )
    location_id = DynamicModelMultipleChoiceField(
        queryset=Location.objects.prefetch_related('site'),
        required=False,
        label=_('Location'),
        null_option='None',
        fetch_trigger='open'
    )
    user_id = DynamicModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        label=_('User'),
        widget=APISelectMultiple(
            api_url='/api/users/users/',
        ),
        fetch_trigger='open'
    )
    tag = TagFilterField(model)


#
# Manufacturers
#

class ManufacturerForm(BootstrapMixin, CustomFieldModelForm):
    slug = SlugField()

    class Meta:
        model = Manufacturer
        fields = [
            'name', 'slug', 'description',
        ]


class ManufacturerCSVForm(CustomFieldModelCSVForm):

    class Meta:
        model = Manufacturer
        fields = ('name', 'slug', 'description')


class ManufacturerBulkEditForm(BootstrapMixin, CustomFieldModelBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=Manufacturer.objects.all(),
        widget=forms.MultipleHiddenInput
    )
    description = forms.CharField(
        max_length=200,
        required=False
    )

    class Meta:
        nullable_fields = ['description']


#
# Device types
#

class DeviceTypeForm(BootstrapMixin, CustomFieldModelForm):
    manufacturer = DynamicModelChoiceField(
        queryset=Manufacturer.objects.all()
    )
    slug = SlugField(
        slug_source='model'
    )
    comments = CommentField()
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = DeviceType
        fields = [
            'manufacturer', 'model', 'slug', 'part_number', 'u_height', 'is_full_depth', 'subdevice_role',
            'front_image', 'rear_image', 'comments', 'tags',
        ]
        fieldsets = (
            ('Device Type', (
                'manufacturer', 'model', 'slug', 'part_number', 'u_height', 'is_full_depth', 'subdevice_role', 'tags',
            )),
            ('Images', ('front_image', 'rear_image')),
        )
        widgets = {
            'subdevice_role': StaticSelect(),
            'front_image': forms.ClearableFileInput(attrs={
                'accept': DEVICETYPE_IMAGE_FORMATS
            }),
            'rear_image': forms.ClearableFileInput(attrs={
                'accept': DEVICETYPE_IMAGE_FORMATS
            })
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
            'comments',
        ]


class DeviceTypeBulkEditForm(BootstrapMixin, AddRemoveTagsForm, CustomFieldModelBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=DeviceType.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
    manufacturer = DynamicModelChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False
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


class DeviceTypeFilterForm(BootstrapMixin, CustomFieldModelFilterForm):
    model = DeviceType
    field_groups = [
        ['q', 'tag'],
        ['manufacturer_id', 'subdevice_role'],
        ['console_ports', 'console_server_ports', 'power_ports', 'power_outlets', 'interfaces', 'pass_through_ports'],
    ]
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': _('All Fields')}),
        label=_('Search')
    )
    manufacturer_id = DynamicModelMultipleChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False,
        label=_('Manufacturer'),
        fetch_trigger='open'
    )
    subdevice_role = forms.MultipleChoiceField(
        choices=add_blank_choice(SubdeviceRoleChoices),
        required=False,
        widget=StaticSelectMultiple()
    )
    console_ports = forms.NullBooleanField(
        required=False,
        label='Has console ports',
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    console_server_ports = forms.NullBooleanField(
        required=False,
        label='Has console server ports',
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    power_ports = forms.NullBooleanField(
        required=False,
        label='Has power ports',
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    power_outlets = forms.NullBooleanField(
        required=False,
        label='Has power outlets',
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    interfaces = forms.NullBooleanField(
        required=False,
        label='Has interfaces',
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    pass_through_ports = forms.NullBooleanField(
        required=False,
        label='Has pass-through ports',
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    tag = TagFilterField(model)


#
# Device component templates
#

class ComponentTemplateCreateForm(BootstrapMixin, ComponentForm):
    """
    Base form for the creation of device component templates (subclassed from ComponentTemplateModel).
    """
    manufacturer = DynamicModelChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False,
        initial_params={
            'device_types': 'device_type'
        }
    )
    device_type = DynamicModelChoiceField(
        queryset=DeviceType.objects.all(),
        query_params={
            'manufacturer_id': '$manufacturer'
        }
    )
    description = forms.CharField(
        required=False
    )


class ConsolePortTemplateForm(BootstrapMixin, forms.ModelForm):

    class Meta:
        model = ConsolePortTemplate
        fields = [
            'device_type', 'name', 'label', 'type', 'description',
        ]
        widgets = {
            'device_type': forms.HiddenInput(),
        }


class ConsolePortTemplateCreateForm(ComponentTemplateCreateForm):
    type = forms.ChoiceField(
        choices=add_blank_choice(ConsolePortTypeChoices),
        widget=StaticSelect()
    )
    field_order = ('manufacturer', 'device_type', 'name_pattern', 'label_pattern', 'type', 'description')


class ConsolePortTemplateBulkEditForm(BootstrapMixin, BulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=ConsolePortTemplate.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
    label = forms.CharField(
        max_length=64,
        required=False
    )
    type = forms.ChoiceField(
        choices=add_blank_choice(ConsolePortTypeChoices),
        required=False,
        widget=StaticSelect()
    )

    class Meta:
        nullable_fields = ('label', 'type', 'description')


class ConsoleServerPortTemplateForm(BootstrapMixin, forms.ModelForm):

    class Meta:
        model = ConsoleServerPortTemplate
        fields = [
            'device_type', 'name', 'label', 'type', 'description',
        ]
        widgets = {
            'device_type': forms.HiddenInput(),
        }


class ConsoleServerPortTemplateCreateForm(ComponentTemplateCreateForm):
    type = forms.ChoiceField(
        choices=add_blank_choice(ConsolePortTypeChoices),
        widget=StaticSelect()
    )
    field_order = ('manufacturer', 'device_type', 'name_pattern', 'label_pattern', 'type', 'description')


class ConsoleServerPortTemplateBulkEditForm(BootstrapMixin, BulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=ConsoleServerPortTemplate.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
    label = forms.CharField(
        max_length=64,
        required=False
    )
    type = forms.ChoiceField(
        choices=add_blank_choice(ConsolePortTypeChoices),
        required=False,
        widget=StaticSelect()
    )
    description = forms.CharField(
        required=False
    )

    class Meta:
        nullable_fields = ('label', 'type', 'description')


class PowerPortTemplateForm(BootstrapMixin, forms.ModelForm):

    class Meta:
        model = PowerPortTemplate
        fields = [
            'device_type', 'name', 'label', 'type', 'maximum_draw', 'allocated_draw', 'description',
        ]
        widgets = {
            'device_type': forms.HiddenInput(),
        }


class PowerPortTemplateCreateForm(ComponentTemplateCreateForm):
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
    field_order = (
        'manufacturer', 'device_type', 'name_pattern', 'label_pattern', 'type', 'maximum_draw', 'allocated_draw',
        'description',
    )


class PowerPortTemplateBulkEditForm(BootstrapMixin, BulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=PowerPortTemplate.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
    label = forms.CharField(
        max_length=64,
        required=False
    )
    type = forms.ChoiceField(
        choices=add_blank_choice(PowerPortTypeChoices),
        required=False,
        widget=StaticSelect()
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
    description = forms.CharField(
        required=False
    )

    class Meta:
        nullable_fields = ('label', 'type', 'maximum_draw', 'allocated_draw', 'description')


class PowerOutletTemplateForm(BootstrapMixin, forms.ModelForm):

    class Meta:
        model = PowerOutletTemplate
        fields = [
            'device_type', 'name', 'label', 'type', 'power_port', 'feed_leg', 'description',
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


class PowerOutletTemplateCreateForm(ComponentTemplateCreateForm):
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
        widget=StaticSelect()
    )
    field_order = (
        'manufacturer', 'device_type', 'name_pattern', 'label_pattern', 'type', 'power_port', 'feed_leg',
        'description',
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
    device_type = forms.ModelChoiceField(
        queryset=DeviceType.objects.all(),
        required=False,
        disabled=True,
        widget=forms.HiddenInput()
    )
    label = forms.CharField(
        max_length=64,
        required=False
    )
    type = forms.ChoiceField(
        choices=add_blank_choice(PowerOutletTypeChoices),
        required=False,
        widget=StaticSelect()
    )
    power_port = forms.ModelChoiceField(
        queryset=PowerPortTemplate.objects.all(),
        required=False
    )
    feed_leg = forms.ChoiceField(
        choices=add_blank_choice(PowerOutletFeedLegChoices),
        required=False,
        widget=StaticSelect()
    )
    description = forms.CharField(
        required=False
    )

    class Meta:
        nullable_fields = ('label', 'type', 'power_port', 'feed_leg', 'description')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Limit power_port queryset to PowerPortTemplates which belong to the parent DeviceType
        if 'device_type' in self.initial:
            device_type = DeviceType.objects.filter(pk=self.initial['device_type']).first()
            self.fields['power_port'].queryset = PowerPortTemplate.objects.filter(device_type=device_type)
        else:
            self.fields['power_port'].choices = ()
            self.fields['power_port'].widget.attrs['disabled'] = True


class InterfaceTemplateForm(BootstrapMixin, forms.ModelForm):

    class Meta:
        model = InterfaceTemplate
        fields = [
            'device_type', 'name', 'label', 'type', 'mgmt_only', 'description',
        ]
        widgets = {
            'device_type': forms.HiddenInput(),
            'type': StaticSelect(),
        }


class InterfaceTemplateCreateForm(ComponentTemplateCreateForm):
    type = forms.ChoiceField(
        choices=InterfaceTypeChoices,
        widget=StaticSelect()
    )
    mgmt_only = forms.BooleanField(
        required=False,
        label='Management only'
    )
    field_order = ('manufacturer', 'device_type', 'name_pattern', 'label_pattern', 'type', 'mgmt_only', 'description')


class InterfaceTemplateBulkEditForm(BootstrapMixin, BulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=InterfaceTemplate.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
    label = forms.CharField(
        max_length=64,
        required=False
    )
    type = forms.ChoiceField(
        choices=add_blank_choice(InterfaceTypeChoices),
        required=False,
        widget=StaticSelect()
    )
    mgmt_only = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect,
        label='Management only'
    )
    description = forms.CharField(
        required=False
    )

    class Meta:
        nullable_fields = ('label', 'description')


class FrontPortTemplateForm(BootstrapMixin, forms.ModelForm):

    class Meta:
        model = FrontPortTemplate
        fields = [
            'device_type', 'name', 'label', 'type', 'color', 'rear_port', 'rear_port_position', 'description',
        ]
        widgets = {
            'device_type': forms.HiddenInput(),
            'rear_port': StaticSelect(),
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        # Limit rear_port choices to current DeviceType
        if hasattr(self.instance, 'device_type'):
            self.fields['rear_port'].queryset = RearPortTemplate.objects.filter(
                device_type=self.instance.device_type
            )


class FrontPortTemplateCreateForm(ComponentTemplateCreateForm):
    type = forms.ChoiceField(
        choices=PortTypeChoices,
        widget=StaticSelect()
    )
    color = ColorField(
        required=False
    )
    rear_port_set = forms.MultipleChoiceField(
        choices=[],
        label='Rear ports',
        help_text='Select one rear port assignment for each front port being created.',
    )
    field_order = (
        'manufacturer', 'device_type', 'name_pattern', 'label_pattern', 'type', 'color', 'rear_port_set', 'description',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        device_type = DeviceType.objects.get(
            pk=self.initial.get('device_type') or self.data.get('device_type')
        )

        # Determine which rear port positions are occupied. These will be excluded from the list of available mappings.
        occupied_port_positions = [
            (front_port.rear_port_id, front_port.rear_port_position)
            for front_port in device_type.frontporttemplates.all()
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
        super().clean()

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
    label = forms.CharField(
        max_length=64,
        required=False
    )
    type = forms.ChoiceField(
        choices=add_blank_choice(PortTypeChoices),
        required=False,
        widget=StaticSelect()
    )
    color = ColorField(
        required=False
    )
    description = forms.CharField(
        required=False
    )

    class Meta:
        nullable_fields = ('description',)


class RearPortTemplateForm(BootstrapMixin, forms.ModelForm):

    class Meta:
        model = RearPortTemplate
        fields = [
            'device_type', 'name', 'label', 'type', 'color', 'positions', 'description',
        ]
        widgets = {
            'device_type': forms.HiddenInput(),
            'type': StaticSelect(),
        }


class RearPortTemplateCreateForm(ComponentTemplateCreateForm):
    type = forms.ChoiceField(
        choices=PortTypeChoices,
        widget=StaticSelect(),
    )
    color = ColorField(
        required=False
    )
    positions = forms.IntegerField(
        min_value=REARPORT_POSITIONS_MIN,
        max_value=REARPORT_POSITIONS_MAX,
        initial=1,
        help_text='The number of front ports which may be mapped to each rear port'
    )
    field_order = (
        'manufacturer', 'device_type', 'name_pattern', 'label_pattern', 'type', 'color', 'positions', 'description',
    )


class RearPortTemplateBulkEditForm(BootstrapMixin, BulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=RearPortTemplate.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
    label = forms.CharField(
        max_length=64,
        required=False
    )
    type = forms.ChoiceField(
        choices=add_blank_choice(PortTypeChoices),
        required=False,
        widget=StaticSelect()
    )
    color = ColorField(
        required=False
    )
    description = forms.CharField(
        required=False
    )

    class Meta:
        nullable_fields = ('description',)


class DeviceBayTemplateForm(BootstrapMixin, forms.ModelForm):

    class Meta:
        model = DeviceBayTemplate
        fields = [
            'device_type', 'name', 'label', 'description',
        ]
        widgets = {
            'device_type': forms.HiddenInput(),
        }


class DeviceBayTemplateCreateForm(ComponentTemplateCreateForm):
    field_order = ('manufacturer', 'device_type', 'name_pattern', 'label_pattern', 'description')


class DeviceBayTemplateBulkEditForm(BootstrapMixin, BulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=DeviceBayTemplate.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
    label = forms.CharField(
        max_length=64,
        required=False
    )
    description = forms.CharField(
        required=False
    )

    class Meta:
        nullable_fields = ('label', 'description')


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
            'device_type', 'name', 'label', 'type', 'description',
        ]


class ConsoleServerPortTemplateImportForm(ComponentTemplateImportForm):

    class Meta:
        model = ConsoleServerPortTemplate
        fields = [
            'device_type', 'name', 'label', 'type', 'description',
        ]


class PowerPortTemplateImportForm(ComponentTemplateImportForm):

    class Meta:
        model = PowerPortTemplate
        fields = [
            'device_type', 'name', 'label', 'type', 'maximum_draw', 'allocated_draw', 'description',
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
            'device_type', 'name', 'label', 'type', 'power_port', 'feed_leg', 'description',
        ]


class InterfaceTemplateImportForm(ComponentTemplateImportForm):
    type = forms.ChoiceField(
        choices=InterfaceTypeChoices.CHOICES
    )

    class Meta:
        model = InterfaceTemplate
        fields = [
            'device_type', 'name', 'label', 'type', 'mgmt_only', 'description',
        ]


class FrontPortTemplateImportForm(ComponentTemplateImportForm):
    type = forms.ChoiceField(
        choices=PortTypeChoices.CHOICES
    )
    rear_port = forms.ModelChoiceField(
        queryset=RearPortTemplate.objects.all(),
        to_field_name='name'
    )

    class Meta:
        model = FrontPortTemplate
        fields = [
            'device_type', 'name', 'type', 'rear_port', 'rear_port_position', 'label', 'description',
        ]


class RearPortTemplateImportForm(ComponentTemplateImportForm):
    type = forms.ChoiceField(
        choices=PortTypeChoices.CHOICES
    )

    class Meta:
        model = RearPortTemplate
        fields = [
            'device_type', 'name', 'type', 'positions', 'label', 'description',
        ]


class DeviceBayTemplateImportForm(ComponentTemplateImportForm):

    class Meta:
        model = DeviceBayTemplate
        fields = [
            'device_type', 'name', 'label', 'description',
        ]


#
# Device roles
#

class DeviceRoleForm(BootstrapMixin, CustomFieldModelForm):
    slug = SlugField()

    class Meta:
        model = DeviceRole
        fields = [
            'name', 'slug', 'color', 'vm_role', 'description',
        ]


class DeviceRoleCSVForm(CustomFieldModelCSVForm):
    slug = SlugField()

    class Meta:
        model = DeviceRole
        fields = ('name', 'slug', 'color', 'vm_role', 'description')
        help_texts = {
            'color': mark_safe('RGB color in hexadecimal (e.g. <code>00ff00</code>)'),
        }


class DeviceRoleBulkEditForm(BootstrapMixin, CustomFieldModelBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=DeviceRole.objects.all(),
        widget=forms.MultipleHiddenInput
    )
    color = ColorField(
        required=False
    )
    vm_role = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect,
        label='VM role'
    )
    description = forms.CharField(
        max_length=200,
        required=False
    )

    class Meta:
        nullable_fields = ['color', 'description']


#
# Platforms
#

class PlatformForm(BootstrapMixin, CustomFieldModelForm):
    manufacturer = DynamicModelChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False
    )
    slug = SlugField(
        max_length=64
    )

    class Meta:
        model = Platform
        fields = [
            'name', 'slug', 'manufacturer', 'napalm_driver', 'napalm_args', 'description',
        ]
        widgets = {
            'napalm_args': SmallTextarea(),
        }


class PlatformCSVForm(CustomFieldModelCSVForm):
    slug = SlugField()
    manufacturer = CSVModelChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Limit platform assignments to this manufacturer'
    )

    class Meta:
        model = Platform
        fields = ('name', 'slug', 'manufacturer', 'napalm_driver', 'napalm_args', 'description')


class PlatformBulkEditForm(BootstrapMixin, CustomFieldModelBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=Platform.objects.all(),
        widget=forms.MultipleHiddenInput
    )
    manufacturer = DynamicModelChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False
    )
    napalm_driver = forms.CharField(
        max_length=50,
        required=False
    )
    # TODO: Bulk edit support for napalm_args
    description = forms.CharField(
        max_length=200,
        required=False
    )

    class Meta:
        nullable_fields = ['manufacturer', 'napalm_driver', 'description']


class PlatformFilterForm(BootstrapMixin, CustomFieldModelFilterForm):
    model = Platform
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': _('All Fields')}),
        label=_('Search')
    )
    manufacturer_id = DynamicModelMultipleChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False,
        label=_('Manufacturer'),
        fetch_trigger='open'
    )


#
# Devices
#

class DeviceForm(BootstrapMixin, TenancyForm, CustomFieldModelForm):
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
        query_params={
            'region_id': '$region',
            'group_id': '$site_group',
        }
    )
    location = DynamicModelChoiceField(
        queryset=Location.objects.all(),
        required=False,
        query_params={
            'site_id': '$site'
        },
        initial_params={
            'racks': '$rack'
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
    position = forms.IntegerField(
        required=False,
        help_text="The lowest-numbered unit occupied by the device",
        widget=APISelect(
            api_url='/api/dcim/racks/{{rack}}/elevation/',
            attrs={
                'disabled-indicator': 'device',
                'data-query-param-face': "[\"$face\"]",
                # The UI will not sort this element's options.
                'pre-sorted': ''
            }
        )
    )
    manufacturer = DynamicModelChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False,
        initial_params={
            'device_types': '$device_type'
        }
    )
    device_type = DynamicModelChoiceField(
        queryset=DeviceType.objects.all(),
        query_params={
            'manufacturer_id': '$manufacturer'
        }
    )
    device_role = DynamicModelChoiceField(
        queryset=DeviceRole.objects.all()
    )
    platform = DynamicModelChoiceField(
        queryset=Platform.objects.all(),
        required=False,
        query_params={
            'manufacturer_id': ['$manufacturer', 'null']
        }
    )
    cluster_group = DynamicModelChoiceField(
        queryset=ClusterGroup.objects.all(),
        required=False,
        null_option='None',
        initial_params={
            'clusters': '$cluster'
        }
    )
    cluster = DynamicModelChoiceField(
        queryset=Cluster.objects.all(),
        required=False,
        query_params={
            'group_id': '$cluster_group'
        }
    )
    comments = CommentField()
    local_context_data = JSONField(
        required=False,
        label=''
    )
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = Device
        fields = [
            'name', 'device_role', 'device_type', 'serial', 'asset_tag', 'region', 'site_group', 'site', 'rack',
            'location', 'position', 'face', 'status', 'platform', 'primary_ip4', 'primary_ip6', 'cluster_group',
            'cluster', 'tenant_group', 'tenant', 'comments', 'tags', 'local_context_data'
        ]
        help_texts = {
            'device_role': "The function this device serves",
            'serial': "Chassis serial number",
            'local_context_data': "Local config context data overwrites all source contexts in the final rendered "
                                  "config context",
        }
        widgets = {
            'face': StaticSelect(),
            'status': StaticSelect(),
            'primary_ip4': StaticSelect(),
            'primary_ip6': StaticSelect(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk:

            # Compile list of choices for primary IPv4 and IPv6 addresses
            for family in [4, 6]:
                ip_choices = [(None, '---------')]

                # Gather PKs of all interfaces belonging to this Device or a peer VirtualChassis member
                interface_ids = self.instance.vc_interfaces(if_master=False).values_list('pk', flat=True)

                # Collect interface IPs
                interface_ips = IPAddress.objects.filter(
                    address__family=family,
                    assigned_object_type=ContentType.objects.get_for_model(Interface),
                    assigned_object_id__in=interface_ids
                ).prefetch_related('assigned_object')
                if interface_ips:
                    ip_list = [(ip.id, f'{ip.address} ({ip.assigned_object})') for ip in interface_ips]
                    ip_choices.append(('Interface IPs', ip_list))
                # Collect NAT IPs
                nat_ips = IPAddress.objects.prefetch_related('nat_inside').filter(
                    address__family=family,
                    nat_inside__assigned_object_type=ContentType.objects.get_for_model(Interface),
                    nat_inside__assigned_object_id__in=interface_ids
                ).prefetch_related('assigned_object')
                if nat_ips:
                    ip_list = [(ip.id, f'{ip.address} (NAT)') for ip in nat_ips]
                    ip_choices.append(('NAT IPs', ip_list))
                self.fields['primary_ip{}'.format(family)].choices = ip_choices

            # If editing an existing device, exclude it from the list of occupied rack units. This ensures that a device
            # can be flipped from one face to another.
            self.fields['position'].widget.add_query_param('exclude', self.instance.pk)

            # Limit platform by manufacturer
            self.fields['platform'].queryset = Platform.objects.filter(
                Q(manufacturer__isnull=True) | Q(manufacturer=self.instance.device_type.manufacturer)
            )

            # Disable rack assignment if this is a child device installed in a parent device
            if self.instance.device_type.is_child_device and hasattr(self.instance, 'parent_bay'):
                self.fields['site'].disabled = True
                self.fields['rack'].disabled = True
                self.initial['site'] = self.instance.parent_bay.device.site_id
                self.initial['rack'] = self.instance.parent_bay.device.rack_id

        else:

            # An object that doesn't exist yet can't have any IPs assigned to it
            self.fields['primary_ip4'].choices = []
            self.fields['primary_ip4'].widget.attrs['readonly'] = True
            self.fields['primary_ip6'].choices = []
            self.fields['primary_ip6'].widget.attrs['readonly'] = True

        # Rack position
        position = self.data.get('position') or self.initial.get('position')
        if position:
            self.fields['position'].widget.choices = [(position, f'U{position}')]


class BaseDeviceCSVForm(CustomFieldModelCSVForm):
    device_role = CSVModelChoiceField(
        queryset=DeviceRole.objects.all(),
        to_field_name='name',
        help_text='Assigned role'
    )
    tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Assigned tenant'
    )
    manufacturer = CSVModelChoiceField(
        queryset=Manufacturer.objects.all(),
        to_field_name='name',
        help_text='Device type manufacturer'
    )
    device_type = CSVModelChoiceField(
        queryset=DeviceType.objects.all(),
        to_field_name='model',
        help_text='Device type model'
    )
    platform = CSVModelChoiceField(
        queryset=Platform.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Assigned platform'
    )
    status = CSVChoiceField(
        choices=DeviceStatusChoices,
        help_text='Operational status'
    )
    virtual_chassis = CSVModelChoiceField(
        queryset=VirtualChassis.objects.all(),
        to_field_name='name',
        required=False,
        help_text='Virtual chassis'
    )
    cluster = CSVModelChoiceField(
        queryset=Cluster.objects.all(),
        to_field_name='name',
        required=False,
        help_text='Virtualization cluster'
    )

    class Meta:
        fields = []
        model = Device
        help_texts = {
            'vc_position': 'Virtual chassis position',
            'vc_priority': 'Virtual chassis priority',
        }

    def __init__(self, data=None, *args, **kwargs):
        super().__init__(data, *args, **kwargs)

        if data:

            # Limit device type queryset by manufacturer
            params = {f"manufacturer__{self.fields['manufacturer'].to_field_name}": data.get('manufacturer')}
            self.fields['device_type'].queryset = self.fields['device_type'].queryset.filter(**params)


class DeviceCSVForm(BaseDeviceCSVForm):
    site = CSVModelChoiceField(
        queryset=Site.objects.all(),
        to_field_name='name',
        help_text='Assigned site'
    )
    location = CSVModelChoiceField(
        queryset=Location.objects.all(),
        to_field_name='name',
        required=False,
        help_text="Assigned location (if any)"
    )
    rack = CSVModelChoiceField(
        queryset=Rack.objects.all(),
        to_field_name='name',
        required=False,
        help_text="Assigned rack (if any)"
    )
    face = CSVChoiceField(
        choices=DeviceFaceChoices,
        required=False,
        help_text='Mounted rack face'
    )

    class Meta(BaseDeviceCSVForm.Meta):
        fields = [
            'name', 'device_role', 'tenant', 'manufacturer', 'device_type', 'platform', 'serial', 'asset_tag', 'status',
            'site', 'location', 'rack', 'position', 'face', 'virtual_chassis', 'vc_position', 'vc_priority', 'cluster',
            'comments',
        ]

    def __init__(self, data=None, *args, **kwargs):
        super().__init__(data, *args, **kwargs)

        if data:

            # Limit location queryset by assigned site
            params = {f"site__{self.fields['site'].to_field_name}": data.get('site')}
            self.fields['location'].queryset = self.fields['location'].queryset.filter(**params)

            # Limit rack queryset by assigned site and group
            params = {
                f"site__{self.fields['site'].to_field_name}": data.get('site'),
                f"location__{self.fields['location'].to_field_name}": data.get('location'),
            }
            self.fields['rack'].queryset = self.fields['rack'].queryset.filter(**params)


class ChildDeviceCSVForm(BaseDeviceCSVForm):
    parent = CSVModelChoiceField(
        queryset=Device.objects.all(),
        to_field_name='name',
        help_text='Parent device'
    )
    device_bay = CSVModelChoiceField(
        queryset=DeviceBay.objects.all(),
        to_field_name='name',
        help_text='Device bay in which this device is installed'
    )

    class Meta(BaseDeviceCSVForm.Meta):
        fields = [
            'name', 'device_role', 'tenant', 'manufacturer', 'device_type', 'platform', 'serial', 'asset_tag', 'status',
            'parent', 'device_bay', 'virtual_chassis', 'vc_position', 'vc_priority', 'cluster', 'comments',
        ]

    def __init__(self, data=None, *args, **kwargs):
        super().__init__(data, *args, **kwargs)

        if data:

            # Limit device bay queryset by parent device
            params = {f"device__{self.fields['parent'].to_field_name}": data.get('parent')}
            self.fields['device_bay'].queryset = self.fields['device_bay'].queryset.filter(**params)

    def clean(self):
        super().clean()

        # Set parent_bay reverse relationship
        device_bay = self.cleaned_data.get('device_bay')
        if device_bay:
            self.instance.parent_bay = device_bay

        # Inherit site and rack from parent device
        parent = self.cleaned_data.get('parent')
        if parent:
            self.instance.site = parent.site
            self.instance.rack = parent.rack


class DeviceBulkEditForm(BootstrapMixin, AddRemoveTagsForm, CustomFieldModelBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=Device.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
    manufacturer = DynamicModelChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False
    )
    device_type = DynamicModelChoiceField(
        queryset=DeviceType.objects.all(),
        required=False,
        query_params={
            'manufacturer_id': '$manufacturer'
        }
    )
    device_role = DynamicModelChoiceField(
        queryset=DeviceRole.objects.all(),
        required=False
    )
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False
    )
    location = DynamicModelChoiceField(
        queryset=Location.objects.all(),
        required=False,
        query_params={
            'site_id': '$site'
        }
    )
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False
    )
    platform = DynamicModelChoiceField(
        queryset=Platform.objects.all(),
        required=False
    )
    status = forms.ChoiceField(
        choices=add_blank_choice(DeviceStatusChoices),
        required=False,
        widget=StaticSelect()
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


class DeviceFilterForm(BootstrapMixin, LocalConfigContextFilterForm, TenancyFilterForm, CustomFieldModelFilterForm):
    model = Device
    field_order = [
        'q', 'region_id', 'site_group_id', 'site_id', 'location_id', 'rack_id', 'status', 'role_id', 'tenant_group_id',
        'tenant_id', 'manufacturer_id', 'device_type_id', 'asset_tag', 'mac_address', 'has_primary_ip',
    ]
    field_groups = [
        ['q', 'tag'],
        ['region_id', 'site_group_id', 'site_id', 'location_id', 'rack_id'],
        ['status', 'role_id', 'asset_tag', 'mac_address'],
        ['manufacturer_id', 'device_type_id', 'platform_id'],
        ['tenant_group_id', 'tenant_id'],
        [
            'has_primary_ip', 'virtual_chassis_member', 'console_ports', 'console_server_ports', 'power_ports',
            'power_outlets', 'interfaces', 'pass_through_ports', 'local_context_data',
        ],
    ]
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': _('All Fields')}),
        label=_('Search')
    )
    region_id = DynamicModelMultipleChoiceField(
        queryset=Region.objects.all(),
        required=False,
        label=_('Region'),
        fetch_trigger='open'
    )
    site_group_id = DynamicModelMultipleChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False,
        label=_('Site group'),
        fetch_trigger='open'
    )
    site_id = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        query_params={
            'region_id': '$region_id',
            'group_id': '$site_group_id',
        },
        label=_('Site'),
        fetch_trigger='open'
    )
    location_id = DynamicModelMultipleChoiceField(
        queryset=Location.objects.all(),
        required=False,
        null_option='None',
        query_params={
            'site_id': '$site_id'
        },
        label=_('Location'),
        fetch_trigger='open'
    )
    rack_id = DynamicModelMultipleChoiceField(
        queryset=Rack.objects.all(),
        required=False,
        null_option='None',
        query_params={
            'site_id': '$site_id',
            'location_id': '$location_id',
        },
        label=_('Rack'),
        fetch_trigger='open'
    )
    role_id = DynamicModelMultipleChoiceField(
        queryset=DeviceRole.objects.all(),
        required=False,
        label=_('Role'),
        fetch_trigger='open'
    )
    manufacturer_id = DynamicModelMultipleChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False,
        label=_('Manufacturer'),
        fetch_trigger='open'
    )
    device_type_id = DynamicModelMultipleChoiceField(
        queryset=DeviceType.objects.all(),
        required=False,
        query_params={
            'manufacturer_id': '$manufacturer_id'
        },
        label=_('Model'),
        fetch_trigger='open'
    )
    platform_id = DynamicModelMultipleChoiceField(
        queryset=Platform.objects.all(),
        required=False,
        null_option='None',
        label=_('Platform'),
        fetch_trigger='open'
    )
    status = forms.MultipleChoiceField(
        choices=DeviceStatusChoices,
        required=False,
        widget=StaticSelectMultiple()
    )
    asset_tag = forms.CharField(
        required=False
    )
    mac_address = forms.CharField(
        required=False,
        label='MAC address'
    )
    has_primary_ip = forms.NullBooleanField(
        required=False,
        label='Has a primary IP',
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    virtual_chassis_member = forms.NullBooleanField(
        required=False,
        label='Virtual chassis member',
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    console_ports = forms.NullBooleanField(
        required=False,
        label='Has console ports',
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    console_server_ports = forms.NullBooleanField(
        required=False,
        label='Has console server ports',
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    power_ports = forms.NullBooleanField(
        required=False,
        label='Has power ports',
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    power_outlets = forms.NullBooleanField(
        required=False,
        label='Has power outlets',
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    interfaces = forms.NullBooleanField(
        required=False,
        label='Has interfaces',
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    pass_through_ports = forms.NullBooleanField(
        required=False,
        label='Has pass-through ports',
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    tag = TagFilterField(model)


#
# Device components
#

class ComponentCreateForm(BootstrapMixin, CustomFieldsMixin, ComponentForm):
    """
    Base form for the creation of device components (models subclassed from ComponentModel).
    """
    device = DynamicModelChoiceField(
        queryset=Device.objects.all()
    )
    description = forms.CharField(
        max_length=200,
        required=False
    )
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )


class DeviceBulkAddComponentForm(BootstrapMixin, CustomFieldsMixin, ComponentForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=Device.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
    description = forms.CharField(
        max_length=100,
        required=False
    )
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )


#
# Console ports
#


class ConsolePortFilterForm(DeviceComponentFilterForm):
    model = ConsolePort
    field_groups = [
        ['q', 'tag'],
        ['name', 'label', 'type', 'speed'],
        ['region_id', 'site_group_id', 'site_id', 'location_id', 'device_id'],
    ]
    type = forms.MultipleChoiceField(
        choices=ConsolePortTypeChoices,
        required=False,
        widget=StaticSelectMultiple()
    )
    speed = forms.MultipleChoiceField(
        choices=ConsolePortSpeedChoices,
        required=False,
        widget=StaticSelectMultiple()
    )
    tag = TagFilterField(model)


class ConsolePortForm(BootstrapMixin, CustomFieldModelForm):
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = ConsolePort
        fields = [
            'device', 'name', 'label', 'type', 'speed', 'mark_connected', 'description', 'tags',
        ]
        widgets = {
            'device': forms.HiddenInput(),
        }


class ConsolePortCreateForm(ComponentCreateForm):
    model = ConsolePort
    type = forms.ChoiceField(
        choices=add_blank_choice(ConsolePortTypeChoices),
        required=False,
        widget=StaticSelect()
    )
    speed = forms.ChoiceField(
        choices=add_blank_choice(ConsolePortSpeedChoices),
        required=False,
        widget=StaticSelect()
    )
    field_order = ('device', 'name_pattern', 'label_pattern', 'type', 'speed', 'mark_connected', 'description', 'tags')


class ConsolePortBulkCreateForm(
    form_from_model(ConsolePort, ['type', 'speed', 'mark_connected']),
    DeviceBulkAddComponentForm
):
    model = ConsolePort
    field_order = ('name_pattern', 'label_pattern', 'type', 'mark_connected', 'description', 'tags')


class ConsolePortBulkEditForm(
    form_from_model(ConsolePort, ['label', 'type', 'speed', 'mark_connected', 'description']),
    BootstrapMixin,
    AddRemoveTagsForm,
    CustomFieldModelBulkEditForm
):
    pk = forms.ModelMultipleChoiceField(
        queryset=ConsolePort.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
    mark_connected = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect
    )

    class Meta:
        nullable_fields = ['label', 'description']


class ConsolePortCSVForm(CustomFieldModelCSVForm):
    device = CSVModelChoiceField(
        queryset=Device.objects.all(),
        to_field_name='name'
    )
    type = CSVChoiceField(
        choices=ConsolePortTypeChoices,
        required=False,
        help_text='Port type'
    )
    speed = CSVTypedChoiceField(
        choices=ConsolePortSpeedChoices,
        coerce=int,
        empty_value=None,
        required=False,
        help_text='Port speed in bps'
    )

    class Meta:
        model = ConsolePort
        fields = ('device', 'name', 'label', 'type', 'speed', 'mark_connected', 'description')


#
# Console server ports
#


class ConsoleServerPortFilterForm(DeviceComponentFilterForm):
    model = ConsoleServerPort
    field_groups = [
        ['q', 'tag'],
        ['name', 'label', 'type', 'speed'],
        ['region_id', 'site_group_id', 'site_id', 'location_id', 'device_id'],
    ]
    type = forms.MultipleChoiceField(
        choices=ConsolePortTypeChoices,
        required=False,
        widget=StaticSelectMultiple()
    )
    speed = forms.MultipleChoiceField(
        choices=ConsolePortSpeedChoices,
        required=False,
        widget=StaticSelectMultiple()
    )
    tag = TagFilterField(model)


class ConsoleServerPortForm(BootstrapMixin, CustomFieldModelForm):
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = ConsoleServerPort
        fields = [
            'device', 'name', 'label', 'type', 'speed', 'mark_connected', 'description', 'tags',
        ]
        widgets = {
            'device': forms.HiddenInput(),
        }


class ConsoleServerPortCreateForm(ComponentCreateForm):
    model = ConsoleServerPort
    type = forms.ChoiceField(
        choices=add_blank_choice(ConsolePortTypeChoices),
        required=False,
        widget=StaticSelect()
    )
    speed = forms.ChoiceField(
        choices=add_blank_choice(ConsolePortSpeedChoices),
        required=False,
        widget=StaticSelect()
    )
    field_order = ('device', 'name_pattern', 'label_pattern', 'type', 'speed', 'mark_connected', 'description', 'tags')


class ConsoleServerPortBulkCreateForm(
    form_from_model(ConsoleServerPort, ['type', 'speed', 'mark_connected']),
    DeviceBulkAddComponentForm
):
    model = ConsoleServerPort
    field_order = ('name_pattern', 'label_pattern', 'type', 'speed', 'description', 'tags')


class ConsoleServerPortBulkEditForm(
    form_from_model(ConsoleServerPort, ['label', 'type', 'speed', 'mark_connected', 'description']),
    BootstrapMixin,
    AddRemoveTagsForm,
    CustomFieldModelBulkEditForm
):
    pk = forms.ModelMultipleChoiceField(
        queryset=ConsoleServerPort.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
    mark_connected = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect
    )

    class Meta:
        nullable_fields = ['label', 'description']


class ConsoleServerPortCSVForm(CustomFieldModelCSVForm):
    device = CSVModelChoiceField(
        queryset=Device.objects.all(),
        to_field_name='name'
    )
    type = CSVChoiceField(
        choices=ConsolePortTypeChoices,
        required=False,
        help_text='Port type'
    )
    speed = CSVTypedChoiceField(
        choices=ConsolePortSpeedChoices,
        coerce=int,
        empty_value=None,
        required=False,
        help_text='Port speed in bps'
    )

    class Meta:
        model = ConsoleServerPort
        fields = ('device', 'name', 'label', 'type', 'speed', 'mark_connected', 'description')


#
# Power ports
#


class PowerPortFilterForm(DeviceComponentFilterForm):
    model = PowerPort
    field_groups = [
        ['q', 'tag'],
        ['name', 'label', 'type'],
        ['region_id', 'site_group_id', 'site_id', 'location_id', 'device_id'],
    ]
    type = forms.MultipleChoiceField(
        choices=PowerPortTypeChoices,
        required=False,
        widget=StaticSelectMultiple()
    )
    tag = TagFilterField(model)


class PowerPortForm(BootstrapMixin, CustomFieldModelForm):
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = PowerPort
        fields = [
            'device', 'name', 'label', 'type', 'maximum_draw', 'allocated_draw', 'mark_connected', 'description',
            'tags',
        ]
        widgets = {
            'device': forms.HiddenInput(),
        }


class PowerPortCreateForm(ComponentCreateForm):
    model = PowerPort
    type = forms.ChoiceField(
        choices=add_blank_choice(PowerPortTypeChoices),
        required=False,
        widget=StaticSelect()
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
    field_order = (
        'device', 'name_pattern', 'label_pattern', 'type', 'maximum_draw', 'allocated_draw', 'mark_connected',
        'description', 'tags',
    )


class PowerPortBulkCreateForm(
    form_from_model(PowerPort, ['type', 'maximum_draw', 'allocated_draw', 'mark_connected']),
    DeviceBulkAddComponentForm
):
    model = PowerPort
    field_order = ('name_pattern', 'label_pattern', 'type', 'maximum_draw', 'allocated_draw', 'description', 'tags')


class PowerPortBulkEditForm(
    form_from_model(PowerPort, ['label', 'type', 'maximum_draw', 'allocated_draw', 'mark_connected', 'description']),
    BootstrapMixin,
    AddRemoveTagsForm,
    CustomFieldModelBulkEditForm
):
    pk = forms.ModelMultipleChoiceField(
        queryset=PowerPort.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
    mark_connected = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect
    )

    class Meta:
        nullable_fields = ['label', 'description']


class PowerPortCSVForm(CustomFieldModelCSVForm):
    device = CSVModelChoiceField(
        queryset=Device.objects.all(),
        to_field_name='name'
    )
    type = CSVChoiceField(
        choices=PowerPortTypeChoices,
        required=False,
        help_text='Port type'
    )

    class Meta:
        model = PowerPort
        fields = (
            'device', 'name', 'label', 'type', 'mark_connected', 'maximum_draw', 'allocated_draw', 'description',
        )


#
# Power outlets
#


class PowerOutletFilterForm(DeviceComponentFilterForm):
    model = PowerOutlet
    field_groups = [
        ['q', 'tag'],
        ['name', 'label', 'type'],
        ['region_id', 'site_group_id', 'site_id', 'location_id', 'device_id'],
    ]
    type = forms.MultipleChoiceField(
        choices=PowerOutletTypeChoices,
        required=False,
        widget=StaticSelectMultiple()
    )
    tag = TagFilterField(model)


class PowerOutletForm(BootstrapMixin, CustomFieldModelForm):
    power_port = forms.ModelChoiceField(
        queryset=PowerPort.objects.all(),
        required=False
    )
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = PowerOutlet
        fields = [
            'device', 'name', 'label', 'type', 'power_port', 'feed_leg', 'mark_connected', 'description', 'tags',
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


class PowerOutletCreateForm(ComponentCreateForm):
    model = PowerOutlet
    type = forms.ChoiceField(
        choices=add_blank_choice(PowerOutletTypeChoices),
        required=False,
        widget=StaticSelect()
    )
    power_port = forms.ModelChoiceField(
        queryset=PowerPort.objects.all(),
        required=False
    )
    feed_leg = forms.ChoiceField(
        choices=add_blank_choice(PowerOutletFeedLegChoices),
        required=False
    )
    field_order = (
        'device', 'name_pattern', 'label_pattern', 'type', 'power_port', 'feed_leg', 'mark_connected', 'description',
        'tags',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Limit power_port queryset to PowerPorts which belong to the parent Device
        device = Device.objects.get(
            pk=self.initial.get('device') or self.data.get('device')
        )
        self.fields['power_port'].queryset = PowerPort.objects.filter(device=device)


class PowerOutletBulkCreateForm(
    form_from_model(PowerOutlet, ['type', 'feed_leg', 'mark_connected']),
    DeviceBulkAddComponentForm
):
    model = PowerOutlet
    field_order = ('name_pattern', 'label_pattern', 'type', 'feed_leg', 'description', 'tags')


class PowerOutletBulkEditForm(
    form_from_model(PowerOutlet, ['label', 'type', 'feed_leg', 'power_port', 'mark_connected', 'description']),
    BootstrapMixin,
    AddRemoveTagsForm,
    CustomFieldModelBulkEditForm
):
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
    mark_connected = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect
    )

    class Meta:
        nullable_fields = ['label', 'type', 'feed_leg', 'power_port', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Limit power_port queryset to PowerPorts which belong to the parent Device
        if 'device' in self.initial:
            device = Device.objects.filter(pk=self.initial['device']).first()
            self.fields['power_port'].queryset = PowerPort.objects.filter(device=device)
        else:
            self.fields['power_port'].choices = ()
            self.fields['power_port'].widget.attrs['disabled'] = True


class PowerOutletCSVForm(CustomFieldModelCSVForm):
    device = CSVModelChoiceField(
        queryset=Device.objects.all(),
        to_field_name='name'
    )
    type = CSVChoiceField(
        choices=PowerOutletTypeChoices,
        required=False,
        help_text='Outlet type'
    )
    power_port = CSVModelChoiceField(
        queryset=PowerPort.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Local power port which feeds this outlet'
    )
    feed_leg = CSVChoiceField(
        choices=PowerOutletFeedLegChoices,
        required=False,
        help_text='Electrical phase (for three-phase circuits)'
    )

    class Meta:
        model = PowerOutlet
        fields = ('device', 'name', 'label', 'type', 'mark_connected', 'power_port', 'feed_leg', 'description')

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


#
# Interfaces
#


class InterfaceFilterForm(DeviceComponentFilterForm):
    model = Interface
    field_groups = [
        ['q', 'tag'],
        ['name', 'label', 'type', 'enabled', 'mgmt_only', 'mac_address'],
        ['region_id', 'site_group_id', 'site_id', 'location_id', 'device_id'],
    ]
    type = forms.MultipleChoiceField(
        choices=InterfaceTypeChoices,
        required=False,
        widget=StaticSelectMultiple()
    )
    enabled = forms.NullBooleanField(
        required=False,
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    mgmt_only = forms.NullBooleanField(
        required=False,
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    mac_address = forms.CharField(
        required=False,
        label='MAC address'
    )
    tag = TagFilterField(model)


class InterfaceForm(BootstrapMixin, InterfaceCommonForm, CustomFieldModelForm):
    parent = DynamicModelChoiceField(
        queryset=Interface.objects.all(),
        required=False,
        label='Parent interface'
    )
    lag = DynamicModelChoiceField(
        queryset=Interface.objects.all(),
        required=False,
        label='LAG interface',
        query_params={
            'type': 'lag',
        }
    )
    vlan_group = DynamicModelChoiceField(
        queryset=VLANGroup.objects.all(),
        required=False,
        label='VLAN group'
    )
    untagged_vlan = DynamicModelChoiceField(
        queryset=VLAN.objects.all(),
        required=False,
        label='Untagged VLAN',
        query_params={
            'group_id': '$vlan_group',
        }
    )
    tagged_vlans = DynamicModelMultipleChoiceField(
        queryset=VLAN.objects.all(),
        required=False,
        label='Tagged VLANs',
        query_params={
            'group_id': '$vlan_group',
        }
    )
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = Interface
        fields = [
            'device', 'name', 'label', 'type', 'enabled', 'parent', 'lag', 'mac_address', 'mtu', 'mgmt_only',
            'mark_connected', 'description', 'mode', 'untagged_vlan', 'tagged_vlans', 'tags',
        ]
        widgets = {
            'device': forms.HiddenInput(),
            'type': StaticSelect(),
            'mode': StaticSelect(),
        }
        labels = {
            'mode': '802.1Q Mode',
        }
        help_texts = {
            'mode': INTERFACE_MODE_HELP_TEXT,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        device = Device.objects.get(pk=self.data['device']) if self.is_bound else self.instance.device

        # Restrict parent/LAG interface assignment by device/VC
        self.fields['parent'].widget.add_query_param('device_id', device.pk)
        if device.virtual_chassis and device.virtual_chassis.master:
            # Get available LAG interfaces by VirtualChassis master
            self.fields['lag'].widget.add_query_param('device_id', device.virtual_chassis.master.pk)
        else:
            self.fields['lag'].widget.add_query_param('device_id', device.pk)

        # Limit VLAN choices by device
        self.fields['untagged_vlan'].widget.add_query_param('available_on_device', device.pk)
        self.fields['tagged_vlans'].widget.add_query_param('available_on_device', device.pk)


class InterfaceCreateForm(ComponentCreateForm, InterfaceCommonForm):
    model = Interface
    type = forms.ChoiceField(
        choices=InterfaceTypeChoices,
        widget=StaticSelect(),
    )
    enabled = forms.BooleanField(
        required=False,
        initial=True
    )
    parent = DynamicModelChoiceField(
        queryset=Interface.objects.all(),
        required=False,
        query_params={
            'device_id': '$device',
        }
    )
    lag = DynamicModelChoiceField(
        queryset=Interface.objects.all(),
        required=False,
        query_params={
            'device_id': '$device',
            'type': 'lag',
        }
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
    mode = forms.ChoiceField(
        choices=add_blank_choice(InterfaceModeChoices),
        required=False,
        widget=StaticSelect(),
    )
    untagged_vlan = DynamicModelChoiceField(
        queryset=VLAN.objects.all(),
        required=False
    )
    tagged_vlans = DynamicModelMultipleChoiceField(
        queryset=VLAN.objects.all(),
        required=False
    )
    field_order = (
        'device', 'name_pattern', 'label_pattern', 'type', 'enabled', 'parent', 'lag', 'mtu', 'mac_address',
        'description', 'mgmt_only', 'mark_connected', 'mode', 'untagged_vlan', 'tagged_vlans', 'tags'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Limit VLAN choices by device
        device_id = self.initial.get('device') or self.data.get('device')
        self.fields['untagged_vlan'].widget.add_query_param('available_on_device', device_id)
        self.fields['tagged_vlans'].widget.add_query_param('available_on_device', device_id)


class InterfaceBulkCreateForm(
    form_from_model(Interface, ['type', 'enabled', 'mtu', 'mgmt_only', 'mark_connected']),
    DeviceBulkAddComponentForm
):
    model = Interface
    field_order = (
        'name_pattern', 'label_pattern', 'type', 'enabled', 'mtu', 'mgmt_only', 'mark_connected', 'description', 'tags',
    )


class InterfaceBulkEditForm(
    form_from_model(Interface, [
        'label', 'type', 'parent', 'lag', 'mac_address', 'mtu', 'mgmt_only', 'mark_connected', 'description', 'mode',
    ]),
    BootstrapMixin,
    AddRemoveTagsForm,
    CustomFieldModelBulkEditForm
):
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
    enabled = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect
    )
    parent = DynamicModelChoiceField(
        queryset=Interface.objects.all(),
        required=False
    )
    lag = DynamicModelChoiceField(
        queryset=Interface.objects.all(),
        required=False,
        query_params={
            'type': 'lag',
        }
    )
    mgmt_only = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect,
        label='Management only'
    )
    mark_connected = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect
    )
    untagged_vlan = DynamicModelChoiceField(
        queryset=VLAN.objects.all(),
        required=False
    )
    tagged_vlans = DynamicModelMultipleChoiceField(
        queryset=VLAN.objects.all(),
        required=False
    )

    class Meta:
        nullable_fields = [
            'label', 'parent', 'lag', 'mac_address', 'mtu', 'description', 'mode', 'untagged_vlan', 'tagged_vlans'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'device' in self.initial:
            device = Device.objects.filter(pk=self.initial['device']).first()

            # Restrict parent/LAG interface assignment by device
            self.fields['parent'].widget.add_query_param('device_id', device.pk)
            self.fields['lag'].widget.add_query_param('device_id', device.pk)

            # Limit VLAN choices by device
            self.fields['untagged_vlan'].widget.add_query_param('available_on_device', device.pk)
            self.fields['tagged_vlans'].widget.add_query_param('available_on_device', device.pk)

        else:
            # See #4523
            if 'pk' in self.initial:
                site = None
                interfaces = Interface.objects.filter(pk__in=self.initial['pk']).prefetch_related('device__site')

                # Check interface sites.  First interface should set site, further interfaces will either continue the
                # loop or reset back to no site and break the loop.
                for interface in interfaces:
                    if site is None:
                        site = interface.device.site
                    elif interface.device.site is not site:
                        site = None
                        break

                if site is not None:
                    self.fields['untagged_vlan'].widget.add_query_param('site_id', site.pk)
                    self.fields['tagged_vlans'].widget.add_query_param('site_id', site.pk)

            self.fields['parent'].choices = ()
            self.fields['parent'].widget.attrs['disabled'] = True
            self.fields['lag'].choices = ()
            self.fields['lag'].widget.attrs['disabled'] = True

    def clean(self):
        super().clean()

        # Untagged interfaces cannot be assigned tagged VLANs
        if self.cleaned_data['mode'] == InterfaceModeChoices.MODE_ACCESS and self.cleaned_data['tagged_vlans']:
            raise forms.ValidationError({
                'mode': "An access interface cannot have tagged VLANs assigned."
            })

        # Remove all tagged VLAN assignments from "tagged all" interfaces
        elif self.cleaned_data['mode'] == InterfaceModeChoices.MODE_TAGGED_ALL:
            self.cleaned_data['tagged_vlans'] = []


class InterfaceCSVForm(CustomFieldModelCSVForm):
    device = CSVModelChoiceField(
        queryset=Device.objects.all(),
        to_field_name='name'
    )
    parent = CSVModelChoiceField(
        queryset=Interface.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Parent interface'
    )
    lag = CSVModelChoiceField(
        queryset=Interface.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Parent LAG interface'
    )
    type = CSVChoiceField(
        choices=InterfaceTypeChoices,
        help_text='Physical medium'
    )
    mode = CSVChoiceField(
        choices=InterfaceModeChoices,
        required=False,
        help_text='IEEE 802.1Q operational mode (for L2 interfaces)'
    )

    class Meta:
        model = Interface
        fields = (
            'device', 'name', 'label', 'parent', 'lag', 'type', 'enabled', 'mark_connected', 'mac_address', 'mtu',
            'mgmt_only', 'description', 'mode',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Limit LAG choices to interfaces belonging to this device (or virtual chassis)
        device = None
        if self.is_bound and 'device' in self.data:
            try:
                device = self.fields['device'].to_python(self.data['device'])
            except forms.ValidationError:
                pass
        if device and device.virtual_chassis:
            self.fields['lag'].queryset = Interface.objects.filter(
                Q(device=device) | Q(device__virtual_chassis=device.virtual_chassis),
                type=InterfaceTypeChoices.TYPE_LAG
            )
            self.fields['parent'].queryset = Interface.objects.filter(
                Q(device=device) | Q(device__virtual_chassis=device.virtual_chassis)
            )
        elif device:
            self.fields['lag'].queryset = Interface.objects.filter(
                device=device,
                type=InterfaceTypeChoices.TYPE_LAG
            )
            self.fields['parent'].queryset = Interface.objects.filter(device=device)
        else:
            self.fields['lag'].queryset = Interface.objects.none()
            self.fields['parent'].queryset = Interface.objects.none()

    def clean_enabled(self):
        # Make sure enabled is True when it's not included in the uploaded data
        if 'enabled' not in self.data:
            return True
        else:
            return self.cleaned_data['enabled']


#
# Front pass-through ports
#

class FrontPortFilterForm(DeviceComponentFilterForm):
    field_groups = [
        ['q', 'tag'],
        ['name', 'label', 'type', 'color'],
        ['region_id', 'site_group_id', 'site_id', 'location_id', 'device_id'],
    ]
    model = FrontPort
    type = forms.MultipleChoiceField(
        choices=PortTypeChoices,
        required=False,
        widget=StaticSelectMultiple()
    )
    color = ColorField(
        required=False
    )
    tag = TagFilterField(model)


class FrontPortForm(BootstrapMixin, CustomFieldModelForm):
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = FrontPort
        fields = [
            'device', 'name', 'label', 'type', 'color', 'rear_port', 'rear_port_position', 'mark_connected',
            'description', 'tags',
        ]
        widgets = {
            'device': forms.HiddenInput(),
            'type': StaticSelect(),
            'rear_port': StaticSelect(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Limit RearPort choices to the local device
        if hasattr(self.instance, 'device'):
            self.fields['rear_port'].queryset = self.fields['rear_port'].queryset.filter(
                device=self.instance.device
            )


# TODO: Merge with FrontPortTemplateCreateForm to remove duplicate logic
class FrontPortCreateForm(ComponentCreateForm):
    model = FrontPort
    type = forms.ChoiceField(
        choices=PortTypeChoices,
        widget=StaticSelect(),
    )
    color = ColorField(
        required=False
    )
    rear_port_set = forms.MultipleChoiceField(
        choices=[],
        label='Rear ports',
        help_text='Select one rear port assignment for each front port being created.',
    )
    field_order = (
        'device', 'name_pattern', 'label_pattern', 'type', 'color', 'rear_port_set', 'mark_connected', 'description',
        'tags',
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
        super().clean()

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


# class FrontPortBulkCreateForm(
#     form_from_model(FrontPort, ['label', 'type', 'description', 'tags']),
#     DeviceBulkAddComponentForm
# ):
#     pass


class FrontPortBulkEditForm(
    form_from_model(FrontPort, ['label', 'type', 'color', 'mark_connected', 'description']),
    BootstrapMixin,
    AddRemoveTagsForm,
    CustomFieldModelBulkEditForm
):
    pk = forms.ModelMultipleChoiceField(
        queryset=FrontPort.objects.all(),
        widget=forms.MultipleHiddenInput()
    )

    class Meta:
        nullable_fields = ['label', 'description']


class FrontPortCSVForm(CustomFieldModelCSVForm):
    device = CSVModelChoiceField(
        queryset=Device.objects.all(),
        to_field_name='name'
    )
    rear_port = CSVModelChoiceField(
        queryset=RearPort.objects.all(),
        to_field_name='name',
        help_text='Corresponding rear port'
    )
    type = CSVChoiceField(
        choices=PortTypeChoices,
        help_text='Physical medium classification'
    )

    class Meta:
        model = FrontPort
        fields = (
            'device', 'name', 'label', 'type', 'color', 'mark_connected', 'rear_port', 'rear_port_position',
            'description',
        )
        help_texts = {
            'rear_port_position': 'Mapped position on corresponding rear port',
        }

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


#
# Rear pass-through ports
#

class RearPortFilterForm(DeviceComponentFilterForm):
    model = RearPort
    field_groups = [
        ['q', 'tag'],
        ['name', 'label', 'type', 'color'],
        ['region_id', 'site_group_id', 'site_id', 'location_id', 'device_id'],
    ]
    type = forms.MultipleChoiceField(
        choices=PortTypeChoices,
        required=False,
        widget=StaticSelectMultiple()
    )
    color = ColorField(
        required=False
    )
    tag = TagFilterField(model)


class RearPortForm(BootstrapMixin, CustomFieldModelForm):
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = RearPort
        fields = [
            'device', 'name', 'label', 'type', 'color', 'positions', 'mark_connected', 'description', 'tags',
        ]
        widgets = {
            'device': forms.HiddenInput(),
            'type': StaticSelect(),
        }


class RearPortCreateForm(ComponentCreateForm):
    model = RearPort
    type = forms.ChoiceField(
        choices=PortTypeChoices,
        widget=StaticSelect(),
    )
    color = ColorField(
        required=False
    )
    positions = forms.IntegerField(
        min_value=REARPORT_POSITIONS_MIN,
        max_value=REARPORT_POSITIONS_MAX,
        initial=1,
        help_text='The number of front ports which may be mapped to each rear port'
    )
    field_order = (
        'device', 'name_pattern', 'label_pattern', 'type', 'color', 'positions', 'mark_connected', 'description',
        'tags',
    )


class RearPortBulkCreateForm(
    form_from_model(RearPort, ['type', 'color', 'positions', 'mark_connected']),
    DeviceBulkAddComponentForm
):
    model = RearPort
    field_order = ('name_pattern', 'label_pattern', 'type', 'positions', 'mark_connected', 'description', 'tags')


class RearPortBulkEditForm(
    form_from_model(RearPort, ['label', 'type', 'color', 'mark_connected', 'description']),
    BootstrapMixin,
    AddRemoveTagsForm,
    CustomFieldModelBulkEditForm
):
    pk = forms.ModelMultipleChoiceField(
        queryset=RearPort.objects.all(),
        widget=forms.MultipleHiddenInput()
    )

    class Meta:
        nullable_fields = ['label', 'description']


class RearPortCSVForm(CustomFieldModelCSVForm):
    device = CSVModelChoiceField(
        queryset=Device.objects.all(),
        to_field_name='name'
    )
    type = CSVChoiceField(
        help_text='Physical medium classification',
        choices=PortTypeChoices,
    )

    class Meta:
        model = RearPort
        fields = ('device', 'name', 'label', 'type', 'color', 'mark_connected', 'positions', 'description')
        help_texts = {
            'positions': 'Number of front ports which may be mapped'
        }


#
# Device bays
#

class DeviceBayFilterForm(DeviceComponentFilterForm):
    model = DeviceBay
    field_groups = [
        ['q', 'tag'],
        ['name', 'label'],
        ['region_id', 'site_group_id', 'site_id', 'location_id', 'device_id'],
    ]
    tag = TagFilterField(model)


class DeviceBayForm(BootstrapMixin, CustomFieldModelForm):
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = DeviceBay
        fields = [
            'device', 'name', 'label', 'description', 'tags',
        ]
        widgets = {
            'device': forms.HiddenInput(),
        }


class DeviceBayCreateForm(ComponentCreateForm):
    model = DeviceBay
    field_order = ('device', 'name_pattern', 'label_pattern', 'description', 'tags')


class PopulateDeviceBayForm(BootstrapMixin, forms.Form):
    installed_device = forms.ModelChoiceField(
        queryset=Device.objects.all(),
        label='Child Device',
        help_text="Child devices must first be created and assigned to the site/rack of the parent device.",
        widget=StaticSelect(),
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


class DeviceBayBulkCreateForm(DeviceBulkAddComponentForm):
    model = DeviceBay
    field_order = ('name_pattern', 'label_pattern', 'description', 'tags')


class DeviceBayBulkEditForm(
    form_from_model(DeviceBay, ['label', 'description']),
    BootstrapMixin,
    AddRemoveTagsForm,
    CustomFieldModelBulkEditForm
):
    pk = forms.ModelMultipleChoiceField(
        queryset=DeviceBay.objects.all(),
        widget=forms.MultipleHiddenInput()
    )

    class Meta:
        nullable_fields = ['label', 'description']


class DeviceBayCSVForm(CustomFieldModelCSVForm):
    device = CSVModelChoiceField(
        queryset=Device.objects.all(),
        to_field_name='name'
    )
    installed_device = CSVModelChoiceField(
        queryset=Device.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Child device installed within this bay',
        error_messages={
            'invalid_choice': 'Child device not found.',
        }
    )

    class Meta:
        model = DeviceBay
        fields = ('device', 'name', 'label', 'installed_device', 'description')

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


#
# Inventory items
#

class InventoryItemForm(BootstrapMixin, CustomFieldModelForm):
    device = DynamicModelChoiceField(
        queryset=Device.objects.all()
    )
    parent = DynamicModelChoiceField(
        queryset=InventoryItem.objects.all(),
        required=False,
        query_params={
            'device_id': '$device'
        }
    )
    manufacturer = DynamicModelChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False
    )
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = InventoryItem
        fields = [
            'device', 'parent', 'name', 'label', 'manufacturer', 'part_id', 'serial', 'asset_tag', 'description',
            'tags',
        ]


class InventoryItemCreateForm(ComponentCreateForm):
    model = InventoryItem
    manufacturer = DynamicModelChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False
    )
    parent = DynamicModelChoiceField(
        queryset=InventoryItem.objects.all(),
        required=False,
        query_params={
            'device_id': '$device'
        }
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
    field_order = (
        'device', 'parent', 'name_pattern', 'label_pattern', 'manufacturer', 'part_id', 'serial', 'asset_tag',
        'description', 'tags',
    )


class InventoryItemCSVForm(CustomFieldModelCSVForm):
    device = CSVModelChoiceField(
        queryset=Device.objects.all(),
        to_field_name='name'
    )
    manufacturer = CSVModelChoiceField(
        queryset=Manufacturer.objects.all(),
        to_field_name='name',
        required=False
    )
    parent = CSVModelChoiceField(
        queryset=Device.objects.all(),
        to_field_name='name',
        required=False,
        help_text='Parent inventory item'
    )

    class Meta:
        model = InventoryItem
        fields = (
            'device', 'name', 'label', 'manufacturer', 'part_id', 'serial', 'asset_tag', 'discovered', 'description',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Limit parent choices to inventory items belonging to this device
        device = None
        if self.is_bound and 'device' in self.data:
            try:
                device = self.fields['device'].to_python(self.data['device'])
            except forms.ValidationError:
                pass
        if device:
            self.fields['parent'].queryset = InventoryItem.objects.filter(device=device)
        else:
            self.fields['parent'].queryset = InventoryItem.objects.none()


class InventoryItemBulkCreateForm(
    form_from_model(InventoryItem, ['manufacturer', 'part_id', 'serial', 'asset_tag', 'discovered']),
    DeviceBulkAddComponentForm
):
    model = InventoryItem
    field_order = (
        'name_pattern', 'label_pattern', 'manufacturer', 'part_id', 'serial', 'asset_tag', 'discovered', 'description',
        'tags',
    )


class InventoryItemBulkEditForm(
    form_from_model(InventoryItem, ['label', 'manufacturer', 'part_id', 'description']),
    BootstrapMixin,
    AddRemoveTagsForm,
    CustomFieldModelBulkEditForm
):
    pk = forms.ModelMultipleChoiceField(
        queryset=InventoryItem.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
    manufacturer = DynamicModelChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False
    )

    class Meta:
        nullable_fields = ['label', 'manufacturer', 'part_id', 'description']


class InventoryItemFilterForm(DeviceComponentFilterForm):
    model = InventoryItem
    field_groups = [
        ['q', 'tag'],
        ['name', 'label', 'manufacturer_id', 'serial', 'asset_tag', 'discovered'],
        ['region_id', 'site_group_id', 'site_id', 'location_id', 'device_id'],
    ]
    manufacturer_id = DynamicModelMultipleChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False,
        label=_('Manufacturer'),
        fetch_trigger='open'
    )
    serial = forms.CharField(
        required=False
    )
    asset_tag = forms.CharField(
        required=False
    )
    discovered = forms.NullBooleanField(
        required=False,
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    tag = TagFilterField(model)


#
# Cables
#

class ConnectCableToDeviceForm(BootstrapMixin, CustomFieldModelForm):
    """
    Base form for connecting a Cable to a Device component
    """
    termination_b_region = DynamicModelChoiceField(
        queryset=Region.objects.all(),
        label='Region',
        required=False
    )
    termination_b_site_group = DynamicModelChoiceField(
        queryset=SiteGroup.objects.all(),
        label='Site group',
        required=False
    )
    termination_b_site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        label='Site',
        required=False,
        query_params={
            'region_id': '$termination_b_region',
            'group_id': '$termination_b_site_group',
        }
    )
    termination_b_location = DynamicModelChoiceField(
        queryset=Location.objects.all(),
        label='Location',
        required=False,
        null_option='None',
        query_params={
            'site_id': '$termination_b_site'
        }
    )
    termination_b_rack = DynamicModelChoiceField(
        queryset=Rack.objects.all(),
        label='Rack',
        required=False,
        null_option='None',
        query_params={
            'site_id': '$termination_b_site',
            'location_id': '$termination_b_location',
        }
    )
    termination_b_device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        label='Device',
        required=False,
        query_params={
            'site_id': '$termination_b_site',
            'location_id': '$termination_b_location',
            'rack_id': '$termination_b_rack',
        }
    )
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = Cable
        fields = [
            'termination_b_region', 'termination_b_site', 'termination_b_rack', 'termination_b_device',
            'termination_b_id', 'type', 'status', 'label', 'color', 'length', 'length_unit', 'tags',
        ]
        widgets = {
            'status': StaticSelect,
            'type': StaticSelect,
            'length_unit': StaticSelect,
        }

    def clean_termination_b_id(self):
        # Return the PK rather than the object
        return getattr(self.cleaned_data['termination_b_id'], 'pk', None)


class ConnectCableToConsolePortForm(ConnectCableToDeviceForm):
    termination_b_id = DynamicModelChoiceField(
        queryset=ConsolePort.objects.all(),
        label='Name',
        disabled_indicator='_occupied',
        query_params={
            'device_id': '$termination_b_device'
        }
    )


class ConnectCableToConsoleServerPortForm(ConnectCableToDeviceForm):
    termination_b_id = DynamicModelChoiceField(
        queryset=ConsoleServerPort.objects.all(),
        label='Name',
        disabled_indicator='_occupied',
        query_params={
            'device_id': '$termination_b_device'
        }
    )


class ConnectCableToPowerPortForm(ConnectCableToDeviceForm):
    termination_b_id = DynamicModelChoiceField(
        queryset=PowerPort.objects.all(),
        label='Name',
        disabled_indicator='_occupied',
        query_params={
            'device_id': '$termination_b_device'
        }
    )


class ConnectCableToPowerOutletForm(ConnectCableToDeviceForm):
    termination_b_id = DynamicModelChoiceField(
        queryset=PowerOutlet.objects.all(),
        label='Name',
        disabled_indicator='_occupied',
        query_params={
            'device_id': '$termination_b_device'
        }
    )


class ConnectCableToInterfaceForm(ConnectCableToDeviceForm):
    termination_b_id = DynamicModelChoiceField(
        queryset=Interface.objects.all(),
        label='Name',
        disabled_indicator='_occupied',
        query_params={
            'device_id': '$termination_b_device',
            'kind': 'physical',
        }
    )


class ConnectCableToFrontPortForm(ConnectCableToDeviceForm):
    termination_b_id = DynamicModelChoiceField(
        queryset=FrontPort.objects.all(),
        label='Name',
        disabled_indicator='_occupied',
        query_params={
            'device_id': '$termination_b_device'
        }
    )


class ConnectCableToRearPortForm(ConnectCableToDeviceForm):
    termination_b_id = DynamicModelChoiceField(
        queryset=RearPort.objects.all(),
        label='Name',
        disabled_indicator='_occupied',
        query_params={
            'device_id': '$termination_b_device'
        }
    )


class ConnectCableToCircuitTerminationForm(BootstrapMixin, CustomFieldModelForm):
    termination_b_provider = DynamicModelChoiceField(
        queryset=Provider.objects.all(),
        label='Provider',
        required=False
    )
    termination_b_region = DynamicModelChoiceField(
        queryset=Region.objects.all(),
        label='Region',
        required=False
    )
    termination_b_site_group = DynamicModelChoiceField(
        queryset=SiteGroup.objects.all(),
        label='Site group',
        required=False
    )
    termination_b_site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        label='Site',
        required=False,
        query_params={
            'region_id': '$termination_b_region',
            'group_id': '$termination_b_site_group',
        }
    )
    termination_b_circuit = DynamicModelChoiceField(
        queryset=Circuit.objects.all(),
        label='Circuit',
        query_params={
            'provider_id': '$termination_b_provider',
            'site_id': '$termination_b_site',
        }
    )
    termination_b_id = DynamicModelChoiceField(
        queryset=CircuitTermination.objects.all(),
        label='Side',
        disabled_indicator='_occupied',
        query_params={
            'circuit_id': '$termination_b_circuit'
        }
    )
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = Cable
        fields = [
            'termination_b_provider', 'termination_b_region', 'termination_b_site', 'termination_b_circuit',
            'termination_b_id', 'type', 'status', 'label', 'color', 'length', 'length_unit', 'tags',
        ]

    def clean_termination_b_id(self):
        # Return the PK rather than the object
        return getattr(self.cleaned_data['termination_b_id'], 'pk', None)


class ConnectCableToPowerFeedForm(BootstrapMixin, CustomFieldModelForm):
    termination_b_region = DynamicModelChoiceField(
        queryset=Region.objects.all(),
        label='Region',
        required=False
    )
    termination_b_site_group = DynamicModelChoiceField(
        queryset=SiteGroup.objects.all(),
        label='Site group',
        required=False
    )
    termination_b_site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        label='Site',
        required=False,
        query_params={
            'region_id': '$termination_b_region',
            'group_id': '$termination_b_site_group',
        }
    )
    termination_b_location = DynamicModelChoiceField(
        queryset=Location.objects.all(),
        label='Location',
        required=False,
        query_params={
            'site_id': '$termination_b_site'
        }
    )
    termination_b_powerpanel = DynamicModelChoiceField(
        queryset=PowerPanel.objects.all(),
        label='Power Panel',
        required=False,
        query_params={
            'site_id': '$termination_b_site',
            'location_id': '$termination_b_location',
        }
    )
    termination_b_id = DynamicModelChoiceField(
        queryset=PowerFeed.objects.all(),
        label='Name',
        disabled_indicator='_occupied',
        query_params={
            'power_panel_id': '$termination_b_powerpanel'
        }
    )
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = Cable
        fields = [
            'termination_b_location', 'termination_b_powerpanel', 'termination_b_id', 'type', 'status', 'label',
            'color', 'length', 'length_unit', 'tags',
        ]

    def clean_termination_b_id(self):
        # Return the PK rather than the object
        return getattr(self.cleaned_data['termination_b_id'], 'pk', None)


class CableForm(BootstrapMixin, CustomFieldModelForm):
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = Cable
        fields = [
            'type', 'status', 'label', 'color', 'length', 'length_unit', 'tags',
        ]
        widgets = {
            'status': StaticSelect,
            'type': StaticSelect,
            'length_unit': StaticSelect,
        }
        error_messages = {
            'length': {
                'max_value': 'Maximum length is 32767 (any unit)'
            }
        }


class CableCSVForm(CustomFieldModelCSVForm):
    # Termination A
    side_a_device = CSVModelChoiceField(
        queryset=Device.objects.all(),
        to_field_name='name',
        help_text='Side A device'
    )
    side_a_type = CSVContentTypeField(
        queryset=ContentType.objects.all(),
        limit_choices_to=CABLE_TERMINATION_MODELS,
        help_text='Side A type'
    )
    side_a_name = forms.CharField(
        help_text='Side A component name'
    )

    # Termination B
    side_b_device = CSVModelChoiceField(
        queryset=Device.objects.all(),
        to_field_name='name',
        help_text='Side B device'
    )
    side_b_type = CSVContentTypeField(
        queryset=ContentType.objects.all(),
        limit_choices_to=CABLE_TERMINATION_MODELS,
        help_text='Side B type'
    )
    side_b_name = forms.CharField(
        help_text='Side B component name'
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
        help_text='Physical medium classification'
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
            'color': mark_safe('RGB color in hexadecimal (e.g. <code>00ff00</code>)'),
        }

    def _clean_side(self, side):
        """
        Derive a Cable's A/B termination objects.

        :param side: 'a' or 'b'
        """
        assert side in 'ab', f"Invalid side designation: {side}"

        device = self.cleaned_data.get(f'side_{side}_device')
        content_type = self.cleaned_data.get(f'side_{side}_type')
        name = self.cleaned_data.get(f'side_{side}_name')
        if not device or not content_type or not name:
            return None

        model = content_type.model_class()
        try:
            termination_object = model.objects.get(device=device, name=name)
            if termination_object.cable is not None:
                raise forms.ValidationError(f"Side {side.upper()}: {device} {termination_object} is already connected")
        except ObjectDoesNotExist:
            raise forms.ValidationError(f"{side.upper()} side termination not found: {device} {name}")

        setattr(self.instance, f'termination_{side}', termination_object)
        return termination_object

    def clean_side_a_name(self):
        return self._clean_side('a')

    def clean_side_b_name(self):
        return self._clean_side('b')

    def clean_length_unit(self):
        # Avoid trying to save as NULL
        length_unit = self.cleaned_data.get('length_unit', None)
        return length_unit if length_unit is not None else ''


class CableBulkEditForm(BootstrapMixin, AddRemoveTagsForm, CustomFieldModelBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=Cable.objects.all(),
        widget=forms.MultipleHiddenInput
    )
    type = forms.ChoiceField(
        choices=add_blank_choice(CableTypeChoices),
        required=False,
        initial='',
        widget=StaticSelect()
    )
    status = forms.ChoiceField(
        choices=add_blank_choice(CableStatusChoices),
        required=False,
        widget=StaticSelect(),
        initial=''
    )
    label = forms.CharField(
        max_length=100,
        required=False
    )
    color = ColorField(
        required=False
    )
    length = forms.DecimalField(
        min_value=0,
        required=False
    )
    length_unit = forms.ChoiceField(
        choices=add_blank_choice(CableLengthUnitChoices),
        required=False,
        initial='',
        widget=StaticSelect()
    )

    class Meta:
        nullable_fields = [
            'type', 'status', 'label', 'color', 'length',
        ]

    def clean(self):
        super().clean()

        # Validate length/unit
        length = self.cleaned_data.get('length')
        length_unit = self.cleaned_data.get('length_unit')
        if length and not length_unit:
            raise forms.ValidationError({
                'length_unit': "Must specify a unit when setting length"
            })


class CableFilterForm(BootstrapMixin, CustomFieldModelFilterForm):
    model = Cable
    field_groups = [
        ['q', 'tag'],
        ['site_id', 'rack_id', 'device_id'],
        ['type', 'status', 'color'],
        ['tenant_id'],
    ]
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': _('All Fields')}),
        label=_('Search')
    )
    region_id = DynamicModelMultipleChoiceField(
        queryset=Region.objects.all(),
        required=False,
        label=_('Region'),
        fetch_trigger='open'
    )
    site_id = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        query_params={
            'region_id': '$region_id'
        },
        label=_('Site'),
        fetch_trigger='open'
    )
    tenant_id = DynamicModelMultipleChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        label=_('Tenant'),
        fetch_trigger='open'
    )
    rack_id = DynamicModelMultipleChoiceField(
        queryset=Rack.objects.all(),
        required=False,
        label=_('Rack'),
        null_option='None',
        query_params={
            'site_id': '$site_id'
        },
        fetch_trigger='open'
    )
    type = forms.MultipleChoiceField(
        choices=add_blank_choice(CableTypeChoices),
        required=False,
        widget=StaticSelect()
    )
    status = forms.ChoiceField(
        required=False,
        choices=add_blank_choice(CableStatusChoices),
        widget=StaticSelect()
    )
    color = ColorField(
        required=False
    )
    device_id = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        required=False,
        query_params={
            'site_id': '$site_id',
            'tenant_id': '$tenant_id',
            'rack_id': '$rack_id',
        },
        label=_('Device'),
        fetch_trigger='open'
    )
    tag = TagFilterField(model)


#
# Connections
#

class ConsoleConnectionFilterForm(BootstrapMixin, forms.Form):
    region_id = DynamicModelMultipleChoiceField(
        queryset=Region.objects.all(),
        required=False,
        label=_('Region'),
        fetch_trigger='open'
    )
    site_id = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        query_params={
            'region_id': '$region_id'
        },
        label=_('Site'),
        fetch_trigger='open'
    )
    device_id = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        required=False,
        query_params={
            'site_id': '$site_id'
        },
        label=_('Device'),
        fetch_trigger='open'
    )


class PowerConnectionFilterForm(BootstrapMixin, forms.Form):
    region_id = DynamicModelMultipleChoiceField(
        queryset=Region.objects.all(),
        required=False,
        label=_('Region'),
        fetch_trigger='open'
    )
    site_id = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        query_params={
            'region_id': '$region_id'
        },
        label=_('Site'),
        fetch_trigger='open'
    )
    device_id = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        required=False,
        query_params={
            'site_id': '$site_id'
        },
        label=_('Device'),
        fetch_trigger='open'
    )


class InterfaceConnectionFilterForm(BootstrapMixin, forms.Form):
    region_id = DynamicModelMultipleChoiceField(
        queryset=Region.objects.all(),
        required=False,
        label=_('Region'),
        fetch_trigger='open'
    )
    site_id = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        query_params={
            'region_id': '$region_id'
        },
        label=_('Site'),
        fetch_trigger='open'
    )
    device_id = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        required=False,
        query_params={
            'site_id': '$site_id'
        },
        label=_('Device'),
        fetch_trigger='open'
    )


#
# Virtual chassis
#

class DeviceSelectionForm(forms.Form):
    pk = forms.ModelMultipleChoiceField(
        queryset=Device.objects.all(),
        widget=forms.MultipleHiddenInput()
    )


class VirtualChassisCreateForm(BootstrapMixin, CustomFieldModelForm):
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
        query_params={
            'region_id': '$region',
            'group_id': '$site_group',
        }
    )
    rack = DynamicModelChoiceField(
        queryset=Rack.objects.all(),
        required=False,
        null_option='None',
        query_params={
            'site_id': '$site'
        }
    )
    members = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        required=False,
        query_params={
            'site_id': '$site',
            'rack_id': '$rack',
        }
    )
    initial_position = forms.IntegerField(
        initial=1,
        required=False,
        help_text='Position of the first member device. Increases by one for each additional member.'
    )
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = VirtualChassis
        fields = [
            'name', 'domain', 'region', 'site_group', 'site', 'rack', 'members', 'initial_position', 'tags',
        ]

    def save(self, *args, **kwargs):
        instance = super().save(*args, **kwargs)

        # Assign VC members
        if instance.pk:
            initial_position = self.cleaned_data.get('initial_position') or 1
            for i, member in enumerate(self.cleaned_data['members'], start=initial_position):
                member.virtual_chassis = instance
                member.vc_position = i
                member.save()

        return instance


class VirtualChassisForm(BootstrapMixin, CustomFieldModelForm):
    master = forms.ModelChoiceField(
        queryset=Device.objects.all(),
        required=False,
    )
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = VirtualChassis
        fields = [
            'name', 'domain', 'master', 'tags',
        ]
        widgets = {
            'master': SelectWithPK(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['master'].queryset = Device.objects.filter(virtual_chassis=self.instance)


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

        # Add bootstrap classes to form elements.
        self.fields['vc_position'].widget.attrs = {'class': 'form-control'}
        self.fields['vc_priority'].widget.attrs = {'class': 'form-control'}

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
        query_params={
            'region_id': '$region',
            'group_id': '$site_group',
        }
    )
    rack = DynamicModelChoiceField(
        queryset=Rack.objects.all(),
        required=False,
        null_option='None',
        query_params={
            'site_id': '$site'
        }
    )
    device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        query_params={
            'site_id': '$site',
            'rack_id': '$rack',
            'virtual_chassis_id': 'null',
        }
    )

    def clean_device(self):
        device = self.cleaned_data['device']
        if device.virtual_chassis is not None:
            raise forms.ValidationError(
                f"Device {device} is already assigned to a virtual chassis."
            )
        return device


class VirtualChassisBulkEditForm(BootstrapMixin, AddRemoveTagsForm, CustomFieldModelBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=VirtualChassis.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
    domain = forms.CharField(
        max_length=30,
        required=False
    )

    class Meta:
        nullable_fields = ['domain']


class VirtualChassisCSVForm(CustomFieldModelCSVForm):
    master = CSVModelChoiceField(
        queryset=Device.objects.all(),
        to_field_name='name',
        required=False,
        help_text='Master device'
    )

    class Meta:
        model = VirtualChassis
        fields = ('name', 'domain', 'master')


class VirtualChassisFilterForm(BootstrapMixin, TenancyFilterForm, CustomFieldModelFilterForm):
    model = VirtualChassis
    field_order = ['q', 'region_id', 'site_group_id', 'site_id', 'tenant_group_id', 'tenant_id']
    field_groups = [
        ['q', 'tag'],
        ['region_id', 'site_group_id', 'site_id'],
        ['tenant_group_id', 'tenant_id'],
    ]
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': _('All Fields')}),
        label=_('Search')
    )
    region_id = DynamicModelMultipleChoiceField(
        queryset=Region.objects.all(),
        required=False,
        label=_('Region'),
        fetch_trigger='open'
    )
    site_group_id = DynamicModelMultipleChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False,
        label=_('Site group'),
        fetch_trigger='open'
    )
    site_id = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        query_params={
            'region_id': '$region_id',
            'group_id': '$site_group_id',
        },
        label=_('Site'),
        fetch_trigger='open'
    )
    tag = TagFilterField(model)


#
# Power panels
#

class PowerPanelForm(BootstrapMixin, CustomFieldModelForm):
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
        query_params={
            'region_id': '$region',
            'group_id': '$site_group',
        }
    )
    location = DynamicModelChoiceField(
        queryset=Location.objects.all(),
        required=False,
        query_params={
            'site_id': '$site'
        }
    )
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = PowerPanel
        fields = [
            'region', 'site_group', 'site', 'location', 'name', 'tags',
        ]
        fieldsets = (
            ('Power Panel', ('region', 'site_group', 'site', 'location', 'name', 'tags')),
        )


class PowerPanelCSVForm(CustomFieldModelCSVForm):
    site = CSVModelChoiceField(
        queryset=Site.objects.all(),
        to_field_name='name',
        help_text='Name of parent site'
    )
    location = CSVModelChoiceField(
        queryset=Location.objects.all(),
        required=False,
        to_field_name='name'
    )

    class Meta:
        model = PowerPanel
        fields = ('site', 'location', 'name')

    def __init__(self, data=None, *args, **kwargs):
        super().__init__(data, *args, **kwargs)

        if data:

            # Limit group queryset by assigned site
            params = {f"site__{self.fields['site'].to_field_name}": data.get('site')}
            self.fields['location'].queryset = self.fields['location'].queryset.filter(**params)


class PowerPanelBulkEditForm(BootstrapMixin, AddRemoveTagsForm, CustomFieldModelBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=PowerPanel.objects.all(),
        widget=forms.MultipleHiddenInput
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
        query_params={
            'region_id': '$region',
            'group_id': '$site_group',
        }
    )
    location = DynamicModelChoiceField(
        queryset=Location.objects.all(),
        required=False,
        query_params={
            'site_id': '$site'
        }
    )

    class Meta:
        nullable_fields = ['location']


class PowerPanelFilterForm(BootstrapMixin, CustomFieldModelFilterForm):
    model = PowerPanel
    field_groups = (
        ('q', 'tag'),
        ('region_id', 'site_group_id', 'site_id', 'location_id')
    )
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': _('All Fields')}),
        label=_('Search')
    )
    region_id = DynamicModelMultipleChoiceField(
        queryset=Region.objects.all(),
        required=False,
        label=_('Region'),
        fetch_trigger='open'
    )
    site_group_id = DynamicModelMultipleChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False,
        label=_('Site group'),
        fetch_trigger='open'
    )
    site_id = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        query_params={
            'region_id': '$region_id',
            'group_id': '$site_group_id',
        },
        label=_('Site'),
        fetch_trigger='open'
    )
    location_id = DynamicModelMultipleChoiceField(
        queryset=Location.objects.all(),
        required=False,
        null_option='None',
        query_params={
            'site_id': '$site_id'
        },
        label=_('Location'),
        fetch_trigger='open'
    )
    tag = TagFilterField(model)


#
# Power feeds
#

class PowerFeedForm(BootstrapMixin, CustomFieldModelForm):
    region = DynamicModelChoiceField(
        queryset=Region.objects.all(),
        required=False,
        initial_params={
            'sites__powerpanel': '$power_panel'
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
        initial_params={
            'powerpanel': '$power_panel'
        },
        query_params={
            'region_id': '$region',
            'group_id': '$site_group',
        }
    )
    power_panel = DynamicModelChoiceField(
        queryset=PowerPanel.objects.all(),
        query_params={
            'site_id': '$site'
        }
    )
    rack = DynamicModelChoiceField(
        queryset=Rack.objects.all(),
        required=False,
        query_params={
            'site_id': '$site'
        }
    )
    comments = CommentField()
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = PowerFeed
        fields = [
            'region', 'site_group', 'site', 'power_panel', 'rack', 'name', 'status', 'type', 'mark_connected', 'supply',
            'phase', 'voltage', 'amperage', 'max_utilization', 'comments', 'tags',
        ]
        fieldsets = (
            ('Power Panel', ('region', 'site', 'power_panel')),
            ('Power Feed', ('rack', 'name', 'status', 'type', 'mark_connected', 'tags')),
            ('Characteristics', ('supply', 'voltage', 'amperage', 'phase', 'max_utilization')),
        )
        widgets = {
            'status': StaticSelect(),
            'type': StaticSelect(),
            'supply': StaticSelect(),
            'phase': StaticSelect(),
        }


class PowerFeedCSVForm(CustomFieldModelCSVForm):
    site = CSVModelChoiceField(
        queryset=Site.objects.all(),
        to_field_name='name',
        help_text='Assigned site'
    )
    power_panel = CSVModelChoiceField(
        queryset=PowerPanel.objects.all(),
        to_field_name='name',
        help_text='Upstream power panel'
    )
    location = CSVModelChoiceField(
        queryset=Location.objects.all(),
        to_field_name='name',
        required=False,
        help_text="Rack's location (if any)"
    )
    rack = CSVModelChoiceField(
        queryset=Rack.objects.all(),
        to_field_name='name',
        required=False,
        help_text='Rack'
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
        help_text='Supply type (AC/DC)'
    )
    phase = CSVChoiceField(
        choices=PowerFeedPhaseChoices,
        required=False,
        help_text='Single or three-phase'
    )

    class Meta:
        model = PowerFeed
        fields = (
            'site', 'power_panel', 'location', 'rack', 'name', 'status', 'type', 'mark_connected', 'supply', 'phase',
            'voltage', 'amperage', 'max_utilization', 'comments',
        )

    def __init__(self, data=None, *args, **kwargs):
        super().__init__(data, *args, **kwargs)

        if data:

            # Limit power_panel queryset by site
            params = {f"site__{self.fields['site'].to_field_name}": data.get('site')}
            self.fields['power_panel'].queryset = self.fields['power_panel'].queryset.filter(**params)

            # Limit location queryset by site
            params = {f"site__{self.fields['site'].to_field_name}": data.get('site')}
            self.fields['location'].queryset = self.fields['location'].queryset.filter(**params)

            # Limit rack queryset by site and group
            params = {
                f"site__{self.fields['site'].to_field_name}": data.get('site'),
                f"location__{self.fields['location'].to_field_name}": data.get('location'),
            }
            self.fields['rack'].queryset = self.fields['rack'].queryset.filter(**params)


class PowerFeedBulkEditForm(BootstrapMixin, AddRemoveTagsForm, CustomFieldModelBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=PowerFeed.objects.all(),
        widget=forms.MultipleHiddenInput
    )
    power_panel = DynamicModelChoiceField(
        queryset=PowerPanel.objects.all(),
        required=False
    )
    rack = DynamicModelChoiceField(
        queryset=Rack.objects.all(),
        required=False,
    )
    status = forms.ChoiceField(
        choices=add_blank_choice(PowerFeedStatusChoices),
        required=False,
        initial='',
        widget=StaticSelect()
    )
    type = forms.ChoiceField(
        choices=add_blank_choice(PowerFeedTypeChoices),
        required=False,
        initial='',
        widget=StaticSelect()
    )
    supply = forms.ChoiceField(
        choices=add_blank_choice(PowerFeedSupplyChoices),
        required=False,
        initial='',
        widget=StaticSelect()
    )
    phase = forms.ChoiceField(
        choices=add_blank_choice(PowerFeedPhaseChoices),
        required=False,
        initial='',
        widget=StaticSelect()
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
    mark_connected = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect
    )
    comments = CommentField(
        widget=SmallTextarea,
        label='Comments'
    )

    class Meta:
        nullable_fields = [
            'location', 'comments',
        ]


class PowerFeedFilterForm(BootstrapMixin, CustomFieldModelFilterForm):
    model = PowerFeed
    field_groups = [
        ['q', 'tag'],
        ['region_id', 'site_group_id', 'site_id'],
        ['power_panel_id', 'rack_id'],
        ['status', 'type', 'supply', 'phase', 'voltage', 'amperage', 'max_utilization'],
    ]
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': _('All Fields')}),
        label=_('Search')
    )
    region_id = DynamicModelMultipleChoiceField(
        queryset=Region.objects.all(),
        required=False,
        label=_('Region'),
        fetch_trigger='open'
    )
    site_group_id = DynamicModelMultipleChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False,
        label=_('Site group'),
        fetch_trigger='open'
    )
    site_id = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        query_params={
            'region_id': '$region_id'
        },
        label=_('Site'),
        fetch_trigger='open'
    )
    power_panel_id = DynamicModelMultipleChoiceField(
        queryset=PowerPanel.objects.all(),
        required=False,
        null_option='None',
        query_params={
            'site_id': '$site_id'
        },
        label=_('Power panel'),
        fetch_trigger='open'
    )
    rack_id = DynamicModelMultipleChoiceField(
        queryset=Rack.objects.all(),
        required=False,
        null_option='None',
        query_params={
            'site_id': '$site_id'
        },
        label=_('Rack'),
        fetch_trigger='open'
    )
    status = forms.MultipleChoiceField(
        choices=PowerFeedStatusChoices,
        required=False,
        widget=StaticSelectMultiple()
    )
    type = forms.ChoiceField(
        choices=add_blank_choice(PowerFeedTypeChoices),
        required=False,
        widget=StaticSelect()
    )
    supply = forms.ChoiceField(
        choices=add_blank_choice(PowerFeedSupplyChoices),
        required=False,
        widget=StaticSelect()
    )
    phase = forms.ChoiceField(
        choices=add_blank_choice(PowerFeedPhaseChoices),
        required=False,
        widget=StaticSelect()
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
