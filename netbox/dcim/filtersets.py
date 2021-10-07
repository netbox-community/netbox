import django_filters
from django.contrib.auth.models import User

from extras.filters import TagFilter
from extras.filtersets import LocalConfigContextFilterSet
from netbox.filtersets import (
    BaseFilterSet, ChangeLoggedModelFilterSet, OrganizationalModelFilterSet, PrimaryModelFilterSet,
)
from tenancy.filtersets import TenancyFilterSet
from tenancy.models import Tenant
from utilities.choices import ColorChoices
from utilities.filters import (
    ContentTypeFilter, MultiValueCharFilter, MultiValueMACAddressFilter, MultiValueNumberFilter, MultiValueWWNFilter,
    TreeNodeMultipleChoiceFilter,
)
from virtualization.models import Cluster
from .choices import *
from .constants import *
from .models import *

__all__ = (
    'CableFilterSet',
    'CableTerminationFilterSet',
    'ConsoleConnectionFilterSet',
    'ConsolePortFilterSet',
    'ConsolePortTemplateFilterSet',
    'ConsoleServerPortFilterSet',
    'ConsoleServerPortTemplateFilterSet',
    'DeviceBayFilterSet',
    'DeviceBayTemplateFilterSet',
    'DeviceFilterSet',
    'DeviceRoleFilterSet',
    'DeviceTypeFilterSet',
    'FrontPortFilterSet',
    'FrontPortTemplateFilterSet',
    'InterfaceConnectionFilterSet',
    'InterfaceFilterSet',
    'InterfaceTemplateFilterSet',
    'InventoryItemFilterSet',
    'LocationFilterSet',
    'ManufacturerFilterSet',
    'PathEndpointFilterSet',
    'PlatformFilterSet',
    'PowerConnectionFilterSet',
    'PowerFeedFilterSet',
    'PowerOutletFilterSet',
    'PowerOutletTemplateFilterSet',
    'PowerPanelFilterSet',
    'PowerPortFilterSet',
    'PowerPortTemplateFilterSet',
    'RackFilterSet',
    'RackReservationFilterSet',
    'RackRoleFilterSet',
    'RearPortFilterSet',
    'RearPortTemplateFilterSet',
    'RegionFilterSet',
    'SiteFilterSet',
    'SiteGroupFilterSet',
    'VirtualChassisFilterSet',
)


class RegionFilterSet(OrganizationalModelFilterSet):
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
        fields = ['id', 'name', 'slug', 'description']


class SiteGroupFilterSet(OrganizationalModelFilterSet):
    parent_id = django_filters.ModelMultipleChoiceFilter(
        queryset=SiteGroup.objects.all(),
        label='Parent site group (ID)',
    )
    parent = django_filters.ModelMultipleChoiceFilter(
        field_name='parent__slug',
        queryset=SiteGroup.objects.all(),
        to_field_name='slug',
        label='Parent site group (slug)',
    )

    class Meta:
        model = SiteGroup
        fields = ['id', 'name', 'slug', 'description']


class SiteFilterSet(PrimaryModelFilterSet, TenancyFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    status = django_filters.MultipleChoiceFilter(
        choices=SiteStatusChoices,
        null_value=None
    )
    region_id = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='region',
        lookup_expr='in',
        label='Region (ID)',
    )
    region = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        lookup_expr='in',
        to_field_name='slug',
        label='Region (slug)',
    )
    group_id = TreeNodeMultipleChoiceFilter(
        queryset=SiteGroup.objects.all(),
        field_name='group',
        lookup_expr='in',
        label='Group (ID)',
    )
    group = TreeNodeMultipleChoiceFilter(
        queryset=SiteGroup.objects.all(),
        lookup_expr='in',
        to_field_name='slug',
        label='Group (slug)',
    )
    tag = TagFilter()

    class Meta:
        model = Site
        fields = [
            'id', 'name', 'slug', 'facility', 'asn', 'latitude', 'longitude', 'contact_name', 'contact_phone',
            'contact_email',
        ]

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


class LocationFilterSet(OrganizationalModelFilterSet):
    region_id = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='site__region',
        lookup_expr='in',
        label='Region (ID)',
    )
    region = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='site__region',
        lookup_expr='in',
        to_field_name='slug',
        label='Region (slug)',
    )
    site_group_id = TreeNodeMultipleChoiceFilter(
        queryset=SiteGroup.objects.all(),
        field_name='site__group',
        lookup_expr='in',
        label='Site group (ID)',
    )
    site_group = TreeNodeMultipleChoiceFilter(
        queryset=SiteGroup.objects.all(),
        field_name='site__group',
        lookup_expr='in',
        to_field_name='slug',
        label='Site group (slug)',
    )
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
    parent_id = TreeNodeMultipleChoiceFilter(
        queryset=Location.objects.all(),
        field_name='parent',
        lookup_expr='in',
        label='Location (ID)',
    )
    parent = TreeNodeMultipleChoiceFilter(
        queryset=Location.objects.all(),
        field_name='parent',
        lookup_expr='in',
        to_field_name='slug',
        label='Location (slug)',
    )

    class Meta:
        model = Location
        fields = ['id', 'name', 'slug', 'description']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value)
        )


class RackRoleFilterSet(OrganizationalModelFilterSet):

    class Meta:
        model = RackRole
        fields = ['id', 'name', 'slug', 'color']


class RackFilterSet(PrimaryModelFilterSet, TenancyFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    region_id = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='site__region',
        lookup_expr='in',
        label='Region (ID)',
    )
    region = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='site__region',
        lookup_expr='in',
        to_field_name='slug',
        label='Region (slug)',
    )
    site_group_id = TreeNodeMultipleChoiceFilter(
        queryset=SiteGroup.objects.all(),
        field_name='site__group',
        lookup_expr='in',
        label='Site group (ID)',
    )
    site_group = TreeNodeMultipleChoiceFilter(
        queryset=SiteGroup.objects.all(),
        field_name='site__group',
        lookup_expr='in',
        to_field_name='slug',
        label='Site group (slug)',
    )
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
    location_id = TreeNodeMultipleChoiceFilter(
        queryset=Location.objects.all(),
        field_name='location',
        lookup_expr='in',
        label='Location (ID)',
    )
    location = TreeNodeMultipleChoiceFilter(
        queryset=Location.objects.all(),
        field_name='location',
        lookup_expr='in',
        to_field_name='slug',
        label='Location (slug)',
    )
    status = django_filters.MultipleChoiceFilter(
        choices=RackStatusChoices,
        null_value=None
    )
    type = django_filters.MultipleChoiceFilter(
        choices=RackTypeChoices
    )
    width = django_filters.MultipleChoiceFilter(
        choices=RackWidthChoices
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
    serial = django_filters.CharFilter(
        lookup_expr='iexact'
    )
    tag = TagFilter()

    class Meta:
        model = Rack
        fields = [
            'id', 'name', 'facility_id', 'asset_tag', 'u_height', 'desc_units', 'outer_width', 'outer_depth',
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


class RackReservationFilterSet(PrimaryModelFilterSet, TenancyFilterSet):
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
    location_id = TreeNodeMultipleChoiceFilter(
        queryset=Location.objects.all(),
        field_name='rack__location',
        lookup_expr='in',
        label='Location (ID)',
    )
    location = TreeNodeMultipleChoiceFilter(
        queryset=Location.objects.all(),
        field_name='rack__location',
        lookup_expr='in',
        to_field_name='slug',
        label='Location (slug)',
    )
    user_id = django_filters.ModelMultipleChoiceFilter(
        queryset=User.objects.all(),
        label='User (ID)',
    )
    user = django_filters.ModelMultipleChoiceFilter(
        field_name='user__username',
        queryset=User.objects.all(),
        to_field_name='username',
        label='User (name)',
    )
    tag = TagFilter()

    class Meta:
        model = RackReservation
        fields = ['id', 'created']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(rack__name__icontains=value) |
            Q(rack__facility_id__icontains=value) |
            Q(user__username__icontains=value) |
            Q(description__icontains=value)
        )


class ManufacturerFilterSet(OrganizationalModelFilterSet):

    class Meta:
        model = Manufacturer
        fields = ['id', 'name', 'slug', 'description']


class DeviceTypeFilterSet(PrimaryModelFilterSet):
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
    device_bays = django_filters.BooleanFilter(
        method='_device_bays',
        label='Has device bays',
    )
    tag = TagFilter()

    class Meta:
        model = DeviceType
        fields = [
            'id', 'model', 'slug', 'part_number', 'u_height', 'is_full_depth', 'subdevice_role',
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
        return queryset.exclude(consoleporttemplates__isnull=value)

    def _console_server_ports(self, queryset, name, value):
        return queryset.exclude(consoleserverporttemplates__isnull=value)

    def _power_ports(self, queryset, name, value):
        return queryset.exclude(powerporttemplates__isnull=value)

    def _power_outlets(self, queryset, name, value):
        return queryset.exclude(poweroutlettemplates__isnull=value)

    def _interfaces(self, queryset, name, value):
        return queryset.exclude(interfacetemplates__isnull=value)

    def _pass_through_ports(self, queryset, name, value):
        return queryset.exclude(
            frontporttemplates__isnull=value,
            rearporttemplates__isnull=value
        )

    def _device_bays(self, queryset, name, value):
        return queryset.exclude(devicebaytemplates__isnull=value)


class DeviceTypeComponentFilterSet(django_filters.FilterSet):
    devicetype_id = django_filters.ModelMultipleChoiceFilter(
        queryset=DeviceType.objects.all(),
        field_name='device_type_id',
        label='Device type (ID)',
    )


class ConsolePortTemplateFilterSet(ChangeLoggedModelFilterSet, DeviceTypeComponentFilterSet):

    class Meta:
        model = ConsolePortTemplate
        fields = ['id', 'name', 'type']


class ConsoleServerPortTemplateFilterSet(ChangeLoggedModelFilterSet, DeviceTypeComponentFilterSet):

    class Meta:
        model = ConsoleServerPortTemplate
        fields = ['id', 'name', 'type']


class PowerPortTemplateFilterSet(ChangeLoggedModelFilterSet, DeviceTypeComponentFilterSet):

    class Meta:
        model = PowerPortTemplate
        fields = ['id', 'name', 'type', 'maximum_draw', 'allocated_draw']


class PowerOutletTemplateFilterSet(ChangeLoggedModelFilterSet, DeviceTypeComponentFilterSet):
    feed_leg = django_filters.MultipleChoiceFilter(
        choices=PowerOutletFeedLegChoices,
        null_value=None
    )

    class Meta:
        model = PowerOutletTemplate
        fields = ['id', 'name', 'type', 'feed_leg']


class InterfaceTemplateFilterSet(ChangeLoggedModelFilterSet, DeviceTypeComponentFilterSet):
    type = django_filters.MultipleChoiceFilter(
        choices=InterfaceTypeChoices,
        null_value=None
    )

    class Meta:
        model = InterfaceTemplate
        fields = ['id', 'name', 'type', 'mgmt_only']


class FrontPortTemplateFilterSet(ChangeLoggedModelFilterSet, DeviceTypeComponentFilterSet):
    type = django_filters.MultipleChoiceFilter(
        choices=PortTypeChoices,
        null_value=None
    )

    class Meta:
        model = FrontPortTemplate
        fields = ['id', 'name', 'type', 'color']


class RearPortTemplateFilterSet(ChangeLoggedModelFilterSet, DeviceTypeComponentFilterSet):
    type = django_filters.MultipleChoiceFilter(
        choices=PortTypeChoices,
        null_value=None
    )

    class Meta:
        model = RearPortTemplate
        fields = ['id', 'name', 'type', 'color', 'positions']


class DeviceBayTemplateFilterSet(ChangeLoggedModelFilterSet, DeviceTypeComponentFilterSet):

    class Meta:
        model = DeviceBayTemplate
        fields = ['id', 'name']


class DeviceRoleFilterSet(OrganizationalModelFilterSet):

    class Meta:
        model = DeviceRole
        fields = ['id', 'name', 'slug', 'color', 'vm_role']


class PlatformFilterSet(OrganizationalModelFilterSet):
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
        fields = ['id', 'name', 'slug', 'napalm_driver', 'description']


class DeviceFilterSet(PrimaryModelFilterSet, TenancyFilterSet, LocalConfigContextFilterSet):
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
    region_id = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='site__region',
        lookup_expr='in',
        label='Region (ID)',
    )
    region = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='site__region',
        lookup_expr='in',
        to_field_name='slug',
        label='Region (slug)',
    )
    site_group_id = TreeNodeMultipleChoiceFilter(
        queryset=SiteGroup.objects.all(),
        field_name='site__group',
        lookup_expr='in',
        label='Site group (ID)',
    )
    site_group = TreeNodeMultipleChoiceFilter(
        queryset=SiteGroup.objects.all(),
        field_name='site__group',
        lookup_expr='in',
        to_field_name='slug',
        label='Site group (slug)',
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
    location_id = TreeNodeMultipleChoiceFilter(
        queryset=Location.objects.all(),
        field_name='location',
        lookup_expr='in',
        label='Location (ID)',
    )
    rack_id = django_filters.ModelMultipleChoiceFilter(
        field_name='rack',
        queryset=Rack.objects.all(),
        label='Rack (ID)',
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
        choices=DeviceStatusChoices,
        null_value=None
    )
    is_full_depth = django_filters.BooleanFilter(
        field_name='device_type__is_full_depth',
        label='Is full depth',
    )
    mac_address = MultiValueMACAddressFilter(
        field_name='interfaces__mac_address',
        label='MAC address',
    )
    serial = django_filters.CharFilter(
        lookup_expr='iexact'
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
    virtual_chassis_member = django_filters.BooleanFilter(
        method='_virtual_chassis_member',
        label='Is a virtual chassis member'
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
    device_bays = django_filters.BooleanFilter(
        method='_device_bays',
        label='Has device bays',
    )
    tag = TagFilter()

    class Meta:
        model = Device
        fields = ['id', 'name', 'asset_tag', 'face', 'position', 'vc_position', 'vc_priority']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(serial__icontains=value.strip()) |
            Q(inventoryitems__serial__icontains=value.strip()) |
            Q(asset_tag__icontains=value.strip()) |
            Q(comments__icontains=value)
        ).distinct()

    def _has_primary_ip(self, queryset, name, value):
        params = Q(primary_ip4__isnull=False) | Q(primary_ip6__isnull=False)
        if value:
            return queryset.filter(params)
        return queryset.exclude(params)

    def _virtual_chassis_member(self, queryset, name, value):
        return queryset.exclude(virtual_chassis__isnull=value)

    def _console_ports(self, queryset, name, value):
        return queryset.exclude(consoleports__isnull=value)

    def _console_server_ports(self, queryset, name, value):
        return queryset.exclude(consoleserverports__isnull=value)

    def _power_ports(self, queryset, name, value):
        return queryset.exclude(powerports__isnull=value)

    def _power_outlets(self, queryset, name, value):
        return queryset.exclude(poweroutlets__isnull=value)

    def _interfaces(self, queryset, name, value):
        return queryset.exclude(interfaces__isnull=value)

    def _pass_through_ports(self, queryset, name, value):
        return queryset.exclude(
            frontports__isnull=value,
            rearports__isnull=value
        )

    def _device_bays(self, queryset, name, value):
        return queryset.exclude(devicebays__isnull=value)


class DeviceComponentFilterSet(django_filters.FilterSet):
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    region_id = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='device__site__region',
        lookup_expr='in',
        label='Region (ID)',
    )
    region = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='device__site__region',
        lookup_expr='in',
        to_field_name='slug',
        label='Region (slug)',
    )
    site_group_id = TreeNodeMultipleChoiceFilter(
        queryset=SiteGroup.objects.all(),
        field_name='device__site__group',
        lookup_expr='in',
        label='Site group (ID)',
    )
    site_group = TreeNodeMultipleChoiceFilter(
        queryset=SiteGroup.objects.all(),
        field_name='device__site__group',
        lookup_expr='in',
        to_field_name='slug',
        label='Site group (slug)',
    )
    site_id = django_filters.ModelMultipleChoiceFilter(
        field_name='device__site',
        queryset=Site.objects.all(),
        label='Site (ID)',
    )
    site = django_filters.ModelMultipleChoiceFilter(
        field_name='device__site__slug',
        queryset=Site.objects.all(),
        to_field_name='slug',
        label='Site name (slug)',
    )
    location_id = django_filters.ModelMultipleChoiceFilter(
        field_name='device__location',
        queryset=Location.objects.all(),
        label='Location (ID)',
    )
    location = django_filters.ModelMultipleChoiceFilter(
        field_name='device__location__slug',
        queryset=Location.objects.all(),
        to_field_name='slug',
        label='Location (slug)',
    )
    device_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Device.objects.all(),
        label='Device (ID)',
    )
    device = django_filters.ModelMultipleChoiceFilter(
        field_name='device__name',
        queryset=Device.objects.all(),
        to_field_name='name',
        label='Device (name)',
    )
    tag = TagFilter()

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(label__icontains=value) |
            Q(description__icontains=value)
        )


class CableTerminationFilterSet(django_filters.FilterSet):
    cabled = django_filters.BooleanFilter(
        field_name='cable',
        lookup_expr='isnull',
        exclude=True
    )


class PathEndpointFilterSet(django_filters.FilterSet):
    connected = django_filters.BooleanFilter(
        method='filter_connected'
    )

    def filter_connected(self, queryset, name, value):
        if value:
            return queryset.filter(_path__is_active=True)
        else:
            return queryset.filter(Q(_path__isnull=True) | Q(_path__is_active=False))


class ConsolePortFilterSet(PrimaryModelFilterSet, DeviceComponentFilterSet, CableTerminationFilterSet, PathEndpointFilterSet):
    type = django_filters.MultipleChoiceFilter(
        choices=ConsolePortTypeChoices,
        null_value=None
    )

    class Meta:
        model = ConsolePort
        fields = ['id', 'name', 'label', 'description']


class ConsoleServerPortFilterSet(PrimaryModelFilterSet, DeviceComponentFilterSet, CableTerminationFilterSet, PathEndpointFilterSet):
    type = django_filters.MultipleChoiceFilter(
        choices=ConsolePortTypeChoices,
        null_value=None
    )

    class Meta:
        model = ConsoleServerPort
        fields = ['id', 'name', 'label', 'description']


class PowerPortFilterSet(PrimaryModelFilterSet, DeviceComponentFilterSet, CableTerminationFilterSet, PathEndpointFilterSet):
    type = django_filters.MultipleChoiceFilter(
        choices=PowerPortTypeChoices,
        null_value=None
    )

    class Meta:
        model = PowerPort
        fields = ['id', 'name', 'label', 'maximum_draw', 'allocated_draw', 'description']


class PowerOutletFilterSet(PrimaryModelFilterSet, DeviceComponentFilterSet, CableTerminationFilterSet, PathEndpointFilterSet):
    type = django_filters.MultipleChoiceFilter(
        choices=PowerOutletTypeChoices,
        null_value=None
    )
    feed_leg = django_filters.MultipleChoiceFilter(
        choices=PowerOutletFeedLegChoices,
        null_value=None
    )

    class Meta:
        model = PowerOutlet
        fields = ['id', 'name', 'label', 'feed_leg', 'description']


class InterfaceFilterSet(PrimaryModelFilterSet, DeviceComponentFilterSet, CableTerminationFilterSet, PathEndpointFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    # Override device and device_id filters from DeviceComponentFilterSet to match against any peer virtual chassis
    # members
    device = MultiValueCharFilter(
        method='filter_device',
        field_name='name',
        label='Device',
    )
    device_id = MultiValueNumberFilter(
        method='filter_device_id',
        field_name='pk',
        label='Device (ID)',
    )
    kind = django_filters.CharFilter(
        method='filter_kind',
        label='Kind of interface',
    )
    parent_id = django_filters.ModelMultipleChoiceFilter(
        field_name='parent',
        queryset=Interface.objects.all(),
        label='Parent interface (ID)',
    )
    lag_id = django_filters.ModelMultipleChoiceFilter(
        field_name='lag',
        queryset=Interface.objects.all(),
        label='LAG interface (ID)',
    )
    mac_address = MultiValueMACAddressFilter()
    wwn = MultiValueWWNFilter()
    tag = TagFilter()
    vlan_id = django_filters.CharFilter(
        method='filter_vlan_id',
        label='Assigned VLAN'
    )
    vlan = django_filters.CharFilter(
        method='filter_vlan',
        label='Assigned VID'
    )
    type = django_filters.MultipleChoiceFilter(
        choices=InterfaceTypeChoices,
        null_value=None
    )

    class Meta:
        model = Interface
        fields = ['id', 'name', 'label', 'type', 'enabled', 'mtu', 'mgmt_only', 'mode', 'description']

    def filter_device(self, queryset, name, value):
        try:
            devices = Device.objects.filter(**{'{}__in'.format(name): value})
            vc_interface_ids = []
            for device in devices:
                vc_interface_ids.extend(device.vc_interfaces().values_list('id', flat=True))
            return queryset.filter(pk__in=vc_interface_ids)
        except Device.DoesNotExist:
            return queryset.none()

    def filter_device_id(self, queryset, name, id_list):
        # Include interfaces belonging to peer virtual chassis members
        vc_interface_ids = []
        try:
            devices = Device.objects.filter(pk__in=id_list)
            for device in devices:
                vc_interface_ids += device.vc_interfaces().values_list('id', flat=True)
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

    def filter_kind(self, queryset, name, value):
        value = value.strip().lower()
        return {
            'physical': queryset.exclude(type__in=NONCONNECTABLE_IFACE_TYPES),
            'virtual': queryset.filter(type__in=VIRTUAL_IFACE_TYPES),
            'wireless': queryset.filter(type__in=WIRELESS_IFACE_TYPES),
        }.get(value, queryset.none())


class FrontPortFilterSet(PrimaryModelFilterSet, DeviceComponentFilterSet, CableTerminationFilterSet):
    type = django_filters.MultipleChoiceFilter(
        choices=PortTypeChoices,
        null_value=None
    )

    class Meta:
        model = FrontPort
        fields = ['id', 'name', 'label', 'type', 'color', 'description']


class RearPortFilterSet(PrimaryModelFilterSet, DeviceComponentFilterSet, CableTerminationFilterSet):
    type = django_filters.MultipleChoiceFilter(
        choices=PortTypeChoices,
        null_value=None
    )

    class Meta:
        model = RearPort
        fields = ['id', 'name', 'label', 'type', 'color', 'positions', 'description']


class DeviceBayFilterSet(PrimaryModelFilterSet, DeviceComponentFilterSet):

    class Meta:
        model = DeviceBay
        fields = ['id', 'name', 'label', 'description']


class InventoryItemFilterSet(PrimaryModelFilterSet, DeviceComponentFilterSet):
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
        field_name='manufacturer__slug',
        queryset=Manufacturer.objects.all(),
        to_field_name='slug',
        label='Manufacturer (slug)',
    )
    serial = django_filters.CharFilter(
        lookup_expr='iexact'
    )

    class Meta:
        model = InventoryItem
        fields = ['id', 'name', 'label', 'part_id', 'asset_tag', 'discovered']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = (
            Q(name__icontains=value) |
            Q(part_id__icontains=value) |
            Q(serial__icontains=value) |
            Q(asset_tag__icontains=value) |
            Q(description__icontains=value)
        )
        return queryset.filter(qs_filter)


class VirtualChassisFilterSet(PrimaryModelFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    master_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Device.objects.all(),
        label='Master (ID)',
    )
    master = django_filters.ModelMultipleChoiceFilter(
        field_name='master__name',
        queryset=Device.objects.all(),
        to_field_name='name',
        label='Master (name)',
    )
    region_id = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='master__site__region',
        lookup_expr='in',
        label='Region (ID)',
    )
    region = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='master__site__region',
        lookup_expr='in',
        to_field_name='slug',
        label='Region (slug)',
    )
    site_group_id = TreeNodeMultipleChoiceFilter(
        queryset=SiteGroup.objects.all(),
        field_name='master__site__group',
        lookup_expr='in',
        label='Site group (ID)',
    )
    site_group = TreeNodeMultipleChoiceFilter(
        queryset=SiteGroup.objects.all(),
        field_name='master__site__group',
        lookup_expr='in',
        to_field_name='slug',
        label='Site group (slug)',
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
        fields = ['id', 'domain', 'name']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = (
            Q(name__icontains=value) |
            Q(members__name__icontains=value) |
            Q(domain__icontains=value)
        )
        return queryset.filter(qs_filter).distinct()


class CableFilterSet(PrimaryModelFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    termination_a_type = ContentTypeFilter()
    termination_a_id = MultiValueNumberFilter()
    termination_b_type = ContentTypeFilter()
    termination_b_id = MultiValueNumberFilter()
    type = django_filters.MultipleChoiceFilter(
        choices=CableTypeChoices
    )
    status = django_filters.MultipleChoiceFilter(
        choices=CableStatusChoices
    )
    color = django_filters.MultipleChoiceFilter(
        choices=ColorChoices
    )
    device_id = MultiValueNumberFilter(
        method='filter_device'
    )
    device = MultiValueCharFilter(
        method='filter_device',
        field_name='device__name'
    )
    rack_id = MultiValueNumberFilter(
        method='filter_device',
        field_name='device__rack_id'
    )
    rack = MultiValueNumberFilter(
        method='filter_device',
        field_name='device__rack__name'
    )
    site_id = MultiValueNumberFilter(
        method='filter_device',
        field_name='device__site_id'
    )
    site = MultiValueNumberFilter(
        method='filter_device',
        field_name='device__site__slug'
    )
    tenant_id = MultiValueNumberFilter(
        method='filter_device',
        field_name='device__tenant_id'
    )
    tenant = MultiValueNumberFilter(
        method='filter_device',
        field_name='device__tenant__slug'
    )
    tag = TagFilter()

    class Meta:
        model = Cable
        fields = ['id', 'label', 'length', 'length_unit', 'termination_a_id', 'termination_b_id']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(label__icontains=value)

    def filter_device(self, queryset, name, value):
        queryset = queryset.filter(
            Q(**{'_termination_a_{}__in'.format(name): value}) |
            Q(**{'_termination_b_{}__in'.format(name): value})
        )
        return queryset


class PowerPanelFilterSet(PrimaryModelFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    region_id = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='site__region',
        lookup_expr='in',
        label='Region (ID)',
    )
    region = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='site__region',
        lookup_expr='in',
        to_field_name='slug',
        label='Region (slug)',
    )
    site_group_id = TreeNodeMultipleChoiceFilter(
        queryset=SiteGroup.objects.all(),
        field_name='site__group',
        lookup_expr='in',
        label='Site group (ID)',
    )
    site_group = TreeNodeMultipleChoiceFilter(
        queryset=SiteGroup.objects.all(),
        field_name='site__group',
        lookup_expr='in',
        to_field_name='slug',
        label='Site group (slug)',
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
    location_id = TreeNodeMultipleChoiceFilter(
        queryset=Location.objects.all(),
        field_name='location',
        lookup_expr='in',
        label='Location (ID)',
    )
    tag = TagFilter()

    class Meta:
        model = PowerPanel
        fields = ['id', 'name']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = (
            Q(name__icontains=value)
        )
        return queryset.filter(qs_filter)


class PowerFeedFilterSet(PrimaryModelFilterSet, CableTerminationFilterSet, PathEndpointFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    region_id = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='power_panel__site__region',
        lookup_expr='in',
        label='Region (ID)',
    )
    region = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='power_panel__site__region',
        lookup_expr='in',
        to_field_name='slug',
        label='Region (slug)',
    )
    site_group_id = TreeNodeMultipleChoiceFilter(
        queryset=SiteGroup.objects.all(),
        field_name='power_panel__site__group',
        lookup_expr='in',
        label='Site group (ID)',
    )
    site_group = TreeNodeMultipleChoiceFilter(
        queryset=SiteGroup.objects.all(),
        field_name='power_panel__site__group',
        lookup_expr='in',
        to_field_name='slug',
        label='Site group (slug)',
    )
    site_id = django_filters.ModelMultipleChoiceFilter(
        field_name='power_panel__site',
        queryset=Site.objects.all(),
        label='Site (ID)',
    )
    site = django_filters.ModelMultipleChoiceFilter(
        field_name='power_panel__site__slug',
        queryset=Site.objects.all(),
        to_field_name='slug',
        label='Site name (slug)',
    )
    power_panel_id = django_filters.ModelMultipleChoiceFilter(
        queryset=PowerPanel.objects.all(),
        label='Power panel (ID)',
    )
    rack_id = django_filters.ModelMultipleChoiceFilter(
        field_name='rack',
        queryset=Rack.objects.all(),
        label='Rack (ID)',
    )
    status = django_filters.MultipleChoiceFilter(
        choices=PowerFeedStatusChoices,
        null_value=None
    )
    tag = TagFilter()

    class Meta:
        model = PowerFeed
        fields = ['id', 'name', 'status', 'type', 'supply', 'phase', 'voltage', 'amperage', 'max_utilization']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = (
            Q(name__icontains=value) |
            Q(comments__icontains=value)
        )
        return queryset.filter(qs_filter)


#
# Connection filter sets
#

class ConnectionFilterSet(BaseFilterSet):
    site_id = MultiValueNumberFilter(
        method='filter_connections',
        field_name='device__site_id'
    )
    site = MultiValueCharFilter(
        method='filter_connections',
        field_name='device__site__slug'
    )
    device_id = MultiValueNumberFilter(
        method='filter_connections',
        field_name='device_id'
    )
    device = MultiValueCharFilter(
        method='filter_connections',
        field_name='device__name'
    )

    def filter_connections(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(**{f'{name}__in': value})


class ConsoleConnectionFilterSet(ConnectionFilterSet):

    class Meta:
        model = ConsolePort
        fields = ['name']


class PowerConnectionFilterSet(ConnectionFilterSet):

    class Meta:
        model = PowerPort
        fields = ['name']


class InterfaceConnectionFilterSet(ConnectionFilterSet):

    class Meta:
        model = Interface
        fields = []
