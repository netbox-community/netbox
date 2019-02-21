import django_filters
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from netaddr import EUI
from netaddr.core import AddrFormatError

from extras.filters import CustomFieldFilterSet
from tenancy.models import Tenant
from utilities.constants import COLOR_CHOICES
from utilities.filters import NameSlugSearchFilterSet, NullableCharFieldFilter, NumericInFilter, TagFilter
from virtualization.models import Cluster
from .constants import *
from .models import (
    Cable, ConsolePort, ConsolePortTemplate, ConsoleServerPort, ConsoleServerPortTemplate, Device, DeviceBay,
    DeviceBayTemplate, DeviceRole, DeviceType, FrontPort, FrontPortTemplate, Interface, InterfaceTemplate,
    InventoryItem, Manufacturer, Platform, PowerOutlet, PowerOutletTemplate, PowerPort, PowerPortTemplate, Rack,
    RackGroup, RackReservation, RackRole, RearPort, RearPortTemplate, Region, Site, VirtualChassis,
)


class RegionFilter(NameSlugSearchFilterSet):
    parent_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Region.objects.all(),
        label='Parent region (ID)',
    )
    parent = django_filters.ModelMultipleChoiceFilter(
        field_name='parent__slug',
        queryset=Region.objects.all(),
        to_field_name='slug',
        label='Parent region (slug)',
    )

    class Meta:
        model = Region
        fields = ['name', 'slug']


class SiteFilter(CustomFieldFilterSet, django_filters.FilterSet):
    id__in = NumericInFilter(
        field_name='id',
        lookup_expr='in'
    )
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    status = django_filters.MultipleChoiceFilter(
        choices=SITE_STATUS_CHOICES,
        null_value=None
    )
    region_id = django_filters.NumberFilter(
        method='filter_region',
        field_name='pk',
        label='Region (ID)',
    )
    region = django_filters.CharFilter(
        method='filter_region',
        field_name='slug',
        label='Region (slug)',
    )
    tenant_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Tenant.objects.all(),
        label='Tenant (ID)',
    )
    tenant = django_filters.ModelMultipleChoiceFilter(
        field_name='tenant__slug',
        queryset=Tenant.objects.all(),
        to_field_name='slug',
        label='Tenant (slug)',
    )
    tag = TagFilter()

    class Meta:
        model = Site
        fields = ['q', 'name', 'slug', 'facility', 'asn', 'contact_name', 'contact_phone', 'contact_email']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = (
            Q(name__icontains=value) |
            Q(facility__icontains=value) |
            Q(description__icontains=value) |
            Q(physical_address__icontains=value) |
            Q(shipping_address__icontains=value) |
            Q(contact_name__icontains=value) |
            Q(contact_phone__icontains=value) |
            Q(contact_email__icontains=value) |
            Q(comments__icontains=value)
        )
        try:
            qs_filter |= Q(asn=int(value.strip()))
        except ValueError:
            pass
        return queryset.filter(qs_filter)

    def filter_region(self, queryset, name, value):
        try:
            region = Region.objects.get(**{name: value})
        except ObjectDoesNotExist:
            return queryset.none()
        return queryset.filter(
            Q(region=region) |
            Q(region__in=region.get_descendants())
        )


class RackGroupFilter(NameSlugSearchFilterSet):
    site_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Site.objects.all(),
        label='Site (ID)',
    )
    site = django_filters.ModelMultipleChoiceFilter(
        field_name='site__slug',
        queryset=Site.objects.all(),
        to_field_name='slug',
        label='Site (slug)',
    )

    class Meta:
        model = RackGroup
        fields = ['site_id', 'name', 'slug']


class RackRoleFilter(NameSlugSearchFilterSet):

    class Meta:
        model = RackRole
        fields = ['name', 'slug', 'color']


class RackFilter(CustomFieldFilterSet, django_filters.FilterSet):
    id__in = NumericInFilter(
        field_name='id',
        lookup_expr='in'
    )
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    facility_id = NullableCharFieldFilter()
    site_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Site.objects.all(),
        label='Site (ID)',
    )
    site = django_filters.ModelMultipleChoiceFilter(
        field_name='site__slug',
        queryset=Site.objects.all(),
        to_field_name='slug',
        label='Site (slug)',
    )
    group_id = django_filters.ModelMultipleChoiceFilter(
        queryset=RackGroup.objects.all(),
        label='Group (ID)',
    )
    group = django_filters.ModelMultipleChoiceFilter(
        field_name='group__slug',
        queryset=RackGroup.objects.all(),
        to_field_name='slug',
        label='Group',
    )
    tenant_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Tenant.objects.all(),
        label='Tenant (ID)',
    )
    tenant = django_filters.ModelMultipleChoiceFilter(
        field_name='tenant__slug',
        queryset=Tenant.objects.all(),
        to_field_name='slug',
        label='Tenant (slug)',
    )
    status = django_filters.MultipleChoiceFilter(
        choices=RACK_STATUS_CHOICES,
        null_value=None
    )
    role_id = django_filters.ModelMultipleChoiceFilter(
        queryset=RackRole.objects.all(),
        label='Role (ID)',
    )
    role = django_filters.ModelMultipleChoiceFilter(
        field_name='role__slug',
        queryset=RackRole.objects.all(),
        to_field_name='slug',
        label='Role (slug)',
    )
    asset_tag = NullableCharFieldFilter()
    tag = TagFilter()

    class Meta:
        model = Rack
        fields = [
            'name', 'serial', 'asset_tag', 'type', 'width', 'u_height', 'desc_units', 'outer_width', 'outer_depth',
            'outer_unit',
        ]

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(facility_id__icontains=value) |
            Q(serial__icontains=value.strip()) |
            Q(asset_tag__icontains=value.strip()) |
            Q(comments__icontains=value)
        )


class RackReservationFilter(django_filters.FilterSet):
    id__in = NumericInFilter(
        field_name='id',
        lookup_expr='in'
    )
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    rack_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Rack.objects.all(),
        label='Rack (ID)',
    )
    site_id = django_filters.ModelMultipleChoiceFilter(
        field_name='rack__site',
        queryset=Site.objects.all(),
        label='Site (ID)',
    )
    site = django_filters.ModelMultipleChoiceFilter(
        field_name='rack__site__slug',
        queryset=Site.objects.all(),
        to_field_name='slug',
        label='Site (slug)',
    )
    group_id = django_filters.ModelMultipleChoiceFilter(
        field_name='rack__group',
        queryset=RackGroup.objects.all(),
        label='Group (ID)',
    )
    group = django_filters.ModelMultipleChoiceFilter(
        field_name='rack__group__slug',
        queryset=RackGroup.objects.all(),
        to_field_name='slug',
        label='Group',
    )
    tenant_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Tenant.objects.all(),
        label='Tenant (ID)',
    )
    tenant = django_filters.ModelMultipleChoiceFilter(
        field_name='tenant__slug',
        queryset=Tenant.objects.all(),
        to_field_name='slug',
        label='Tenant (slug)',
    )
    user_id = django_filters.ModelMultipleChoiceFilter(
        queryset=User.objects.all(),
        label='User (ID)',
    )
    user = django_filters.ModelMultipleChoiceFilter(
        field_name='user',
        queryset=User.objects.all(),
        to_field_name='username',
        label='User (name)',
    )

    class Meta:
        model = RackReservation
        fields = ['created']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(rack__name__icontains=value) |
            Q(rack__facility_id__icontains=value) |
            Q(user__username__icontains=value) |
            Q(description__icontains=value)
        )


class ManufacturerFilter(NameSlugSearchFilterSet):

    class Meta:
        model = Manufacturer
        fields = ['name', 'slug']


class DeviceTypeFilter(CustomFieldFilterSet):
    id__in = NumericInFilter(
        field_name='id',
        lookup_expr='in'
    )
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    manufacturer_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Manufacturer.objects.all(),
        label='Manufacturer (ID)',
    )
    manufacturer = django_filters.ModelMultipleChoiceFilter(
        field_name='manufacturer__slug',
        queryset=Manufacturer.objects.all(),
        to_field_name='slug',
        label='Manufacturer (slug)',
    )
    console_ports = django_filters.BooleanFilter(
        method='_console_ports',
        label='Has console ports',
    )
    console_server_ports = django_filters.BooleanFilter(
        method='_console_server_ports',
        label='Has console server ports',
    )
    power_ports = django_filters.BooleanFilter(
        method='_power_ports',
        label='Has power ports',
    )
    power_outlets = django_filters.BooleanFilter(
        method='_power_outlets',
        label='Has power outlets',
    )
    interfaces = django_filters.BooleanFilter(
        method='_interfaces',
        label='Has interfaces',
    )
    pass_through_ports = django_filters.BooleanFilter(
        method='_pass_through_ports',
        label='Has pass-through ports',
    )
    tag = TagFilter()

    class Meta:
        model = DeviceType
        fields = [
            'model', 'slug', 'part_number', 'u_height', 'is_full_depth', 'subdevice_role',
        ]

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(manufacturer__name__icontains=value) |
            Q(model__icontains=value) |
            Q(part_number__icontains=value) |
            Q(comments__icontains=value)
        )

    def _console_ports(self, queryset, name, value):
        return queryset.exclude(consoleport_templates__isnull=value)

    def _console_server_ports(self, queryset, name, value):
        return queryset.exclude(consoleserverport_templates__isnull=value)

    def _power_ports(self, queryset, name, value):
        return queryset.exclude(powerport_templates__isnull=value)

    def _power_outlets(self, queryset, name, value):
        return queryset.exclude(poweroutlet_templates__isnull=value)

    def _interfaces(self, queryset, name, value):
        return queryset.exclude(interface_templates__isnull=value)

    def _pass_through_ports(self, queryset, name, value):
        return queryset.exclude(
            frontport_templates__isnull=value,
            rearport_templates__isnull=value
        )


class DeviceTypeComponentFilterSet(NameSlugSearchFilterSet):
    devicetype_id = django_filters.ModelMultipleChoiceFilter(
        queryset=DeviceType.objects.all(),
        field_name='device_type_id',
        label='Device type (ID)',
    )


class ConsolePortTemplateFilter(DeviceTypeComponentFilterSet):

    class Meta:
        model = ConsolePortTemplate
        fields = ['name']


class ConsoleServerPortTemplateFilter(DeviceTypeComponentFilterSet):

    class Meta:
        model = ConsoleServerPortTemplate
        fields = ['name']


class PowerPortTemplateFilter(DeviceTypeComponentFilterSet):

    class Meta:
        model = PowerPortTemplate
        fields = ['name']


class PowerOutletTemplateFilter(DeviceTypeComponentFilterSet):

    class Meta:
        model = PowerOutletTemplate
        fields = ['name']


class InterfaceTemplateFilter(DeviceTypeComponentFilterSet):

    class Meta:
        model = InterfaceTemplate
        fields = ['name', 'form_factor', 'mgmt_only']


class FrontPortTemplateFilter(DeviceTypeComponentFilterSet):

    class Meta:
        model = FrontPortTemplate
        fields = ['name', 'type']


class RearPortTemplateFilter(DeviceTypeComponentFilterSet):

    class Meta:
        model = RearPortTemplate
        fields = ['name', 'type']


class DeviceBayTemplateFilter(DeviceTypeComponentFilterSet):

    class Meta:
        model = DeviceBayTemplate
        fields = ['name']


class DeviceRoleFilter(NameSlugSearchFilterSet):

    class Meta:
        model = DeviceRole
        fields = ['name', 'slug', 'color', 'vm_role']


class PlatformFilter(NameSlugSearchFilterSet):
    manufacturer_id = django_filters.ModelMultipleChoiceFilter(
        field_name='manufacturer',
        queryset=Manufacturer.objects.all(),
        label='Manufacturer (ID)',
    )
    manufacturer = django_filters.ModelMultipleChoiceFilter(
        field_name='manufacturer__slug',
        queryset=Manufacturer.objects.all(),
        to_field_name='slug',
        label='Manufacturer (slug)',
    )

    class Meta:
        model = Platform
        fields = ['name', 'slug']


class DeviceFilter(CustomFieldFilterSet):
    id__in = NumericInFilter(
        field_name='id',
        lookup_expr='in'
    )
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    manufacturer_id = django_filters.ModelMultipleChoiceFilter(
        field_name='device_type__manufacturer',
        queryset=Manufacturer.objects.all(),
        label='Manufacturer (ID)',
    )
    manufacturer = django_filters.ModelMultipleChoiceFilter(
        field_name='device_type__manufacturer__slug',
        queryset=Manufacturer.objects.all(),
        to_field_name='slug',
        label='Manufacturer (slug)',
    )
    device_type_id = django_filters.ModelMultipleChoiceFilter(
        queryset=DeviceType.objects.all(),
        label='Device type (ID)',
    )
    role_id = django_filters.ModelMultipleChoiceFilter(
        field_name='device_role_id',
        queryset=DeviceRole.objects.all(),
        label='Role (ID)',
    )
    role = django_filters.ModelMultipleChoiceFilter(
        field_name='device_role__slug',
        queryset=DeviceRole.objects.all(),
        to_field_name='slug',
        label='Role (slug)',
    )
    tenant_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Tenant.objects.all(),
        label='Tenant (ID)',
    )
    tenant = django_filters.ModelMultipleChoiceFilter(
        field_name='tenant__slug',
        queryset=Tenant.objects.all(),
        to_field_name='slug',
        label='Tenant (slug)',
    )
    platform_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Platform.objects.all(),
        label='Platform (ID)',
    )
    platform = django_filters.ModelMultipleChoiceFilter(
        field_name='platform__slug',
        queryset=Platform.objects.all(),
        to_field_name='slug',
        label='Platform (slug)',
    )
    name = NullableCharFieldFilter()
    asset_tag = NullableCharFieldFilter()
    region_id = django_filters.NumberFilter(
        method='filter_region',
        field_name='pk',
        label='Region (ID)',
    )
    region = django_filters.CharFilter(
        method='filter_region',
        field_name='slug',
        label='Region (slug)',
    )
    site_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Site.objects.all(),
        label='Site (ID)',
    )
    site = django_filters.ModelMultipleChoiceFilter(
        field_name='site__slug',
        queryset=Site.objects.all(),
        to_field_name='slug',
        label='Site name (slug)',
    )
    rack_group_id = django_filters.ModelMultipleChoiceFilter(
        field_name='rack__group',
        queryset=RackGroup.objects.all(),
        label='Rack group (ID)',
    )
    rack_id = django_filters.ModelMultipleChoiceFilter(
        field_name='rack',
        queryset=Rack.objects.all(),
        label='Rack (ID)',
    )
    position = django_filters.ChoiceFilter(
        choices=DEVICE_POSITION_CHOICES,
        null_label='Non-racked'
    )
    cluster_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Cluster.objects.all(),
        label='VM cluster (ID)',
    )
    model = django_filters.ModelMultipleChoiceFilter(
        field_name='device_type__slug',
        queryset=DeviceType.objects.all(),
        to_field_name='slug',
        label='Device model (slug)',
    )
    status = django_filters.MultipleChoiceFilter(
        choices=DEVICE_STATUS_CHOICES,
        null_value=None
    )
    is_full_depth = django_filters.BooleanFilter(
        field_name='device_type__is_full_depth',
        label='Is full depth',
    )
    mac_address = django_filters.CharFilter(
        method='_mac_address',
        label='MAC address',
    )
    has_primary_ip = django_filters.BooleanFilter(
        method='_has_primary_ip',
        label='Has a primary IP',
    )
    virtual_chassis_id = django_filters.ModelMultipleChoiceFilter(
        field_name='virtual_chassis',
        queryset=VirtualChassis.objects.all(),
        label='Virtual chassis (ID)',
    )
    console_ports = django_filters.BooleanFilter(
        method='_console_ports',
        label='Has console ports',
    )
    console_server_ports = django_filters.BooleanFilter(
        method='_console_server_ports',
        label='Has console server ports',
    )
    power_ports = django_filters.BooleanFilter(
        method='_power_ports',
        label='Has power ports',
    )
    power_outlets = django_filters.BooleanFilter(
        method='_power_outlets',
        label='Has power outlets',
    )
    interfaces = django_filters.BooleanFilter(
        method='_interfaces',
        label='Has interfaces',
    )
    pass_through_ports = django_filters.BooleanFilter(
        method='_pass_through_ports',
        label='Has pass-through ports',
    )
    tag = TagFilter()

    class Meta:
        model = Device
        fields = ['serial', 'face']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(serial__icontains=value.strip()) |
            Q(inventory_items__serial__icontains=value.strip()) |
            Q(asset_tag__icontains=value.strip()) |
            Q(comments__icontains=value)
        ).distinct()

    def filter_region(self, queryset, name, value):
        try:
            region = Region.objects.get(**{name: value})
        except ObjectDoesNotExist:
            return queryset.none()
        return queryset.filter(
            Q(site__region=region) |
            Q(site__region__in=region.get_descendants())
        )

    def _mac_address(self, queryset, name, value):
        value = value.strip()
        if not value:
            return queryset
        try:
            mac = EUI(value.strip())
            return queryset.filter(interfaces__mac_address=mac).distinct()
        except AddrFormatError:
            return queryset.none()

    def _has_primary_ip(self, queryset, name, value):
        if value:
            return queryset.filter(
                Q(primary_ip4__isnull=False) |
                Q(primary_ip6__isnull=False)
            )
        else:
            return queryset.exclude(
                Q(primary_ip4__isnull=False) |
                Q(primary_ip6__isnull=False)
            )

    def _console_ports(self, queryset, name, value):
        return queryset.exclude(consoleports__isnull=value)

    def _console_server_ports(self, queryset, name, value):
        return queryset.exclude(consoleserverports__isnull=value)

    def _power_ports(self, queryset, name, value):
        return queryset.exclude(powerports__isnull=value)

    def _power_outlets(self, queryset, name, value):
        return queryset.exclude(poweroutlets_isnull=value)

    def _interfaces(self, queryset, name, value):
        return queryset.exclude(interfaces__isnull=value)

    def _pass_through_ports(self, queryset, name, value):
        return queryset.exclude(
            frontports__isnull=value,
            rearports__isnull=value
        )


class DeviceComponentFilterSet(django_filters.FilterSet):
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    device_id = django_filters.ModelChoiceFilter(
        queryset=Device.objects.all(),
        label='Device (ID)',
    )
    device = django_filters.ModelChoiceFilter(
        queryset=Device.objects.all(),
        to_field_name='name',
        label='Device (name)',
    )
    tag = TagFilter()

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value)
        )


class ConsolePortFilter(DeviceComponentFilterSet):
    cabled = django_filters.BooleanFilter(
        field_name='cable',
        lookup_expr='isnull',
        exclude=True
    )

    class Meta:
        model = ConsolePort
        fields = ['name', 'connection_status']


class ConsoleServerPortFilter(DeviceComponentFilterSet):
    cabled = django_filters.BooleanFilter(
        field_name='cable',
        lookup_expr='isnull',
        exclude=True
    )

    class Meta:
        model = ConsoleServerPort
        fields = ['name', 'connection_status']


class PowerPortFilter(DeviceComponentFilterSet):
    cabled = django_filters.BooleanFilter(
        field_name='cable',
        lookup_expr='isnull',
        exclude=True
    )

    class Meta:
        model = PowerPort
        fields = ['name', 'connection_status']


class PowerOutletFilter(DeviceComponentFilterSet):
    cabled = django_filters.BooleanFilter(
        field_name='cable',
        lookup_expr='isnull',
        exclude=True
    )

    class Meta:
        model = PowerOutlet
        fields = ['name', 'connection_status']


class InterfaceFilter(django_filters.FilterSet):
    """
    Not using DeviceComponentFilterSet for Interfaces because we need to check for VirtualChassis membership.
    """
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    device = django_filters.CharFilter(
        method='filter_device',
        field_name='name',
        label='Device',
    )
    device_id = django_filters.NumberFilter(
        method='filter_device',
        field_name='pk',
        label='Device (ID)',
    )
    cabled = django_filters.BooleanFilter(
        field_name='cable',
        lookup_expr='isnull',
        exclude=True
    )
    type = django_filters.CharFilter(
        method='filter_type',
        label='Interface type',
    )
    lag_id = django_filters.ModelMultipleChoiceFilter(
        field_name='lag',
        queryset=Interface.objects.all(),
        label='LAG interface (ID)',
    )
    mac_address = django_filters.CharFilter(
        method='_mac_address',
        label='MAC address',
    )
    tag = TagFilter()
    vlan_id = django_filters.CharFilter(
        method='filter_vlan_id',
        label='Assigned VLAN'
    )
    vlan = django_filters.CharFilter(
        method='filter_vlan',
        label='Assigned VID'
    )
    form_factor = django_filters.MultipleChoiceFilter(
        choices=IFACE_FF_CHOICES,
        null_value=None
    )

    class Meta:
        model = Interface
        fields = ['name', 'connection_status', 'form_factor', 'enabled', 'mtu', 'mgmt_only']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value)
        ).distinct()

    def filter_device(self, queryset, name, value):
        try:
            device = Device.objects.get(**{name: value})
            vc_interface_ids = device.vc_interfaces.values_list('id', flat=True)
            return queryset.filter(pk__in=vc_interface_ids)
        except Device.DoesNotExist:
            return queryset.none()

    def filter_vlan_id(self, queryset, name, value):
        value = value.strip()
        if not value:
            return queryset
        return queryset.filter(
            Q(untagged_vlan_id=value) |
            Q(tagged_vlans=value)
        )

    def filter_vlan(self, queryset, name, value):
        value = value.strip()
        if not value:
            return queryset
        return queryset.filter(
            Q(untagged_vlan_id__vid=value) |
            Q(tagged_vlans__vid=value)
        )

    def filter_type(self, queryset, name, value):
        value = value.strip().lower()
        return {
            'physical': queryset.exclude(form_factor__in=NONCONNECTABLE_IFACE_TYPES),
            'virtual': queryset.filter(form_factor__in=VIRTUAL_IFACE_TYPES),
            'wireless': queryset.filter(form_factor__in=WIRELESS_IFACE_TYPES),
            'lag': queryset.filter(form_factor=IFACE_FF_LAG),
        }.get(value, queryset.none())

    def _mac_address(self, queryset, name, value):
        value = value.strip()
        if not value:
            return queryset
        try:
            mac = EUI(value.strip())
            return queryset.filter(mac_address=mac)
        except AddrFormatError:
            return queryset.none()


class FrontPortFilter(DeviceComponentFilterSet):
    cabled = django_filters.BooleanFilter(
        field_name='cable',
        lookup_expr='isnull',
        exclude=True
    )

    class Meta:
        model = FrontPort
        fields = ['name', 'type']


class RearPortFilter(DeviceComponentFilterSet):
    cabled = django_filters.BooleanFilter(
        field_name='cable',
        lookup_expr='isnull',
        exclude=True
    )

    class Meta:
        model = RearPort
        fields = ['name', 'type']


class DeviceBayFilter(DeviceComponentFilterSet):

    class Meta:
        model = DeviceBay
        fields = ['name']


class InventoryItemFilter(DeviceComponentFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    device_id = django_filters.ModelChoiceFilter(
        queryset=Device.objects.all(),
        label='Device (ID)',
    )
    device = django_filters.ModelChoiceFilter(
        queryset=Device.objects.all(),
        to_field_name='name',
        label='Device (name)',
    )
    parent_id = django_filters.ModelMultipleChoiceFilter(
        queryset=InventoryItem.objects.all(),
        label='Parent inventory item (ID)',
    )
    manufacturer_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Manufacturer.objects.all(),
        label='Manufacturer (ID)',
    )
    manufacturer = django_filters.ModelMultipleChoiceFilter(
        field_name='manufacturer__slug',
        queryset=Manufacturer.objects.all(),
        to_field_name='slug',
        label='Manufacturer (slug)',
    )
    asset_tag = NullableCharFieldFilter()

    class Meta:
        model = InventoryItem
        fields = ['name', 'part_id', 'serial', 'asset_tag', 'discovered']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = (
            Q(name__icontains=value) |
            Q(part_id__icontains=value) |
            Q(serial__iexact=value) |
            Q(asset_tag__iexact=value) |
            Q(description__icontains=value)
        )
        return queryset.filter(qs_filter)


class VirtualChassisFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    site_id = django_filters.ModelMultipleChoiceFilter(
        field_name='master__site',
        queryset=Site.objects.all(),
        label='Site (ID)',
    )
    site = django_filters.ModelMultipleChoiceFilter(
        field_name='master__site__slug',
        queryset=Site.objects.all(),
        to_field_name='slug',
        label='Site name (slug)',
    )
    tenant_id = django_filters.ModelMultipleChoiceFilter(
        field_name='master__tenant',
        queryset=Tenant.objects.all(),
        label='Tenant (ID)',
    )
    tenant = django_filters.ModelMultipleChoiceFilter(
        field_name='master__tenant__slug',
        queryset=Tenant.objects.all(),
        to_field_name='slug',
        label='Tenant (slug)',
    )
    tag = TagFilter()

    class Meta:
        model = VirtualChassis
        fields = ['domain']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = (
            Q(master__name__icontains=value) |
            Q(domain__icontains=value)
        )
        return queryset.filter(qs_filter)


class CableFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    type = django_filters.MultipleChoiceFilter(
        choices=CABLE_TYPE_CHOICES
    )
    color = django_filters.MultipleChoiceFilter(
        choices=COLOR_CHOICES
    )

    class Meta:
        model = Cable
        fields = ['type', 'status', 'color', 'length', 'length_unit']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(label__icontains=value)


class ConsoleConnectionFilter(django_filters.FilterSet):
    site = django_filters.CharFilter(
        method='filter_site',
        label='Site (slug)',
    )
    device = django_filters.CharFilter(
        method='filter_device',
        label='Device',
    )

    class Meta:
        model = ConsolePort
        fields = ['name', 'connection_status']

    def filter_site(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(connected_endpoint__device__site__slug=value)

    def filter_device(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(device__name__icontains=value) |
            Q(connected_endpoint__device__name__icontains=value)
        )


class PowerConnectionFilter(django_filters.FilterSet):
    site = django_filters.CharFilter(
        method='filter_site',
        label='Site (slug)',
    )
    device = django_filters.CharFilter(
        method='filter_device',
        label='Device',
    )

    class Meta:
        model = PowerPort
        fields = ['name', 'connection_status']

    def filter_site(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(connected_endpoint__device__site__slug=value)

    def filter_device(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(device__name__icontains=value) |
            Q(connected_endpoint__device__name__icontains=value)
        )


class InterfaceConnectionFilter(django_filters.FilterSet):
    site = django_filters.CharFilter(
        method='filter_site',
        label='Site (slug)',
    )
    device = django_filters.CharFilter(
        method='filter_device',
        label='Device',
    )

    class Meta:
        model = Interface
        fields = ['connection_status']

    def filter_site(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(device__site__slug=value) |
            Q(_connected_interface__device__site__slug=value)
        )

    def filter_device(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(device__name__icontains=value) |
            Q(_connected_interface__device__name__icontains=value)
        )
