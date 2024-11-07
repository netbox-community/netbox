from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from timezone_field import TimeZoneFormField

from dcim.choices import *
from dcim.constants import *
from dcim.models import *
from extras.models import ConfigTemplate
from ipam.models import ASN, VLAN, VLANGroup, VRF
from netbox.forms import NetBoxModelBulkEditForm
from tenancy.models import Tenant
from users.models import User
from utilities.forms import BulkEditForm, add_blank_choice, form_from_model
from utilities.forms.fields import ColorField, CommentField, DynamicModelChoiceField, DynamicModelMultipleChoiceField
from utilities.forms.rendering import FieldSet, InlineFields, TabbedGroups
from utilities.forms.widgets import BulkEditNullBooleanSelect, NumberWithOptions
from wireless.models import WirelessLAN, WirelessLANGroup
from wireless.choices import WirelessRoleChoices

__all__ = (
    'CableBulkEditForm',
    'ConsolePortBulkEditForm',
    'ConsolePortTemplateBulkEditForm',
    'ConsoleServerPortBulkEditForm',
    'ConsoleServerPortTemplateBulkEditForm',
    'DeviceBayBulkEditForm',
    'DeviceBayTemplateBulkEditForm',
    'DeviceBulkEditForm',
    'DeviceRoleBulkEditForm',
    'DeviceTypeBulkEditForm',
    'FrontPortBulkEditForm',
    'FrontPortTemplateBulkEditForm',
    'InterfaceBulkEditForm',
    'InterfaceTemplateBulkEditForm',
    'InventoryItemBulkEditForm',
    'InventoryItemRoleBulkEditForm',
    'InventoryItemTemplateBulkEditForm',
    'LocationBulkEditForm',
    'ManufacturerBulkEditForm',
    'ModuleBulkEditForm',
    'ModuleBayBulkEditForm',
    'ModuleBayTemplateBulkEditForm',
    'ModuleTypeBulkEditForm',
    'PlatformBulkEditForm',
    'PowerFeedBulkEditForm',
    'PowerOutletBulkEditForm',
    'PowerOutletTemplateBulkEditForm',
    'PowerPanelBulkEditForm',
    'PowerPortBulkEditForm',
    'PowerPortTemplateBulkEditForm',
    'RackBulkEditForm',
    'RackReservationBulkEditForm',
    'RackRoleBulkEditForm',
    'RackTypeBulkEditForm',
    'RearPortBulkEditForm',
    'RearPortTemplateBulkEditForm',
    'RegionBulkEditForm',
    'SiteBulkEditForm',
    'SiteGroupBulkEditForm',
    'VirtualChassisBulkEditForm',
    'VirtualDeviceContextBulkEditForm'
)


class RegionBulkEditForm(NetBoxModelBulkEditForm):
    parent = DynamicModelChoiceField(
        label=_('Parent'),
        queryset=Region.objects.all(),
        required=False
    )
    description = forms.CharField(
        label=_('Description'),
        max_length=200,
        required=False
    )

    model = Region
    fieldsets = (
        FieldSet('parent', 'description'),
    )
    nullable_fields = ('parent', 'description')


class SiteGroupBulkEditForm(NetBoxModelBulkEditForm):
    parent = DynamicModelChoiceField(
        label=_('Parent'),
        queryset=SiteGroup.objects.all(),
        required=False
    )
    description = forms.CharField(
        label=_('Description'),
        max_length=200,
        required=False
    )

    model = SiteGroup
    fieldsets = (
        FieldSet('parent', 'description'),
    )
    nullable_fields = ('parent', 'description')


class SiteBulkEditForm(NetBoxModelBulkEditForm):
    status = forms.ChoiceField(
        label=_('Status'),
        choices=add_blank_choice(SiteStatusChoices),
        required=False,
        initial=''
    )
    region = DynamicModelChoiceField(
        label=_('Region'),
        queryset=Region.objects.all(),
        required=False
    )
    group = DynamicModelChoiceField(
        label=_('Group'),
        queryset=SiteGroup.objects.all(),
        required=False
    )
    tenant = DynamicModelChoiceField(
        label=_('Tenant'),
        queryset=Tenant.objects.all(),
        required=False
    )
    asns = DynamicModelMultipleChoiceField(
        queryset=ASN.objects.all(),
        label=_('ASNs'),
        required=False
    )
    contact_name = forms.CharField(
        label=_('Contact name'),
        max_length=50,
        required=False
    )
    contact_phone = forms.CharField(
        label=_('Contact phone'),
        max_length=20,
        required=False
    )
    contact_email = forms.EmailField(
        required=False,
        label=_('Contact E-mail')
    )
    time_zone = TimeZoneFormField(
        label=_('Time zone'),
        choices=add_blank_choice(TimeZoneFormField().choices),
        required=False
    )
    description = forms.CharField(
        label=_('Description'),
        max_length=200,
        required=False
    )
    comments = CommentField()

    model = Site
    fieldsets = (
        FieldSet('status', 'region', 'group', 'tenant', 'asns', 'time_zone', 'description'),
    )
    nullable_fields = (
        'region', 'group', 'tenant', 'asns', 'time_zone', 'description', 'comments',
    )


class LocationBulkEditForm(NetBoxModelBulkEditForm):
    site = DynamicModelChoiceField(
        label=_('Site'),
        queryset=Site.objects.all(),
        required=False
    )
    parent = DynamicModelChoiceField(
        label=_('Parent'),
        queryset=Location.objects.all(),
        required=False,
        query_params={
            'site_id': '$site'
        }
    )
    status = forms.ChoiceField(
        label=_('Status'),
        choices=add_blank_choice(LocationStatusChoices),
        required=False,
        initial=''
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

    model = Location
    fieldsets = (
        FieldSet('site', 'parent', 'status', 'tenant', 'description'),
    )
    nullable_fields = ('parent', 'tenant', 'description')


class RackRoleBulkEditForm(NetBoxModelBulkEditForm):
    color = ColorField(
        label=_('Color'),
        required=False
    )
    description = forms.CharField(
        label=_('Description'),
        max_length=200,
        required=False
    )

    model = RackRole
    fieldsets = (
        FieldSet('color', 'description'),
    )
    nullable_fields = ('color', 'description')


class RackTypeBulkEditForm(NetBoxModelBulkEditForm):
    manufacturer = DynamicModelChoiceField(
        label=_('Manufacturer'),
        queryset=Manufacturer.objects.all(),
        required=False
    )
    form_factor = forms.ChoiceField(
        label=_('Form factor'),
        choices=add_blank_choice(RackFormFactorChoices),
        required=False
    )
    width = forms.ChoiceField(
        label=_('Width'),
        choices=add_blank_choice(RackWidthChoices),
        required=False
    )
    u_height = forms.IntegerField(
        required=False,
        label=_('Height (U)')
    )
    starting_unit = forms.IntegerField(
        required=False,
        min_value=1
    )
    desc_units = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect,
        label=_('Descending units')
    )
    outer_width = forms.IntegerField(
        label=_('Outer width'),
        required=False,
        min_value=1
    )
    outer_depth = forms.IntegerField(
        label=_('Outer depth'),
        required=False,
        min_value=1
    )
    outer_unit = forms.ChoiceField(
        label=_('Outer unit'),
        choices=add_blank_choice(RackDimensionUnitChoices),
        required=False
    )
    mounting_depth = forms.IntegerField(
        label=_('Mounting depth'),
        required=False,
        min_value=1
    )
    weight = forms.DecimalField(
        label=_('Weight'),
        min_value=0,
        required=False
    )
    max_weight = forms.IntegerField(
        label=_('Max weight'),
        min_value=0,
        required=False
    )
    weight_unit = forms.ChoiceField(
        label=_('Weight unit'),
        choices=add_blank_choice(WeightUnitChoices),
        required=False,
        initial=''
    )
    description = forms.CharField(
        label=_('Description'),
        max_length=200,
        required=False
    )
    comments = CommentField()

    model = RackType
    fieldsets = (
        FieldSet('manufacturer', 'description', 'form_factor', 'width', 'u_height', name=_('Rack Type')),
        FieldSet(
            InlineFields('outer_width', 'outer_depth', 'outer_unit', label=_('Outer Dimensions')),
            InlineFields('weight', 'max_weight', 'weight_unit', label=_('Weight')),
            'mounting_depth',
            name=_('Dimensions')
        ),
        FieldSet('starting_unit', 'desc_units', name=_('Numbering')),
    )
    nullable_fields = (
        'outer_width', 'outer_depth', 'outer_unit', 'weight',
        'max_weight', 'weight_unit', 'description', 'comments',
    )


class RackBulkEditForm(NetBoxModelBulkEditForm):
    region = DynamicModelChoiceField(
        label=_('Region'),
        queryset=Region.objects.all(),
        required=False,
        initial_params={
            'sites': '$site'
        }
    )
    site_group = DynamicModelChoiceField(
        label=_('Site group'),
        queryset=SiteGroup.objects.all(),
        required=False,
        initial_params={
            'sites': '$site'
        }
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
    location = DynamicModelChoiceField(
        label=_('Location'),
        queryset=Location.objects.all(),
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
        choices=add_blank_choice(RackStatusChoices),
        required=False,
        initial=''
    )
    role = DynamicModelChoiceField(
        label=_('Role'),
        queryset=RackRole.objects.all(),
        required=False
    )
    serial = forms.CharField(
        max_length=50,
        required=False,
        label=_('Serial Number')
    )
    asset_tag = forms.CharField(
        label=_('Asset tag'),
        max_length=50,
        required=False
    )
    form_factor = forms.ChoiceField(
        label=_('Form factor'),
        choices=add_blank_choice(RackFormFactorChoices),
        required=False
    )
    width = forms.ChoiceField(
        label=_('Width'),
        choices=add_blank_choice(RackWidthChoices),
        required=False
    )
    u_height = forms.IntegerField(
        required=False,
        label=_('Height (U)')
    )
    desc_units = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect,
        label=_('Descending units')
    )
    outer_width = forms.IntegerField(
        label=_('Outer width'),
        required=False,
        min_value=1
    )
    outer_depth = forms.IntegerField(
        label=_('Outer depth'),
        required=False,
        min_value=1
    )
    outer_unit = forms.ChoiceField(
        label=_('Outer unit'),
        choices=add_blank_choice(RackDimensionUnitChoices),
        required=False
    )
    mounting_depth = forms.IntegerField(
        label=_('Mounting depth'),
        required=False,
        min_value=1
    )
    airflow = forms.ChoiceField(
        label=_('Airflow'),
        choices=add_blank_choice(RackAirflowChoices),
        required=False
    )
    weight = forms.DecimalField(
        label=_('Weight'),
        min_value=0,
        required=False
    )
    max_weight = forms.IntegerField(
        label=_('Max weight'),
        min_value=0,
        required=False
    )
    weight_unit = forms.ChoiceField(
        label=_('Weight unit'),
        choices=add_blank_choice(WeightUnitChoices),
        required=False,
        initial=''
    )
    description = forms.CharField(
        label=_('Description'),
        max_length=200,
        required=False
    )
    comments = CommentField()

    model = Rack
    fieldsets = (
        FieldSet('status', 'role', 'tenant', 'serial', 'asset_tag', 'description', name=_('Rack')),
        FieldSet('region', 'site_group', 'site', 'location', name=_('Location')),
        FieldSet(
            'form_factor', 'width', 'u_height', 'desc_units', 'airflow', 'outer_width', 'outer_depth', 'outer_unit',
            'mounting_depth', name=_('Hardware')
        ),
        FieldSet('weight', 'max_weight', 'weight_unit', name=_('Weight')),
    )
    nullable_fields = (
        'location', 'tenant', 'role', 'serial', 'asset_tag', 'outer_width', 'outer_depth', 'outer_unit', 'weight',
        'max_weight', 'weight_unit', 'description', 'comments',
    )


class RackReservationBulkEditForm(NetBoxModelBulkEditForm):
    user = forms.ModelChoiceField(
        label=_('User'),
        queryset=User.objects.order_by('username'),
        required=False
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

    model = RackReservation
    fieldsets = (
        FieldSet('user', 'tenant', 'description'),
    )
    nullable_fields = ('comments',)


class ManufacturerBulkEditForm(NetBoxModelBulkEditForm):
    description = forms.CharField(
        label=_('Description'),
        max_length=200,
        required=False
    )

    model = Manufacturer
    fieldsets = (
        FieldSet('description'),
    )
    nullable_fields = ('description',)


class DeviceTypeBulkEditForm(NetBoxModelBulkEditForm):
    manufacturer = DynamicModelChoiceField(
        label=_('Manufacturer'),
        queryset=Manufacturer.objects.all(),
        required=False
    )
    default_platform = DynamicModelChoiceField(
        label=_('Default platform'),
        queryset=Platform.objects.all(),
        required=False
    )
    part_number = forms.CharField(
        label=_('Part number'),
        required=False
    )
    u_height = forms.IntegerField(
        label=_('U height'),
        min_value=0,
        required=False
    )
    is_full_depth = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect(),
        label=_('Is full depth')
    )
    exclude_from_utilization = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect(),
        label=_('Exclude from utilization')
    )
    airflow = forms.ChoiceField(
        label=_('Airflow'),
        choices=add_blank_choice(DeviceAirflowChoices),
        required=False
    )
    weight = forms.DecimalField(
        label=_('Weight'),
        min_value=0,
        required=False
    )
    weight_unit = forms.ChoiceField(
        label=_('Weight unit'),
        choices=add_blank_choice(WeightUnitChoices),
        required=False,
        initial=''
    )
    description = forms.CharField(
        label=_('Description'),
        max_length=200,
        required=False
    )
    comments = CommentField()

    model = DeviceType
    fieldsets = (
        FieldSet(
            'manufacturer', 'default_platform', 'part_number', 'u_height', 'exclude_from_utilization', 'is_full_depth',
            'airflow', 'description', name=_('Device Type')
        ),
        FieldSet('weight', 'weight_unit', name=_('Weight')),
    )
    nullable_fields = ('part_number', 'airflow', 'weight', 'weight_unit', 'description', 'comments')


class ModuleTypeBulkEditForm(NetBoxModelBulkEditForm):
    manufacturer = DynamicModelChoiceField(
        label=_('Manufacturer'),
        queryset=Manufacturer.objects.all(),
        required=False
    )
    part_number = forms.CharField(
        label=_('Part number'),
        required=False
    )
    airflow = forms.ChoiceField(
        label=_('Airflow'),
        choices=add_blank_choice(ModuleAirflowChoices),
        required=False
    )
    weight = forms.DecimalField(
        label=_('Weight'),
        min_value=0,
        required=False
    )
    weight_unit = forms.ChoiceField(
        label=_('Weight unit'),
        choices=add_blank_choice(WeightUnitChoices),
        required=False,
        initial=''
    )
    description = forms.CharField(
        label=_('Description'),
        max_length=200,
        required=False
    )
    comments = CommentField()

    model = ModuleType
    fieldsets = (
        FieldSet('manufacturer', 'part_number', 'description', name=_('Module Type')),
        FieldSet(
            'airflow',
            InlineFields('weight', 'max_weight', 'weight_unit', label=_('Weight')),
            name=_('Chassis')
        ),
    )
    nullable_fields = ('part_number', 'weight', 'weight_unit', 'description', 'comments')


class DeviceRoleBulkEditForm(NetBoxModelBulkEditForm):
    color = ColorField(
        label=_('Color'),
        required=False
    )
    vm_role = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect,
        label=_('VM role')
    )
    config_template = DynamicModelChoiceField(
        label=_('Config template'),
        queryset=ConfigTemplate.objects.all(),
        required=False
    )
    description = forms.CharField(
        label=_('Description'),
        max_length=200,
        required=False
    )

    model = DeviceRole
    fieldsets = (
        FieldSet('color', 'vm_role', 'config_template', 'description'),
    )
    nullable_fields = ('color', 'config_template', 'description')


class PlatformBulkEditForm(NetBoxModelBulkEditForm):
    manufacturer = DynamicModelChoiceField(
        label=_('Manufacturer'),
        queryset=Manufacturer.objects.all(),
        required=False
    )
    config_template = DynamicModelChoiceField(
        label=_('Config template'),
        queryset=ConfigTemplate.objects.all(),
        required=False
    )
    description = forms.CharField(
        label=_('Description'),
        max_length=200,
        required=False
    )

    model = Platform
    fieldsets = (
        FieldSet('manufacturer', 'config_template', 'description'),
    )
    nullable_fields = ('manufacturer', 'config_template', 'description')


class DeviceBulkEditForm(NetBoxModelBulkEditForm):
    manufacturer = DynamicModelChoiceField(
        label=_('Manufacturer'),
        queryset=Manufacturer.objects.all(),
        required=False
    )
    device_type = DynamicModelChoiceField(
        label=_('Device type'),
        queryset=DeviceType.objects.all(),
        required=False,
        context={
            'parent': 'manufacturer',
        },
        query_params={
            'manufacturer_id': '$manufacturer'
        }
    )
    role = DynamicModelChoiceField(
        label=_('Device role'),
        queryset=DeviceRole.objects.all(),
        required=False
    )
    site = DynamicModelChoiceField(
        label=_('Site'),
        queryset=Site.objects.all(),
        required=False
    )
    location = DynamicModelChoiceField(
        label=_('Location'),
        queryset=Location.objects.all(),
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
    platform = DynamicModelChoiceField(
        label=_('Platform'),
        queryset=Platform.objects.all(),
        required=False
    )
    status = forms.ChoiceField(
        label=_('Status'),
        choices=add_blank_choice(DeviceStatusChoices),
        required=False
    )
    airflow = forms.ChoiceField(
        label=_('Airflow'),
        choices=add_blank_choice(DeviceAirflowChoices),
        required=False
    )
    serial = forms.CharField(
        max_length=50,
        required=False,
        label=_('Serial Number')
    )
    description = forms.CharField(
        label=_('Description'),
        max_length=200,
        required=False
    )
    config_template = DynamicModelChoiceField(
        label=_('Config template'),
        queryset=ConfigTemplate.objects.all(),
        required=False
    )
    comments = CommentField()

    model = Device
    fieldsets = (
        FieldSet('role', 'status', 'tenant', 'platform', 'description', name=_('Device')),
        FieldSet('site', 'location', name=_('Location')),
        FieldSet('manufacturer', 'device_type', 'airflow', 'serial', name=_('Hardware')),
        FieldSet('config_template', name=_('Configuration')),
    )
    nullable_fields = (
        'location', 'tenant', 'platform', 'serial', 'airflow', 'description', 'comments',
    )


class ModuleBulkEditForm(NetBoxModelBulkEditForm):
    manufacturer = DynamicModelChoiceField(
        label=_('Manufacturer'),
        queryset=Manufacturer.objects.all(),
        required=False
    )
    module_type = DynamicModelChoiceField(
        label=_('Module type'),
        queryset=ModuleType.objects.all(),
        required=False,
        query_params={
            'manufacturer_id': '$manufacturer'
        },
        context={
            'parent': 'manufacturer',
        }
    )
    status = forms.ChoiceField(
        label=_('Status'),
        choices=add_blank_choice(ModuleStatusChoices),
        required=False,
        initial=''
    )
    serial = forms.CharField(
        max_length=50,
        required=False,
        label=_('Serial Number')
    )
    description = forms.CharField(
        label=_('Description'),
        max_length=200,
        required=False
    )
    comments = CommentField()

    model = Module
    fieldsets = (
        FieldSet('manufacturer', 'module_type', 'status', 'serial', 'description'),
    )
    nullable_fields = ('serial', 'description', 'comments')


class CableBulkEditForm(NetBoxModelBulkEditForm):
    type = forms.ChoiceField(
        label=_('Type'),
        choices=add_blank_choice(CableTypeChoices),
        required=False,
        initial=''
    )
    status = forms.ChoiceField(
        label=_('Status'),
        choices=add_blank_choice(LinkStatusChoices),
        required=False,
        initial=''
    )
    tenant = DynamicModelChoiceField(
        label=_('Tenant'),
        queryset=Tenant.objects.all(),
        required=False
    )
    label = forms.CharField(
        label=_('Label'),
        max_length=100,
        required=False
    )
    color = ColorField(
        label=_('Color'),
        required=False
    )
    length = forms.DecimalField(
        label=_('Length'),
        min_value=0,
        required=False
    )
    length_unit = forms.ChoiceField(
        label=_('Length unit'),
        choices=add_blank_choice(CableLengthUnitChoices),
        required=False,
        initial=''
    )
    description = forms.CharField(
        label=_('Description'),
        max_length=200,
        required=False
    )
    comments = CommentField()

    model = Cable
    fieldsets = (
        FieldSet('type', 'status', 'tenant', 'label', 'description'),
        FieldSet('color', 'length', 'length_unit', name=_('Attributes')),
    )
    nullable_fields = (
        'type', 'status', 'tenant', 'label', 'color', 'length', 'description', 'comments',
    )


class VirtualChassisBulkEditForm(NetBoxModelBulkEditForm):
    domain = forms.CharField(
        label=_('Domain'),
        max_length=30,
        required=False
    )
    description = forms.CharField(
        label=_('Description'),
        max_length=200,
        required=False
    )
    comments = CommentField()

    model = VirtualChassis
    fieldsets = (
        FieldSet('domain', 'description'),
    )
    nullable_fields = ('domain', 'description', 'comments')


class PowerPanelBulkEditForm(NetBoxModelBulkEditForm):
    region = DynamicModelChoiceField(
        label=_('Region'),
        queryset=Region.objects.all(),
        required=False,
        initial_params={
            'sites': '$site'
        }
    )
    site_group = DynamicModelChoiceField(
        label=_('Site group'),
        queryset=SiteGroup.objects.all(),
        required=False,
        initial_params={
            'sites': '$site'
        }
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
    location = DynamicModelChoiceField(
        label=_('Location'),
        queryset=Location.objects.all(),
        required=False,
        query_params={
            'site_id': '$site'
        }
    )
    description = forms.CharField(
        label=_('Description'),
        max_length=200,
        required=False
    )
    comments = CommentField()

    model = PowerPanel
    fieldsets = (
        FieldSet('region', 'site_group', 'site', 'location', 'description'),
    )
    nullable_fields = ('location', 'description', 'comments')


class PowerFeedBulkEditForm(NetBoxModelBulkEditForm):
    power_panel = DynamicModelChoiceField(
        label=_('Power panel'),
        queryset=PowerPanel.objects.all(),
        required=False
    )
    rack = DynamicModelChoiceField(
        label=_('Rack'),
        queryset=Rack.objects.all(),
        required=False,
    )
    status = forms.ChoiceField(
        label=_('Status'),
        choices=add_blank_choice(PowerFeedStatusChoices),
        required=False,
        initial=''
    )
    type = forms.ChoiceField(
        label=_('Type'),
        choices=add_blank_choice(PowerFeedTypeChoices),
        required=False,
        initial=''
    )
    supply = forms.ChoiceField(
        label=_('Supply'),
        choices=add_blank_choice(PowerFeedSupplyChoices),
        required=False,
        initial=''
    )
    phase = forms.ChoiceField(
        label=_('Phase'),
        choices=add_blank_choice(PowerFeedPhaseChoices),
        required=False,
        initial=''
    )
    voltage = forms.IntegerField(
        label=_('Voltage'),
        required=False
    )
    amperage = forms.IntegerField(
        label=_('Amperage'),
        required=False
    )
    max_utilization = forms.IntegerField(
        label=_('Max utilization'),
        required=False
    )
    mark_connected = forms.NullBooleanField(
        label=_('Mark connected'),
        required=False,
        widget=BulkEditNullBooleanSelect
    )
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False
    )
    description = forms.CharField(
        label=_('Description'),
        max_length=200,
        required=False
    )
    comments = CommentField()

    model = PowerFeed
    fieldsets = (
        FieldSet('power_panel', 'rack', 'status', 'type', 'mark_connected', 'description', 'tenant'),
        FieldSet('supply', 'phase', 'voltage', 'amperage', 'max_utilization', name=_('Power'))
    )
    nullable_fields = ('location', 'tenant', 'description', 'comments')


#
# Device component templates
#

class ConsolePortTemplateBulkEditForm(BulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=ConsolePortTemplate.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
    label = forms.CharField(
        label=_('Label'),
        max_length=64,
        required=False
    )
    type = forms.ChoiceField(
        label=_('Type'),
        choices=add_blank_choice(ConsolePortTypeChoices),
        required=False
    )

    nullable_fields = ('label', 'type', 'description')


class ConsoleServerPortTemplateBulkEditForm(BulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=ConsoleServerPortTemplate.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
    label = forms.CharField(
        label=_('Label'),
        max_length=64,
        required=False
    )
    type = forms.ChoiceField(
        label=_('Type'),
        choices=add_blank_choice(ConsolePortTypeChoices),
        required=False
    )
    description = forms.CharField(
        label=_('Description'),
        required=False
    )

    nullable_fields = ('label', 'type', 'description')


class PowerPortTemplateBulkEditForm(BulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=PowerPortTemplate.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
    label = forms.CharField(
        label=_('Label'),
        max_length=64,
        required=False
    )
    type = forms.ChoiceField(
        label=_('Type'),
        choices=add_blank_choice(PowerPortTypeChoices),
        required=False
    )
    maximum_draw = forms.IntegerField(
        label=_('Maximum draw'),
        min_value=1,
        required=False,
        help_text=_("Maximum power draw (watts)")
    )
    allocated_draw = forms.IntegerField(
        label=_('Allocated draw'),
        min_value=1,
        required=False,
        help_text=_("Allocated power draw (watts)")
    )
    description = forms.CharField(
        label=_('Description'),
        required=False
    )

    nullable_fields = ('label', 'type', 'maximum_draw', 'allocated_draw', 'description')


class PowerOutletTemplateBulkEditForm(BulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=PowerOutletTemplate.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
    device_type = forms.ModelChoiceField(
        label=_('Device type'),
        queryset=DeviceType.objects.all(),
        required=False,
        disabled=True,
        widget=forms.HiddenInput()
    )
    label = forms.CharField(
        label=_('Label'),
        max_length=64,
        required=False
    )
    type = forms.ChoiceField(
        label=_('Type'),
        choices=add_blank_choice(PowerOutletTypeChoices),
        required=False
    )
    power_port = forms.ModelChoiceField(
        label=_('Power port'),
        queryset=PowerPortTemplate.objects.all(),
        required=False
    )
    feed_leg = forms.ChoiceField(
        label=_('Feed leg'),
        choices=add_blank_choice(PowerOutletFeedLegChoices),
        required=False
    )
    description = forms.CharField(
        label=_('Description'),
        required=False
    )

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


class InterfaceTemplateBulkEditForm(BulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=InterfaceTemplate.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
    label = forms.CharField(
        label=_('Label'),
        max_length=64,
        required=False
    )
    type = forms.ChoiceField(
        label=_('Type'),
        choices=add_blank_choice(InterfaceTypeChoices),
        required=False
    )
    enabled = forms.NullBooleanField(
        label=_('Enabled'),
        required=False,
        widget=BulkEditNullBooleanSelect
    )
    mgmt_only = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect,
        label=_('Management only')
    )
    description = forms.CharField(
        label=_('Description'),
        required=False
    )
    poe_mode = forms.ChoiceField(
        choices=add_blank_choice(InterfacePoEModeChoices),
        required=False,
        initial='',
        label=_('PoE mode')
    )
    poe_type = forms.ChoiceField(
        choices=add_blank_choice(InterfacePoETypeChoices),
        required=False,
        initial='',
        label=_('PoE type')
    )
    rf_role = forms.ChoiceField(
        choices=add_blank_choice(WirelessRoleChoices),
        required=False,
        initial='',
        label=_('Wireless role')
    )

    nullable_fields = ('label', 'description', 'poe_mode', 'poe_type', 'rf_role')


class FrontPortTemplateBulkEditForm(BulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=FrontPortTemplate.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
    label = forms.CharField(
        label=_('Label'),
        max_length=64,
        required=False
    )
    type = forms.ChoiceField(
        label=_('Type'),
        choices=add_blank_choice(PortTypeChoices),
        required=False
    )
    color = ColorField(
        label=_('Color'),
        required=False
    )
    description = forms.CharField(
        label=_('Description'),
        required=False
    )

    nullable_fields = ('description',)


class RearPortTemplateBulkEditForm(BulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=RearPortTemplate.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
    label = forms.CharField(
        label=_('Label'),
        max_length=64,
        required=False
    )
    type = forms.ChoiceField(
        label=_('Type'),
        choices=add_blank_choice(PortTypeChoices),
        required=False
    )
    color = ColorField(
        label=_('Color'),
        required=False
    )
    description = forms.CharField(
        label=_('Description'),
        required=False
    )

    nullable_fields = ('description',)


class ModuleBayTemplateBulkEditForm(BulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=ModuleBayTemplate.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
    label = forms.CharField(
        label=_('Label'),
        max_length=64,
        required=False
    )
    description = forms.CharField(
        label=_('Description'),
        required=False
    )

    nullable_fields = ('label', 'position', 'description')


class DeviceBayTemplateBulkEditForm(BulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=DeviceBayTemplate.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
    label = forms.CharField(
        label=_('Label'),
        max_length=64,
        required=False
    )
    description = forms.CharField(
        label=_('Description'),
        required=False
    )

    nullable_fields = ('label', 'description')


class InventoryItemTemplateBulkEditForm(BulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=InventoryItemTemplate.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
    label = forms.CharField(
        label=_('Label'),
        max_length=64,
        required=False
    )
    description = forms.CharField(
        label=_('Description'),
        required=False
    )
    role = DynamicModelChoiceField(
        label=_('Role'),
        queryset=InventoryItemRole.objects.all(),
        required=False
    )
    manufacturer = DynamicModelChoiceField(
        label=_('Manufacturer'),
        queryset=Manufacturer.objects.all(),
        required=False
    )

    nullable_fields = ('label', 'role', 'manufacturer', 'part_id', 'description')


#
# Device components
#

class ComponentBulkEditForm(NetBoxModelBulkEditForm):
    device = forms.ModelChoiceField(
        label=_('Device'),
        queryset=Device.objects.all(),
        required=False,
        disabled=True,
        widget=forms.HiddenInput()
    )
    module = forms.ModelChoiceField(
        label=_('Module'),
        queryset=Module.objects.all(),
        required=False
    )

    def __init__(self, *args, initial=None, **kwargs):
        try:
            self.device_id = int(initial.get('device'))
        except (TypeError, ValueError):
            self.device_id = None

        super().__init__(*args, initial=initial, **kwargs)

        # Limit module queryset to Modules which belong to the parent Device
        if self.device_id:
            device = Device.objects.filter(pk=self.device_id).first()
            self.fields['module'].queryset = Module.objects.filter(device=device)
        else:
            self.fields['module'].choices = ()
            self.fields['module'].widget.attrs['disabled'] = True


class ConsolePortBulkEditForm(
    ComponentBulkEditForm,
    form_from_model(ConsolePort, ['label', 'type', 'speed', 'mark_connected', 'description'])
):
    mark_connected = forms.NullBooleanField(
        label=_('Mark connected'),
        required=False,
        widget=BulkEditNullBooleanSelect
    )

    model = ConsolePort
    fieldsets = (
        FieldSet('module', 'type', 'label', 'speed', 'description', 'mark_connected'),
    )
    nullable_fields = ('module', 'label', 'description')


class ConsoleServerPortBulkEditForm(
    ComponentBulkEditForm,
    form_from_model(ConsoleServerPort, ['label', 'type', 'speed', 'mark_connected', 'description'])
):
    mark_connected = forms.NullBooleanField(
        label=_('Mark connected'),
        required=False,
        widget=BulkEditNullBooleanSelect
    )

    model = ConsoleServerPort
    fieldsets = (
        FieldSet('module', 'type', 'label', 'speed', 'description', 'mark_connected'),
    )
    nullable_fields = ('module', 'label', 'description')


class PowerPortBulkEditForm(
    ComponentBulkEditForm,
    form_from_model(PowerPort, ['label', 'type', 'maximum_draw', 'allocated_draw', 'mark_connected', 'description'])
):
    mark_connected = forms.NullBooleanField(
        label=_('Mark connected'),
        required=False,
        widget=BulkEditNullBooleanSelect
    )

    model = PowerPort
    fieldsets = (
        FieldSet('module', 'type', 'label', 'description', 'mark_connected'),
        FieldSet('maximum_draw', 'allocated_draw', name=_('Power')),
    )
    nullable_fields = ('module', 'label', 'description', 'maximum_draw', 'allocated_draw')


class PowerOutletBulkEditForm(
    ComponentBulkEditForm,
    form_from_model(PowerOutlet, ['label', 'type', 'feed_leg', 'power_port', 'mark_connected', 'description'])
):
    mark_connected = forms.NullBooleanField(
        label=_('Mark connected'),
        required=False,
        widget=BulkEditNullBooleanSelect
    )

    model = PowerOutlet
    fieldsets = (
        FieldSet('module', 'type', 'label', 'description', 'mark_connected'),
        FieldSet('feed_leg', 'power_port', name=_('Power')),
    )
    nullable_fields = ('module', 'label', 'type', 'feed_leg', 'power_port', 'description')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Limit power_port queryset to PowerPorts which belong to the parent Device
        if self.device_id:
            device = Device.objects.filter(pk=self.device_id).first()
            self.fields['power_port'].queryset = PowerPort.objects.filter(device=device)
        else:
            self.fields['power_port'].choices = ()
            self.fields['power_port'].widget.attrs['disabled'] = True


class InterfaceBulkEditForm(
    ComponentBulkEditForm,
    form_from_model(Interface, [
        'label', 'type', 'parent', 'bridge', 'lag', 'speed', 'duplex', 'mac_address', 'wwn', 'mtu', 'mgmt_only',
        'mark_connected', 'description', 'mode', 'rf_role', 'rf_channel', 'rf_channel_frequency', 'rf_channel_width',
        'tx_power', 'wireless_lans'
    ])
):
    enabled = forms.NullBooleanField(
        label=_('Enabled'),
        required=False,
        widget=BulkEditNullBooleanSelect
    )
    parent = DynamicModelChoiceField(
        label=_('Parent'),
        queryset=Interface.objects.all(),
        required=False,
        query_params={
            'virtual_chassis_member_id': '$device',
        }
    )
    bridge = DynamicModelChoiceField(
        label=_('Bridge'),
        queryset=Interface.objects.all(),
        required=False,
        query_params={
            'virtual_chassis_member_id': '$device',
        }
    )
    lag = DynamicModelChoiceField(
        queryset=Interface.objects.all(),
        required=False,
        query_params={
            'type': 'lag',
            'virtual_chassis_member_id': '$device',
        },
        label=_('LAG')
    )
    vdcs = DynamicModelMultipleChoiceField(
        queryset=VirtualDeviceContext.objects.all(),
        required=False,
        label=_('Virtual device contexts'),
        query_params={
            'device_id': '$device',
        }
    )
    speed = forms.IntegerField(
        label=_('Speed'),
        required=False,
        widget=NumberWithOptions(
            options=InterfaceSpeedChoices
        )
    )
    mgmt_only = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect,
        label=_('Management only')
    )
    poe_mode = forms.ChoiceField(
        choices=add_blank_choice(InterfacePoEModeChoices),
        required=False,
        initial='',
        label=_('PoE mode')
    )
    poe_type = forms.ChoiceField(
        choices=add_blank_choice(InterfacePoETypeChoices),
        required=False,
        initial='',
        label=_('PoE type')
    )
    mark_connected = forms.NullBooleanField(
        label=_('Mark connected'),
        required=False,
        widget=BulkEditNullBooleanSelect
    )
    mode = forms.ChoiceField(
        label=_('Mode'),
        choices=add_blank_choice(InterfaceModeChoices),
        required=False,
        initial=''
    )
    vlan_group = DynamicModelChoiceField(
        queryset=VLANGroup.objects.all(),
        required=False,
        label=_('VLAN group')
    )
    untagged_vlan = DynamicModelChoiceField(
        queryset=VLAN.objects.all(),
        required=False,
        query_params={
            'group_id': '$vlan_group',
            'available_on_device': '$device',
        },
        label=_('Untagged VLAN')
    )
    tagged_vlans = DynamicModelMultipleChoiceField(
        queryset=VLAN.objects.all(),
        required=False,
        query_params={
            'group_id': '$vlan_group',
            'available_on_device': '$device',
        },
        label=_('Tagged VLANs')
    )
    add_tagged_vlans = DynamicModelMultipleChoiceField(
        label=_('Add tagged VLANs'),
        queryset=VLAN.objects.all(),
        required=False,
        query_params={
            'group_id': '$vlan_group',
            'available_on_device': '$device',
        },
    )
    remove_tagged_vlans = DynamicModelMultipleChoiceField(
        label=_('Remove tagged VLANs'),
        queryset=VLAN.objects.all(),
        required=False,
        query_params={
            'group_id': '$vlan_group',
            'available_on_device': '$device',
        }
    )
    vrf = DynamicModelChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label=_('VRF')
    )
    wireless_lan_group = DynamicModelChoiceField(
        queryset=WirelessLANGroup.objects.all(),
        required=False,
        label=_('Wireless LAN group')
    )
    wireless_lans = DynamicModelMultipleChoiceField(
        queryset=WirelessLAN.objects.all(),
        required=False,
        label=_('Wireless LANs'),
        query_params={
            'group_id': '$wireless_lan_group',
        }
    )

    model = Interface
    fieldsets = (
        FieldSet('module', 'type', 'label', 'speed', 'duplex', 'description'),
        FieldSet('vrf', 'mac_address', 'wwn', name=_('Addressing')),
        FieldSet('vdcs', 'mtu', 'tx_power', 'enabled', 'mgmt_only', 'mark_connected', name=_('Operation')),
        FieldSet('poe_mode', 'poe_type', name=_('PoE')),
        FieldSet('parent', 'bridge', 'lag', name=_('Related Interfaces')),
        FieldSet('mode', 'vlan_group', 'untagged_vlan', name=_('802.1Q Switching')),
        FieldSet(
            TabbedGroups(
                FieldSet('tagged_vlans', name=_('Assignment')),
                FieldSet('add_tagged_vlans', 'remove_tagged_vlans', name=_('Add/Remove')),
            ),
        ),
        FieldSet(
            'rf_role', 'rf_channel', 'rf_channel_frequency', 'rf_channel_width', 'wireless_lan_group', 'wireless_lans',
            name=_('Wireless')
        ),
    )
    nullable_fields = (
        'module', 'label', 'parent', 'bridge', 'lag', 'speed', 'duplex', 'mac_address', 'wwn', 'vdcs', 'mtu',
        'description', 'poe_mode', 'poe_type', 'mode', 'rf_channel', 'rf_channel_frequency', 'rf_channel_width',
        'tx_power', 'untagged_vlan', 'tagged_vlans', 'vrf', 'wireless_lans'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.device_id:
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
                    # Query for VLANs assigned to the same site and VLANs with no site assigned (null).
                    self.fields['untagged_vlan'].widget.add_query_param(
                        'site_id', [site.pk, settings.FILTERS_NULL_CHOICE_VALUE]
                    )
                    self.fields['tagged_vlans'].widget.add_query_param(
                        'site_id', [site.pk, settings.FILTERS_NULL_CHOICE_VALUE]
                    )

                    self.fields['add_tagged_vlans'].widget.add_query_param(
                        'site_id', [site.pk, settings.FILTERS_NULL_CHOICE_VALUE]
                    )
                    self.fields['remove_tagged_vlans'].widget.add_query_param(
                        'site_id', [site.pk, settings.FILTERS_NULL_CHOICE_VALUE]
                    )

            self.fields['parent'].choices = ()
            self.fields['parent'].widget.attrs['disabled'] = True
            self.fields['bridge'].choices = ()
            self.fields['bridge'].widget.attrs['disabled'] = True
            self.fields['lag'].choices = ()
            self.fields['lag'].widget.attrs['disabled'] = True

    def clean(self):
        super().clean()

        if not self.cleaned_data['mode']:
            if self.cleaned_data['untagged_vlan']:
                raise forms.ValidationError({'untagged_vlan': _("Interface mode must be specified to assign VLANs")})
            elif self.cleaned_data['tagged_vlans']:
                raise forms.ValidationError({'tagged_vlans': _("Interface mode must be specified to assign VLANs")})

        # Untagged interfaces cannot be assigned tagged VLANs
        elif self.cleaned_data['mode'] == InterfaceModeChoices.MODE_ACCESS and self.cleaned_data['tagged_vlans']:
            raise forms.ValidationError({
                'mode': _("An access interface cannot have tagged VLANs assigned.")
            })

        # Remove all tagged VLAN assignments from "tagged all" interfaces
        elif self.cleaned_data['mode'] == InterfaceModeChoices.MODE_TAGGED_ALL:
            self.cleaned_data['tagged_vlans'] = []


class FrontPortBulkEditForm(
    ComponentBulkEditForm,
    form_from_model(FrontPort, ['label', 'type', 'color', 'mark_connected', 'description'])
):
    mark_connected = forms.NullBooleanField(
        label=_('Mark connected'),
        required=False,
        widget=BulkEditNullBooleanSelect
    )

    model = FrontPort
    fieldsets = (
        FieldSet('module', 'type', 'label', 'color', 'description', 'mark_connected'),
    )
    nullable_fields = ('module', 'label', 'description', 'color')


class RearPortBulkEditForm(
    ComponentBulkEditForm,
    form_from_model(RearPort, ['label', 'type', 'color', 'mark_connected', 'description'])
):
    mark_connected = forms.NullBooleanField(
        label=_('Mark connected'),
        required=False,
        widget=BulkEditNullBooleanSelect
    )

    model = RearPort
    fieldsets = (
        FieldSet('module', 'type', 'label', 'color', 'description', 'mark_connected'),
    )
    nullable_fields = ('module', 'label', 'description', 'color')


class ModuleBayBulkEditForm(
    form_from_model(ModuleBay, ['label', 'position', 'description']),
    NetBoxModelBulkEditForm
):
    model = ModuleBay
    fieldsets = (
        FieldSet('label', 'position', 'description'),
    )
    nullable_fields = ('label', 'position', 'description')


class DeviceBayBulkEditForm(
    form_from_model(DeviceBay, ['label', 'description']),
    NetBoxModelBulkEditForm
):
    model = DeviceBay
    fieldsets = (
        FieldSet('label', 'description'),
    )
    nullable_fields = ('label', 'description')


class InventoryItemBulkEditForm(
    form_from_model(InventoryItem, ['label', 'role', 'manufacturer', 'part_id', 'description']),
    NetBoxModelBulkEditForm
):
    device = DynamicModelChoiceField(
        label=_('Device'),
        queryset=Device.objects.all(),
        required=False
    )
    role = DynamicModelChoiceField(
        label=_('Role'),
        queryset=InventoryItemRole.objects.all(),
        required=False
    )
    manufacturer = DynamicModelChoiceField(
        label=_('Manufacturer'),
        queryset=Manufacturer.objects.all(),
        required=False
    )

    model = InventoryItem
    fieldsets = (
        FieldSet('device', 'label', 'role', 'manufacturer', 'part_id', 'description'),
    )
    nullable_fields = ('label', 'role', 'manufacturer', 'part_id', 'description')


#
# Device component roles
#

class InventoryItemRoleBulkEditForm(NetBoxModelBulkEditForm):
    color = ColorField(
        label=_('Color'),
        required=False
    )
    description = forms.CharField(
        label=_('Description'),
        max_length=200,
        required=False
    )

    model = InventoryItemRole
    fieldsets = (
        FieldSet('color', 'description'),
    )
    nullable_fields = ('color', 'description')


class VirtualDeviceContextBulkEditForm(NetBoxModelBulkEditForm):
    device = DynamicModelChoiceField(
        label=_('Device'),
        queryset=Device.objects.all(),
        required=False
    )
    status = forms.ChoiceField(
        label=_('Status'),
        required=False,
        choices=add_blank_choice(VirtualDeviceContextStatusChoices)
    )
    tenant = DynamicModelChoiceField(
        label=_('Tenant'),
        queryset=Tenant.objects.all(),
        required=False
    )
    model = VirtualDeviceContext
    fieldsets = (
        FieldSet('device', 'status', 'tenant'),
    )
    nullable_fields = ('device', 'tenant', )
