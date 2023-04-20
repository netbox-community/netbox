from django import forms
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from timezone_field import TimeZoneFormField

from dcim.choices import *
from dcim.constants import *
from dcim.models import *
from ipam.models import ASN, VLAN, VLANGroup, VRF
from netbox.forms import NetBoxModelBulkEditForm
from tenancy.models import Tenant
from utilities.forms import (
    add_blank_choice, BulkEditForm, BulkEditNullBooleanSelect, ColorField, CommentField, DynamicModelChoiceField,
    DynamicModelMultipleChoiceField, form_from_model, StaticSelect, SelectSpeedWidget
)

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
        queryset=Region.objects.all(),
        required=False
    )
    description = forms.CharField(
        max_length=200,
        required=False
    )

    model = Region
    fieldsets = (
        (None, ('parent', 'description')),
    )
    nullable_fields = ('parent', 'description')


class SiteGroupBulkEditForm(NetBoxModelBulkEditForm):
    parent = DynamicModelChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False
    )
    description = forms.CharField(
        max_length=200,
        required=False
    )

    model = SiteGroup
    fieldsets = (
        (None, ('parent', 'description')),
    )
    nullable_fields = ('parent', 'description')


class SiteBulkEditForm(NetBoxModelBulkEditForm):
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
    asns = DynamicModelMultipleChoiceField(
        queryset=ASN.objects.all(),
        label=_('ASNs'),
        required=False
    )
    contact_name = forms.CharField(
        max_length=50,
        required=False
    )
    contact_phone = forms.CharField(
        max_length=20,
        required=False
    )
    contact_email = forms.EmailField(
        required=False,
        label=_('Contact E-mail')
    )
    time_zone = TimeZoneFormField(
        choices=add_blank_choice(TimeZoneFormField().choices),
        required=False,
        widget=StaticSelect()
    )
    description = forms.CharField(
        max_length=200,
        required=False
    )
    comments = CommentField(
        label='Comments'
    )

    model = Site
    fieldsets = (
        (None, ('status', 'region', 'group', 'tenant', 'asns', 'time_zone', 'description')),
    )
    nullable_fields = (
        'region', 'group', 'tenant', 'asns', 'time_zone', 'description', 'comments',
    )


class LocationBulkEditForm(NetBoxModelBulkEditForm):
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
    status = forms.ChoiceField(
        choices=add_blank_choice(LocationStatusChoices),
        required=False,
        initial='',
        widget=StaticSelect()
    )
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False
    )
    description = forms.CharField(
        max_length=200,
        required=False
    )

    model = Location
    fieldsets = (
        (None, ('site', 'parent', 'status', 'tenant', 'description')),
    )
    nullable_fields = ('parent', 'tenant', 'description')


class RackRoleBulkEditForm(NetBoxModelBulkEditForm):
    color = ColorField(
        required=False
    )
    description = forms.CharField(
        max_length=200,
        required=False
    )

    model = RackRole
    fieldsets = (
        (None, ('color', 'description')),
    )
    nullable_fields = ('color', 'description')


class RackBulkEditForm(NetBoxModelBulkEditForm):
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
        label=_('Serial Number')
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
        label=_('Height (U)')
    )
    desc_units = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect,
        label=_('Descending units')
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
    mounting_depth = forms.IntegerField(
        required=False,
        min_value=1
    )
    weight = forms.DecimalField(
        min_value=0,
        required=False
    )
    max_weight = forms.IntegerField(
        min_value=0,
        required=False
    )
    weight_unit = forms.ChoiceField(
        choices=add_blank_choice(WeightUnitChoices),
        required=False,
        initial='',
        widget=StaticSelect()
    )
    description = forms.CharField(
        max_length=200,
        required=False
    )
    comments = CommentField(
        label='Comments'
    )

    model = Rack
    fieldsets = (
        ('Rack', ('status', 'role', 'tenant', 'serial', 'asset_tag', 'description')),
        ('Location', ('region', 'site_group', 'site', 'location')),
        ('Hardware', (
            'type', 'width', 'u_height', 'desc_units', 'outer_width', 'outer_depth', 'outer_unit', 'mounting_depth',
        )),
        ('Weight', ('weight', 'max_weight', 'weight_unit')),
    )
    nullable_fields = (
        'location', 'tenant', 'role', 'serial', 'asset_tag', 'outer_width', 'outer_depth', 'outer_unit', 'weight',
        'max_weight', 'weight_unit', 'description', 'comments',
    )


class RackReservationBulkEditForm(NetBoxModelBulkEditForm):
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
        max_length=200,
        required=False
    )
    comments = CommentField(
        label='Comments'
    )

    model = RackReservation
    fieldsets = (
        (None, ('user', 'tenant', 'description')),
    )
    nullable_fields = ('comments',)


class ManufacturerBulkEditForm(NetBoxModelBulkEditForm):
    description = forms.CharField(
        max_length=200,
        required=False
    )

    model = Manufacturer
    fieldsets = (
        (None, ('description',)),
    )
    nullable_fields = ('description',)


class DeviceTypeBulkEditForm(NetBoxModelBulkEditForm):
    manufacturer = DynamicModelChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False
    )
    part_number = forms.CharField(
        required=False
    )
    u_height = forms.IntegerField(
        min_value=1,
        required=False
    )
    is_full_depth = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect(),
        label=_('Is full depth')
    )
    airflow = forms.ChoiceField(
        choices=add_blank_choice(DeviceAirflowChoices),
        required=False,
        widget=StaticSelect()
    )
    weight = forms.DecimalField(
        min_value=0,
        required=False
    )
    weight_unit = forms.ChoiceField(
        choices=add_blank_choice(WeightUnitChoices),
        required=False,
        initial='',
        widget=StaticSelect()
    )
    description = forms.CharField(
        max_length=200,
        required=False
    )
    comments = CommentField(
        label='Comments'
    )

    model = DeviceType
    fieldsets = (
        ('Device Type', ('manufacturer', 'part_number', 'u_height', 'is_full_depth', 'airflow', 'description')),
        ('Weight', ('weight', 'weight_unit')),
    )
    nullable_fields = ('part_number', 'airflow', 'weight', 'weight_unit', 'description', 'comments')


class ModuleTypeBulkEditForm(NetBoxModelBulkEditForm):
    manufacturer = DynamicModelChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False
    )
    part_number = forms.CharField(
        required=False
    )
    weight = forms.DecimalField(
        min_value=0,
        required=False
    )
    weight_unit = forms.ChoiceField(
        choices=add_blank_choice(WeightUnitChoices),
        required=False,
        initial='',
        widget=StaticSelect()
    )
    description = forms.CharField(
        max_length=200,
        required=False
    )
    comments = CommentField(
        label='Comments'
    )

    model = ModuleType
    fieldsets = (
        ('Module Type', ('manufacturer', 'part_number', 'description')),
        ('Weight', ('weight', 'weight_unit')),
    )
    nullable_fields = ('part_number', 'weight', 'weight_unit', 'description', 'comments')


class DeviceRoleBulkEditForm(NetBoxModelBulkEditForm):
    color = ColorField(
        required=False
    )
    vm_role = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect,
        label=_('VM role')
    )
    description = forms.CharField(
        max_length=200,
        required=False
    )

    model = DeviceRole
    fieldsets = (
        (None, ('color', 'vm_role', 'description')),
    )
    nullable_fields = ('color', 'description')


class PlatformBulkEditForm(NetBoxModelBulkEditForm):
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

    model = Platform
    fieldsets = (
        (None, ('manufacturer', 'napalm_driver', 'description')),
    )
    nullable_fields = ('manufacturer', 'napalm_driver', 'description')


class DeviceBulkEditForm(NetBoxModelBulkEditForm):
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
    airflow = forms.ChoiceField(
        choices=add_blank_choice(DeviceAirflowChoices),
        required=False,
        widget=StaticSelect()
    )
    serial = forms.CharField(
        max_length=50,
        required=False,
        label=_('Serial Number')
    )
    description = forms.CharField(
        max_length=200,
        required=False
    )
    comments = CommentField(
        label='Comments'
    )

    model = Device
    fieldsets = (
        ('Device', ('device_role', 'status', 'tenant', 'platform', 'description')),
        ('Location', ('site', 'location')),
        ('Hardware', ('manufacturer', 'device_type', 'airflow', 'serial')),
    )
    nullable_fields = (
        'location', 'tenant', 'platform', 'serial', 'airflow', 'description', 'comments',
    )


class ModuleBulkEditForm(NetBoxModelBulkEditForm):
    manufacturer = DynamicModelChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False
    )
    module_type = DynamicModelChoiceField(
        queryset=ModuleType.objects.all(),
        required=False,
        query_params={
            'manufacturer_id': '$manufacturer'
        }
    )
    status = forms.ChoiceField(
        choices=add_blank_choice(ModuleStatusChoices),
        required=False,
        initial='',
        widget=StaticSelect()
    )
    serial = forms.CharField(
        max_length=50,
        required=False,
        label=_('Serial Number')
    )
    description = forms.CharField(
        max_length=200,
        required=False
    )
    comments = CommentField(
        label='Comments'
    )

    model = Module
    fieldsets = (
        (None, ('manufacturer', 'module_type', 'status', 'serial', 'description')),
    )
    nullable_fields = ('serial', 'description', 'comments')


class CableBulkEditForm(NetBoxModelBulkEditForm):
    type = forms.ChoiceField(
        choices=add_blank_choice(CableTypeChoices),
        required=False,
        initial='',
        widget=StaticSelect()
    )
    status = forms.ChoiceField(
        choices=add_blank_choice(LinkStatusChoices),
        required=False,
        widget=StaticSelect(),
        initial=''
    )
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False
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
    description = forms.CharField(
        max_length=200,
        required=False
    )
    comments = CommentField(
        label='Comments'
    )

    model = Cable
    fieldsets = (
        (None, ('type', 'status', 'tenant', 'label', 'description')),
        ('Attributes', ('color', 'length', 'length_unit')),
    )
    nullable_fields = (
        'type', 'status', 'tenant', 'label', 'color', 'length', 'description', 'comments',
    )


class VirtualChassisBulkEditForm(NetBoxModelBulkEditForm):
    domain = forms.CharField(
        max_length=30,
        required=False
    )
    description = forms.CharField(
        max_length=200,
        required=False
    )
    comments = CommentField(
        label='Comments'
    )

    model = VirtualChassis
    fieldsets = (
        (None, ('domain', 'description')),
    )
    nullable_fields = ('domain', 'description', 'comments')


class PowerPanelBulkEditForm(NetBoxModelBulkEditForm):
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
    description = forms.CharField(
        max_length=200,
        required=False
    )
    comments = CommentField(
        label='Comments'
    )

    model = PowerPanel
    fieldsets = (
        (None, ('region', 'site_group', 'site', 'location', 'description')),
    )
    nullable_fields = ('location', 'description', 'comments')


class PowerFeedBulkEditForm(NetBoxModelBulkEditForm):
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
    description = forms.CharField(
        max_length=200,
        required=False
    )
    comments = CommentField(
        label=_('Comments')
    )

    model = PowerFeed
    fieldsets = (
        (None, ('power_panel', 'rack', 'status', 'type', 'mark_connected', 'description')),
        ('Power', ('supply', 'phase', 'voltage', 'amperage', 'max_utilization'))
    )
    nullable_fields = ('location', 'description', 'comments')


#
# Device component templates
#

class ConsolePortTemplateBulkEditForm(BulkEditForm):
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

    nullable_fields = ('label', 'type', 'description')


class ConsoleServerPortTemplateBulkEditForm(BulkEditForm):
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

    nullable_fields = ('label', 'type', 'description')


class PowerPortTemplateBulkEditForm(BulkEditForm):
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
        help_text=_("Maximum power draw (watts)")
    )
    allocated_draw = forms.IntegerField(
        min_value=1,
        required=False,
        help_text=_("Allocated power draw (watts)")
    )
    description = forms.CharField(
        required=False
    )

    nullable_fields = ('label', 'type', 'maximum_draw', 'allocated_draw', 'description')


class PowerOutletTemplateBulkEditForm(BulkEditForm):
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
        label=_('Management only')
    )
    description = forms.CharField(
        required=False
    )
    poe_mode = forms.ChoiceField(
        choices=add_blank_choice(InterfacePoEModeChoices),
        required=False,
        initial='',
        widget=StaticSelect(),
        label=_('PoE mode')
    )
    poe_type = forms.ChoiceField(
        choices=add_blank_choice(InterfacePoETypeChoices),
        required=False,
        initial='',
        widget=StaticSelect(),
        label=_('PoE type')
    )

    nullable_fields = ('label', 'description', 'poe_mode', 'poe_type')


class FrontPortTemplateBulkEditForm(BulkEditForm):
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

    nullable_fields = ('description',)


class RearPortTemplateBulkEditForm(BulkEditForm):
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

    nullable_fields = ('description',)


class ModuleBayTemplateBulkEditForm(BulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=ModuleBayTemplate.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
    label = forms.CharField(
        max_length=64,
        required=False
    )
    description = forms.CharField(
        required=False
    )

    nullable_fields = ('label', 'position', 'description')


class DeviceBayTemplateBulkEditForm(BulkEditForm):
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

    nullable_fields = ('label', 'description')


class InventoryItemTemplateBulkEditForm(BulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=InventoryItemTemplate.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
    label = forms.CharField(
        max_length=64,
        required=False
    )
    description = forms.CharField(
        required=False
    )
    role = DynamicModelChoiceField(
        queryset=InventoryItemRole.objects.all(),
        required=False
    )
    manufacturer = DynamicModelChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False
    )

    nullable_fields = ('label', 'role', 'manufacturer', 'part_id', 'description')


#
# Device components
#

class ComponentBulkEditForm(NetBoxModelBulkEditForm):
    device = forms.ModelChoiceField(
        queryset=Device.objects.all(),
        required=False,
        disabled=True,
        widget=forms.HiddenInput()
    )
    module = forms.ModelChoiceField(
        queryset=Module.objects.all(),
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Limit module queryset to Modules which belong to the parent Device
        if 'device' in self.initial:
            device = Device.objects.filter(pk=self.initial['device']).first()
            self.fields['module'].queryset = Module.objects.filter(device=device)
        else:
            self.fields['module'].choices = ()
            self.fields['module'].widget.attrs['disabled'] = True


class ConsolePortBulkEditForm(
    form_from_model(ConsolePort, ['label', 'type', 'speed', 'mark_connected', 'description']),
    ComponentBulkEditForm
):
    mark_connected = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect
    )

    model = ConsolePort
    fieldsets = (
        (None, ('module', 'type', 'label', 'speed', 'description', 'mark_connected')),
    )
    nullable_fields = ('module', 'label', 'description')


class ConsoleServerPortBulkEditForm(
    form_from_model(ConsoleServerPort, ['label', 'type', 'speed', 'mark_connected', 'description']),
    ComponentBulkEditForm
):
    mark_connected = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect
    )

    model = ConsoleServerPort
    fieldsets = (
        (None, ('module', 'type', 'label', 'speed', 'description', 'mark_connected')),
    )
    nullable_fields = ('module', 'label', 'description')


class PowerPortBulkEditForm(
    form_from_model(PowerPort, ['label', 'type', 'maximum_draw', 'allocated_draw', 'mark_connected', 'description']),
    ComponentBulkEditForm
):
    mark_connected = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect
    )

    model = PowerPort
    fieldsets = (
        (None, ('module', 'type', 'label', 'description', 'mark_connected')),
        ('Power', ('maximum_draw', 'allocated_draw')),
    )
    nullable_fields = ('module', 'label', 'description')


class PowerOutletBulkEditForm(
    form_from_model(PowerOutlet, ['label', 'type', 'feed_leg', 'power_port', 'mark_connected', 'description']),
    ComponentBulkEditForm
):
    mark_connected = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect
    )

    model = PowerOutlet
    fieldsets = (
        (None, ('module', 'type', 'label', 'description', 'mark_connected')),
        ('Power', ('feed_leg', 'power_port')),
    )
    nullable_fields = ('module', 'label', 'type', 'feed_leg', 'power_port', 'description')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Limit power_port queryset to PowerPorts which belong to the parent Device
        if 'device' in self.initial:
            device = Device.objects.filter(pk=self.initial['device']).first()
            self.fields['power_port'].queryset = PowerPort.objects.filter(device=device)
        else:
            self.fields['power_port'].choices = ()
            self.fields['power_port'].widget.attrs['disabled'] = True


class InterfaceBulkEditForm(
    form_from_model(Interface, [
        'label', 'type', 'parent', 'bridge', 'lag', 'speed', 'duplex', 'mac_address', 'wwn', 'mtu', 'mgmt_only',
        'mark_connected', 'description', 'mode', 'rf_role', 'rf_channel', 'rf_channel_frequency', 'rf_channel_width',
        'tx_power',
    ]),
    ComponentBulkEditForm
):
    enabled = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect
    )
    parent = DynamicModelChoiceField(
        queryset=Interface.objects.all(),
        required=False
    )
    bridge = DynamicModelChoiceField(
        queryset=Interface.objects.all(),
        required=False
    )
    lag = DynamicModelChoiceField(
        queryset=Interface.objects.all(),
        required=False,
        query_params={
            'type': 'lag',
        },
        label=_('LAG')
    )
    vdcs = DynamicModelMultipleChoiceField(
        queryset=VirtualDeviceContext.objects.all(),
        required=False,
        label='Virtual Device Contexts',
        query_params={
            'device_id': '$device',
        }
    )
    speed = forms.IntegerField(
        required=False,
        widget=SelectSpeedWidget(),
        label=_('Speed')
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
        widget=StaticSelect(),
        label=_('PoE mode')
    )
    poe_type = forms.ChoiceField(
        choices=add_blank_choice(InterfacePoETypeChoices),
        required=False,
        initial='',
        widget=StaticSelect(),
        label=_('PoE type')
    )
    mark_connected = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect
    )
    mode = forms.ChoiceField(
        choices=add_blank_choice(InterfaceModeChoices),
        required=False,
        initial='',
        widget=StaticSelect()
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
        },
        label=_('Untagged VLAN')
    )
    tagged_vlans = DynamicModelMultipleChoiceField(
        queryset=VLAN.objects.all(),
        required=False,
        query_params={
            'group_id': '$vlan_group',
        },
        label=_('Tagged VLANs')
    )
    vrf = DynamicModelChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label=_('VRF')
    )

    model = Interface
    fieldsets = (
        (None, ('module', 'type', 'label', 'speed', 'duplex', 'description')),
        ('Addressing', ('vrf', 'mac_address', 'wwn')),
        ('Operation', ('vdcs', 'mtu', 'tx_power', 'enabled', 'mgmt_only', 'mark_connected')),
        ('PoE', ('poe_mode', 'poe_type')),
        ('Related Interfaces', ('parent', 'bridge', 'lag')),
        ('802.1Q Switching', ('mode', 'vlan_group', 'untagged_vlan', 'tagged_vlans')),
        ('Wireless', ('rf_role', 'rf_channel', 'rf_channel_frequency', 'rf_channel_width')),
    )
    nullable_fields = (
        'module', 'label', 'parent', 'bridge', 'lag', 'speed', 'duplex', 'mac_address', 'wwn', 'vdcs', 'mtu', 'description',
        'poe_mode', 'poe_type', 'mode', 'rf_channel', 'rf_channel_frequency', 'rf_channel_width', 'tx_power',
        'vlan_group', 'untagged_vlan', 'tagged_vlans', 'vrf',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'device' in self.initial:
            device = Device.objects.filter(pk=self.initial['device']).first()

            # Restrict parent/bridge/LAG interface assignment by device
            self.fields['parent'].widget.add_query_param('device_id', device.pk)
            self.fields['bridge'].widget.add_query_param('device_id', device.pk)
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
            self.fields['bridge'].choices = ()
            self.fields['bridge'].widget.attrs['disabled'] = True
            self.fields['lag'].choices = ()
            self.fields['lag'].widget.attrs['disabled'] = True

    def clean(self):
        super().clean()

        if not self.cleaned_data['mode']:
            if self.cleaned_data['untagged_vlan']:
                raise forms.ValidationError({'untagged_vlan': "Interface mode must be specified to assign VLANs"})
            elif self.cleaned_data['tagged_vlans']:
                raise forms.ValidationError({'tagged_vlans': "Interface mode must be specified to assign VLANs"})

        # Untagged interfaces cannot be assigned tagged VLANs
        elif self.cleaned_data['mode'] == InterfaceModeChoices.MODE_ACCESS and self.cleaned_data['tagged_vlans']:
            raise forms.ValidationError({
                'mode': "An access interface cannot have tagged VLANs assigned."
            })

        # Remove all tagged VLAN assignments from "tagged all" interfaces
        elif self.cleaned_data['mode'] == InterfaceModeChoices.MODE_TAGGED_ALL:
            self.cleaned_data['tagged_vlans'] = []


class FrontPortBulkEditForm(
    form_from_model(FrontPort, ['label', 'type', 'color', 'mark_connected', 'description']),
    ComponentBulkEditForm
):
    mark_connected = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect
    )

    model = FrontPort
    fieldsets = (
        (None, ('module', 'type', 'label', 'color', 'description', 'mark_connected')),
    )
    nullable_fields = ('module', 'label', 'description', 'color')


class RearPortBulkEditForm(
    form_from_model(RearPort, ['label', 'type', 'color', 'mark_connected', 'description']),
    ComponentBulkEditForm
):
    mark_connected = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect
    )

    model = RearPort
    fieldsets = (
        (None, ('module', 'type', 'label', 'color', 'description', 'mark_connected')),
    )
    nullable_fields = ('module', 'label', 'description', 'color')


class ModuleBayBulkEditForm(
    form_from_model(ModuleBay, ['label', 'position', 'description']),
    NetBoxModelBulkEditForm
):
    model = ModuleBay
    fieldsets = (
        (None, ('label', 'position', 'description')),
    )
    nullable_fields = ('label', 'position', 'description')


class DeviceBayBulkEditForm(
    form_from_model(DeviceBay, ['label', 'description']),
    NetBoxModelBulkEditForm
):
    model = DeviceBay
    fieldsets = (
        (None, ('label', 'description')),
    )
    nullable_fields = ('label', 'description')


class InventoryItemBulkEditForm(
    form_from_model(InventoryItem, ['label', 'role', 'manufacturer', 'part_id', 'description']),
    NetBoxModelBulkEditForm
):
    device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        required=False
    )
    role = DynamicModelChoiceField(
        queryset=InventoryItemRole.objects.all(),
        required=False
    )
    manufacturer = DynamicModelChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False
    )

    model = InventoryItem
    fieldsets = (
        (None, ('device', 'label', 'role', 'manufacturer', 'part_id', 'description')),
    )
    nullable_fields = ('label', 'role', 'manufacturer', 'part_id', 'description')


#
# Device component roles
#

class InventoryItemRoleBulkEditForm(NetBoxModelBulkEditForm):
    color = ColorField(
        required=False
    )
    description = forms.CharField(
        max_length=200,
        required=False
    )

    model = InventoryItemRole
    fieldsets = (
        (None, ('color', 'description')),
    )
    nullable_fields = ('color', 'description')


class VirtualDeviceContextBulkEditForm(NetBoxModelBulkEditForm):
    device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        required=False
    )
    status = forms.ChoiceField(
        required=False,
        choices=add_blank_choice(VirtualDeviceContextStatusChoices),
        widget=StaticSelect()
    )
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False
    )
    model = VirtualDeviceContext
    fieldsets = (
        (None, ('device', 'status', 'tenant')),
    )
    nullable_fields = ('device', 'tenant', )
