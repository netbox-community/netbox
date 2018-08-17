from __future__ import unicode_literals

import django_filters
from django.contrib.auth.models import User
from django.db.models import Q
from netaddr import EUI
from netaddr.core import AddrFormatError

from extras.filters import CustomFieldFilterSet
from tenancy.models import Tenant
from utilities.filters import NullableCharFieldFilter, NumericInFilter
from virtualization.models import Cluster
from .constants import (
    DEVICE_STATUS_CHOICES, IFACE_FF_LAG, NONCONNECTABLE_IFACE_TYPES, SITE_STATUS_CHOICES, VIRTUAL_IFACE_TYPES,
    WIRELESS_IFACE_TYPES,
)
from .models import (
    ConsolePort, ConsolePortTemplate, ConsoleServerPort, ConsoleServerPortTemplate, Device, DeviceBay,
    DeviceBayTemplate, DeviceRole, DeviceType, Interface, InterfaceConnection, InterfaceTemplate, Manufacturer,
    InventoryItem, Platform, PowerOutlet, PowerOutletTemplate, PowerPort, PowerPortTemplate, Rack, RackGroup,
    RackReservation, RackRole, Region, Site, VirtualChassis,
)


class RegionFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    parent_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Region.objects.all(),
        label='Parent region (ID)',
    )
    parent = django_filters.ModelMultipleChoiceFilter(
        name='parent__slug',
        queryset=Region.objects.all(),
        to_field_name='slug',
        label='Parent region (slug)',
    )

    class Meta:
        model = Region
        fields = ['name', 'slug']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = (
            Q(name__icontains=value) |
            Q(slug__icontains=value)
        )
        return queryset.filter(qs_filter)


class SiteFilter(CustomFieldFilterSet, django_filters.FilterSet):
    id__in = NumericInFilter(name='id', lookup_expr='in')
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    status = django_filters.MultipleChoiceFilter(
        choices=SITE_STATUS_CHOICES,
        null_value=None
    )
    region_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Region.objects.all(),
        label='Region (ID)',
    )
    region = django_filters.ModelMultipleChoiceFilter(
        name='region__slug',
        queryset=Region.objects.all(),
        to_field_name='slug',
        label='Region (slug)',
    )
    tenant_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Tenant.objects.all(),
        label='Tenant (ID)',
    )
    tenant = django_filters.ModelMultipleChoiceFilter(
        name='tenant__slug',
        queryset=Tenant.objects.all(),
        to_field_name='slug',
        label='Tenant (slug)',
    )
    tag = django_filters.CharFilter(
        name='tags__slug',
    )

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


class RackGroupFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    site_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Site.objects.all(),
        label='Site (ID)',
    )
    site = django_filters.ModelMultipleChoiceFilter(
        name='site__slug',
        queryset=Site.objects.all(),
        to_field_name='slug',
        label='Site (slug)',
    )

    class Meta:
        model = RackGroup
        fields = ['site_id', 'name', 'slug']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = (
            Q(name__icontains=value) |
            Q(slug__icontains=value)
        )
        return queryset.filter(qs_filter)


class RackRoleFilter(django_filters.FilterSet):

    class Meta:
        model = RackRole
        fields = ['name', 'slug', 'color']


class RackFilter(CustomFieldFilterSet, django_filters.FilterSet):
    id__in = NumericInFilter(name='id', lookup_expr='in')
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
        name='site__slug',
        queryset=Site.objects.all(),
        to_field_name='slug',
        label='Site (slug)',
    )
    group_id = django_filters.ModelMultipleChoiceFilter(
        queryset=RackGroup.objects.all(),
        label='Group (ID)',
    )
    group = django_filters.ModelMultipleChoiceFilter(
        name='group__slug',
        queryset=RackGroup.objects.all(),
        to_field_name='slug',
        label='Group',
    )
    tenant_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Tenant.objects.all(),
        label='Tenant (ID)',
    )
    tenant = django_filters.ModelMultipleChoiceFilter(
        name='tenant__slug',
        queryset=Tenant.objects.all(),
        to_field_name='slug',
        label='Tenant (slug)',
    )
    role_id = django_filters.ModelMultipleChoiceFilter(
        queryset=RackRole.objects.all(),
        label='Role (ID)',
    )
    role = django_filters.ModelMultipleChoiceFilter(
        name='role__slug',
        queryset=RackRole.objects.all(),
        to_field_name='slug',
        label='Role (slug)',
    )
    tag = django_filters.CharFilter(
        name='tags__slug',
    )

    class Meta:
        model = Rack
        fields = ['name', 'serial', 'type', 'width', 'u_height', 'desc_units']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(facility_id__icontains=value) |
            Q(serial__icontains=value.strip()) |
            Q(comments__icontains=value)
        )


class RackReservationFilter(django_filters.FilterSet):
    id__in = NumericInFilter(name='id', lookup_expr='in')
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    rack_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Rack.objects.all(),
        label='Rack (ID)',
    )
    site_id = django_filters.ModelMultipleChoiceFilter(
        name='rack__site',
        queryset=Site.objects.all(),
        label='Site (ID)',
    )
    site = django_filters.ModelMultipleChoiceFilter(
        name='rack__site__slug',
        queryset=Site.objects.all(),
        to_field_name='slug',
        label='Site (slug)',
    )
    group_id = django_filters.ModelMultipleChoiceFilter(
        name='rack__group',
        queryset=RackGroup.objects.all(),
        label='Group (ID)',
    )
    group = django_filters.ModelMultipleChoiceFilter(
        name='rack__group__slug',
        queryset=RackGroup.objects.all(),
        to_field_name='slug',
        label='Group',
    )
    tenant_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Tenant.objects.all(),
        label='Tenant (ID)',
    )
    tenant = django_filters.ModelMultipleChoiceFilter(
        name='tenant__slug',
        queryset=Tenant.objects.all(),
        to_field_name='slug',
        label='Tenant (slug)',
    )
    user_id = django_filters.ModelMultipleChoiceFilter(
        queryset=User.objects.all(),
        label='User (ID)',
    )
    user = django_filters.ModelMultipleChoiceFilter(
        name='user',
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


class ManufacturerFilter(django_filters.FilterSet):

    class Meta:
        model = Manufacturer
        fields = ['name', 'slug']


class DeviceTypeFilter(CustomFieldFilterSet, django_filters.FilterSet):
    id__in = NumericInFilter(name='id', lookup_expr='in')
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    manufacturer_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Manufacturer.objects.all(),
        label='Manufacturer (ID)',
    )
    manufacturer = django_filters.ModelMultipleChoiceFilter(
        name='manufacturer__slug',
        queryset=Manufacturer.objects.all(),
        to_field_name='slug',
        label='Manufacturer (slug)',
    )
    tag = django_filters.CharFilter(
        name='tags__slug',
    )

    class Meta:
        model = DeviceType
        fields = [
            'model', 'slug', 'part_number', 'u_height', 'is_full_depth', 'is_console_server', 'is_pdu',
            'is_network_device', 'subdevice_role',
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


class DeviceTypeComponentFilterSet(django_filters.FilterSet):
    devicetype_id = django_filters.ModelMultipleChoiceFilter(
        queryset=DeviceType.objects.all(),
        name='device_type_id',
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


class DeviceBayTemplateFilter(DeviceTypeComponentFilterSet):

    class Meta:
        model = DeviceBayTemplate
        fields = ['name']


class DeviceRoleFilter(django_filters.FilterSet):

    class Meta:
        model = DeviceRole
        fields = ['name', 'slug', 'color', 'vm_role']


class PlatformFilter(django_filters.FilterSet):
    manufacturer_id = django_filters.ModelMultipleChoiceFilter(
        name='manufacturer',
        queryset=Manufacturer.objects.all(),
        label='Manufacturer (ID)',
    )
    manufacturer = django_filters.ModelMultipleChoiceFilter(
        name='manufacturer__slug',
        queryset=Manufacturer.objects.all(),
        to_field_name='slug',
        label='Manufacturer (slug)',
    )

    class Meta:
        model = Platform
        fields = ['name', 'slug']


class DeviceFilter(CustomFieldFilterSet, django_filters.FilterSet):
    id__in = NumericInFilter(name='id', lookup_expr='in')
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    manufacturer_id = django_filters.ModelMultipleChoiceFilter(
        name='device_type__manufacturer',
        queryset=Manufacturer.objects.all(),
        label='Manufacturer (ID)',
    )
    manufacturer = django_filters.ModelMultipleChoiceFilter(
        name='device_type__manufacturer__slug',
        queryset=Manufacturer.objects.all(),
        to_field_name='slug',
        label='Manufacturer (slug)',
    )
    device_type_id = django_filters.ModelMultipleChoiceFilter(
        queryset=DeviceType.objects.all(),
        label='Device type (ID)',
    )
    role_id = django_filters.ModelMultipleChoiceFilter(
        name='device_role_id',
        queryset=DeviceRole.objects.all(),
        label='Role (ID)',
    )
    role = django_filters.ModelMultipleChoiceFilter(
        name='device_role__slug',
        queryset=DeviceRole.objects.all(),
        to_field_name='slug',
        label='Role (slug)',
    )
    tenant_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Tenant.objects.all(),
        label='Tenant (ID)',
    )
    tenant = django_filters.ModelMultipleChoiceFilter(
        name='tenant__slug',
        queryset=Tenant.objects.all(),
        to_field_name='slug',
        label='Tenant (slug)',
    )
    platform_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Platform.objects.all(),
        label='Platform (ID)',
    )
    platform = django_filters.ModelMultipleChoiceFilter(
        name='platform__slug',
        queryset=Platform.objects.all(),
        to_field_name='slug',
        label='Platform (slug)',
    )
    name = NullableCharFieldFilter()
    asset_tag = NullableCharFieldFilter()
    site_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Site.objects.all(),
        label='Site (ID)',
    )
    site = django_filters.ModelMultipleChoiceFilter(
        name='site__slug',
        queryset=Site.objects.all(),
        to_field_name='slug',
        label='Site name (slug)',
    )
    rack_group_id = django_filters.ModelMultipleChoiceFilter(
        name='rack__group',
        queryset=RackGroup.objects.all(),
        label='Rack group (ID)',
    )
    rack_id = django_filters.ModelMultipleChoiceFilter(
        name='rack',
        queryset=Rack.objects.all(),
        label='Rack (ID)',
    )
    cluster_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Cluster.objects.all(),
        label='VM cluster (ID)',
    )
    model = django_filters.ModelMultipleChoiceFilter(
        name='device_type__slug',
        queryset=DeviceType.objects.all(),
        to_field_name='slug',
        label='Device model (slug)',
    )
    status = django_filters.MultipleChoiceFilter(
        choices=DEVICE_STATUS_CHOICES,
        null_value=None
    )
    is_full_depth = django_filters.BooleanFilter(
        name='device_type__is_full_depth',
        label='Is full depth',
    )
    is_console_server = django_filters.BooleanFilter(
        name='device_type__is_console_server',
        label='Is a console server',
    )
    is_pdu = django_filters.BooleanFilter(
        name='device_type__is_pdu',
        label='Is a PDU',
    )
    is_network_device = django_filters.BooleanFilter(
        name='device_type__is_network_device',
        label='Is a network device',
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
        name='virtual_chassis',
        queryset=VirtualChassis.objects.all(),
        label='Virtual chassis (ID)',
    )
    tag = django_filters.CharFilter(
        name='tags__slug',
    )

    class Meta:
        model = Device
        fields = ['serial', 'position']

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


class DeviceComponentFilterSet(django_filters.FilterSet):
    device_id = django_filters.ModelChoiceFilter(
        queryset=Device.objects.all(),
        label='Device (ID)',
    )
    device = django_filters.ModelChoiceFilter(
        queryset=Device.objects.all(),
        to_field_name='name',
        label='Device (name)',
    )
    tag = django_filters.CharFilter(
        name='tags__slug',
    )


class ConsolePortFilter(DeviceComponentFilterSet):

    class Meta:
        model = ConsolePort
        fields = ['name']


class ConsoleServerPortFilter(DeviceComponentFilterSet):

    class Meta:
        model = ConsoleServerPort
        fields = ['name']


class PowerPortFilter(DeviceComponentFilterSet):

    class Meta:
        model = PowerPort
        fields = ['name']


class PowerOutletFilter(DeviceComponentFilterSet):

    class Meta:
        model = PowerOutlet
        fields = ['name']


class InterfaceFilter(django_filters.FilterSet):
    """
    Not using DeviceComponentFilterSet for Interfaces because we need to glean the ordering logic from the parent
    Device's DeviceType.
    """
    device = django_filters.CharFilter(
        method='filter_device',
        name='name',
        label='Device',
    )
    device_id = django_filters.NumberFilter(
        method='filter_device',
        name='pk',
        label='Device (ID)',
    )
    type = django_filters.CharFilter(
        method='filter_type',
        label='Interface type',
    )
    lag_id = django_filters.ModelMultipleChoiceFilter(
        name='lag',
        queryset=Interface.objects.all(),
        label='LAG interface (ID)',
    )
    mac_address = django_filters.CharFilter(
        method='_mac_address',
        label='MAC address',
    )
    tag = django_filters.CharFilter(
        name='tags__slug',
    )

    class Meta:
        model = Interface
        fields = ['name', 'form_factor', 'enabled', 'mtu', 'mgmt_only']

    def filter_device(self, queryset, name, value):
        try:
            device = Device.objects.select_related('device_type').get(**{name: value})
            vc_interface_ids = [i['id'] for i in device.vc_interfaces.values('id')]
            ordering = device.device_type.interface_ordering
            return queryset.filter(pk__in=vc_interface_ids).order_naturally(ordering)
        except Device.DoesNotExist:
            return queryset.none()

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


class DeviceBayFilter(DeviceComponentFilterSet):

    class Meta:
        model = DeviceBay
        fields = ['name']


class InventoryItemFilter(DeviceComponentFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label='Search',
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
        name='manufacturer__slug',
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
        name='master__site',
        queryset=Site.objects.all(),
        label='Site (ID)',
    )
    site = django_filters.ModelMultipleChoiceFilter(
        name='master__site__slug',
        queryset=Site.objects.all(),
        to_field_name='slug',
        label='Site name (slug)',
    )
    tenant_id = django_filters.ModelMultipleChoiceFilter(
        name='master__tenant',
        queryset=Tenant.objects.all(),
        label='Tenant (ID)',
    )
    tenant = django_filters.ModelMultipleChoiceFilter(
        name='master__tenant__slug',
        queryset=Tenant.objects.all(),
        to_field_name='slug',
        label='Tenant (slug)',
    )
    tag = django_filters.CharFilter(
        name='tags__slug',
    )

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
        return queryset.filter(cs_port__device__site__slug=value)

    def filter_device(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(device__name__icontains=value) |
            Q(cs_port__device__name__icontains=value)
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
        return queryset.filter(power_outlet__device__site__slug=value)

    def filter_device(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(device__name__icontains=value) |
            Q(power_outlet__device__name__icontains=value)
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
        model = InterfaceConnection
        fields = ['connection_status']

    def filter_site(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(interface_a__device__site__slug=value) |
            Q(interface_b__device__site__slug=value)
        )

    def filter_device(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(interface_a__device__name__icontains=value) |
            Q(interface_b__device__name__icontains=value)
        )
