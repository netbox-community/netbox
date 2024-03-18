from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from dcim.choices import *
from dcim.constants import *
from dcim.models import *
from extras.forms import LocalConfigContextFilterForm
from extras.models import ConfigTemplate
from ipam.models import ASN, VRF
from netbox.forms import NetBoxModelFilterSetForm
from tenancy.forms import ContactModelFilterForm, TenancyFilterForm
from utilities.forms import BOOLEAN_WITH_BLANK_CHOICES, FilterForm, add_blank_choice
from utilities.forms.fields import ColorField, DynamicModelMultipleChoiceField, TagFilterField
from utilities.forms.rendering import FieldSet
from utilities.forms.widgets import NumberWithOptions
from vpn.models import L2VPN
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
    'VirtualDeviceContextFilterForm'
)


class DeviceComponentFilterForm(NetBoxModelFilterSetForm):
    name = forms.CharField(
        label=_('Name'),
        required=False
    )
    label = forms.CharField(
        label=_('Label'),
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
    rack_id = DynamicModelMultipleChoiceField(
        queryset=Rack.objects.all(),
        required=False,
        query_params={
            'site_id': '$site_id',
            'location_id': '$location_id',
        },
        label=_('Rack')
    )
    virtual_chassis_id = DynamicModelMultipleChoiceField(
        queryset=VirtualChassis.objects.all(),
        required=False,
        label=_('Virtual Chassis')
    )
    device_type_id = DynamicModelMultipleChoiceField(
        queryset=DeviceType.objects.all(),
        required=False,
        label=_('Device type')
    )
    device_role_id = DynamicModelMultipleChoiceField(
        queryset=DeviceRole.objects.all(),
        required=False,
        label=_('Device role')
    )
    device_id = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        required=False,
        query_params={
            'site_id': '$site_id',
            'location_id': '$location_id',
            'virtual_chassis_id': '$virtual_chassis_id',
            'device_type_id': '$device_type_id',
            'role_id': '$role_id'
        },
        label=_('Device')
    )


class RegionFilterForm(ContactModelFilterForm, NetBoxModelFilterSetForm):
    model = Region
    fieldsets = (
        FieldSet('q', 'filter_id', 'tag', 'parent_id'),
        FieldSet('contact', 'contact_role', 'contact_group', name=_('Contacts'))
    )
    parent_id = DynamicModelMultipleChoiceField(
        queryset=Region.objects.all(),
        required=False,
        label=_('Parent region')
    )
    tag = TagFilterField(model)


class SiteGroupFilterForm(ContactModelFilterForm, NetBoxModelFilterSetForm):
    model = SiteGroup
    fieldsets = (
        FieldSet('q', 'filter_id', 'tag', 'parent_id'),
        FieldSet('contact', 'contact_role', 'contact_group', name=_('Contacts'))
    )
    parent_id = DynamicModelMultipleChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False,
        label=_('Parent group')
    )
    tag = TagFilterField(model)


class SiteFilterForm(TenancyFilterForm, ContactModelFilterForm, NetBoxModelFilterSetForm):
    model = Site
    fieldsets = (
        FieldSet('q', 'filter_id', 'tag'),
        FieldSet('status', 'region_id', 'group_id', 'asn_id', name=_('Attributes')),
        FieldSet('tenant_group_id', 'tenant_id', name=_('Tenant')),
        FieldSet('contact', 'contact_role', 'contact_group', name=_('Contacts')),
    )
    selector_fields = ('filter_id', 'q', 'region_id', 'group_id')
    status = forms.MultipleChoiceField(
        label=_('Status'),
        choices=SiteStatusChoices,
        required=False
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


class LocationFilterForm(TenancyFilterForm, ContactModelFilterForm, NetBoxModelFilterSetForm):
    model = Location
    fieldsets = (
        FieldSet('q', 'filter_id', 'tag'),
        FieldSet('region_id', 'site_group_id', 'site_id', 'parent_id', 'status', name=_('Attributes')),
        FieldSet('tenant_group_id', 'tenant_id', name=_('Tenant')),
        FieldSet('contact', 'contact_role', 'contact_group', name=_('Contacts')),
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
    status = forms.MultipleChoiceField(
        label=_('Status'),
        choices=LocationStatusChoices,
        required=False
    )
    tag = TagFilterField(model)


class RackRoleFilterForm(NetBoxModelFilterSetForm):
    model = RackRole
    tag = TagFilterField(model)


class RackFilterForm(TenancyFilterForm, ContactModelFilterForm, NetBoxModelFilterSetForm):
    model = Rack
    fieldsets = (
        FieldSet('q', 'filter_id', 'tag'),
        FieldSet('region_id', 'site_group_id', 'site_id', 'location_id', name=_('Location')),
        FieldSet('status', 'role_id', name=_('Function')),
        FieldSet('type', 'width', 'serial', 'asset_tag', name=_('Hardware')),
        FieldSet('tenant_group_id', 'tenant_id', name=_('Tenant')),
        FieldSet('contact', 'contact_role', 'contact_group', name=_('Contacts')),
        FieldSet('weight', 'max_weight', 'weight_unit', name=_('Weight')),
    )
    selector_fields = ('filter_id', 'q', 'region_id', 'site_group_id', 'site_id', 'location_id')
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
    site_group_id = DynamicModelMultipleChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False,
        label=_('Site group')
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
        label=_('Status'),
        choices=RackStatusChoices,
        required=False
    )
    type = forms.MultipleChoiceField(
        label=_('Type'),
        choices=RackTypeChoices,
        required=False
    )
    width = forms.MultipleChoiceField(
        label=_('Width'),
        choices=RackWidthChoices,
        required=False
    )
    role_id = DynamicModelMultipleChoiceField(
        queryset=RackRole.objects.all(),
        required=False,
        null_option='None',
        label=_('Role')
    )
    serial = forms.CharField(
        label=_('Serial'),
        required=False
    )
    asset_tag = forms.CharField(
        label=_('Asset tag'),
        required=False
    )
    tag = TagFilterField(model)
    weight = forms.DecimalField(
        label=_('Weight'),
        required=False,
        min_value=1
    )
    max_weight = forms.IntegerField(
        label=_('Max weight'),
        required=False,
        min_value=1
    )
    weight_unit = forms.ChoiceField(
        label=_('Weight unit'),
        choices=add_blank_choice(WeightUnitChoices),
        required=False
    )


class RackElevationFilterForm(RackFilterForm):
    fieldsets = (
        FieldSet('q', 'filter_id', 'tag'),
        FieldSet('region_id', 'site_group_id', 'site_id', 'location_id', 'id', name=_('Location')),
        FieldSet('status', 'role_id', name=_('Function')),
        FieldSet('type', 'width', 'serial', 'asset_tag', name=_('Hardware')),
        FieldSet('tenant_group_id', 'tenant_id', name=_('Tenant')),
        FieldSet('contact', 'contact_role', 'contact_group', name=_('Contacts')),
        FieldSet('weight', 'max_weight', 'weight_unit', name=_('Weight')),
    )
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
        FieldSet('q', 'filter_id', 'tag'),
        FieldSet('user_id', name=_('User')),
        FieldSet('region_id', 'site_group_id', 'site_id', 'location_id', 'rack_id', name=_('Rack')),
        FieldSet('tenant_group_id', 'tenant_id', name=_('Tenant')),
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
        label=_('Location'),
        null_option='None'
    )
    rack_id = DynamicModelMultipleChoiceField(
        queryset=Rack.objects.all(),
        required=False,
        query_params={
            'site_id': '$site_id',
            'location_id': '$location_id',
        },
        label=_('Rack')
    )
    user_id = DynamicModelMultipleChoiceField(
        queryset=get_user_model().objects.all(),
        required=False,
        label=_('User')
    )
    tag = TagFilterField(model)


class ManufacturerFilterForm(ContactModelFilterForm, NetBoxModelFilterSetForm):
    model = Manufacturer
    fieldsets = (
        FieldSet('q', 'filter_id', 'tag'),
        FieldSet('contact', 'contact_role', 'contact_group', name=_('Contacts'))
    )
    tag = TagFilterField(model)


class DeviceTypeFilterForm(NetBoxModelFilterSetForm):
    model = DeviceType
    fieldsets = (
        FieldSet('q', 'filter_id', 'tag'),
        FieldSet(
            'manufacturer_id', 'default_platform_id', 'part_number', 'subdevice_role', 'airflow', name=_('Hardware')
        ),
        FieldSet('has_front_image', 'has_rear_image', name=_('Images')),
        FieldSet(
            'console_ports', 'console_server_ports', 'power_ports', 'power_outlets', 'interfaces',
            'pass_through_ports', 'device_bays', 'module_bays', 'inventory_items', name=_('Components')
        ),
        FieldSet('weight', 'weight_unit', name=_('Weight')),
    )
    selector_fields = ('filter_id', 'q', 'manufacturer_id')
    manufacturer_id = DynamicModelMultipleChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False,
        label=_('Manufacturer')
    )
    default_platform_id = DynamicModelMultipleChoiceField(
        queryset=Platform.objects.all(),
        required=False,
        label=_('Default platform')
    )
    part_number = forms.CharField(
        label=_('Part number'),
        required=False
    )
    subdevice_role = forms.MultipleChoiceField(
        label=_('Subdevice role'),
        choices=add_blank_choice(SubdeviceRoleChoices),
        required=False
    )
    airflow = forms.MultipleChoiceField(
        label=_('Airflow'),
        choices=add_blank_choice(DeviceAirflowChoices),
        required=False
    )
    has_front_image = forms.NullBooleanField(
        required=False,
        label=_('Has a front image'),
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    has_rear_image = forms.NullBooleanField(
        required=False,
        label=_('Has a rear image'),
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    console_ports = forms.NullBooleanField(
        required=False,
        label=_('Has console ports'),
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    console_server_ports = forms.NullBooleanField(
        required=False,
        label=_('Has console server ports'),
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    power_ports = forms.NullBooleanField(
        required=False,
        label=_('Has power ports'),
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    power_outlets = forms.NullBooleanField(
        required=False,
        label=_('Has power outlets'),
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    interfaces = forms.NullBooleanField(
        required=False,
        label=_('Has interfaces'),
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    pass_through_ports = forms.NullBooleanField(
        required=False,
        label=_('Has pass-through ports'),
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    device_bays = forms.NullBooleanField(
        required=False,
        label=_('Has device bays'),
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    module_bays = forms.NullBooleanField(
        required=False,
        label=_('Has module bays'),
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    inventory_items = forms.NullBooleanField(
        required=False,
        label=_('Has inventory items'),
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    tag = TagFilterField(model)
    weight = forms.DecimalField(
        label=_('Weight'),
        required=False
    )
    weight_unit = forms.ChoiceField(
        label=_('Weight unit'),
        choices=add_blank_choice(WeightUnitChoices),
        required=False
    )


class ModuleTypeFilterForm(NetBoxModelFilterSetForm):
    model = ModuleType
    fieldsets = (
        FieldSet('q', 'filter_id', 'tag'),
        FieldSet('manufacturer_id', 'part_number', name=_('Hardware')),
        FieldSet(
            'console_ports', 'console_server_ports', 'power_ports', 'power_outlets', 'interfaces',
            'pass_through_ports', name=_('Components')
        ),
        FieldSet('weight', 'weight_unit', name=_('Weight')),
    )
    selector_fields = ('filter_id', 'q', 'manufacturer_id')
    manufacturer_id = DynamicModelMultipleChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False,
        label=_('Manufacturer')
    )
    part_number = forms.CharField(
        label=_('Part number'),
        required=False
    )
    console_ports = forms.NullBooleanField(
        required=False,
        label=_('Has console ports'),
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    console_server_ports = forms.NullBooleanField(
        required=False,
        label=_('Has console server ports'),
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    power_ports = forms.NullBooleanField(
        required=False,
        label=_('Has power ports'),
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    power_outlets = forms.NullBooleanField(
        required=False,
        label=_('Has power outlets'),
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    interfaces = forms.NullBooleanField(
        required=False,
        label=_('Has interfaces'),
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    pass_through_ports = forms.NullBooleanField(
        required=False,
        label=_('Has pass-through ports'),
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    tag = TagFilterField(model)
    weight = forms.DecimalField(
        label=_('Weight'),
        required=False
    )
    weight_unit = forms.ChoiceField(
        label=_('Weight unit'),
        choices=add_blank_choice(WeightUnitChoices),
        required=False
    )


class DeviceRoleFilterForm(NetBoxModelFilterSetForm):
    model = DeviceRole
    config_template_id = DynamicModelMultipleChoiceField(
        queryset=ConfigTemplate.objects.all(),
        required=False,
        label=_('Config template')
    )
    tag = TagFilterField(model)


class PlatformFilterForm(NetBoxModelFilterSetForm):
    model = Platform
    selector_fields = ('filter_id', 'q', 'manufacturer_id')
    manufacturer_id = DynamicModelMultipleChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False,
        label=_('Manufacturer')
    )
    config_template_id = DynamicModelMultipleChoiceField(
        queryset=ConfigTemplate.objects.all(),
        required=False,
        label=_('Config template')
    )
    tag = TagFilterField(model)


class DeviceFilterForm(
    LocalConfigContextFilterForm,
    TenancyFilterForm,
    ContactModelFilterForm,
    NetBoxModelFilterSetForm
):
    model = Device
    fieldsets = (
        FieldSet('q', 'filter_id', 'tag'),
        FieldSet('region_id', 'site_group_id', 'site_id', 'location_id', 'rack_id', name=_('Location')),
        FieldSet('status', 'role_id', 'airflow', 'serial', 'asset_tag', 'mac_address', name=_('Operation')),
        FieldSet('manufacturer_id', 'device_type_id', 'platform_id', name=_('Hardware')),
        FieldSet('tenant_group_id', 'tenant_id', name=_('Tenant')),
        FieldSet('contact', 'contact_role', 'contact_group', name=_('Contacts')),
        FieldSet(
            'console_ports', 'console_server_ports', 'power_ports', 'power_outlets', 'interfaces', 'pass_through_ports',
            name=_('Components')
        ),
        FieldSet(
            'has_primary_ip', 'has_oob_ip', 'virtual_chassis_member', 'config_template_id', 'local_context_data',
            name=_('Miscellaneous')
        )
    )
    selector_fields = ('filter_id', 'q', 'region_id', 'site_group_id', 'site_id', 'location_id', 'rack_id')
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
        label=_('Status'),
        choices=DeviceStatusChoices,
        required=False
    )
    airflow = forms.MultipleChoiceField(
        label=_('Airflow'),
        choices=add_blank_choice(DeviceAirflowChoices),
        required=False
    )
    serial = forms.CharField(
        label=_('Serial'),
        required=False
    )
    asset_tag = forms.CharField(
        label=_('Asset tag'),
        required=False
    )
    mac_address = forms.CharField(
        required=False,
        label=_('MAC address')
    )
    config_template_id = DynamicModelMultipleChoiceField(
        queryset=ConfigTemplate.objects.all(),
        required=False,
        label=_('Config template')
    )
    has_primary_ip = forms.NullBooleanField(
        required=False,
        label=_('Has a primary IP'),
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    has_oob_ip = forms.NullBooleanField(
        required=False,
        label=_('Has an OOB IP'),
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    virtual_chassis_member = forms.NullBooleanField(
        required=False,
        label=_('Virtual chassis member'),
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    console_ports = forms.NullBooleanField(
        required=False,
        label=_('Has console ports'),
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    console_server_ports = forms.NullBooleanField(
        required=False,
        label=_('Has console server ports'),
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    power_ports = forms.NullBooleanField(
        required=False,
        label=_('Has power ports'),
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    power_outlets = forms.NullBooleanField(
        required=False,
        label=_('Has power outlets'),
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    interfaces = forms.NullBooleanField(
        required=False,
        label=_('Has interfaces'),
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    pass_through_ports = forms.NullBooleanField(
        required=False,
        label=_('Has pass-through ports'),
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    tag = TagFilterField(model)


class VirtualDeviceContextFilterForm(
    TenancyFilterForm,
    NetBoxModelFilterSetForm
):
    model = VirtualDeviceContext
    fieldsets = (
        FieldSet('q', 'filter_id', 'tag'),
        FieldSet('device', 'status', 'has_primary_ip', name=_('Attributes')),
        FieldSet('tenant_group_id', 'tenant_id', name=_('Tenant')),
    )
    device = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        required=False,
        label=_('Device')
    )
    status = forms.MultipleChoiceField(
        label=_('Status'),
        required=False,
        choices=add_blank_choice(VirtualDeviceContextStatusChoices)
    )
    has_primary_ip = forms.NullBooleanField(
        required=False,
        label=_('Has a primary IP'),
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    tag = TagFilterField(model)


class ModuleFilterForm(LocalConfigContextFilterForm, TenancyFilterForm, NetBoxModelFilterSetForm):
    model = Module
    fieldsets = (
        FieldSet('q', 'filter_id', 'tag'),
        FieldSet('manufacturer_id', 'module_type_id', 'status', 'serial', 'asset_tag', name=_('Hardware')),
    )
    manufacturer_id = DynamicModelMultipleChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False,
        label=_('Manufacturer')
    )
    module_type_id = DynamicModelMultipleChoiceField(
        queryset=ModuleType.objects.all(),
        required=False,
        query_params={
            'manufacturer_id': '$manufacturer_id'
        },
        label=_('Type')
    )
    status = forms.MultipleChoiceField(
        label=_('Status'),
        choices=ModuleStatusChoices,
        required=False
    )
    serial = forms.CharField(
        label=_('Serial'),
        required=False
    )
    asset_tag = forms.CharField(
        label=_('Asset tag'),
        required=False
    )
    tag = TagFilterField(model)


class VirtualChassisFilterForm(TenancyFilterForm, NetBoxModelFilterSetForm):
    model = VirtualChassis
    fieldsets = (
        FieldSet('q', 'filter_id', 'tag'),
        FieldSet('region_id', 'site_group_id', 'site_id', name=_('Location')),
        FieldSet('tenant_group_id', 'tenant_id', name=_('Tenant')),
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
        FieldSet('q', 'filter_id', 'tag'),
        FieldSet('site_id', 'location_id', 'rack_id', 'device_id', name=_('Location')),
        FieldSet('type', 'status', 'color', 'length', 'length_unit', 'unterminated', name=_('Attributes')),
        FieldSet('tenant_group_id', 'tenant_id', name=_('Tenant')),
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
        label=_('Location'),
        null_option='None',
        query_params={
            'site_id': '$site_id'
        }
    )
    rack_id = DynamicModelMultipleChoiceField(
        queryset=Rack.objects.all(),
        required=False,
        label=_('Rack'),
        null_option='None',
        query_params={
            'site_id': '$site_id',
            'location_id': '$location_id',
        }
    )
    device_id = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        required=False,
        query_params={
            'site_id': '$site_id',
            'location_id': '$location_id',
            'rack_id': '$rack_id',
            'tenant_id': '$tenant_id',
        },
        label=_('Device')
    )
    type = forms.MultipleChoiceField(
        label=_('Type'),
        choices=add_blank_choice(CableTypeChoices),
        required=False
    )
    status = forms.MultipleChoiceField(
        label=_('Status'),
        required=False,
        choices=add_blank_choice(LinkStatusChoices)
    )
    color = ColorField(
        label=_('Color'),
        required=False
    )
    length = forms.IntegerField(
        label=_('Length'),
        required=False
    )
    length_unit = forms.ChoiceField(
        label=_('Length unit'),
        choices=add_blank_choice(CableLengthUnitChoices),
        required=False
    )
    unterminated = forms.NullBooleanField(
        label=_('Unterminated'),
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    tag = TagFilterField(model)


class PowerPanelFilterForm(ContactModelFilterForm, NetBoxModelFilterSetForm):
    model = PowerPanel
    fieldsets = (
        FieldSet('q', 'filter_id', 'tag'),
        FieldSet('region_id', 'site_group_id', 'site_id', 'location_id', name=_('Location')),
        FieldSet('contact', 'contact_role', 'contact_group', name=_('Contacts')),
    )
    selector_fields = ('filter_id', 'q', 'site_id', 'location_id')
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


class PowerFeedFilterForm(TenancyFilterForm, NetBoxModelFilterSetForm):
    model = PowerFeed
    fieldsets = (
        FieldSet('q', 'filter_id', 'tag'),
        FieldSet('region_id', 'site_group_id', 'site_id', 'power_panel_id', 'rack_id', name=_('Location')),
        FieldSet('tenant_group_id', 'tenant_id', name=_('Tenant')),
        FieldSet('status', 'type', 'supply', 'phase', 'voltage', 'amperage', 'max_utilization', name=_('Attributes')),
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
        label=_('Status'),
        choices=PowerFeedStatusChoices,
        required=False
    )
    type = forms.ChoiceField(
        label=_('Type'),
        choices=add_blank_choice(PowerFeedTypeChoices),
        required=False
    )
    supply = forms.ChoiceField(
        label=_('Supply'),
        choices=add_blank_choice(PowerFeedSupplyChoices),
        required=False
    )
    phase = forms.ChoiceField(
        label=_('Phase'),
        choices=add_blank_choice(PowerFeedPhaseChoices),
        required=False
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
    tag = TagFilterField(model)


#
# Device components
#

class CabledFilterForm(forms.Form):
    cabled = forms.NullBooleanField(
        label=_('Cabled'),
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    occupied = forms.NullBooleanField(
        label=_('Occupied'),
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )


class PathEndpointFilterForm(CabledFilterForm):
    connected = forms.NullBooleanField(
        label=_('Connected'),
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )


class ConsolePortFilterForm(PathEndpointFilterForm, DeviceComponentFilterForm):
    model = ConsolePort
    fieldsets = (
        FieldSet('q', 'filter_id', 'tag'),
        FieldSet('name', 'label', 'type', 'speed', name=_('Attributes')),
        FieldSet('region_id', 'site_group_id', 'site_id', 'location_id', 'rack_id', name=_('Location')),
        FieldSet('device_type_id', 'device_role_id', 'device_id', 'virtual_chassis_id', name=_('Device')),
        FieldSet('cabled', 'connected', 'occupied', name=_('Connection')),
    )
    type = forms.MultipleChoiceField(
        label=_('Type'),
        choices=ConsolePortTypeChoices,
        required=False
    )
    speed = forms.MultipleChoiceField(
        label=_('Speed'),
        choices=ConsolePortSpeedChoices,
        required=False
    )
    tag = TagFilterField(model)


class ConsoleServerPortFilterForm(PathEndpointFilterForm, DeviceComponentFilterForm):
    model = ConsoleServerPort
    fieldsets = (
        FieldSet('q', 'filter_id', 'tag'),
        FieldSet('name', 'label', 'type', 'speed', name=_('Attributes')),
        FieldSet('region_id', 'site_group_id', 'site_id', 'location_id', 'rack_id', name=_('Location')),
        FieldSet('device_type_id', 'device_role_id', 'device_id', 'virtual_chassis_id', name=_('Device')),
        FieldSet('cabled', 'connected', 'occupied', name=_('Connection')),
    )
    type = forms.MultipleChoiceField(
        label=_('Type'),
        choices=ConsolePortTypeChoices,
        required=False
    )
    speed = forms.MultipleChoiceField(
        label=_('Speed'),
        choices=ConsolePortSpeedChoices,
        required=False
    )
    tag = TagFilterField(model)


class PowerPortFilterForm(PathEndpointFilterForm, DeviceComponentFilterForm):
    model = PowerPort
    fieldsets = (
        FieldSet('q', 'filter_id', 'tag'),
        FieldSet('name', 'label', 'type', name=_('Attributes')),
        FieldSet('region_id', 'site_group_id', 'site_id', 'location_id', 'rack_id', name=_('Location')),
        FieldSet('device_type_id', 'device_role_id', 'device_id', 'virtual_chassis_id', name=_('Device')),
        FieldSet('cabled', 'connected', 'occupied', name=_('Connection')),
    )
    type = forms.MultipleChoiceField(
        label=_('Type'),
        choices=PowerPortTypeChoices,
        required=False
    )
    tag = TagFilterField(model)


class PowerOutletFilterForm(PathEndpointFilterForm, DeviceComponentFilterForm):
    model = PowerOutlet
    fieldsets = (
        FieldSet('q', 'filter_id', 'tag'),
        FieldSet('name', 'label', 'type', name=_('Attributes')),
        FieldSet('region_id', 'site_group_id', 'site_id', 'location_id', 'rack_id', name=_('Location')),
        FieldSet('device_type_id', 'device_role_id', 'device_id', 'virtual_chassis_id', name=_('Device')),
        FieldSet('cabled', 'connected', 'occupied', name=_('Connection')),
    )
    type = forms.MultipleChoiceField(
        label=_('Type'),
        choices=PowerOutletTypeChoices,
        required=False
    )
    tag = TagFilterField(model)


class InterfaceFilterForm(PathEndpointFilterForm, DeviceComponentFilterForm):
    model = Interface
    fieldsets = (
        FieldSet('q', 'filter_id', 'tag'),
        FieldSet('name', 'label', 'kind', 'type', 'speed', 'duplex', 'enabled', 'mgmt_only', name=_('Attributes')),
        FieldSet('vrf_id', 'l2vpn_id', 'mac_address', 'wwn', name=_('Addressing')),
        FieldSet('poe_mode', 'poe_type', name=_('PoE')),
        FieldSet('rf_role', 'rf_channel', 'rf_channel_width', 'tx_power', name=_('Wireless')),
        FieldSet('region_id', 'site_group_id', 'site_id', 'location_id', 'rack_id', name=_('Location')),
        FieldSet('device_type_id', 'device_role_id', 'device_id', 'virtual_chassis_id', 'vdc_id', name=_('Device')),
        FieldSet('cabled', 'connected', 'occupied', name=_('Connection')),
    )
    selector_fields = ('filter_id', 'q', 'device_id')
    vdc_id = DynamicModelMultipleChoiceField(
        queryset=VirtualDeviceContext.objects.all(),
        required=False,
        query_params={
            'device_id': '$device_id',
        },
        label=_('Virtual Device Context')
    )
    kind = forms.MultipleChoiceField(
        label=_('Kind'),
        choices=InterfaceKindChoices,
        required=False
    )
    type = forms.MultipleChoiceField(
        label=_('Type'),
        choices=InterfaceTypeChoices,
        required=False
    )
    speed = forms.IntegerField(
        label=_('Speed'),
        required=False,
        widget=NumberWithOptions(
            options=InterfaceSpeedChoices
        )
    )
    duplex = forms.MultipleChoiceField(
        label=_('Duplex'),
        choices=InterfaceDuplexChoices,
        required=False
    )
    enabled = forms.NullBooleanField(
        label=_('Enabled'),
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    mgmt_only = forms.NullBooleanField(
        label=_('Mgmt only'),
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    mac_address = forms.CharField(
        required=False,
        label=_('MAC address')
    )
    wwn = forms.CharField(
        required=False,
        label=_('WWN')
    )
    poe_mode = forms.MultipleChoiceField(
        choices=InterfacePoEModeChoices,
        required=False,
        label=_('PoE mode')
    )
    poe_type = forms.MultipleChoiceField(
        choices=InterfacePoETypeChoices,
        required=False,
        label=_('PoE type')
    )
    rf_role = forms.MultipleChoiceField(
        choices=WirelessRoleChoices,
        required=False,
        label=_('Wireless role')
    )
    rf_channel = forms.MultipleChoiceField(
        choices=WirelessChannelChoices,
        required=False,
        label=_('Wireless channel')
    )
    rf_channel_frequency = forms.IntegerField(
        required=False,
        label=_('Channel frequency (MHz)')
    )
    rf_channel_width = forms.IntegerField(
        required=False,
        label=_('Channel width (MHz)')
    )
    tx_power = forms.IntegerField(
        required=False,
        label=_('Transmit power (dBm)'),
        min_value=0,
        max_value=127
    )
    vrf_id = DynamicModelMultipleChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label=_('VRF')
    )
    l2vpn_id = DynamicModelMultipleChoiceField(
        queryset=L2VPN.objects.all(),
        required=False,
        label=_('L2VPN')
    )
    tag = TagFilterField(model)


class FrontPortFilterForm(CabledFilterForm, DeviceComponentFilterForm):
    fieldsets = (
        FieldSet('q', 'filter_id', 'tag'),
        FieldSet('name', 'label', 'type', 'color', name=_('Attributes')),
        FieldSet('region_id', 'site_group_id', 'site_id', 'location_id', 'rack_id', name=_('Location')),
        FieldSet('device_type_id', 'device_role_id', 'device_id', 'virtual_chassis_id', name=_('Device')),
        FieldSet('cabled', 'occupied', name=_('Cable')),
    )
    model = FrontPort
    type = forms.MultipleChoiceField(
        label=_('Type'),
        choices=PortTypeChoices,
        required=False
    )
    color = ColorField(
        label=_('Color'),
        required=False
    )
    tag = TagFilterField(model)


class RearPortFilterForm(CabledFilterForm, DeviceComponentFilterForm):
    model = RearPort
    fieldsets = (
        FieldSet('q', 'filter_id', 'tag'),
        FieldSet('name', 'label', 'type', 'color', name=_('Attributes')),
        FieldSet('region_id', 'site_group_id', 'site_id', 'location_id', 'rack_id', name=_('Location')),
        FieldSet('device_type_id', 'device_role_id', 'device_id', 'virtual_chassis_id', name=_('Device')),
        FieldSet('cabled', 'occupied', name=_('Cable')),
    )
    type = forms.MultipleChoiceField(
        label=_('Type'),
        choices=PortTypeChoices,
        required=False
    )
    color = ColorField(
        label=_('Color'),
        required=False
    )
    tag = TagFilterField(model)


class ModuleBayFilterForm(DeviceComponentFilterForm):
    model = ModuleBay
    fieldsets = (
        FieldSet('q', 'filter_id', 'tag'),
        FieldSet('name', 'label', 'position', name=_('Attributes')),
        FieldSet('region_id', 'site_group_id', 'site_id', 'location_id', 'rack_id', name=_('Location')),
        FieldSet('device_type_id', 'device_role_id', 'device_id', 'virtual_chassis_id', name=_('Device')),
    )
    tag = TagFilterField(model)
    position = forms.CharField(
        label=_('Position'),
        required=False
    )


class DeviceBayFilterForm(DeviceComponentFilterForm):
    model = DeviceBay
    fieldsets = (
        FieldSet('q', 'filter_id', 'tag'),
        FieldSet('name', 'label', name=_('Attributes')),
        FieldSet('region_id', 'site_group_id', 'site_id', 'location_id', 'rack_id', name=_('Location')),
        FieldSet('device_type_id', 'device_role_id', 'device_id', 'virtual_chassis_id', name=_('Device')),
    )
    tag = TagFilterField(model)


class InventoryItemFilterForm(DeviceComponentFilterForm):
    model = InventoryItem
    fieldsets = (
        FieldSet('q', 'filter_id', 'tag'),
        FieldSet(
            'name', 'label', 'role_id', 'manufacturer_id', 'serial', 'asset_tag', 'discovered',
            name=_('Attributes')
        ),
        FieldSet('region_id', 'site_group_id', 'site_id', 'location_id', 'rack_id', name=_('Location')),
        FieldSet('device_type_id', 'device_role_id', 'device_id', 'virtual_chassis_id', name=_('Device')),
    )
    role_id = DynamicModelMultipleChoiceField(
        queryset=InventoryItemRole.objects.all(),
        required=False,
        label=_('Role')
    )
    manufacturer_id = DynamicModelMultipleChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False,
        label=_('Manufacturer')
    )
    serial = forms.CharField(
        label=_('Serial'),
        required=False
    )
    asset_tag = forms.CharField(
        label=_('Asset tag'),
        required=False
    )
    discovered = forms.NullBooleanField(
        label=_('Discovered'),
        required=False,
        widget=forms.Select(
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
