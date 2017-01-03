import django_filters
from netaddr.core import AddrFormatError

from django.db.models import Q

from extras.filters import CustomFieldFilterSet
from tenancy.models import Tenant
from utilities.filters import NullableModelMultipleChoiceFilter
from .models import (
    ConsolePort, ConsoleServerPort, Device, DeviceRole, DeviceType, Interface, InterfaceConnection, Manufacturer,
    Platform, PowerOutlet, PowerPort, Rack, RackGroup, RackRole, Site,
)


class SiteFilter(CustomFieldFilterSet, django_filters.FilterSet):
    q = django_filters.MethodFilter(
        action='search',
        label='Search',
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

    def search(self, queryset, value):
        qs_filter = Q(name__icontains=value) | Q(facility__icontains=value) | Q(physical_address__icontains=value) | \
            Q(shipping_address__icontains=value) | Q(comments__icontains=value)
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


class RackFilter(CustomFieldFilterSet, django_filters.FilterSet):
    q = django_filters.MethodFilter(
        action='search',
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

    def search(self, queryset, value):
        return queryset.filter(
            Q(name__icontains=value) |
            Q(facility_id__icontains=value) |
            Q(comments__icontains=value)
        )


class DeviceTypeFilter(CustomFieldFilterSet, django_filters.FilterSet):
    q = django_filters.MethodFilter(
        action='search',
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
        fields = ['model', 'part_number', 'u_height', 'is_console_server', 'is_pdu', 'is_network_device',
                  'subdevice_role']

    def search(self, queryset, value):
        return queryset.filter(
            Q(manufacturer__name__icontains=value) |
            Q(model__icontains=value) |
            Q(part_number__icontains=value) |
            Q(comments__icontains=value)
        )


class DeviceFilter(CustomFieldFilterSet, django_filters.FilterSet):
    q = django_filters.MethodFilter(
        action='search',
        label='Search',
    )
    mac_address = django_filters.MethodFilter(
        action='_mac_address',
        label='MAC address',
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
    status = django_filters.BooleanFilter(
        name='status',
        label='Status',
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

    class Meta:
        model = Device
        fields = ['name', 'serial', 'asset_tag']

    def search(self, queryset, value):
        return queryset.filter(
            Q(name__icontains=value) |
            Q(serial__icontains=value.strip()) |
            Q(modules__serial__icontains=value.strip()) |
            Q(asset_tag=value.strip()) |
            Q(comments__icontains=value)
        ).distinct()

    def _mac_address(self, queryset, value):
        value = value.strip()
        if not value:
            return queryset
        try:
            return queryset.filter(interfaces__mac_address=value).distinct()
        except AddrFormatError:
            return queryset.none()


class ConsolePortFilter(django_filters.FilterSet):
    device_id = django_filters.ModelMultipleChoiceFilter(
        name='device',
        queryset=Device.objects.all(),
        label='Device (ID)',
    )
    device = django_filters.ModelMultipleChoiceFilter(
        name='device',
        queryset=Device.objects.all(),
        to_field_name='name',
        label='Device (name)',
    )

    class Meta:
        model = ConsolePort
        fields = ['name']


class ConsoleServerPortFilter(django_filters.FilterSet):
    device_id = django_filters.ModelMultipleChoiceFilter(
        name='device',
        queryset=Device.objects.all(),
        label='Device (ID)',
    )
    device = django_filters.ModelMultipleChoiceFilter(
        name='device',
        queryset=Device.objects.all(),
        to_field_name='name',
        label='Device (name)',
    )

    class Meta:
        model = ConsoleServerPort
        fields = ['name']


class PowerPortFilter(django_filters.FilterSet):
    device_id = django_filters.ModelMultipleChoiceFilter(
        name='device',
        queryset=Device.objects.all(),
        label='Device (ID)',
    )
    device = django_filters.ModelMultipleChoiceFilter(
        name='device',
        queryset=Device.objects.all(),
        to_field_name='name',
        label='Device (name)',
    )

    class Meta:
        model = PowerPort
        fields = ['name']


class PowerOutletFilter(django_filters.FilterSet):
    device_id = django_filters.ModelMultipleChoiceFilter(
        name='device',
        queryset=Device.objects.all(),
        label='Device (ID)',
    )
    device = django_filters.ModelMultipleChoiceFilter(
        name='device',
        queryset=Device.objects.all(),
        to_field_name='name',
        label='Device (name)',
    )

    class Meta:
        model = PowerOutlet
        fields = ['name']


class InterfaceFilter(django_filters.FilterSet):
    device_id = django_filters.ModelMultipleChoiceFilter(
        name='device',
        queryset=Device.objects.all(),
        label='Device (ID)',
    )
    device = django_filters.ModelMultipleChoiceFilter(
        name='device',
        queryset=Device.objects.all(),
        to_field_name='name',
        label='Device (name)',
    )

    class Meta:
        model = Interface
        fields = ['name']


class ConsoleConnectionFilter(django_filters.FilterSet):
    site = django_filters.MethodFilter(
        action='filter_site',
        label='Site (slug)',
    )

    class Meta:
        model = ConsoleServerPort

    def filter_site(self, queryset, value):
        value = value.strip()
        if not value:
            return queryset
        return queryset.filter(cs_port__device__rack__site__slug=value)


class PowerConnectionFilter(django_filters.FilterSet):
    site = django_filters.MethodFilter(
        action='filter_site',
        label='Site (slug)',
    )

    class Meta:
        model = PowerOutlet

    def filter_site(self, queryset, value):
        value = value.strip()
        if not value:
            return queryset
        return queryset.filter(power_outlet__device__rack__site__slug=value)


class InterfaceConnectionFilter(django_filters.FilterSet):
    site = django_filters.MethodFilter(
        action='filter_site',
        label='Site (slug)',
    )

    class Meta:
        model = InterfaceConnection

    def filter_site(self, queryset, value):
        value = value.strip()
        if not value:
            return queryset
        return queryset.filter(
            Q(interface_a__device__rack__site__slug=value) |
            Q(interface_b__device__rack__site__slug=value)
        )
