import django_filters
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field

from circuits.models import CircuitTermination, VirtualCircuit, VirtualCircuitTermination
from extras.filtersets import LocalConfigContextFilterSet
from extras.models import ConfigTemplate
from ipam.filtersets import PrimaryIPFilterSet
from ipam.models import ASN, IPAddress, VLANTranslationPolicy, VRF
from netbox.choices import ColorChoices
from netbox.filtersets import (
    AttributeFiltersMixin, BaseFilterSet, ChangeLoggedModelFilterSet, NestedGroupModelFilterSet, NetBoxModelFilterSet,
    OrganizationalModelFilterSet,
)
from tenancy.filtersets import TenancyFilterSet, ContactModelFilterSet
from tenancy.models import *
from users.models import User
from utilities.filters import (
    ContentTypeFilter, MultiValueCharFilter, MultiValueMACAddressFilter, MultiValueNumberFilter, MultiValueWWNFilter,
    NumericArrayFilter, TreeNodeMultipleChoiceFilter,
)
from virtualization.models import Cluster, ClusterGroup, VMInterface, VirtualMachine
from vpn.models import L2VPN
from wireless.choices import WirelessRoleChoices, WirelessChannelChoices
from wireless.models import WirelessLAN, WirelessLink
from .choices import *
from .constants import *
from .models import *

__all__ = (
    'CableFilterSet',
    'CabledObjectFilterSet',
    'CableTerminationFilterSet',
    'CommonInterfaceFilterSet',
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
    'InventoryItemRoleFilterSet',
    'InventoryItemTemplateFilterSet',
    'LocationFilterSet',
    'MACAddressFilterSet',
    'ManufacturerFilterSet',
    'ModuleBayFilterSet',
    'ModuleBayTemplateFilterSet',
    'ModuleFilterSet',
    'ModuleTypeFilterSet',
    'ModuleTypeProfileFilterSet',
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
    'RackTypeFilterSet',
    'RearPortFilterSet',
    'RearPortTemplateFilterSet',
    'RegionFilterSet',
    'SiteFilterSet',
    'SiteGroupFilterSet',
    'VirtualChassisFilterSet',
    'VirtualDeviceContextFilterSet',
)


class RegionFilterSet(NestedGroupModelFilterSet, ContactModelFilterSet):
    parent_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Region.objects.all(),
        label=_('Parent region (ID)'),
    )
    parent = django_filters.ModelMultipleChoiceFilter(
        field_name='parent__slug',
        queryset=Region.objects.all(),
        to_field_name='slug',
        label=_('Parent region (slug)'),
    )
    ancestor_id = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='parent',
        lookup_expr='in',
        label=_('Region (ID)'),
    )
    ancestor = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='parent',
        lookup_expr='in',
        to_field_name='slug',
        label=_('Region (slug)'),
    )

    class Meta:
        model = Region
        fields = ('id', 'name', 'slug', 'description')


class SiteGroupFilterSet(NestedGroupModelFilterSet, ContactModelFilterSet):
    parent_id = django_filters.ModelMultipleChoiceFilter(
        queryset=SiteGroup.objects.all(),
        label=_('Parent site group (ID)'),
    )
    parent = django_filters.ModelMultipleChoiceFilter(
        field_name='parent__slug',
        queryset=SiteGroup.objects.all(),
        to_field_name='slug',
        label=_('Parent site group (slug)'),
    )
    ancestor_id = TreeNodeMultipleChoiceFilter(
        queryset=SiteGroup.objects.all(),
        field_name='parent',
        lookup_expr='in',
        label=_('Site group (ID)'),
    )
    ancestor = TreeNodeMultipleChoiceFilter(
        queryset=SiteGroup.objects.all(),
        field_name='parent',
        lookup_expr='in',
        to_field_name='slug',
        label=_('Site group (slug)'),
    )

    class Meta:
        model = SiteGroup
        fields = ('id', 'name', 'slug', 'description')


class SiteFilterSet(NetBoxModelFilterSet, TenancyFilterSet, ContactModelFilterSet):
    status = django_filters.MultipleChoiceFilter(
        choices=SiteStatusChoices,
        null_value=None
    )
    region_id = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='region',
        lookup_expr='in',
        label=_('Region (ID)'),
    )
    region = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        lookup_expr='in',
        to_field_name='slug',
        label=_('Region (slug)'),
    )
    group_id = TreeNodeMultipleChoiceFilter(
        queryset=SiteGroup.objects.all(),
        field_name='group',
        lookup_expr='in',
        label=_('Group (ID)'),
    )
    group = TreeNodeMultipleChoiceFilter(
        queryset=SiteGroup.objects.all(),
        lookup_expr='in',
        to_field_name='slug',
        label=_('Group (slug)'),
    )
    asn = django_filters.ModelMultipleChoiceFilter(
        field_name='asns__asn',
        queryset=ASN.objects.all(),
        to_field_name='asn',
        label=_('AS (ID)'),
    )
    asn_id = django_filters.ModelMultipleChoiceFilter(
        field_name='asns',
        queryset=ASN.objects.all(),
        label=_('AS (ID)'),
    )
    time_zone = MultiValueCharFilter()

    class Meta:
        model = Site
        fields = ('id', 'name', 'slug', 'facility', 'latitude', 'longitude', 'description')

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = (
            Q(name__icontains=value) |
            Q(facility__icontains=value) |
            Q(description__icontains=value) |
            Q(physical_address__icontains=value) |
            Q(shipping_address__icontains=value) |
            Q(comments__icontains=value)
        )
        try:
            qs_filter |= Q(asns__asn=int(value.strip()))
        except ValueError:
            pass
        return queryset.filter(qs_filter).distinct()


class LocationFilterSet(TenancyFilterSet, ContactModelFilterSet, NestedGroupModelFilterSet):
    region_id = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='site__region',
        lookup_expr='in',
        label=_('Region (ID)'),
    )
    region = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='site__region',
        lookup_expr='in',
        to_field_name='slug',
        label=_('Region (slug)'),
    )
    site_group_id = TreeNodeMultipleChoiceFilter(
        queryset=SiteGroup.objects.all(),
        field_name='site__group',
        lookup_expr='in',
        label=_('Site group (ID)'),
    )
    site_group = TreeNodeMultipleChoiceFilter(
        queryset=SiteGroup.objects.all(),
        field_name='site__group',
        lookup_expr='in',
        to_field_name='slug',
        label=_('Site group (slug)'),
    )
    site_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Site.objects.all(),
        label=_('Site (ID)'),
    )
    site = django_filters.ModelMultipleChoiceFilter(
        field_name='site__slug',
        queryset=Site.objects.all(),
        to_field_name='slug',
        label=_('Site (slug)'),
    )
    parent_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Location.objects.all(),
        label=_('Parent location (ID)'),
    )
    parent = django_filters.ModelMultipleChoiceFilter(
        field_name='parent__slug',
        queryset=Location.objects.all(),
        to_field_name='slug',
        label=_('Parent location (slug)'),
    )
    ancestor_id = TreeNodeMultipleChoiceFilter(
        queryset=Location.objects.all(),
        field_name='parent',
        lookup_expr='in',
        label=_('Location (ID)'),
    )
    ancestor = TreeNodeMultipleChoiceFilter(
        queryset=Location.objects.all(),
        field_name='parent',
        lookup_expr='in',
        to_field_name='slug',
        label=_('Location (slug)'),
    )
    status = django_filters.MultipleChoiceFilter(
        choices=LocationStatusChoices,
        null_value=None
    )

    class Meta:
        model = Location
        fields = ('id', 'name', 'slug', 'facility', 'description')

    def search(self, queryset, name, value):
        # extended in order to include querying on Location.facility
        queryset = super().search(queryset, name, value)

        if value.strip():
            queryset = queryset | queryset.model.objects.filter(facility__icontains=value)

        return queryset


class RackRoleFilterSet(OrganizationalModelFilterSet):

    class Meta:
        model = RackRole
        fields = ('id', 'name', 'slug', 'color', 'description')


class RackTypeFilterSet(NetBoxModelFilterSet):
    manufacturer_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Manufacturer.objects.all(),
        label=_('Manufacturer (ID)'),
    )
    manufacturer = django_filters.ModelMultipleChoiceFilter(
        field_name='manufacturer__slug',
        queryset=Manufacturer.objects.all(),
        to_field_name='slug',
        label=_('Manufacturer (slug)'),
    )
    form_factor = django_filters.MultipleChoiceFilter(
        choices=RackFormFactorChoices
    )
    width = django_filters.MultipleChoiceFilter(
        choices=RackWidthChoices
    )

    class Meta:
        model = RackType
        fields = (
            'id', 'model', 'slug', 'u_height', 'starting_unit', 'desc_units', 'outer_width', 'outer_height',
            'outer_depth', 'outer_unit', 'mounting_depth', 'weight', 'max_weight', 'weight_unit', 'description',
        )

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(model__icontains=value) |
            Q(description__icontains=value) |
            Q(comments__icontains=value)
        )


class RackFilterSet(NetBoxModelFilterSet, TenancyFilterSet, ContactModelFilterSet):
    region_id = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='site__region',
        lookup_expr='in',
        label=_('Region (ID)'),
    )
    region = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='site__region',
        lookup_expr='in',
        to_field_name='slug',
        label=_('Region (slug)'),
    )
    site_group_id = TreeNodeMultipleChoiceFilter(
        queryset=SiteGroup.objects.all(),
        field_name='site__group',
        lookup_expr='in',
        label=_('Site group (ID)'),
    )
    site_group = TreeNodeMultipleChoiceFilter(
        queryset=SiteGroup.objects.all(),
        field_name='site__group',
        lookup_expr='in',
        to_field_name='slug',
        label=_('Site group (slug)'),
    )
    site_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Site.objects.all(),
        label=_('Site (ID)'),
    )
    site = django_filters.ModelMultipleChoiceFilter(
        field_name='site__slug',
        queryset=Site.objects.all(),
        to_field_name='slug',
        label=_('Site (slug)'),
    )
    location_id = TreeNodeMultipleChoiceFilter(
        queryset=Location.objects.all(),
        field_name='location',
        lookup_expr='in',
        label=_('Location (ID)'),
    )
    location = TreeNodeMultipleChoiceFilter(
        queryset=Location.objects.all(),
        field_name='location',
        lookup_expr='in',
        to_field_name='slug',
        label=_('Location (slug)'),
    )
    manufacturer_id = django_filters.ModelMultipleChoiceFilter(
        field_name='rack_type__manufacturer',
        queryset=Manufacturer.objects.all(),
        label=_('Manufacturer (ID)'),
    )
    manufacturer = django_filters.ModelMultipleChoiceFilter(
        field_name='rack_type__manufacturer__slug',
        queryset=Manufacturer.objects.all(),
        to_field_name='slug',
        label=_('Manufacturer (slug)'),
    )
    rack_type = django_filters.ModelMultipleChoiceFilter(
        field_name='rack_type__slug',
        queryset=RackType.objects.all(),
        to_field_name='slug',
        label=_('Rack type (slug)'),
    )
    rack_type_id = django_filters.ModelMultipleChoiceFilter(
        queryset=RackType.objects.all(),
        label=_('Rack type (ID)'),
    )
    status = django_filters.MultipleChoiceFilter(
        choices=RackStatusChoices,
        null_value=None
    )
    form_factor = django_filters.MultipleChoiceFilter(
        choices=RackFormFactorChoices
    )
    width = django_filters.MultipleChoiceFilter(
        choices=RackWidthChoices
    )
    role_id = django_filters.ModelMultipleChoiceFilter(
        queryset=RackRole.objects.all(),
        label=_('Role (ID)'),
    )
    role = django_filters.ModelMultipleChoiceFilter(
        field_name='role__slug',
        queryset=RackRole.objects.all(),
        to_field_name='slug',
        label=_('Role (slug)'),
    )
    serial = MultiValueCharFilter(
        lookup_expr='iexact'
    )

    class Meta:
        model = Rack
        fields = (
            'id', 'name', 'facility_id', 'asset_tag', 'u_height', 'starting_unit', 'desc_units', 'outer_width',
            'outer_height', 'outer_depth', 'outer_unit', 'mounting_depth', 'airflow', 'weight', 'max_weight',
            'weight_unit', 'description',
        )

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(facility_id__icontains=value) |
            Q(serial__icontains=value.strip()) |
            Q(asset_tag__icontains=value.strip()) |
            Q(description__icontains=value) |
            Q(comments__icontains=value)
        )


class RackReservationFilterSet(NetBoxModelFilterSet, TenancyFilterSet):
    rack_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Rack.objects.all(),
        label=_('Rack (ID)'),
    )
    site_id = django_filters.ModelMultipleChoiceFilter(
        field_name='rack__site',
        queryset=Site.objects.all(),
        label=_('Site (ID)'),
    )
    site = django_filters.ModelMultipleChoiceFilter(
        field_name='rack__site__slug',
        queryset=Site.objects.all(),
        to_field_name='slug',
        label=_('Site (slug)'),
    )
    region_id = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='rack__site__region',
        lookup_expr='in',
        label=_('Region (ID)'),
    )
    region = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='rack__site__region',
        lookup_expr='in',
        to_field_name='slug',
        label=_('Region (slug)'),
    )
    site_group_id = TreeNodeMultipleChoiceFilter(
        queryset=SiteGroup.objects.all(),
        field_name='rack__site__group',
        lookup_expr='in',
        label=_('Site group (ID)'),
    )
    site_group = TreeNodeMultipleChoiceFilter(
        queryset=SiteGroup.objects.all(),
        field_name='rack__site__group',
        lookup_expr='in',
        to_field_name='slug',
        label=_('Site group (slug)'),
    )
    location_id = TreeNodeMultipleChoiceFilter(
        queryset=Location.objects.all(),
        field_name='rack__location',
        lookup_expr='in',
        label=_('Location (ID)'),
    )
    location = TreeNodeMultipleChoiceFilter(
        queryset=Location.objects.all(),
        field_name='rack__location',
        lookup_expr='in',
        to_field_name='slug',
        label=_('Location (slug)'),
    )
    user_id = django_filters.ModelMultipleChoiceFilter(
        queryset=User.objects.all(),
        label=_('User (ID)'),
    )
    user = django_filters.ModelMultipleChoiceFilter(
        field_name='user__username',
        queryset=User.objects.all(),
        to_field_name='username',
        label=_('User (name)'),
    )
    unit = NumericArrayFilter(
        field_name='units',
        lookup_expr='contains'
    )

    class Meta:
        model = RackReservation
        fields = ('id', 'created', 'description')

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(rack__name__icontains=value) |
            Q(rack__facility_id__icontains=value) |
            Q(user__username__icontains=value) |
            Q(description__icontains=value)
        )


class ManufacturerFilterSet(OrganizationalModelFilterSet, ContactModelFilterSet):

    class Meta:
        model = Manufacturer
        fields = ('id', 'name', 'slug', 'description')


class DeviceTypeFilterSet(NetBoxModelFilterSet):
    manufacturer_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Manufacturer.objects.all(),
        label=_('Manufacturer (ID)'),
    )
    manufacturer = django_filters.ModelMultipleChoiceFilter(
        field_name='manufacturer__slug',
        queryset=Manufacturer.objects.all(),
        to_field_name='slug',
        label=_('Manufacturer (slug)'),
    )
    default_platform_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Platform.objects.all(),
        label=_('Default platform (ID)'),
    )
    default_platform = django_filters.ModelMultipleChoiceFilter(
        field_name='default_platform__slug',
        queryset=Platform.objects.all(),
        to_field_name='slug',
        label=_('Default platform (slug)'),
    )
    has_front_image = django_filters.BooleanFilter(
        label=_('Has a front image'),
        method='_has_front_image'
    )
    has_rear_image = django_filters.BooleanFilter(
        label=_('Has a rear image'),
        method='_has_rear_image'
    )
    console_ports = django_filters.BooleanFilter(
        method='_console_ports',
        label=_('Has console ports'),
    )
    console_server_ports = django_filters.BooleanFilter(
        method='_console_server_ports',
        label=_('Has console server ports'),
    )
    power_ports = django_filters.BooleanFilter(
        method='_power_ports',
        label=_('Has power ports'),
    )
    power_outlets = django_filters.BooleanFilter(
        method='_power_outlets',
        label=_('Has power outlets'),
    )
    interfaces = django_filters.BooleanFilter(
        method='_interfaces',
        label=_('Has interfaces'),
    )
    pass_through_ports = django_filters.BooleanFilter(
        method='_pass_through_ports',
        label=_('Has pass-through ports'),
    )
    module_bays = django_filters.BooleanFilter(
        method='_module_bays',
        label=_('Has module bays'),
    )
    device_bays = django_filters.BooleanFilter(
        method='_device_bays',
        label=_('Has device bays'),
    )
    inventory_items = django_filters.BooleanFilter(
        method='_inventory_items',
        label=_('Has inventory items'),
    )

    class Meta:
        model = DeviceType
        fields = (
            'id', 'model', 'slug', 'part_number', 'u_height', 'exclude_from_utilization', 'is_full_depth',
            'subdevice_role', 'airflow', 'weight', 'weight_unit', 'description',

            # Counters
            'console_port_template_count',
            'console_server_port_template_count',
            'power_port_template_count',
            'power_outlet_template_count',
            'interface_template_count',
            'front_port_template_count',
            'rear_port_template_count',
            'device_bay_template_count',
            'module_bay_template_count',
            'inventory_item_template_count',
        )

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(manufacturer__name__icontains=value) |
            Q(model__icontains=value) |
            Q(part_number__icontains=value) |
            Q(description__icontains=value) |
            Q(comments__icontains=value)
        )

    def _has_front_image(self, queryset, name, value):
        if value:
            return queryset.exclude(front_image='')
        else:
            return queryset.filter(front_image='')

    def _has_rear_image(self, queryset, name, value):
        if value:
            return queryset.exclude(rear_image='')
        else:
            return queryset.filter(rear_image='')

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

    def _module_bays(self, queryset, name, value):
        return queryset.exclude(modulebaytemplates__isnull=value)

    def _device_bays(self, queryset, name, value):
        return queryset.exclude(devicebaytemplates__isnull=value)

    def _inventory_items(self, queryset, name, value):
        return queryset.exclude(inventoryitemtemplates__isnull=value)


class ModuleTypeProfileFilterSet(NetBoxModelFilterSet):

    class Meta:
        model = ModuleTypeProfile
        fields = ('id', 'name', 'description')

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value) |
            Q(comments__icontains=value)
        )


class ModuleTypeFilterSet(AttributeFiltersMixin, NetBoxModelFilterSet):
    profile_id = django_filters.ModelMultipleChoiceFilter(
        queryset=ModuleTypeProfile.objects.all(),
        label=_('Profile (ID)'),
    )
    profile = django_filters.ModelMultipleChoiceFilter(
        field_name='profile__name',
        queryset=ModuleTypeProfile.objects.all(),
        to_field_name='name',
        label=_('Profile (name)'),
    )
    manufacturer_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Manufacturer.objects.all(),
        label=_('Manufacturer (ID)'),
    )
    manufacturer = django_filters.ModelMultipleChoiceFilter(
        field_name='manufacturer__slug',
        queryset=Manufacturer.objects.all(),
        to_field_name='slug',
        label=_('Manufacturer (slug)'),
    )
    console_ports = django_filters.BooleanFilter(
        method='_console_ports',
        label=_('Has console ports'),
    )
    console_server_ports = django_filters.BooleanFilter(
        method='_console_server_ports',
        label=_('Has console server ports'),
    )
    power_ports = django_filters.BooleanFilter(
        method='_power_ports',
        label=_('Has power ports'),
    )
    power_outlets = django_filters.BooleanFilter(
        method='_power_outlets',
        label=_('Has power outlets'),
    )
    interfaces = django_filters.BooleanFilter(
        method='_interfaces',
        label=_('Has interfaces'),
    )
    pass_through_ports = django_filters.BooleanFilter(
        method='_pass_through_ports',
        label=_('Has pass-through ports'),
    )

    class Meta:
        model = ModuleType
        fields = ('id', 'model', 'part_number', 'airflow', 'weight', 'weight_unit', 'description')

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(manufacturer__name__icontains=value) |
            Q(model__icontains=value) |
            Q(part_number__icontains=value) |
            Q(description__icontains=value) |
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


class DeviceTypeComponentFilterSet(django_filters.FilterSet):
    q = django_filters.CharFilter(
        method='search',
        label=_('Search'),
    )
    device_type_id = django_filters.ModelMultipleChoiceFilter(
        queryset=DeviceType.objects.all(),
        field_name='device_type_id',
        label=_('Device type (ID)'),
    )

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value)
        )


class ModularDeviceTypeComponentFilterSet(DeviceTypeComponentFilterSet):
    module_type_id = django_filters.ModelMultipleChoiceFilter(
        queryset=ModuleType.objects.all(),
        field_name='module_type_id',
        label=_('Module type (ID)'),
    )


class ConsolePortTemplateFilterSet(ChangeLoggedModelFilterSet, ModularDeviceTypeComponentFilterSet):

    class Meta:
        model = ConsolePortTemplate
        fields = ('id', 'name', 'label', 'type', 'description')


class ConsoleServerPortTemplateFilterSet(ChangeLoggedModelFilterSet, ModularDeviceTypeComponentFilterSet):

    class Meta:
        model = ConsoleServerPortTemplate
        fields = ('id', 'name', 'label', 'type', 'description')


class PowerPortTemplateFilterSet(ChangeLoggedModelFilterSet, ModularDeviceTypeComponentFilterSet):

    class Meta:
        model = PowerPortTemplate
        fields = ('id', 'name', 'label', 'type', 'maximum_draw', 'allocated_draw', 'description')


class PowerOutletTemplateFilterSet(ChangeLoggedModelFilterSet, ModularDeviceTypeComponentFilterSet):
    feed_leg = django_filters.MultipleChoiceFilter(
        choices=PowerOutletFeedLegChoices,
        null_value=None
    )
    power_port_id = django_filters.ModelMultipleChoiceFilter(
        queryset=PowerPortTemplate.objects.all(),
        label=_('Power port (ID)'),
    )

    class Meta:
        model = PowerOutletTemplate
        fields = ('id', 'name', 'label', 'type', 'feed_leg', 'description')


class InterfaceTemplateFilterSet(ChangeLoggedModelFilterSet, ModularDeviceTypeComponentFilterSet):
    type = django_filters.MultipleChoiceFilter(
        choices=InterfaceTypeChoices,
        null_value=None
    )
    bridge_id = django_filters.ModelMultipleChoiceFilter(
        field_name='bridge',
        queryset=InterfaceTemplate.objects.all()
    )
    poe_mode = django_filters.MultipleChoiceFilter(
        choices=InterfacePoEModeChoices
    )
    poe_type = django_filters.MultipleChoiceFilter(
        choices=InterfacePoETypeChoices
    )
    rf_role = django_filters.MultipleChoiceFilter(
        choices=WirelessRoleChoices
    )

    class Meta:
        model = InterfaceTemplate
        fields = ('id', 'name', 'label', 'type', 'enabled', 'mgmt_only', 'description')


class FrontPortTemplateFilterSet(ChangeLoggedModelFilterSet, ModularDeviceTypeComponentFilterSet):
    type = django_filters.MultipleChoiceFilter(
        choices=PortTypeChoices,
        null_value=None
    )
    rear_port_id = django_filters.ModelMultipleChoiceFilter(
        queryset=RearPort.objects.all()
    )

    class Meta:
        model = FrontPortTemplate
        fields = ('id', 'name', 'label', 'type', 'color', 'rear_port_position', 'description')


class RearPortTemplateFilterSet(ChangeLoggedModelFilterSet, ModularDeviceTypeComponentFilterSet):
    type = django_filters.MultipleChoiceFilter(
        choices=PortTypeChoices,
        null_value=None
    )

    class Meta:
        model = RearPortTemplate
        fields = ('id', 'name', 'label', 'type', 'color', 'positions', 'description')


class ModuleBayTemplateFilterSet(ChangeLoggedModelFilterSet, ModularDeviceTypeComponentFilterSet):

    class Meta:
        model = ModuleBayTemplate
        fields = ('id', 'name', 'label', 'position', 'description')


class DeviceBayTemplateFilterSet(ChangeLoggedModelFilterSet, DeviceTypeComponentFilterSet):

    class Meta:
        model = DeviceBayTemplate
        fields = ('id', 'name', 'label', 'description')


class InventoryItemTemplateFilterSet(ChangeLoggedModelFilterSet, DeviceTypeComponentFilterSet):
    parent_id = django_filters.ModelMultipleChoiceFilter(
        queryset=InventoryItemTemplate.objects.all(),
        label=_('Parent inventory item (ID)'),
    )
    manufacturer_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Manufacturer.objects.all(),
        label=_('Manufacturer (ID)'),
    )
    manufacturer = django_filters.ModelMultipleChoiceFilter(
        field_name='manufacturer__slug',
        queryset=Manufacturer.objects.all(),
        to_field_name='slug',
        label=_('Manufacturer (slug)'),
    )
    role_id = django_filters.ModelMultipleChoiceFilter(
        queryset=InventoryItemRole.objects.all(),
        label=_('Role (ID)'),
    )
    role = django_filters.ModelMultipleChoiceFilter(
        field_name='role__slug',
        queryset=InventoryItemRole.objects.all(),
        to_field_name='slug',
        label=_('Role (slug)'),
    )
    component_type = ContentTypeFilter()
    component_id = MultiValueNumberFilter()

    class Meta:
        model = InventoryItemTemplate
        fields = ('id', 'name', 'label', 'part_id', 'description')

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = (
            Q(name__icontains=value) |
            Q(part_id__icontains=value) |
            Q(description__icontains=value)
        )
        return queryset.filter(qs_filter)


class DeviceRoleFilterSet(OrganizationalModelFilterSet):
    config_template_id = django_filters.ModelMultipleChoiceFilter(
        queryset=ConfigTemplate.objects.all(),
        label=_('Config template (ID)'),
    )
    parent_id = django_filters.ModelMultipleChoiceFilter(
        queryset=DeviceRole.objects.all(),
        label=_('Parent device role (ID)'),
    )
    parent = django_filters.ModelMultipleChoiceFilter(
        field_name='parent__slug',
        queryset=DeviceRole.objects.all(),
        to_field_name='slug',
        label=_('Parent device role (slug)'),
    )
    ancestor_id = TreeNodeMultipleChoiceFilter(
        queryset=DeviceRole.objects.all(),
        field_name='parent',
        lookup_expr='in',
        label=_('Parent device role (ID)'),
    )
    ancestor = TreeNodeMultipleChoiceFilter(
        queryset=DeviceRole.objects.all(),
        field_name='parent',
        lookup_expr='in',
        to_field_name='slug',
        label=_('Parent device role (slug)'),
    )

    class Meta:
        model = DeviceRole
        fields = ('id', 'name', 'slug', 'color', 'vm_role', 'description')


class PlatformFilterSet(OrganizationalModelFilterSet):
    manufacturer_id = django_filters.ModelMultipleChoiceFilter(
        field_name='manufacturer',
        queryset=Manufacturer.objects.all(),
        label=_('Manufacturer (ID)'),
    )
    manufacturer = django_filters.ModelMultipleChoiceFilter(
        field_name='manufacturer__slug',
        queryset=Manufacturer.objects.all(),
        to_field_name='slug',
        label=_('Manufacturer (slug)'),
    )
    available_for_device_type = django_filters.ModelChoiceFilter(
        queryset=DeviceType.objects.all(),
        method='get_for_device_type'
    )
    config_template_id = django_filters.ModelMultipleChoiceFilter(
        queryset=ConfigTemplate.objects.all(),
        label=_('Config template (ID)'),
    )

    class Meta:
        model = Platform
        fields = ('id', 'name', 'slug', 'description')

    @extend_schema_field(OpenApiTypes.STR)
    def get_for_device_type(self, queryset, name, value):
        """
        Return all Platforms available for a specific manufacturer based on device type and Platforms not assigned any
        manufacturer
        """
        return queryset.filter(Q(manufacturer=None) | Q(manufacturer__device_types=value))


class DeviceFilterSet(
    NetBoxModelFilterSet,
    TenancyFilterSet,
    ContactModelFilterSet,
    LocalConfigContextFilterSet,
    PrimaryIPFilterSet,
):
    manufacturer_id = django_filters.ModelMultipleChoiceFilter(
        field_name='device_type__manufacturer',
        queryset=Manufacturer.objects.all(),
        label=_('Manufacturer (ID)'),
    )
    manufacturer = django_filters.ModelMultipleChoiceFilter(
        field_name='device_type__manufacturer__slug',
        queryset=Manufacturer.objects.all(),
        to_field_name='slug',
        label=_('Manufacturer (slug)'),
    )
    device_type = django_filters.ModelMultipleChoiceFilter(
        field_name='device_type__slug',
        queryset=DeviceType.objects.all(),
        to_field_name='slug',
        label=_('Device type (slug)'),
    )
    device_type_id = django_filters.ModelMultipleChoiceFilter(
        queryset=DeviceType.objects.all(),
        label=_('Device type (ID)'),
    )
    role_id = TreeNodeMultipleChoiceFilter(
        field_name='role',
        queryset=DeviceRole.objects.all(),
        lookup_expr='in',
        label=_('Role (ID)'),
    )
    role = TreeNodeMultipleChoiceFilter(
        queryset=DeviceRole.objects.all(),
        field_name='role',
        lookup_expr='in',
        to_field_name='slug',
        label=_('Role (slug)'),
    )
    parent_device_id = django_filters.ModelMultipleChoiceFilter(
        field_name='parent_bay__device',
        queryset=Device.objects.all(),
        label=_('Parent Device (ID)'),
    )
    platform_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Platform.objects.all(),
        label=_('Platform (ID)'),
    )
    platform = django_filters.ModelMultipleChoiceFilter(
        field_name='platform__slug',
        queryset=Platform.objects.all(),
        to_field_name='slug',
        label=_('Platform (slug)'),
    )
    region_id = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='site__region',
        lookup_expr='in',
        label=_('Region (ID)'),
    )
    region = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='site__region',
        lookup_expr='in',
        to_field_name='slug',
        label=_('Region (slug)'),
    )
    site_group_id = TreeNodeMultipleChoiceFilter(
        queryset=SiteGroup.objects.all(),
        field_name='site__group',
        lookup_expr='in',
        label=_('Site group (ID)'),
    )
    site_group = TreeNodeMultipleChoiceFilter(
        queryset=SiteGroup.objects.all(),
        field_name='site__group',
        lookup_expr='in',
        to_field_name='slug',
        label=_('Site group (slug)'),
    )
    site_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Site.objects.all(),
        label=_('Site (ID)'),
    )
    site = django_filters.ModelMultipleChoiceFilter(
        field_name='site__slug',
        queryset=Site.objects.all(),
        to_field_name='slug',
        label=_('Site name (slug)'),
    )
    location_id = TreeNodeMultipleChoiceFilter(
        queryset=Location.objects.all(),
        field_name='location',
        lookup_expr='in',
        label=_('Location (ID)'),
    )
    location = TreeNodeMultipleChoiceFilter(
        queryset=Location.objects.all(),
        field_name='location',
        lookup_expr='in',
        to_field_name='slug',
        label=_('Location (slug)'),
    )
    rack_id = django_filters.ModelMultipleChoiceFilter(
        field_name='rack',
        queryset=Rack.objects.all(),
        label=_('Rack (ID)'),
    )
    parent_bay_id = django_filters.ModelMultipleChoiceFilter(
        field_name='parent_bay',
        queryset=DeviceBay.objects.all(),
        label=_('Parent bay (ID)'),
    )
    cluster_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Cluster.objects.all(),
        label=_('VM cluster (ID)'),
    )
    cluster_group = django_filters.ModelMultipleChoiceFilter(
        field_name='cluster__group__slug',
        queryset=ClusterGroup.objects.all(),
        to_field_name='slug',
        label=_('Cluster group (slug)'),
    )
    cluster_group_id = django_filters.ModelMultipleChoiceFilter(
        field_name='cluster__group',
        queryset=ClusterGroup.objects.all(),
        label=_('Cluster group (ID)'),
    )
    model = django_filters.ModelMultipleChoiceFilter(
        field_name='device_type__slug',
        queryset=DeviceType.objects.all(),
        to_field_name='slug',
        label=_('Device model (slug)'),
    )
    name = MultiValueCharFilter(
        lookup_expr='iexact'
    )
    status = django_filters.MultipleChoiceFilter(
        choices=DeviceStatusChoices,
        null_value=None
    )
    is_full_depth = django_filters.BooleanFilter(
        field_name='device_type__is_full_depth',
        label=_('Is full depth'),
    )
    mac_address = MultiValueMACAddressFilter(
        field_name='interfaces__mac_addresses__mac_address',
        label=_('MAC address'),
    )
    serial = MultiValueCharFilter(
        lookup_expr='iexact'
    )
    has_primary_ip = django_filters.BooleanFilter(
        method='_has_primary_ip',
        label=_('Has a primary IP'),
    )
    has_oob_ip = django_filters.BooleanFilter(
        method='_has_oob_ip',
        label=_('Has an out-of-band IP'),
    )
    virtual_chassis_id = django_filters.ModelMultipleChoiceFilter(
        field_name='virtual_chassis',
        queryset=VirtualChassis.objects.all(),
        label=_('Virtual chassis (ID)'),
    )
    virtual_chassis_member = django_filters.BooleanFilter(
        method='_virtual_chassis_member',
        label=_('Is a virtual chassis member')
    )
    config_template_id = django_filters.ModelMultipleChoiceFilter(
        queryset=ConfigTemplate.objects.all(),
        label=_('Config template (ID)'),
    )
    console_ports = django_filters.BooleanFilter(
        method='_console_ports',
        label=_('Has console ports'),
    )
    console_server_ports = django_filters.BooleanFilter(
        method='_console_server_ports',
        label=_('Has console server ports'),
    )
    power_ports = django_filters.BooleanFilter(
        method='_power_ports',
        label=_('Has power ports'),
    )
    power_outlets = django_filters.BooleanFilter(
        method='_power_outlets',
        label=_('Has power outlets'),
    )
    interfaces = django_filters.BooleanFilter(
        method='_interfaces',
        label=_('Has interfaces'),
    )
    pass_through_ports = django_filters.BooleanFilter(
        method='_pass_through_ports',
        label=_('Has pass-through ports'),
    )
    module_bays = django_filters.BooleanFilter(
        method='_module_bays',
        label=_('Has module bays'),
    )
    device_bays = django_filters.BooleanFilter(
        method='_device_bays',
        label=_('Has device bays'),
    )
    oob_ip_id = django_filters.ModelMultipleChoiceFilter(
        field_name='oob_ip',
        queryset=IPAddress.objects.all(),
        label=_('OOB IP (ID)'),
    )
    has_virtual_device_context = django_filters.BooleanFilter(
        method='_has_virtual_device_context',
        label=_('Has virtual device context'),
    )

    class Meta:
        model = Device
        fields = (
            'id', 'asset_tag', 'face', 'position', 'latitude', 'longitude', 'airflow', 'vc_position', 'vc_priority',
            'description',

            # Counters
            'console_port_count',
            'console_server_port_count',
            'power_port_count',
            'power_outlet_count',
            'interface_count',
            'front_port_count',
            'rear_port_count',
            'device_bay_count',
            'module_bay_count',
            'inventory_item_count',
        )

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(virtual_chassis__name__icontains=value) |
            Q(serial__icontains=value.strip()) |
            Q(inventoryitems__serial__icontains=value.strip()) |
            Q(asset_tag__icontains=value.strip()) |
            Q(description__icontains=value.strip()) |
            Q(comments__icontains=value) |
            Q(primary_ip4__address__startswith=value) |
            Q(primary_ip6__address__startswith=value)
        ).distinct()

    def _has_primary_ip(self, queryset, name, value):
        params = Q(primary_ip4__isnull=False) | Q(primary_ip6__isnull=False)
        if value:
            return queryset.filter(params)
        return queryset.exclude(params)

    def _has_oob_ip(self, queryset, name, value):
        params = Q(oob_ip__isnull=False)
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

    def _module_bays(self, queryset, name, value):
        return queryset.exclude(modulebays__isnull=value)

    def _device_bays(self, queryset, name, value):
        return queryset.exclude(devicebays__isnull=value)

    def _has_virtual_device_context(self, queryset, name, value):
        params = Q(vdcs__isnull=False)
        if value:
            return queryset.filter(params).distinct()
        return queryset.exclude(params)


class VirtualDeviceContextFilterSet(NetBoxModelFilterSet, TenancyFilterSet, PrimaryIPFilterSet):
    device_id = django_filters.ModelMultipleChoiceFilter(
        field_name='device',
        queryset=Device.objects.all(),
        label=_('VDC (ID)')
    )
    device = django_filters.ModelMultipleChoiceFilter(
        field_name='device',
        queryset=Device.objects.all(),
        label=_('Device model')
    )
    interface_id = django_filters.ModelMultipleChoiceFilter(
        field_name='interfaces',
        queryset=Interface.objects.all(),
        label=_('Interface (ID)')
    )
    status = django_filters.MultipleChoiceFilter(
        choices=VirtualDeviceContextStatusChoices
    )
    has_primary_ip = django_filters.BooleanFilter(
        method='_has_primary_ip',
        label=_('Has a primary IP')
    )

    class Meta:
        model = VirtualDeviceContext
        fields = ('id', 'device', 'name', 'identifier', 'description')

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset

        qs_filter = (
            Q(name__icontains=value) |
            Q(description__icontains=value)
        )
        try:
            qs_filter |= Q(identifier=int(value))
        except ValueError:
            pass
        return queryset.filter(qs_filter).distinct()

    def _has_primary_ip(self, queryset, name, value):
        params = Q(primary_ip4__isnull=False) | Q(primary_ip6__isnull=False)
        if value:
            return queryset.filter(params)
        return queryset.exclude(params)


class ModuleFilterSet(NetBoxModelFilterSet):
    manufacturer_id = django_filters.ModelMultipleChoiceFilter(
        field_name='module_type__manufacturer',
        queryset=Manufacturer.objects.all(),
        label=_('Manufacturer (ID)'),
    )
    manufacturer = django_filters.ModelMultipleChoiceFilter(
        field_name='module_type__manufacturer__slug',
        queryset=Manufacturer.objects.all(),
        to_field_name='slug',
        label=_('Manufacturer (slug)'),
    )
    module_type_id = django_filters.ModelMultipleChoiceFilter(
        field_name='module_type',
        queryset=ModuleType.objects.all(),
        label=_('Module type (ID)'),
    )
    module_type = django_filters.ModelMultipleChoiceFilter(
        field_name='module_type__model',
        queryset=ModuleType.objects.all(),
        to_field_name='model',
        label=_('Module type (model)'),
    )
    module_bay_id = TreeNodeMultipleChoiceFilter(
        queryset=ModuleBay.objects.all(),
        field_name='module_bay',
        lookup_expr='in',
        label=_('Module bay (ID)'),
    )
    region_id = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='device__site__region',
        lookup_expr='in',
        label=_('Region (ID)'),
    )
    region = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='device__site__region',
        lookup_expr='in',
        to_field_name='slug',
        label=_('Region (slug)'),
    )
    site_group_id = TreeNodeMultipleChoiceFilter(
        queryset=SiteGroup.objects.all(),
        field_name='device__site__group',
        lookup_expr='in',
        label=_('Site group (ID)'),
    )
    site_group = TreeNodeMultipleChoiceFilter(
        queryset=SiteGroup.objects.all(),
        field_name='device__site__group',
        lookup_expr='in',
        to_field_name='slug',
        label=_('Site group (slug)'),
    )
    site_id = django_filters.ModelMultipleChoiceFilter(
        field_name='device__site',
        queryset=Site.objects.all(),
        label=_('Site (ID)'),
    )
    site = django_filters.ModelMultipleChoiceFilter(
        field_name='device__site__slug',
        queryset=Site.objects.all(),
        to_field_name='slug',
        label=_('Site name (slug)'),
    )
    location_id = django_filters.ModelMultipleChoiceFilter(
        field_name='device__location',
        queryset=Location.objects.all(),
        label=_('Location (ID)'),
    )
    location = django_filters.ModelMultipleChoiceFilter(
        field_name='device__location__slug',
        queryset=Location.objects.all(),
        to_field_name='slug',
        label=_('Location (slug)'),
    )
    rack_id = django_filters.ModelMultipleChoiceFilter(
        field_name='device__rack',
        queryset=Rack.objects.all(),
        label=_('Rack (ID)'),
    )
    rack = django_filters.ModelMultipleChoiceFilter(
        field_name='device__rack__name',
        queryset=Rack.objects.all(),
        to_field_name='name',
        label=_('Rack (name)'),
    )
    device_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Device.objects.all(),
        label=_('Device (ID)'),
    )
    device = django_filters.ModelMultipleChoiceFilter(
        field_name='device__name',
        queryset=Device.objects.all(),
        to_field_name='name',
        label=_('Device (name)'),
    )
    status = django_filters.MultipleChoiceFilter(
        choices=ModuleStatusChoices,
        null_value=None
    )
    serial = MultiValueCharFilter(
        lookup_expr='iexact'
    )

    class Meta:
        model = Module
        fields = ('id', 'status', 'asset_tag', 'description')

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(device__name__icontains=value.strip()) |
            Q(serial__icontains=value.strip()) |
            Q(asset_tag__icontains=value.strip()) |
            Q(description__icontains=value) |
            Q(comments__icontains=value)
        ).distinct()


class DeviceComponentFilterSet(django_filters.FilterSet):
    q = django_filters.CharFilter(
        method='search',
        label=_('Search'),
    )
    region_id = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='device__site__region',
        lookup_expr='in',
        label=_('Region (ID)'),
    )
    region = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='device__site__region',
        lookup_expr='in',
        to_field_name='slug',
        label=_('Region (slug)'),
    )
    site_group_id = TreeNodeMultipleChoiceFilter(
        queryset=SiteGroup.objects.all(),
        field_name='device__site__group',
        lookup_expr='in',
        label=_('Site group (ID)'),
    )
    site_group = TreeNodeMultipleChoiceFilter(
        queryset=SiteGroup.objects.all(),
        field_name='device__site__group',
        lookup_expr='in',
        to_field_name='slug',
        label=_('Site group (slug)'),
    )
    site_id = django_filters.ModelMultipleChoiceFilter(
        field_name='_site',
        queryset=Site.objects.all(),
        label=_('Site (ID)'),
    )
    site = django_filters.ModelMultipleChoiceFilter(
        field_name='_site__slug',
        queryset=Site.objects.all(),
        to_field_name='slug',
        label=_('Site name (slug)'),
    )
    location_id = django_filters.ModelMultipleChoiceFilter(
        field_name='_location',
        queryset=Location.objects.all(),
        label=_('Location (ID)'),
    )
    location = django_filters.ModelMultipleChoiceFilter(
        field_name='_location__slug',
        queryset=Location.objects.all(),
        to_field_name='slug',
        label=_('Location (slug)'),
    )
    rack_id = django_filters.ModelMultipleChoiceFilter(
        field_name='_rack',
        queryset=Rack.objects.all(),
        label=_('Rack (ID)'),
    )
    rack = django_filters.ModelMultipleChoiceFilter(
        field_name='_rack__name',
        queryset=Rack.objects.all(),
        to_field_name='name',
        label=_('Rack (name)'),
    )
    device_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Device.objects.all(),
        label=_('Device (ID)'),
    )
    device = django_filters.ModelMultipleChoiceFilter(
        field_name='device__name',
        queryset=Device.objects.all(),
        to_field_name='name',
        label=_('Device (name)'),
    )
    device_type_id = django_filters.ModelMultipleChoiceFilter(
        field_name='device__device_type',
        queryset=DeviceType.objects.all(),
        label=_('Device type (ID)'),
    )
    device_type = django_filters.ModelMultipleChoiceFilter(
        field_name='device__device_type__model',
        queryset=DeviceType.objects.all(),
        to_field_name='model',
        label=_('Device type (model)'),
    )
    device_role_id = django_filters.ModelMultipleChoiceFilter(
        field_name='device__role',
        queryset=DeviceRole.objects.all(),
        label=_('Device role (ID)'),
    )
    device_role = django_filters.ModelMultipleChoiceFilter(
        field_name='device__role__slug',
        queryset=DeviceRole.objects.all(),
        to_field_name='slug',
        label=_('Device role (slug)'),
    )
    virtual_chassis_id = django_filters.ModelMultipleChoiceFilter(
        field_name='device__virtual_chassis',
        queryset=VirtualChassis.objects.all(),
        label=_('Virtual Chassis (ID)')
    )
    virtual_chassis = django_filters.ModelMultipleChoiceFilter(
        field_name='device__virtual_chassis__name',
        queryset=VirtualChassis.objects.all(),
        to_field_name='name',
        label=_('Virtual Chassis'),
    )
    device_status = django_filters.MultipleChoiceFilter(
        choices=DeviceStatusChoices,
        field_name='device__status',
    )

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(label__icontains=value) |
            Q(description__icontains=value)
        )


class ModularDeviceComponentFilterSet(DeviceComponentFilterSet):
    """
    Extends DeviceComponentFilterSet to add a module_id filter for components
    which can be associated with a particular module within a device.
    """
    module_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Module.objects.all(),
        label=_('Module (ID)'),
    )


class CabledObjectFilterSet(django_filters.FilterSet):
    cable_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Cable.objects.all(),
        label=_('Cable (ID)'),
    )
    cabled = django_filters.BooleanFilter(
        field_name='cable',
        lookup_expr='isnull',
        exclude=True
    )
    occupied = django_filters.BooleanFilter(
        method='filter_occupied'
    )

    def filter_occupied(self, queryset, name, value):
        if value:
            return queryset.filter(Q(cable__isnull=False) | Q(mark_connected=True))
        else:
            return queryset.filter(cable__isnull=True, mark_connected=False)


class PathEndpointFilterSet(django_filters.FilterSet):
    connected = django_filters.BooleanFilter(
        method='filter_connected'
    )

    def filter_connected(self, queryset, name, value):
        if value:
            return queryset.filter(_path__is_active=True)
        else:
            return queryset.filter(Q(_path__isnull=True) | Q(_path__is_active=False))


class ConsolePortFilterSet(
    ModularDeviceComponentFilterSet,
    NetBoxModelFilterSet,
    CabledObjectFilterSet,
    PathEndpointFilterSet
):
    type = django_filters.MultipleChoiceFilter(
        choices=ConsolePortTypeChoices,
        null_value=None
    )

    class Meta:
        model = ConsolePort
        fields = ('id', 'name', 'label', 'speed', 'description', 'mark_connected', 'cable_end')


class ConsoleServerPortFilterSet(
    ModularDeviceComponentFilterSet,
    NetBoxModelFilterSet,
    CabledObjectFilterSet,
    PathEndpointFilterSet
):
    type = django_filters.MultipleChoiceFilter(
        choices=ConsolePortTypeChoices,
        null_value=None
    )

    class Meta:
        model = ConsoleServerPort
        fields = ('id', 'name', 'label', 'speed', 'description', 'mark_connected', 'cable_end')


class PowerPortFilterSet(
    ModularDeviceComponentFilterSet,
    NetBoxModelFilterSet,
    CabledObjectFilterSet,
    PathEndpointFilterSet
):
    type = django_filters.MultipleChoiceFilter(
        choices=PowerPortTypeChoices,
        null_value=None
    )

    class Meta:
        model = PowerPort
        fields = (
            'id', 'name', 'label', 'maximum_draw', 'allocated_draw', 'description', 'mark_connected', 'cable_end',
        )


class PowerOutletFilterSet(
    ModularDeviceComponentFilterSet,
    NetBoxModelFilterSet,
    CabledObjectFilterSet,
    PathEndpointFilterSet
):
    type = django_filters.MultipleChoiceFilter(
        choices=PowerOutletTypeChoices,
        null_value=None
    )
    feed_leg = django_filters.MultipleChoiceFilter(
        choices=PowerOutletFeedLegChoices,
        null_value=None
    )
    power_port_id = django_filters.ModelMultipleChoiceFilter(
        queryset=PowerPort.objects.all(),
        label=_('Power port (ID)'),
    )
    status = django_filters.MultipleChoiceFilter(
        choices=PowerOutletStatusChoices,
        null_value=None
    )

    class Meta:
        model = PowerOutlet
        fields = (
            'id', 'name', 'status', 'label', 'feed_leg', 'description', 'color', 'mark_connected', 'cable_end',
        )


class MACAddressFilterSet(NetBoxModelFilterSet):
    mac_address = MultiValueMACAddressFilter()
    device = MultiValueCharFilter(
        method='filter_device',
        field_name='name',
        label=_('Device (name)'),
    )
    device_id = MultiValueNumberFilter(
        method='filter_device',
        field_name='pk',
        label=_('Device (ID)'),
    )
    virtual_machine = MultiValueCharFilter(
        method='filter_virtual_machine',
        field_name='name',
        label=_('Virtual machine (name)'),
    )
    virtual_machine_id = MultiValueNumberFilter(
        method='filter_virtual_machine',
        field_name='pk',
        label=_('Virtual machine (ID)'),
    )
    interface = django_filters.ModelMultipleChoiceFilter(
        field_name='interface__name',
        queryset=Interface.objects.all(),
        to_field_name='name',
        label=_('Interface (name)'),
    )
    interface_id = django_filters.ModelMultipleChoiceFilter(
        field_name='interface',
        queryset=Interface.objects.all(),
        label=_('Interface (ID)'),
    )
    vminterface = django_filters.ModelMultipleChoiceFilter(
        field_name='vminterface__name',
        queryset=VMInterface.objects.all(),
        to_field_name='name',
        label=_('VM interface (name)'),
    )
    vminterface_id = django_filters.ModelMultipleChoiceFilter(
        field_name='vminterface',
        queryset=VMInterface.objects.all(),
        label=_('VM interface (ID)'),
    )

    class Meta:
        model = MACAddress
        fields = ('id', 'description', 'assigned_object_type', 'assigned_object_id')

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = (
            Q(mac_address__icontains=value) |
            Q(description__icontains=value)
        )
        return queryset.filter(qs_filter)

    def filter_device(self, queryset, name, value):
        devices = Device.objects.filter(**{f'{name}__in': value})
        if not devices.exists():
            return queryset.none()
        interface_ids = []
        for device in devices:
            interface_ids.extend(device.vc_interfaces().values_list('id', flat=True))
        return queryset.filter(
            interface__in=interface_ids
        )

    def filter_virtual_machine(self, queryset, name, value):
        virtual_machines = VirtualMachine.objects.filter(**{f'{name}__in': value})
        if not virtual_machines.exists():
            return queryset.none()
        interface_ids = []
        for vm in virtual_machines:
            interface_ids.extend(vm.interfaces.values_list('id', flat=True))
        return queryset.filter(
            vminterface__in=interface_ids
        )


class CommonInterfaceFilterSet(django_filters.FilterSet):
    mode = django_filters.MultipleChoiceFilter(
        choices=InterfaceModeChoices,
        label=_('802.1Q Mode')
    )
    vlan_id = django_filters.CharFilter(
        method='filter_vlan_id',
        label=_('Assigned VLAN')
    )
    vlan = django_filters.CharFilter(
        method='filter_vlan',
        label=_('Assigned VID')
    )
    vrf_id = django_filters.ModelMultipleChoiceFilter(
        field_name='vrf',
        queryset=VRF.objects.all(),
        label=_('VRF'),
    )
    vrf = django_filters.ModelMultipleChoiceFilter(
        field_name='vrf__rd',
        queryset=VRF.objects.all(),
        to_field_name='rd',
        label=_('VRF (RD)'),
    )
    l2vpn_id = django_filters.ModelMultipleChoiceFilter(
        field_name='l2vpn_terminations__l2vpn',
        queryset=L2VPN.objects.all(),
        label=_('L2VPN (ID)'),
    )
    l2vpn = django_filters.ModelMultipleChoiceFilter(
        field_name='l2vpn_terminations__l2vpn__identifier',
        queryset=L2VPN.objects.all(),
        to_field_name='identifier',
        label=_('L2VPN'),
    )
    vlan_translation_policy_id = django_filters.ModelMultipleChoiceFilter(
        field_name='vlan_translation_policy',
        queryset=VLANTranslationPolicy.objects.all(),
        label=_('VLAN Translation Policy (ID)'),
    )
    vlan_translation_policy = django_filters.ModelMultipleChoiceFilter(
        field_name='vlan_translation_policy__name',
        queryset=VLANTranslationPolicy.objects.all(),
        to_field_name='name',
        label=_('VLAN Translation Policy'),
    )

    def filter_vlan_id(self, queryset, name, value):
        value = value.strip()
        if not value:
            return queryset
        return queryset.filter(
            Q(untagged_vlan_id=value) |
            Q(tagged_vlans=value) |
            Q(qinq_svlan=value)
        )

    def filter_vlan(self, queryset, name, value):
        value = value.strip()
        if not value:
            return queryset
        return queryset.filter(
            Q(untagged_vlan_id__vid=value) |
            Q(tagged_vlans__vid=value) |
            Q(qinq_svlan__vid=value)
        )


class InterfaceFilterSet(
    ModularDeviceComponentFilterSet,
    NetBoxModelFilterSet,
    CabledObjectFilterSet,
    PathEndpointFilterSet,
    CommonInterfaceFilterSet
):
    virtual_chassis_member = MultiValueCharFilter(
        method='filter_virtual_chassis_member',
        field_name='name',
        label=_('Virtual Chassis Interfaces for Device')
    )
    virtual_chassis_member_id = MultiValueNumberFilter(
        method='filter_virtual_chassis_member',
        field_name='pk',
        label=_('Virtual Chassis Interfaces for Device (ID)')
    )
    kind = django_filters.CharFilter(
        method='filter_kind',
        label=_('Kind of interface'),
    )
    parent_id = django_filters.ModelMultipleChoiceFilter(
        field_name='parent',
        queryset=Interface.objects.all(),
        label=_('Parent interface (ID)'),
    )
    bridge_id = django_filters.ModelMultipleChoiceFilter(
        field_name='bridge',
        queryset=Interface.objects.all(),
        label=_('Bridged interface (ID)'),
    )
    lag_id = django_filters.ModelMultipleChoiceFilter(
        field_name='lag',
        queryset=Interface.objects.all(),
        label=_('LAG interface (ID)'),
    )
    speed = MultiValueNumberFilter()
    duplex = django_filters.MultipleChoiceFilter(
        choices=InterfaceDuplexChoices
    )
    mac_address = MultiValueMACAddressFilter(
        field_name='mac_addresses__mac_address',
        label=_('MAC Address')
    )
    primary_mac_address_id = django_filters.ModelMultipleChoiceFilter(
        field_name='primary_mac_address',
        queryset=MACAddress.objects.all(),
        label=_('Primary MAC address (ID)'),
    )
    primary_mac_address = django_filters.ModelMultipleChoiceFilter(
        field_name='primary_mac_address__mac_address',
        queryset=MACAddress.objects.all(),
        to_field_name='mac_address',
        label=_('Primary MAC address'),
    )
    wwn = MultiValueWWNFilter()
    poe_mode = django_filters.MultipleChoiceFilter(
        choices=InterfacePoEModeChoices
    )
    poe_type = django_filters.MultipleChoiceFilter(
        choices=InterfacePoETypeChoices
    )
    type = django_filters.MultipleChoiceFilter(
        choices=InterfaceTypeChoices,
        null_value=None
    )
    rf_role = django_filters.MultipleChoiceFilter(
        choices=WirelessRoleChoices
    )
    rf_channel = django_filters.MultipleChoiceFilter(
        choices=WirelessChannelChoices
    )
    vdc_id = django_filters.ModelMultipleChoiceFilter(
        field_name='vdcs',
        queryset=VirtualDeviceContext.objects.all(),
        label=_('Virtual Device Context')
    )
    vdc_identifier = django_filters.ModelMultipleChoiceFilter(
        field_name='vdcs__identifier',
        queryset=VirtualDeviceContext.objects.all(),
        to_field_name='identifier',
        label=_('Virtual Device Context (Identifier)')
    )
    vdc = django_filters.ModelMultipleChoiceFilter(
        field_name='vdcs__name',
        queryset=VirtualDeviceContext.objects.all(),
        to_field_name='name',
        label=_('Virtual Device Context')
    )
    wireless_lan_id = django_filters.ModelMultipleChoiceFilter(
        field_name='wireless_lans',
        queryset=WirelessLAN.objects.all(),
        label=_('Wireless LAN')
    )
    wireless_link_id = django_filters.ModelMultipleChoiceFilter(
        queryset=WirelessLink.objects.all(),
        label=_('Wireless link')
    )
    virtual_circuit_id = django_filters.ModelMultipleChoiceFilter(
        field_name='virtual_circuit_termination__virtual_circuit',
        queryset=VirtualCircuit.objects.all(),
        label=_('Virtual circuit (ID)'),
    )
    virtual_circuit_termination_id = django_filters.ModelMultipleChoiceFilter(
        field_name='virtual_circuit_termination',
        queryset=VirtualCircuitTermination.objects.all(),
        label=_('Virtual circuit termination (ID)'),
    )

    class Meta:
        model = Interface
        fields = (
            'id', 'name', 'label', 'type', 'enabled', 'mtu', 'mgmt_only', 'poe_mode', 'poe_type', 'mode', 'rf_role',
            'rf_channel', 'rf_channel_frequency', 'rf_channel_width', 'tx_power', 'description', 'mark_connected',
            'cable_id', 'cable_end',
        )

    def filter_virtual_chassis_member(self, queryset, name, value):
        try:
            vc_interface_ids = []
            for device in Device.objects.filter(**{f'{name}__in': value}):
                vc_interface_ids.extend(device.vc_interfaces(if_master=False).values_list('id', flat=True))
            return queryset.filter(pk__in=vc_interface_ids)
        except Device.DoesNotExist:
            return queryset.none()

    def filter_kind(self, queryset, name, value):
        value = value.strip().lower()
        return {
            'physical': queryset.exclude(type__in=NONCONNECTABLE_IFACE_TYPES),
            'virtual': queryset.filter(type__in=VIRTUAL_IFACE_TYPES),
            'wireless': queryset.filter(type__in=WIRELESS_IFACE_TYPES),
        }.get(value, queryset.none())

    # Override the method on CabledObjectFilterSet to also check for wireless links
    def filter_occupied(self, queryset, name, value):
        if value:
            return queryset.filter(
                Q(cable__isnull=False) |
                Q(wireless_link__isnull=False) |
                Q(mark_connected=True)
            )
        else:
            return queryset.filter(
                cable__isnull=True,
                wireless_link__isnull=True,
                mark_connected=False
            )


class FrontPortFilterSet(
    ModularDeviceComponentFilterSet,
    NetBoxModelFilterSet,
    CabledObjectFilterSet
):
    type = django_filters.MultipleChoiceFilter(
        choices=PortTypeChoices,
        null_value=None
    )
    rear_port_id = django_filters.ModelMultipleChoiceFilter(
        queryset=RearPort.objects.all()
    )

    class Meta:
        model = FrontPort
        fields = (
            'id', 'name', 'label', 'type', 'color', 'rear_port_position', 'description', 'mark_connected', 'cable_end',
        )


class RearPortFilterSet(
    ModularDeviceComponentFilterSet,
    NetBoxModelFilterSet,
    CabledObjectFilterSet
):
    type = django_filters.MultipleChoiceFilter(
        choices=PortTypeChoices,
        null_value=None
    )

    class Meta:
        model = RearPort
        fields = (
            'id', 'name', 'label', 'type', 'color', 'positions', 'description', 'mark_connected', 'cable_end',
        )


class ModuleBayFilterSet(ModularDeviceComponentFilterSet, NetBoxModelFilterSet):
    parent_id = django_filters.ModelMultipleChoiceFilter(
        queryset=ModuleBay.objects.all(),
        label=_('Parent module bay (ID)'),
    )
    installed_module_id = django_filters.ModelMultipleChoiceFilter(
        field_name='installed_module',
        queryset=ModuleBay.objects.all(),
        label=_('Installed module (ID)'),
    )

    class Meta:
        model = ModuleBay
        fields = ('id', 'name', 'label', 'position', 'description')


class DeviceBayFilterSet(DeviceComponentFilterSet, NetBoxModelFilterSet):
    installed_device_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Device.objects.all(),
        label=_('Installed device (ID)'),
    )
    installed_device = django_filters.ModelMultipleChoiceFilter(
        field_name='installed_device__name',
        queryset=Device.objects.all(),
        to_field_name='name',
        label=_('Installed device (name)'),
    )

    class Meta:
        model = DeviceBay
        fields = ('id', 'name', 'label', 'description')


class InventoryItemFilterSet(DeviceComponentFilterSet, NetBoxModelFilterSet):
    parent_id = django_filters.ModelMultipleChoiceFilter(
        queryset=InventoryItem.objects.all(),
        label=_('Parent inventory item (ID)'),
    )
    manufacturer_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Manufacturer.objects.all(),
        label=_('Manufacturer (ID)'),
    )
    manufacturer = django_filters.ModelMultipleChoiceFilter(
        field_name='manufacturer__slug',
        queryset=Manufacturer.objects.all(),
        to_field_name='slug',
        label=_('Manufacturer (slug)'),
    )
    role_id = django_filters.ModelMultipleChoiceFilter(
        queryset=InventoryItemRole.objects.all(),
        label=_('Role (ID)'),
    )
    role = django_filters.ModelMultipleChoiceFilter(
        field_name='role__slug',
        queryset=InventoryItemRole.objects.all(),
        to_field_name='slug',
        label=_('Role (slug)'),
    )
    component_type = ContentTypeFilter()
    component_id = MultiValueNumberFilter()
    serial = MultiValueCharFilter(
        lookup_expr='iexact'
    )
    status = django_filters.MultipleChoiceFilter(
        choices=InventoryItemStatusChoices,
        null_value=None
    )

    class Meta:
        model = InventoryItem
        fields = ('id', 'name', 'label', 'part_id', 'asset_tag', 'status', 'description', 'discovered')

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


class InventoryItemRoleFilterSet(OrganizationalModelFilterSet):

    class Meta:
        model = InventoryItemRole
        fields = ('id', 'name', 'slug', 'color', 'description')


class VirtualChassisFilterSet(NetBoxModelFilterSet):
    master_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Device.objects.all(),
        label=_('Master (ID)'),
    )
    master = django_filters.ModelMultipleChoiceFilter(
        field_name='master__name',
        queryset=Device.objects.all(),
        to_field_name='name',
        label=_('Master (name)'),
    )
    region_id = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='master__site__region',
        lookup_expr='in',
        label=_('Region (ID)'),
    )
    region = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='master__site__region',
        lookup_expr='in',
        to_field_name='slug',
        label=_('Region (slug)'),
    )
    site_group_id = TreeNodeMultipleChoiceFilter(
        queryset=SiteGroup.objects.all(),
        field_name='master__site__group',
        lookup_expr='in',
        label=_('Site group (ID)'),
    )
    site_group = TreeNodeMultipleChoiceFilter(
        queryset=SiteGroup.objects.all(),
        field_name='master__site__group',
        lookup_expr='in',
        to_field_name='slug',
        label=_('Site group (slug)'),
    )
    site_id = django_filters.ModelMultipleChoiceFilter(
        field_name='master__site',
        queryset=Site.objects.all(),
        label=_('Site (ID)'),
    )
    site = django_filters.ModelMultipleChoiceFilter(
        field_name='master__site__slug',
        queryset=Site.objects.all(),
        to_field_name='slug',
        label=_('Site name (slug)'),
    )
    tenant_id = django_filters.ModelMultipleChoiceFilter(
        field_name='master__tenant',
        queryset=Tenant.objects.all(),
        label=_('Tenant (ID)'),
    )
    tenant = django_filters.ModelMultipleChoiceFilter(
        field_name='master__tenant__slug',
        queryset=Tenant.objects.all(),
        to_field_name='slug',
        label=_('Tenant (slug)'),
    )

    class Meta:
        model = VirtualChassis
        fields = ('id', 'domain', 'name', 'description', 'member_count')

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = (
            Q(name__icontains=value) |
            Q(description__icontains=value) |
            Q(members__name__icontains=value) |
            Q(domain__icontains=value)
        )
        return queryset.filter(qs_filter).distinct()


class CableFilterSet(TenancyFilterSet, NetBoxModelFilterSet):
    termination_a_type = ContentTypeFilter(
        field_name='terminations__termination_type'
    )
    termination_a_id = MultiValueNumberFilter(
        method='filter_by_cable_end_a',
        field_name='terminations__termination_id'
    )
    termination_b_type = ContentTypeFilter(
        field_name='terminations__termination_type'
    )
    termination_b_id = MultiValueNumberFilter(
        method='filter_by_cable_end_b',
        field_name='terminations__termination_id'
    )
    unterminated = django_filters.BooleanFilter(
        method='_unterminated',
        label=_('Unterminated'),
    )
    type = django_filters.MultipleChoiceFilter(
        choices=CableTypeChoices
    )
    status = django_filters.MultipleChoiceFilter(
        choices=LinkStatusChoices
    )
    color = django_filters.MultipleChoiceFilter(
        choices=ColorChoices
    )
    device_id = MultiValueNumberFilter(
        method='filter_by_termination'
    )
    device = MultiValueCharFilter(
        method='filter_by_termination',
        field_name='device__name'
    )
    rack_id = MultiValueNumberFilter(
        method='filter_by_termination',
        field_name='rack_id'
    )
    rack = MultiValueCharFilter(
        method='filter_by_termination',
        field_name='rack__name'
    )
    location_id = MultiValueNumberFilter(
        method='filter_by_termination',
        field_name='location_id'
    )
    location = MultiValueCharFilter(
        method='filter_by_termination',
        field_name='location__name'
    )
    site_id = MultiValueNumberFilter(
        method='filter_by_termination',
        field_name='site_id'
    )
    site = MultiValueCharFilter(
        method='filter_by_termination',
        field_name='site__slug'
    )

    # Termination object filters
    consoleport_id = MultiValueNumberFilter(
        method='filter_by_consoleport'
    )
    consoleserverport_id = MultiValueNumberFilter(
        method='filter_by_consoleserverport'
    )
    powerport_id = MultiValueNumberFilter(
        method='filter_by_powerport'
    )
    poweroutlet_id = MultiValueNumberFilter(
        method='filter_by_poweroutlet'
    )
    interface_id = MultiValueNumberFilter(
        method='filter_by_interface'
    )
    frontport_id = MultiValueNumberFilter(
        method='filter_by_frontport'
    )
    rearport_id = MultiValueNumberFilter(
        method='filter_by_rearport'
    )
    powerfeed_id = MultiValueNumberFilter(
        method='filter_by_powerfeed'
    )
    circuittermination_id = MultiValueNumberFilter(
        method='filter_by_circuittermination'
    )

    class Meta:
        model = Cable
        fields = ('id', 'label', 'length', 'length_unit', 'description')

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = (
            Q(label__icontains=value) |
            Q(description__icontains=value)
        )
        return queryset.filter(qs_filter)

    def filter_by_termination(self, queryset, name, value):
        # Filter by a related object cached on CableTermination. Note the underscore preceding the field name.
        # Supported objects: device, rack, location, site
        return queryset.filter(**{f'terminations___{name}__in': value}).distinct()

    def filter_by_cable_end(self, queryset, name, value, side):
        # Filter by termination id and cable_end type
        return queryset.filter(**{f'{name}__in': value, 'terminations__cable_end': side}).distinct()

    def filter_by_cable_end_a(self, queryset, name, value):
        # Filter by termination id and cable_end type
        return self.filter_by_cable_end(queryset, name, value, CableEndChoices.SIDE_A)

    def filter_by_cable_end_b(self, queryset, name, value):
        # Filter by termination id and cable_end type
        return self.filter_by_cable_end(queryset, name, value, CableEndChoices.SIDE_B)

    def _unterminated(self, queryset, name, value):
        if value:
            terminated_ids = (
                queryset.filter(terminations__cable_end=CableEndChoices.SIDE_A)
                .filter(terminations__cable_end=CableEndChoices.SIDE_B)
                .values("id")
            )
            return queryset.exclude(id__in=terminated_ids)
        else:
            return queryset.filter(terminations__cable_end=CableEndChoices.SIDE_A).filter(
                terminations__cable_end=CableEndChoices.SIDE_B
            )

    def filter_by_termination_object(self, queryset, model, value):
        # Filter by specific termination object(s)
        content_type = ContentType.objects.get_for_model(model)
        cable_ids = CableTermination.objects.filter(
            termination_type=content_type,
            termination_id__in=value
        ).values_list('cable', flat=True)
        return queryset.filter(pk__in=cable_ids)

    def filter_by_consoleport(self, queryset, name, value):
        return self.filter_by_termination_object(queryset, ConsolePort, value)

    def filter_by_consoleserverport(self, queryset, name, value):
        return self.filter_by_termination_object(queryset, ConsoleServerPort, value)

    def filter_by_powerport(self, queryset, name, value):
        return self.filter_by_termination_object(queryset, PowerPort, value)

    def filter_by_poweroutlet(self, queryset, name, value):
        return self.filter_by_termination_object(queryset, PowerOutlet, value)

    def filter_by_interface(self, queryset, name, value):
        return self.filter_by_termination_object(queryset, Interface, value)

    def filter_by_frontport(self, queryset, name, value):
        return self.filter_by_termination_object(queryset, FrontPort, value)

    def filter_by_rearport(self, queryset, name, value):
        return self.filter_by_termination_object(queryset, RearPort, value)

    def filter_by_powerfeed(self, queryset, name, value):
        return self.filter_by_termination_object(queryset, PowerFeed, value)

    def filter_by_circuittermination(self, queryset, name, value):
        return self.filter_by_termination_object(queryset, CircuitTermination, value)


class CableTerminationFilterSet(ChangeLoggedModelFilterSet):
    termination_type = ContentTypeFilter()

    class Meta:
        model = CableTermination
        fields = ('id', 'cable', 'cable_end', 'termination_type', 'termination_id')


class PowerPanelFilterSet(NetBoxModelFilterSet, ContactModelFilterSet):
    region_id = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='site__region',
        lookup_expr='in',
        label=_('Region (ID)'),
    )
    region = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='site__region',
        lookup_expr='in',
        to_field_name='slug',
        label=_('Region (slug)'),
    )
    site_group_id = TreeNodeMultipleChoiceFilter(
        queryset=SiteGroup.objects.all(),
        field_name='site__group',
        lookup_expr='in',
        label=_('Site group (ID)'),
    )
    site_group = TreeNodeMultipleChoiceFilter(
        queryset=SiteGroup.objects.all(),
        field_name='site__group',
        lookup_expr='in',
        to_field_name='slug',
        label=_('Site group (slug)'),
    )
    site_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Site.objects.all(),
        label=_('Site (ID)'),
    )
    site = django_filters.ModelMultipleChoiceFilter(
        field_name='site__slug',
        queryset=Site.objects.all(),
        to_field_name='slug',
        label=_('Site name (slug)'),
    )
    location_id = TreeNodeMultipleChoiceFilter(
        queryset=Location.objects.all(),
        field_name='location',
        lookup_expr='in',
        label=_('Location (ID)'),
    )

    class Meta:
        model = PowerPanel
        fields = ('id', 'name', 'description')

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = (
            Q(name__icontains=value) |
            Q(description__icontains=value)
        )
        return queryset.filter(qs_filter)


class PowerFeedFilterSet(NetBoxModelFilterSet, CabledObjectFilterSet, PathEndpointFilterSet, TenancyFilterSet):
    region_id = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='power_panel__site__region',
        lookup_expr='in',
        label=_('Region (ID)'),
    )
    region = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='power_panel__site__region',
        lookup_expr='in',
        to_field_name='slug',
        label=_('Region (slug)'),
    )
    site_group_id = TreeNodeMultipleChoiceFilter(
        queryset=SiteGroup.objects.all(),
        field_name='power_panel__site__group',
        lookup_expr='in',
        label=_('Site group (ID)'),
    )
    site_group = TreeNodeMultipleChoiceFilter(
        queryset=SiteGroup.objects.all(),
        field_name='power_panel__site__group',
        lookup_expr='in',
        to_field_name='slug',
        label=_('Site group (slug)'),
    )
    site_id = django_filters.ModelMultipleChoiceFilter(
        field_name='power_panel__site',
        queryset=Site.objects.all(),
        label=_('Site (ID)'),
    )
    site = django_filters.ModelMultipleChoiceFilter(
        field_name='power_panel__site__slug',
        queryset=Site.objects.all(),
        to_field_name='slug',
        label=_('Site name (slug)'),
    )
    power_panel_id = django_filters.ModelMultipleChoiceFilter(
        queryset=PowerPanel.objects.all(),
        label=_('Power panel (ID)'),
    )
    rack_id = django_filters.ModelMultipleChoiceFilter(
        field_name='rack',
        queryset=Rack.objects.all(),
        label=_('Rack (ID)'),
    )
    status = django_filters.MultipleChoiceFilter(
        choices=PowerFeedStatusChoices,
        null_value=None
    )

    class Meta:
        model = PowerFeed
        fields = (
            'id', 'name', 'status', 'type', 'supply', 'phase', 'voltage', 'amperage', 'max_utilization',
            'available_power', 'mark_connected', 'cable_end', 'description',
        )

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = (
            Q(name__icontains=value) |
            Q(description__icontains=value) |
            Q(power_panel__name__icontains=value) |
            Q(comments__icontains=value)
        )
        return queryset.filter(qs_filter)


#
# Connection filter sets
#

class ConnectionFilterSet(BaseFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label=_('Search'),
    )
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

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = (
            Q(device__name__icontains=value) |
            Q(cable__label__icontains=value)
        )
        return queryset.filter(qs_filter)


class ConsoleConnectionFilterSet(ConnectionFilterSet):

    class Meta:
        model = ConsolePort
        fields = ('name',)


class PowerConnectionFilterSet(ConnectionFilterSet):

    class Meta:
        model = PowerPort
        fields = ('name',)


class InterfaceConnectionFilterSet(ConnectionFilterSet):

    class Meta:
        model = Interface
        fields = tuple()
