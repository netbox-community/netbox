from __future__ import unicode_literals

import django_filters
from netaddr.core import AddrFormatError

from django.db.models import Q

from extras.filters import CustomFieldFilterSet
from tenancy.models import Tenant
from utilities.filters import NullableModelMultipleChoiceFilter, NumericInFilter
from .models import (
    ConsolePort, ConsolePortTemplate, ConsoleServerPort, ConsoleServerPortTemplate, Device, DeviceBay,
    DeviceBayTemplate, DeviceRole, DeviceType, STATUS_CHOICES, IFACE_FF_LAG, Interface, InterfaceConnection,
    InterfaceTemplate, Manufacturer, InventoryItem, Platform, PowerOutlet, PowerOutletTemplate, PowerPort,
    PowerPortTemplate, Rack, RackGroup, RackReservation, RackRole, Region, Site, VIRTUAL_IFACE_TYPES,
)


class SiteFilter(CustomFieldFilterSet, django_filters.FilterSet):
    id__in = NumericInFilter(name='id', lookup_expr='in')
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    region_id = NullableModelMultipleChoiceFilter(
        name='region',
        queryset=Region.objects.all(),
        label='Region (ID)',
    )
    region = NullableModelMultipleChoiceFilter(
        name='region',
        queryset=Region.objects.all(),
        to_field_name='slug',
        label='Region (slug)',
    )
    tenant_id = NullableModelMultipleChoiceFilter(
        name='tenant',
        queryset=Tenant.objects.all(),
        label='Tenant (ID)',
    )
    tenant = NullableModelMultipleChoiceFilter(
        name='tenant',
        queryset=Tenant.objects.all(),
        to_field_name='slug',
        label='Tenant (slug)',
    )

    class Meta:
        model = Site
        fields = ['q', 'name', 'facility', 'asn']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = (
            Q(name__icontains=value) |
            Q(facility__icontains=value) |
            Q(physical_address__icontains=value) |
            Q(shipping_address__icontains=value) |
            Q(comments__icontains=value)
        )
        try:
            qs_filter |= Q(asn=int(value.strip()))
        except ValueError:
            pass
        return queryset.filter(qs_filter)


class RackGroupFilter(django_filters.FilterSet):
    site_id = django_filters.ModelMultipleChoiceFilter(
        name='site',
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
        fields = ['name']


class RackFilter(CustomFieldFilterSet, django_filters.FilterSet):
    id__in = NumericInFilter(name='id', lookup_expr='in')
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    site_id = django_filters.ModelMultipleChoiceFilter(
        name='site',
        queryset=Site.objects.all(),
        label='Site (ID)',
    )
    site = django_filters.ModelMultipleChoiceFilter(
        name='site__slug',
        queryset=Site.objects.all(),
        to_field_name='slug',
        label='Site (slug)',
    )
    group_id = NullableModelMultipleChoiceFilter(
        name='group',
        queryset=RackGroup.objects.all(),
        label='Group (ID)',
    )
    group = NullableModelMultipleChoiceFilter(
        name='group',
        queryset=RackGroup.objects.all(),
        to_field_name='slug',
        label='Group',
    )
    tenant_id = NullableModelMultipleChoiceFilter(
        name='tenant',
        queryset=Tenant.objects.all(),
        label='Tenant (ID)',
    )
    tenant = NullableModelMultipleChoiceFilter(
        name='tenant',
        queryset=Tenant.objects.all(),
        to_field_name='slug',
        label='Tenant (slug)',
    )
    role_id = NullableModelMultipleChoiceFilter(
        name='role',
        queryset=RackRole.objects.all(),
        label='Role (ID)',
    )
    role = NullableModelMultipleChoiceFilter(
        name='role',
        queryset=RackRole.objects.all(),
        to_field_name='slug',
        label='Role (slug)',
    )

    class Meta:
        model = Rack
        fields = ['u_height']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(facility_id__icontains=value) |
            Q(comments__icontains=value)
        )


class RackReservationFilter(django_filters.FilterSet):
    id__in = NumericInFilter(name='id', lookup_expr='in')
    q = django_filters.CharFilter(
        method='search',
        label='Search',
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
    group_id = NullableModelMultipleChoiceFilter(
        name='rack__group',
        queryset=RackGroup.objects.all(),
        label='Group (ID)',
    )
    group = NullableModelMultipleChoiceFilter(
        name='rack__group',
        queryset=RackGroup.objects.all(),
        to_field_name='slug',
        label='Group',
    )
    rack_id = django_filters.ModelMultipleChoiceFilter(
        name='rack',
        queryset=Rack.objects.all(),
        label='Rack (ID)',
    )

    class Meta:
        model = RackReservation
        fields = ['rack', 'user']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(rack__name__icontains=value) |
            Q(rack__facility_id__icontains=value) |
            Q(user__username__icontains=value) |
            Q(description__icontains=value)
        )


class DeviceTypeFilter(CustomFieldFilterSet, django_filters.FilterSet):
    id__in = NumericInFilter(name='id', lookup_expr='in')
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
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
        model = DeviceType
        fields = [
            'model', 'part_number', 'u_height', 'is_console_server', 'is_pdu', 'is_network_device', 'subdevice_role',
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
        name='device_type',
        queryset=DeviceType.objects.all(),
        label='Device type (ID)',
    )
    devicetype = django_filters.ModelMultipleChoiceFilter(
        name='device_type',
        queryset=DeviceType.objects.all(),
        to_field_name='name',
        label='Device type (name)',
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
        fields = ['name', 'form_factor']


class DeviceBayTemplateFilter(DeviceTypeComponentFilterSet):

    class Meta:
        model = DeviceBayTemplate
        fields = ['name']


class DeviceFilter(CustomFieldFilterSet, django_filters.FilterSet):
    id__in = NumericInFilter(name='id', lookup_expr='in')
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    mac_address = django_filters.CharFilter(
        method='_mac_address',
        label='MAC address',
    )
    site_id = django_filters.ModelMultipleChoiceFilter(
        name='site',
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
    rack_id = NullableModelMultipleChoiceFilter(
        name='rack',
        queryset=Rack.objects.all(),
        label='Rack (ID)',
    )
    role_id = django_filters.ModelMultipleChoiceFilter(
        name='device_role',
        queryset=DeviceRole.objects.all(),
        label='Role (ID)',
    )
    role = django_filters.ModelMultipleChoiceFilter(
        name='device_role__slug',
        queryset=DeviceRole.objects.all(),
        to_field_name='slug',
        label='Role (slug)',
    )
    tenant_id = NullableModelMultipleChoiceFilter(
        name='tenant',
        queryset=Tenant.objects.all(),
        label='Tenant (ID)',
    )
    tenant = NullableModelMultipleChoiceFilter(
        name='tenant',
        queryset=Tenant.objects.all(),
        to_field_name='slug',
        label='Tenant (slug)',
    )
    device_type_id = django_filters.ModelMultipleChoiceFilter(
        name='device_type',
        queryset=DeviceType.objects.all(),
        label='Device type (ID)',
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
    model = django_filters.ModelMultipleChoiceFilter(
        name='device_type__slug',
        queryset=DeviceType.objects.all(),
        to_field_name='slug',
        label='Device model (slug)',
    )
    platform_id = NullableModelMultipleChoiceFilter(
        name='platform',
        queryset=Platform.objects.all(),
        label='Platform (ID)',
    )
    platform = NullableModelMultipleChoiceFilter(
        name='platform',
        queryset=Platform.objects.all(),
        to_field_name='slug',
        label='Platform (slug)',
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
    has_primary_ip = django_filters.BooleanFilter(
        method='_has_primary_ip',
        label='Has a primary IP',
    )
    status = django_filters.MultipleChoiceFilter(
        choices=STATUS_CHOICES
    )

    class Meta:
        model = Device
        fields = ['name', 'serial', 'asset_tag']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(serial__icontains=value.strip()) |
            Q(inventory_items__serial__icontains=value.strip()) |
            Q(asset_tag=value.strip()) |
            Q(comments__icontains=value)
        ).distinct()

    def _mac_address(self, queryset, name, value):
        value = value.strip()
        if not value:
            return queryset
        try:
            return queryset.filter(interfaces__mac_address=value).distinct()
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
        name='device',
        queryset=Device.objects.all(),
        label='Device (ID)',
    )
    device = django_filters.ModelChoiceFilter(
        name='device__name',
        queryset=Device.objects.all(),
        to_field_name='name',
        label='Device (name)',
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

    class Meta:
        model = Interface
        fields = ['name', 'form_factor']

    def filter_device(self, queryset, name, value):
        try:
            device = Device.objects.select_related('device_type').get(**{name: value})
            ordering = device.device_type.interface_ordering
            return queryset.filter(device=device).order_naturally(ordering)
        except Device.DoesNotExist:
            return queryset.none()

    def filter_type(self, queryset, name, value):
        value = value.strip().lower()
        if value == 'physical':
            return queryset.exclude(form_factor__in=VIRTUAL_IFACE_TYPES)
        elif value == 'virtual':
            return queryset.filter(form_factor__in=VIRTUAL_IFACE_TYPES)
        elif value == 'lag':
            return queryset.filter(form_factor=IFACE_FF_LAG)
        return queryset

    def _mac_address(self, queryset, name, value):
        value = value.strip()
        if not value:
            return queryset
        try:
            return queryset.filter(mac_address=value)
        except AddrFormatError:
            return queryset.none()


class DeviceBayFilter(DeviceComponentFilterSet):

    class Meta:
        model = DeviceBay
        fields = ['name']


class InventoryItemFilter(DeviceComponentFilterSet):

    class Meta:
        model = InventoryItem
        fields = ['name']


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
