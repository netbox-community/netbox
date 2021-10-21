from django import forms
from django.contrib.auth.models import User
from django.utils.translation import gettext as _

from dcim.choices import *
from dcim.constants import *
from dcim.models import *
from extras.forms import CustomFieldModelFilterForm, LocalConfigContextFilterForm
from tenancy.forms import TenancyFilterForm
from utilities.forms import (
    APISelectMultiple, add_blank_choice, BootstrapMixin, ColorField, DynamicModelMultipleChoiceField, StaticSelect,
    StaticSelectMultiple, TagFilterField, BOOLEAN_WITH_BLANK_CHOICES,
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
    'LocationFilterForm',
    'ManufacturerFilterForm',
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


class RegionFilterForm(BootstrapMixin, CustomFieldModelFilterForm):
    model = Region
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
    tag = TagFilterField(model)


class SiteGroupFilterForm(BootstrapMixin, CustomFieldModelFilterForm):
    model = SiteGroup
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
    tag = TagFilterField(model)


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


class LocationFilterForm(BootstrapMixin, TenancyFilterForm, CustomFieldModelFilterForm):
    model = Location
    field_groups = [
        ['q'],
        ['region_id', 'site_group_id', 'site_id', 'parent_id'],
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
    tag = TagFilterField(model)


class RackRoleFilterForm(BootstrapMixin, CustomFieldModelFilterForm):
    model = RackRole
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': _('All Fields')}),
        label=_('Search')
    )
    tag = TagFilterField(model)


class RackFilterForm(BootstrapMixin, TenancyFilterForm, CustomFieldModelFilterForm):
    model = Rack
    field_order = ['q', 'region_id', 'site_id', 'location_id', 'status', 'role_id', 'tenant_group_id', 'tenant_id']
    field_groups = [
        ['q', 'tag'],
        ['region_id', 'site_id', 'location_id'],
        ['status', 'role_id'],
        ['type', 'width', 'serial', 'asset_tag'],
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
    serial = forms.CharField(
        required=False
    )
    asset_tag = forms.CharField(
        required=False
    )
    tag = TagFilterField(model)


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


class ManufacturerFilterForm(BootstrapMixin, CustomFieldModelFilterForm):
    model = Manufacturer
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': _('All Fields')}),
        label=_('Search')
    )
    tag = TagFilterField(model)


class DeviceTypeFilterForm(BootstrapMixin, CustomFieldModelFilterForm):
    model = DeviceType
    field_groups = [
        ['q', 'tag'],
        ['manufacturer_id', 'subdevice_role', 'airflow'],
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


class DeviceRoleFilterForm(BootstrapMixin, CustomFieldModelFilterForm):
    model = DeviceRole
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': _('All Fields')}),
        label=_('Search')
    )
    tag = TagFilterField(model)


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
    tag = TagFilterField(model)


class DeviceFilterForm(BootstrapMixin, LocalConfigContextFilterForm, TenancyFilterForm, CustomFieldModelFilterForm):
    model = Device
    field_order = [
        'q', 'region_id', 'site_group_id', 'site_id', 'location_id', 'rack_id', 'status', 'role_id', 'tenant_group_id',
        'tenant_id', 'manufacturer_id', 'device_type_id', 'asset_tag', 'mac_address', 'has_primary_ip',
    ]
    field_groups = [
        ['q', 'tag'],
        ['region_id', 'site_group_id', 'site_id', 'location_id', 'rack_id'],
        ['status', 'role_id', 'airflow', 'serial', 'asset_tag', 'mac_address'],
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


class CableFilterForm(BootstrapMixin, TenancyFilterForm, CustomFieldModelFilterForm):
    model = Cable
    field_groups = [
        ['q', 'tag'],
        ['site_id', 'rack_id', 'device_id'],
        ['type', 'status', 'color'],
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
        choices=add_blank_choice(LinkStatusChoices),
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


#
# Device components
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


class InterfaceFilterForm(DeviceComponentFilterForm):
    model = Interface
    field_groups = [
        ['q', 'tag'],
        ['name', 'label', 'kind', 'type', 'enabled', 'mgmt_only', 'mac_address', 'wwn'],
        ['rf_role', 'rf_channel', 'rf_channel_width'],
        ['region_id', 'site_group_id', 'site_id', 'location_id', 'device_id'],
    ]
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
    tag = TagFilterField(model)


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


class DeviceBayFilterForm(DeviceComponentFilterForm):
    model = DeviceBay
    field_groups = [
        ['q', 'tag'],
        ['name', 'label'],
        ['region_id', 'site_group_id', 'site_id', 'location_id', 'device_id'],
    ]
    tag = TagFilterField(model)


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
