from django import forms
from django.contrib.auth.models import User
from django.utils.translation import gettext as _

from dcim.choices import *
from dcim.constants import *
from dcim.models import *
from extras.forms import LocalConfigContextFilterForm
from ipam.models import ASN, VRF
from netbox.forms import NetBoxModelFilterSetForm
from tenancy.forms import TenancyFilterForm
from utilities.forms import (
    APISelectMultiple, add_blank_choice, ColorField, DynamicModelMultipleChoiceField, FilterForm, StaticSelect,
    StaticSelectMultiple, TagFilterField, BOOLEAN_WITH_BLANK_CHOICES, SelectSpeedWidget,
)
from wireless.choices import *

__all__ = (
    'CableFilterForm',
    'ConsoleConnectionFilterForm',
    'ConsolePortFilterForm',
    'ConsoleServerPortFilterForm',
    'DeviceBayFilterForm',
    'DeviceFilterForm',
    'DeviceRoleFilterForm',
    'DeviceTypeFilterForm',
    'FrontPortFilterForm',
    'InterfaceConnectionFilterForm',
    'InterfaceFilterForm',
    'InventoryItemFilterForm',
    'InventoryItemRoleFilterForm',
    'LocationFilterForm',
    'ManufacturerFilterForm',
    'ModuleFilterForm',
    'ModuleFilterForm',
    'ModuleBayFilterForm',
    'ModuleTypeFilterForm',
    'PlatformFilterForm',
    'PowerConnectionFilterForm',
    'PowerFeedFilterForm',
    'PowerOutletFilterForm',
    'PowerPanelFilterForm',
    'PowerPortFilterForm',
    'RackFilterForm',
    'RackElevationFilterForm',
    'RackReservationFilterForm',
    'RackRoleFilterForm',
    'RearPortFilterForm',
    'RegionFilterForm',
    'SiteFilterForm',
    'SiteGroupFilterForm',
    'VirtualChassisFilterForm',
)


class DeviceComponentFilterForm(NetBoxModelFilterSetForm):
    name = forms.CharField(
        required=False
    )
    label = forms.CharField(
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
        query_params={
            'region_id': '$region_id',
            'group_id': '$site_group_id',
        },
        label=_('Site')
    )
    location_id = DynamicModelMultipleChoiceField(
        queryset=Location.objects.all(),
        required=False,
        query_params={
            'site_id': '$site_id',
        },
        label=_('Location')
    )
    virtual_chassis_id = DynamicModelMultipleChoiceField(
        queryset=VirtualChassis.objects.all(),
        required=False,
        label=_('Virtual Chassis')
    )
    device_id = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        required=False,
        query_params={
            'site_id': '$site_id',
            'location_id': '$location_id',
            'virtual_chassis_id': '$virtual_chassis_id'
        },
        label=_('Device')
    )


class RegionFilterForm(NetBoxModelFilterSetForm):
    model = Region
    parent_id = DynamicModelMultipleChoiceField(
        queryset=Region.objects.all(),
        required=False,
        label=_('Parent region')
    )
    tag = TagFilterField(model)


class SiteGroupFilterForm(NetBoxModelFilterSetForm):
    model = SiteGroup
    parent_id = DynamicModelMultipleChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False,
        label=_('Parent group')
    )
    tag = TagFilterField(model)


class SiteFilterForm(TenancyFilterForm, NetBoxModelFilterSetForm):
    model = Site
    fieldsets = (
        (None, ('q', 'tag')),
        ('Attributes', ('status', 'region_id', 'group_id', 'asn_id')),
        ('Tenant', ('tenant_group_id', 'tenant_id')),
    )
    status = forms.MultipleChoiceField(
        choices=SiteStatusChoices,
        required=False,
        widget=StaticSelectMultiple(),
    )
    region_id = DynamicModelMultipleChoiceField(
        queryset=Region.objects.all(),
        required=False,
        label=_('Region')
    )
    group_id = DynamicModelMultipleChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False,
        label=_('Site group')
    )
    asn_id = DynamicModelMultipleChoiceField(
        queryset=ASN.objects.all(),
        required=False,
        label=_('ASNs')
    )
    tag = TagFilterField(model)


class LocationFilterForm(TenancyFilterForm, NetBoxModelFilterSetForm):
    model = Location
    fieldsets = (
        (None, ('q', 'tag')),
        ('Parent', ('region_id', 'site_group_id', 'site_id', 'parent_id')),
        ('Tenant', ('tenant_group_id', 'tenant_id')),
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
        query_params={
            'region_id': '$region_id',
            'group_id': '$site_group_id',
        },
        label=_('Site')
    )
    parent_id = DynamicModelMultipleChoiceField(
        queryset=Location.objects.all(),
        required=False,
        query_params={
            'region_id': '$region_id',
            'site_id': '$site_id',
        },
        label=_('Parent')
    )
    tag = TagFilterField(model)


class RackRoleFilterForm(NetBoxModelFilterSetForm):
    model = RackRole
    tag = TagFilterField(model)


class RackFilterForm(TenancyFilterForm, NetBoxModelFilterSetForm):
    model = Rack
    fieldsets = (
        (None, ('q', 'tag')),
        ('Location', ('region_id', 'site_id', 'location_id')),
        ('Function', ('status', 'role_id')),
        ('Hardware', ('type', 'width', 'serial', 'asset_tag')),
        ('Tenant', ('tenant_group_id', 'tenant_id')),
    )
    region_id = DynamicModelMultipleChoiceField(
        queryset=Region.objects.all(),
        required=False,
        label=_('Region')
    )
    site_id = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        query_params={
            'region_id': '$region_id'
        },
        label=_('Site')
    )
    location_id = DynamicModelMultipleChoiceField(
        queryset=Location.objects.all(),
        required=False,
        null_option='None',
        query_params={
            'site_id': '$site_id'
        },
        label=_('Location')
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
        label=_('Role')
    )
    serial = forms.CharField(
        required=False
    )
    asset_tag = forms.CharField(
        required=False
    )
    tag = TagFilterField(model)


class RackElevationFilterForm(RackFilterForm):
    id = DynamicModelMultipleChoiceField(
        queryset=Rack.objects.all(),
        label=_('Rack'),
        required=False,
        query_params={
            'site_id': '$site_id',
            'location_id': '$location_id',
        }
    )


class RackReservationFilterForm(TenancyFilterForm, NetBoxModelFilterSetForm):
    model = RackReservation
    fieldsets = (
        (None, ('q', 'tag')),
        ('User', ('user_id',)),
        ('Rack', ('region_id', 'site_id', 'location_id')),
        ('Tenant', ('tenant_group_id', 'tenant_id')),
    )
    region_id = DynamicModelMultipleChoiceField(
        queryset=Region.objects.all(),
        required=False,
        label=_('Region')
    )
    site_id = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        query_params={
            'region_id': '$region_id'
        },
        label=_('Site')
    )
    location_id = DynamicModelMultipleChoiceField(
        queryset=Location.objects.prefetch_related('site'),
        required=False,
        label=_('Location'),
        null_option='None'
    )
    user_id = DynamicModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        label=_('User'),
        widget=APISelectMultiple(
            api_url='/api/users/users/',
        )
    )
    tag = TagFilterField(model)


class ManufacturerFilterForm(NetBoxModelFilterSetForm):
    model = Manufacturer
    tag = TagFilterField(model)


class DeviceTypeFilterForm(NetBoxModelFilterSetForm):
    model = DeviceType
    fieldsets = (
        (None, ('q', 'tag')),
        ('Hardware', ('manufacturer_id', 'part_number', 'subdevice_role', 'airflow')),
        ('Components', (
            'console_ports', 'console_server_ports', 'power_ports', 'power_outlets', 'interfaces',
            'pass_through_ports',
        )),
    )
    manufacturer_id = DynamicModelMultipleChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False,
        label=_('Manufacturer')
    )
    part_number = forms.CharField(
        required=False
    )
    subdevice_role = forms.MultipleChoiceField(
        choices=add_blank_choice(SubdeviceRoleChoices),
        required=False,
        widget=StaticSelectMultiple()
    )
    airflow = forms.MultipleChoiceField(
        choices=add_blank_choice(DeviceAirflowChoices),
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


class ModuleTypeFilterForm(NetBoxModelFilterSetForm):
    model = ModuleType
    fieldsets = (
        (None, ('q', 'tag')),
        ('Hardware', ('manufacturer_id', 'part_number')),
        ('Components', (
            'console_ports', 'console_server_ports', 'power_ports', 'power_outlets', 'interfaces',
            'pass_through_ports',
        )),
    )
    manufacturer_id = DynamicModelMultipleChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False,
        label=_('Manufacturer'),
        fetch_trigger='open'
    )
    part_number = forms.CharField(
        required=False
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


class DeviceRoleFilterForm(NetBoxModelFilterSetForm):
    model = DeviceRole
    tag = TagFilterField(model)


class PlatformFilterForm(NetBoxModelFilterSetForm):
    model = Platform
    manufacturer_id = DynamicModelMultipleChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False,
        label=_('Manufacturer')
    )
    tag = TagFilterField(model)


class DeviceFilterForm(LocalConfigContextFilterForm, TenancyFilterForm, NetBoxModelFilterSetForm):
    model = Device
    fieldsets = (
        (None, ('q', 'tag')),
        ('Location', ('region_id', 'site_group_id', 'site_id', 'location_id', 'rack_id')),
        ('Operation', ('status', 'role_id', 'airflow', 'serial', 'asset_tag', 'mac_address')),
        ('Hardware', ('manufacturer_id', 'device_type_id', 'platform_id')),
        ('Tenant', ('tenant_group_id', 'tenant_id')),
        ('Components', (
            'console_ports', 'console_server_ports', 'power_ports', 'power_outlets', 'interfaces', 'pass_through_ports',
        )),
        ('Miscellaneous', ('has_primary_ip', 'virtual_chassis_member', 'local_context_data'))
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
        query_params={
            'region_id': '$region_id',
            'group_id': '$site_group_id',
        },
        label=_('Site')
    )
    location_id = DynamicModelMultipleChoiceField(
        queryset=Location.objects.all(),
        required=False,
        null_option='None',
        query_params={
            'site_id': '$site_id'
        },
        label=_('Location')
    )
    rack_id = DynamicModelMultipleChoiceField(
        queryset=Rack.objects.all(),
        required=False,
        null_option='None',
        query_params={
            'site_id': '$site_id',
            'location_id': '$location_id',
        },
        label=_('Rack')
    )
    role_id = DynamicModelMultipleChoiceField(
        queryset=DeviceRole.objects.all(),
        required=False,
        label=_('Role')
    )
    manufacturer_id = DynamicModelMultipleChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False,
        label=_('Manufacturer')
    )
    device_type_id = DynamicModelMultipleChoiceField(
        queryset=DeviceType.objects.all(),
        required=False,
        query_params={
            'manufacturer_id': '$manufacturer_id'
        },
        label=_('Model')
    )
    platform_id = DynamicModelMultipleChoiceField(
        queryset=Platform.objects.all(),
        required=False,
        null_option='None',
        label=_('Platform')
    )
    status = forms.MultipleChoiceField(
        choices=DeviceStatusChoices,
        required=False,
        widget=StaticSelectMultiple()
    )
    airflow = forms.MultipleChoiceField(
        choices=add_blank_choice(DeviceAirflowChoices),
        required=False,
        widget=StaticSelectMultiple()
    )
    serial = forms.CharField(
        required=False
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


class ModuleFilterForm(LocalConfigContextFilterForm, TenancyFilterForm, NetBoxModelFilterSetForm):
    model = Module
    fieldsets = (
        (None, ('q', 'tag')),
        ('Hardware', ('manufacturer_id', 'module_type_id', 'serial', 'asset_tag')),
    )
    manufacturer_id = DynamicModelMultipleChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False,
        label=_('Manufacturer'),
        fetch_trigger='open'
    )
    module_type_id = DynamicModelMultipleChoiceField(
        queryset=ModuleType.objects.all(),
        required=False,
        query_params={
            'manufacturer_id': '$manufacturer_id'
        },
        label=_('Type'),
        fetch_trigger='open'
    )
    serial = forms.CharField(
        required=False
    )
    asset_tag = forms.CharField(
        required=False
    )
    tag = TagFilterField(model)


class VirtualChassisFilterForm(TenancyFilterForm, NetBoxModelFilterSetForm):
    model = VirtualChassis
    fieldsets = (
        (None, ('q', 'tag')),
        ('Location', ('region_id', 'site_group_id', 'site_id')),
        ('Tenant', ('tenant_group_id', 'tenant_id')),
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
        query_params={
            'region_id': '$region_id',
            'group_id': '$site_group_id',
        },
        label=_('Site')
    )
    tag = TagFilterField(model)


class CableFilterForm(TenancyFilterForm, NetBoxModelFilterSetForm):
    model = Cable
    fieldsets = (
        (None, ('q', 'tag')),
        ('Location', ('site_id', 'rack_id', 'device_id')),
        ('Attributes', ('type', 'status', 'color', 'length', 'length_unit')),
        ('Tenant', ('tenant_group_id', 'tenant_id')),
    )
    region_id = DynamicModelMultipleChoiceField(
        queryset=Region.objects.all(),
        required=False,
        label=_('Region')
    )
    site_id = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        query_params={
            'region_id': '$region_id'
        },
        label=_('Site')
    )
    rack_id = DynamicModelMultipleChoiceField(
        queryset=Rack.objects.all(),
        required=False,
        label=_('Rack'),
        null_option='None',
        query_params={
            'site_id': '$site_id'
        }
    )
    device_id = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        required=False,
        query_params={
            'site_id': '$site_id',
            'tenant_id': '$tenant_id',
            'rack_id': '$rack_id',
        },
        label=_('Device')
    )
    type = forms.MultipleChoiceField(
        choices=add_blank_choice(CableTypeChoices),
        required=False,
        widget=StaticSelect()
    )
    status = forms.ChoiceField(
        required=False,
        choices=add_blank_choice(LinkStatusChoices),
        widget=StaticSelect()
    )
    color = ColorField(
        required=False
    )
    length = forms.IntegerField(
        required=False
    )
    length_unit = forms.ChoiceField(
        choices=add_blank_choice(CableLengthUnitChoices),
        required=False
    )
    tag = TagFilterField(model)


class PowerPanelFilterForm(NetBoxModelFilterSetForm):
    model = PowerPanel
    fieldsets = (
        (None, ('q', 'tag')),
        ('Location', ('region_id', 'site_group_id', 'site_id', 'location_id'))
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
        query_params={
            'region_id': '$region_id',
            'group_id': '$site_group_id',
        },
        label=_('Site')
    )
    location_id = DynamicModelMultipleChoiceField(
        queryset=Location.objects.all(),
        required=False,
        null_option='None',
        query_params={
            'site_id': '$site_id'
        },
        label=_('Location')
    )
    tag = TagFilterField(model)


class PowerFeedFilterForm(NetBoxModelFilterSetForm):
    model = PowerFeed
    fieldsets = (
        (None, ('q', 'tag')),
        ('Location', ('region_id', 'site_group_id', 'site_id', 'power_panel_id', 'rack_id')),
        ('Attributes', ('status', 'type', 'supply', 'phase', 'voltage', 'amperage', 'max_utilization')),
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
        query_params={
            'region_id': '$region_id'
        },
        label=_('Site')
    )
    power_panel_id = DynamicModelMultipleChoiceField(
        queryset=PowerPanel.objects.all(),
        required=False,
        null_option='None',
        query_params={
            'site_id': '$site_id'
        },
        label=_('Power panel')
    )
    rack_id = DynamicModelMultipleChoiceField(
        queryset=Rack.objects.all(),
        required=False,
        null_option='None',
        query_params={
            'site_id': '$site_id'
        },
        label=_('Rack')
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


#
# Device components
#

class ConsolePortFilterForm(DeviceComponentFilterForm):
    model = ConsolePort
    fieldsets = (
        (None, ('q', 'tag')),
        ('Attributes', ('name', 'label', 'type', 'speed')),
        ('Device', ('region_id', 'site_group_id', 'site_id', 'location_id', 'virtual_chassis_id', 'device_id')),
    )
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


class ConsoleServerPortFilterForm(DeviceComponentFilterForm):
    model = ConsoleServerPort
    fieldsets = (
        (None, ('q', 'tag')),
        ('Attributes', ('name', 'label', 'type', 'speed')),
        ('Device', ('region_id', 'site_group_id', 'site_id', 'location_id', 'virtual_chassis_id', 'device_id')),
    )
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


class PowerPortFilterForm(DeviceComponentFilterForm):
    model = PowerPort
    fieldsets = (
        (None, ('q', 'tag')),
        ('Attributes', ('name', 'label', 'type')),
        ('Device', ('region_id', 'site_group_id', 'site_id', 'location_id', 'virtual_chassis_id', 'device_id')),
    )
    type = forms.MultipleChoiceField(
        choices=PowerPortTypeChoices,
        required=False,
        widget=StaticSelectMultiple()
    )
    tag = TagFilterField(model)


class PowerOutletFilterForm(DeviceComponentFilterForm):
    model = PowerOutlet
    fieldsets = (
        (None, ('q', 'tag')),
        ('Attributes', ('name', 'label', 'type')),
        ('Device', ('region_id', 'site_group_id', 'site_id', 'location_id', 'virtual_chassis_id', 'device_id')),
    )
    type = forms.MultipleChoiceField(
        choices=PowerOutletTypeChoices,
        required=False,
        widget=StaticSelectMultiple()
    )
    tag = TagFilterField(model)


class InterfaceFilterForm(DeviceComponentFilterForm):
    model = Interface
    fieldsets = (
        (None, ('q', 'tag')),
        ('Attributes', ('name', 'label', 'kind', 'type', 'speed', 'duplex', 'enabled', 'mgmt_only')),
        ('Addressing', ('vrf_id', 'mac_address', 'wwn')),
        ('Wireless', ('rf_role', 'rf_channel', 'rf_channel_width', 'tx_power')),
        ('Device', ('region_id', 'site_group_id', 'site_id', 'location_id', 'virtual_chassis_id', 'device_id')),
    )
    kind = forms.MultipleChoiceField(
        choices=InterfaceKindChoices,
        required=False,
        widget=StaticSelectMultiple()
    )
    type = forms.MultipleChoiceField(
        choices=InterfaceTypeChoices,
        required=False,
        widget=StaticSelectMultiple()
    )
    speed = forms.IntegerField(
        required=False,
        label='Select Speed',
        widget=SelectSpeedWidget(attrs={'readonly': None})
    )
    duplex = forms.MultipleChoiceField(
        choices=InterfaceDuplexChoices,
        required=False,
        label='Select Duplex',
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
    wwn = forms.CharField(
        required=False,
        label='WWN'
    )
    rf_role = forms.MultipleChoiceField(
        choices=WirelessRoleChoices,
        required=False,
        widget=StaticSelectMultiple(),
        label='Wireless role'
    )
    rf_channel = forms.MultipleChoiceField(
        choices=WirelessChannelChoices,
        required=False,
        widget=StaticSelectMultiple(),
        label='Wireless channel'
    )
    rf_channel_frequency = forms.IntegerField(
        required=False,
        label='Channel frequency (MHz)'
    )
    rf_channel_width = forms.IntegerField(
        required=False,
        label='Channel width (MHz)'
    )
    tx_power = forms.IntegerField(
        required=False,
        label='Transmit power (dBm)',
        min_value=0,
        max_value=127
    )
    vrf_id = DynamicModelMultipleChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label='VRF'
    )
    tag = TagFilterField(model)


class FrontPortFilterForm(DeviceComponentFilterForm):
    fieldsets = (
        (None, ('q', 'tag')),
        ('Attributes', ('name', 'label', 'type', 'color')),
        ('Device', ('region_id', 'site_group_id', 'site_id', 'location_id', 'virtual_chassis_id', 'device_id')),
    )
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


class RearPortFilterForm(DeviceComponentFilterForm):
    model = RearPort
    fieldsets = (
        (None, ('q', 'tag')),
        ('Attributes', ('name', 'label', 'type', 'color')),
        ('Device', ('region_id', 'site_group_id', 'site_id', 'location_id', 'virtual_chassis_id', 'device_id')),
    )
    type = forms.MultipleChoiceField(
        choices=PortTypeChoices,
        required=False,
        widget=StaticSelectMultiple()
    )
    color = ColorField(
        required=False
    )
    tag = TagFilterField(model)


class ModuleBayFilterForm(DeviceComponentFilterForm):
    model = ModuleBay
    fieldsets = (
        (None, ('q', 'tag')),
        ('Attributes', ('name', 'label', 'position')),
        ('Device', ('region_id', 'site_group_id', 'site_id', 'location_id', 'virtual_chassis_id', 'device_id')),
    )
    tag = TagFilterField(model)
    position = forms.CharField(
        required=False
    )


class DeviceBayFilterForm(DeviceComponentFilterForm):
    model = DeviceBay
    fieldsets = (
        (None, ('q', 'tag')),
        ('Attributes', ('name', 'label')),
        ('Device', ('region_id', 'site_group_id', 'site_id', 'location_id', 'virtual_chassis_id', 'device_id')),
    )
    tag = TagFilterField(model)


class InventoryItemFilterForm(DeviceComponentFilterForm):
    model = InventoryItem
    fieldsets = (
        (None, ('q', 'tag')),
        ('Attributes', ('name', 'label', 'manufacturer_id', 'serial', 'asset_tag', 'discovered')),
        ('Device', ('region_id', 'site_group_id', 'site_id', 'location_id', 'virtual_chassis_id', 'device_id')),
    )
    role_id = DynamicModelMultipleChoiceField(
        queryset=InventoryItemRole.objects.all(),
        required=False,
        label=_('Role'),
        fetch_trigger='open'
    )
    manufacturer_id = DynamicModelMultipleChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False,
        label=_('Manufacturer')
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
# Device component roles
#

class InventoryItemRoleFilterForm(NetBoxModelFilterSetForm):
    model = InventoryItemRole
    tag = TagFilterField(model)


#
# Connections
#

class ConsoleConnectionFilterForm(FilterForm):
    region_id = DynamicModelMultipleChoiceField(
        queryset=Region.objects.all(),
        required=False,
        label=_('Region')
    )
    site_id = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        query_params={
            'region_id': '$region_id'
        },
        label=_('Site')
    )
    device_id = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        required=False,
        query_params={
            'site_id': '$site_id'
        },
        label=_('Device')
    )


class PowerConnectionFilterForm(FilterForm):
    region_id = DynamicModelMultipleChoiceField(
        queryset=Region.objects.all(),
        required=False,
        label=_('Region')
    )
    site_id = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        query_params={
            'region_id': '$region_id'
        },
        label=_('Site')
    )
    device_id = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        required=False,
        query_params={
            'site_id': '$site_id'
        },
        label=_('Device')
    )


class InterfaceConnectionFilterForm(FilterForm):
    region_id = DynamicModelMultipleChoiceField(
        queryset=Region.objects.all(),
        required=False,
        label=_('Region')
    )
    site_id = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        query_params={
            'region_id': '$region_id'
        },
        label=_('Site')
    )
    device_id = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        required=False,
        query_params={
            'site_id': '$site_id'
        },
        label=_('Device')
    )
