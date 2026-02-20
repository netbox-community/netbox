from typing import TYPE_CHECKING, Annotated

import strawberry
import strawberry_django
from django.db.models import Q
from strawberry.scalars import ID
from strawberry_django import BaseFilterLookup, ComparisonFilterLookup, FilterLookup

from dcim import models
from dcim.constants import *
from dcim.graphql.enums import InterfaceKindEnum
from dcim.graphql.filter_mixins import (
    ComponentModelFilterMixin,
    ComponentTemplateFilterMixin,
    ModularComponentFilterMixin,
    ModularComponentTemplateFilterMixin,
    RackFilterMixin,
)
from extras.graphql.filter_mixins import ConfigContextFilterMixin
from netbox.graphql.filter_mixins import ImageAttachmentFilterMixin, WeightFilterMixin
from netbox.graphql.filters import (
    BaseModelFilter,
    ChangeLoggedModelFilter,
    NestedGroupModelFilter,
    NetBoxModelFilter,
    OrganizationalModelFilter,
    PrimaryModelFilter,
)
from tenancy.graphql.filter_mixins import ContactFilterMixin, TenancyFilterMixin
from virtualization.models import VMInterface

from .filter_mixins import (
    CabledObjectModelFilterMixin,
    InterfaceBaseFilterMixin,
    RenderConfigFilterMixin,
)

if TYPE_CHECKING:
    from core.graphql.filters import ContentTypeFilter
    from extras.graphql.filters import ConfigTemplateFilter, ImageAttachmentFilter
    from ipam.graphql.filters import (
        ASNFilter,
        FHRPGroupAssignmentFilter,
        IPAddressFilter,
        PrefixFilter,
        VLANGroupFilter,
        VRFFilter,
    )
    from netbox.graphql.enums import ColorEnum
    from netbox.graphql.filter_lookups import FloatLookup, IntegerArrayLookup, IntegerLookup, TreeNodeFilter
    from users.graphql.filters import UserFilter
    from virtualization.graphql.filters import ClusterFilter
    from vpn.graphql.filters import L2VPNFilter, TunnelTerminationFilter
    from wireless.graphql.enums import WirelessChannelEnum, WirelessRoleEnum
    from wireless.graphql.filters import WirelessLANFilter, WirelessLinkFilter

    from .enums import *

__all__ = (
    'CableFilter',
    'CableTerminationFilter',
    'ConsolePortFilter',
    'ConsolePortTemplateFilter',
    'ConsoleServerPortFilter',
    'ConsoleServerPortTemplateFilter',
    'DeviceBayFilter',
    'DeviceBayTemplateFilter',
    'DeviceFilter',
    'DeviceRoleFilter',
    'DeviceTypeFilter',
    'FrontPortFilter',
    'FrontPortTemplateFilter',
    'InterfaceFilter',
    'InterfaceTemplateFilter',
    'InventoryItemFilter',
    'InventoryItemRoleFilter',
    'InventoryItemTemplateFilter',
    'LocationFilter',
    'MACAddressFilter',
    'ManufacturerFilter',
    'ModuleBayFilter',
    'ModuleBayTemplateFilter',
    'ModuleFilter',
    'ModuleTypeFilter',
    'ModuleTypeProfileFilter',
    'PlatformFilter',
    'PortMappingFilter',
    'PortTemplateMappingFilter',
    'PowerFeedFilter',
    'PowerOutletFilter',
    'PowerOutletTemplateFilter',
    'PowerPanelFilter',
    'PowerPortFilter',
    'PowerPortTemplateFilter',
    'RackFilter',
    'RackReservationFilter',
    'RackRoleFilter',
    'RackTypeFilter',
    'RearPortFilter',
    'RearPortTemplateFilter',
    'RegionFilter',
    'SiteFilter',
    'SiteGroupFilter',
    'VirtualChassisFilter',
    'VirtualDeviceContextFilter',
)


@strawberry_django.filter_type(models.Cable, lookups=True)
class CableFilter(TenancyFilterMixin, PrimaryModelFilter):
    type: BaseFilterLookup[Annotated['CableTypeEnum', strawberry.lazy('dcim.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )
    status: BaseFilterLookup[Annotated['LinkStatusEnum', strawberry.lazy('dcim.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )
    label: FilterLookup[str] | None = strawberry_django.filter_field()
    color: BaseFilterLookup[Annotated['ColorEnum', strawberry.lazy('netbox.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )
    length: Annotated['FloatLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    length_unit: BaseFilterLookup[Annotated['CableLengthUnitEnum', strawberry.lazy('dcim.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )
    terminations: Annotated['CableTerminationFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.CableTermination, lookups=True)
class CableTerminationFilter(ChangeLoggedModelFilter):
    cable: Annotated['CableFilter', strawberry.lazy('dcim.graphql.filters')] | None = strawberry_django.filter_field()
    cable_id: ID | None = strawberry_django.filter_field()
    cable_end: BaseFilterLookup[Annotated['CableEndEnum', strawberry.lazy('dcim.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )
    termination_type: Annotated['CableTerminationFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    termination_id: ID | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.ConsolePort, lookups=True)
class ConsolePortFilter(ModularComponentFilterMixin, CabledObjectModelFilterMixin, NetBoxModelFilter):
    type: BaseFilterLookup[Annotated['ConsolePortTypeEnum', strawberry.lazy('dcim.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )
    speed: BaseFilterLookup[Annotated['ConsolePortSpeedEnum', strawberry.lazy('dcim.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.ConsolePortTemplate, lookups=True)
class ConsolePortTemplateFilter(ModularComponentTemplateFilterMixin, ChangeLoggedModelFilter):
    type: BaseFilterLookup[Annotated['ConsolePortTypeEnum', strawberry.lazy('dcim.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.ConsoleServerPort, lookups=True)
class ConsoleServerPortFilter(ModularComponentFilterMixin, CabledObjectModelFilterMixin, NetBoxModelFilter):
    type: BaseFilterLookup[Annotated['ConsolePortTypeEnum', strawberry.lazy('dcim.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )
    speed: BaseFilterLookup[Annotated['ConsolePortSpeedEnum', strawberry.lazy('dcim.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.ConsoleServerPortTemplate, lookups=True)
class ConsoleServerPortTemplateFilter(ModularComponentTemplateFilterMixin, ChangeLoggedModelFilter):
    type: BaseFilterLookup[Annotated['ConsolePortTypeEnum', strawberry.lazy('dcim.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.Device, lookups=True)
class DeviceFilter(
    ContactFilterMixin,
    TenancyFilterMixin,
    ImageAttachmentFilterMixin,
    RenderConfigFilterMixin,
    ConfigContextFilterMixin,
    PrimaryModelFilter,
):
    device_type: Annotated['DeviceTypeFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    device_type_id: ID | None = strawberry_django.filter_field()
    role: Annotated['DeviceRoleFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    role_id: ID | None = strawberry_django.filter_field()
    platform: Annotated['PlatformFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    serial: FilterLookup[str] | None = strawberry_django.filter_field()
    asset_tag: FilterLookup[str] | None = strawberry_django.filter_field()
    site: Annotated['SiteFilter', strawberry.lazy('dcim.graphql.filters')] | None = strawberry_django.filter_field()
    site_id: ID | None = strawberry_django.filter_field()
    location: Annotated['LocationFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    location_id: Annotated['TreeNodeFilter', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    rack: Annotated['RackFilter', strawberry.lazy('dcim.graphql.filters')] | None = strawberry_django.filter_field()
    rack_id: ID | None = strawberry_django.filter_field()
    position: Annotated['FloatLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    face: BaseFilterLookup[Annotated['DeviceFaceEnum', strawberry.lazy('dcim.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )
    status: BaseFilterLookup[Annotated['DeviceStatusEnum', strawberry.lazy('dcim.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )
    airflow: BaseFilterLookup[Annotated['DeviceAirflowEnum', strawberry.lazy('dcim.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )
    primary_ip4: Annotated['IPAddressFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    primary_ip4_id: ID | None = strawberry_django.filter_field()
    primary_ip6: Annotated['IPAddressFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    primary_ip6_id: ID | None = strawberry_django.filter_field()
    oob_ip: Annotated['IPAddressFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    oob_ip_id: ID | None = strawberry_django.filter_field()
    cluster: Annotated['ClusterFilter', strawberry.lazy('virtualization.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    cluster_id: ID | None = strawberry_django.filter_field()
    virtual_chassis: Annotated['VirtualChassisFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    virtual_chassis_id: ID | None = strawberry_django.filter_field()
    vc_position: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    vc_priority: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    latitude: Annotated['FloatLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    longitude: Annotated['FloatLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    console_ports: Annotated['ConsolePortFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    console_server_ports: Annotated['ConsoleServerPortFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    power_outlets: Annotated['PowerOutletFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    power_ports: Annotated['PowerPortFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    interfaces: Annotated['InterfaceFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    front_ports: Annotated['FrontPortFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    rear_ports: Annotated['RearPortFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    device_bays: Annotated['DeviceBayFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    module_bays: Annotated['ModuleBayFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    modules: Annotated['ModuleFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    console_port_count: FilterLookup[int] | None = strawberry_django.filter_field()
    console_server_port_count: FilterLookup[int] | None = strawberry_django.filter_field()
    power_port_count: FilterLookup[int] | None = strawberry_django.filter_field()
    power_outlet_count: FilterLookup[int] | None = strawberry_django.filter_field()
    interface_count: FilterLookup[int] | None = strawberry_django.filter_field()
    front_port_count: FilterLookup[int] | None = strawberry_django.filter_field()
    rear_port_count: FilterLookup[int] | None = strawberry_django.filter_field()
    device_bay_count: FilterLookup[int] | None = strawberry_django.filter_field()
    module_bay_count: FilterLookup[int] | None = strawberry_django.filter_field()
    inventory_item_count: FilterLookup[int] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.DeviceBay, lookups=True)
class DeviceBayFilter(ComponentModelFilterMixin, NetBoxModelFilter):
    installed_device: Annotated['DeviceFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    installed_device_id: ID | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.DeviceBayTemplate, lookups=True)
class DeviceBayTemplateFilter(ComponentTemplateFilterMixin, ChangeLoggedModelFilter):
    pass


@strawberry_django.filter_type(models.InventoryItemTemplate, lookups=True)
class InventoryItemTemplateFilter(ComponentTemplateFilterMixin, ChangeLoggedModelFilter):
    parent: Annotated['InventoryItemTemplateFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    component_type: Annotated['ContentTypeFilter', strawberry.lazy('core.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    component_id: ID | None = strawberry_django.filter_field()
    role: Annotated['InventoryItemRoleFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    role_id: ID | None = strawberry_django.filter_field()
    manufacturer: Annotated['ManufacturerFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    manufacturer_id: ID | None = strawberry_django.filter_field()
    part_id: FilterLookup[str] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.DeviceRole, lookups=True)
class DeviceRoleFilter(RenderConfigFilterMixin, OrganizationalModelFilter):
    color: BaseFilterLookup[Annotated['ColorEnum', strawberry.lazy('netbox.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )
    vm_role: FilterLookup[bool] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.DeviceType, lookups=True)
class DeviceTypeFilter(ImageAttachmentFilterMixin, WeightFilterMixin, PrimaryModelFilter):
    manufacturer: Annotated['ManufacturerFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    manufacturer_id: ID | None = strawberry_django.filter_field()
    model: FilterLookup[str] | None = strawberry_django.filter_field()
    slug: FilterLookup[str] | None = strawberry_django.filter_field()
    default_platform: Annotated['PlatformFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    default_platform_id: ID | None = strawberry_django.filter_field()
    part_number: FilterLookup[str] | None = strawberry_django.filter_field()
    instances: Annotated['DeviceFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    u_height: Annotated['FloatLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    exclude_from_utilization: FilterLookup[bool] | None = strawberry_django.filter_field()
    is_full_depth: FilterLookup[bool] | None = strawberry_django.filter_field()
    subdevice_role: BaseFilterLookup[Annotated['SubdeviceRoleEnum', strawberry.lazy('dcim.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )
    airflow: BaseFilterLookup[Annotated['DeviceAirflowEnum', strawberry.lazy('dcim.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )
    front_image: Annotated['ImageAttachmentFilter', strawberry.lazy('extras.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    rear_image: Annotated['ImageAttachmentFilter', strawberry.lazy('extras.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    console_port_templates: (
        Annotated['ConsolePortTemplateFilter', strawberry.lazy('dcim.graphql.filters')] | None
    ) = strawberry_django.filter_field()
    console_server_port_templates: (
        Annotated['ConsoleServerPortTemplateFilter', strawberry.lazy('dcim.graphql.filters')] | None
    ) = strawberry_django.filter_field()
    power_port_templates: (
        Annotated['PowerPortTemplateFilter', strawberry.lazy('dcim.graphql.filters')] | None
    ) = strawberry_django.filter_field()
    power_outlet_templates: (
        Annotated['PowerOutletTemplateFilter', strawberry.lazy('dcim.graphql.filters')] | None
    ) = strawberry_django.filter_field()
    interface_templates: (
        Annotated['InterfaceTemplateFilter', strawberry.lazy('dcim.graphql.filters')] | None
    ) = strawberry_django.filter_field()
    front_port_templates: (
        Annotated['FrontPortTemplateFilter', strawberry.lazy('dcim.graphql.filters')] | None
    ) = strawberry_django.filter_field()
    rear_port_templates: (
        Annotated['RearPortTemplateFilter', strawberry.lazy('dcim.graphql.filters')] | None
    ) = strawberry_django.filter_field()
    device_bay_templates: (
        Annotated['DeviceBayTemplateFilter', strawberry.lazy('dcim.graphql.filters')] | None
    ) = strawberry_django.filter_field()
    module_bay_templates: (
        Annotated['ModuleBayTemplateFilter', strawberry.lazy('dcim.graphql.filters')] | None
    ) = strawberry_django.filter_field()
    inventory_item_templates: (
        Annotated['InventoryItemTemplateFilter', strawberry.lazy('dcim.graphql.filters')] | None
    ) = strawberry_django.filter_field()
    console_port_template_count: FilterLookup[int] | None = strawberry_django.filter_field()
    console_server_port_template_count: FilterLookup[int] | None = strawberry_django.filter_field()
    power_port_template_count: FilterLookup[int] | None = strawberry_django.filter_field()
    power_outlet_template_count: FilterLookup[int] | None = strawberry_django.filter_field()
    interface_template_count: FilterLookup[int] | None = strawberry_django.filter_field()
    front_port_template_count: FilterLookup[int] | None = strawberry_django.filter_field()
    rear_port_template_count: FilterLookup[int] | None = strawberry_django.filter_field()
    device_bay_template_count: FilterLookup[int] | None = strawberry_django.filter_field()
    module_bay_template_count: FilterLookup[int] | None = strawberry_django.filter_field()
    inventory_item_template_count: FilterLookup[int] | None = strawberry_django.filter_field()
    device_count: ComparisonFilterLookup[int] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.FrontPort, lookups=True)
class FrontPortFilter(ModularComponentFilterMixin, CabledObjectModelFilterMixin, NetBoxModelFilter):
    type: BaseFilterLookup[Annotated['PortTypeEnum', strawberry.lazy('dcim.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )
    color: BaseFilterLookup[Annotated['ColorEnum', strawberry.lazy('netbox.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.FrontPortTemplate, lookups=True)
class FrontPortTemplateFilter(ModularComponentTemplateFilterMixin, ChangeLoggedModelFilter):
    type: BaseFilterLookup[Annotated['PortTypeEnum', strawberry.lazy('dcim.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )
    color: BaseFilterLookup[Annotated['ColorEnum', strawberry.lazy('netbox.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.PortMapping, lookups=True)
class PortMappingFilter(BaseModelFilter):
    device: Annotated['DeviceFilter', strawberry.lazy('dcim.graphql.filters')] | None = strawberry_django.filter_field()
    front_port: Annotated['FrontPortFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    rear_port: Annotated['RearPortFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    front_port_position: FilterLookup[int] | None = strawberry_django.filter_field()
    rear_port_position: FilterLookup[int] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.PortTemplateMapping, lookups=True)
class PortTemplateMappingFilter(BaseModelFilter):
    device_type: Annotated['DeviceTypeFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    module_type: Annotated['ModuleTypeFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    front_port: Annotated['FrontPortTemplateFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    rear_port: Annotated['RearPortTemplateFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    front_port_position: FilterLookup[int] | None = strawberry_django.filter_field()
    rear_port_position: FilterLookup[int] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.MACAddress, lookups=True)
class MACAddressFilter(PrimaryModelFilter):
    mac_address: FilterLookup[str] | None = strawberry_django.filter_field()
    assigned_object_type: Annotated['ContentTypeFilter', strawberry.lazy('core.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    assigned_object_id: ID | None = strawberry_django.filter_field()

    @strawberry_django.filter_field()
    def assigned(self, value: bool, prefix) -> Q:
        return Q(**{f'{prefix}assigned_object_id__isnull': (not value)})

    @strawberry_django.filter_field()
    def primary(self, value: bool, prefix) -> Q:
        interface_mac_ids = models.Interface.objects.filter(primary_mac_address_id__isnull=False).values_list(
            'primary_mac_address_id', flat=True
        )
        vminterface_mac_ids = VMInterface.objects.filter(primary_mac_address_id__isnull=False).values_list(
            'primary_mac_address_id', flat=True
        )
        query = Q(**{f'{prefix}pk__in': interface_mac_ids}) | Q(**{f'{prefix}pk__in': vminterface_mac_ids})
        if value:
            return Q(query)
        return ~Q(query)


@strawberry_django.filter_type(models.Interface, lookups=True)
class InterfaceFilter(
    ModularComponentFilterMixin,
    InterfaceBaseFilterMixin,
    CabledObjectModelFilterMixin,
    NetBoxModelFilter
):
    vcdcs: Annotated['VirtualDeviceContextFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    lag: Annotated['InterfaceFilter', strawberry.lazy('dcim.graphql.filters')] | None = strawberry_django.filter_field()
    lag_id: ID | None = strawberry_django.filter_field()
    type: BaseFilterLookup[Annotated['InterfaceTypeEnum', strawberry.lazy('dcim.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )
    mgmt_only: FilterLookup[bool] | None = strawberry_django.filter_field()
    speed: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    duplex: BaseFilterLookup[Annotated['InterfaceDuplexEnum', strawberry.lazy('dcim.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )
    wwn: FilterLookup[str] | None = strawberry_django.filter_field()
    parent: Annotated['InterfaceFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    parent_id: ID | None = strawberry_django.filter_field()
    rf_role: BaseFilterLookup[Annotated['WirelessRoleEnum', strawberry.lazy('wireless.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )
    rf_channel: BaseFilterLookup[Annotated['WirelessChannelEnum', strawberry.lazy('wireless.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )
    rf_channel_frequency: Annotated['FloatLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    rf_channel_width: Annotated['FloatLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    tx_power: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    poe_mode: BaseFilterLookup[Annotated['InterfacePoEModeEnum', strawberry.lazy('dcim.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )
    poe_type: BaseFilterLookup[Annotated['InterfacePoETypeEnum', strawberry.lazy('dcim.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )
    wireless_link: Annotated['WirelessLinkFilter', strawberry.lazy('wireless.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    wireless_link_id: ID | None = strawberry_django.filter_field()
    wireless_lans: Annotated['WirelessLANFilter', strawberry.lazy('wireless.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    vrf: Annotated['VRFFilter', strawberry.lazy('ipam.graphql.filters')] | None = strawberry_django.filter_field()
    vrf_id: ID | None = strawberry_django.filter_field()
    ip_addresses: Annotated['IPAddressFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    mac_addresses: Annotated['MACAddressFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    fhrp_group_assignments: Annotated['FHRPGroupAssignmentFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    tunnel_terminations: Annotated['TunnelTerminationFilter', strawberry.lazy('vpn.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    l2vpn_terminations: Annotated['L2VPNFilter', strawberry.lazy('vpn.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )

    @strawberry_django.filter_field
    def cabled(self, value: bool, prefix: str):
        return Q(**{f'{prefix}cable__isnull': (not value)})

    @strawberry_django.filter_field
    def connected(self, queryset, value: bool, prefix: str):
        if value is True:
            return queryset, Q(**{f"{prefix}_path__is_active": True})
        return queryset, Q(**{f"{prefix}_path__isnull": True}) | Q(**{f"{prefix}_path__is_active": False})

    @strawberry_django.filter_field
    def kind(
        self,
        queryset,
        value: Annotated['InterfaceKindEnum', strawberry.lazy('dcim.graphql.enums')],
        prefix: str
    ):
        if value == InterfaceKindEnum.KIND_PHYSICAL:
            return queryset, ~Q(**{f"{prefix}type__in": NONCONNECTABLE_IFACE_TYPES})
        if value == InterfaceKindEnum.KIND_VIRTUAL:
            return queryset, Q(**{f"{prefix}type__in": VIRTUAL_IFACE_TYPES})
        if value == InterfaceKindEnum.KIND_WIRELESS:
            return queryset, Q(**{f"{prefix}type__in": WIRELESS_IFACE_TYPES})
        return queryset, Q()


@strawberry_django.filter_type(models.InterfaceTemplate, lookups=True)
class InterfaceTemplateFilter(ModularComponentTemplateFilterMixin, ChangeLoggedModelFilter):
    type: BaseFilterLookup[Annotated['InterfaceTypeEnum', strawberry.lazy('dcim.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )
    enabled: FilterLookup[bool] | None = strawberry_django.filter_field()
    mgmt_only: FilterLookup[bool] | None = strawberry_django.filter_field()
    bridge: Annotated['InterfaceTemplateFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    bridge_id: ID | None = strawberry_django.filter_field()
    poe_mode: BaseFilterLookup[Annotated['InterfacePoEModeEnum', strawberry.lazy('dcim.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )
    poe_type: BaseFilterLookup[Annotated['InterfacePoETypeEnum', strawberry.lazy('dcim.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )
    rf_role: BaseFilterLookup[Annotated['WirelessRoleEnum', strawberry.lazy('wireless.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.InventoryItem, lookups=True)
class InventoryItemFilter(ComponentModelFilterMixin, NetBoxModelFilter):
    parent: Annotated['InventoryItemFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    parent_id: ID | None = strawberry_django.filter_field()
    component_type: Annotated['ContentTypeFilter', strawberry.lazy('core.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    component_id: ID | None = strawberry_django.filter_field()
    status: BaseFilterLookup[Annotated['InventoryItemStatusEnum', strawberry.lazy('dcim.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )
    role: Annotated['InventoryItemRoleFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    role_id: ID | None = strawberry_django.filter_field()
    manufacturer: Annotated['ManufacturerFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    manufacturer_id: ID | None = strawberry_django.filter_field()
    part_id: FilterLookup[str] | None = strawberry_django.filter_field()
    serial: FilterLookup[str] | None = strawberry_django.filter_field()
    asset_tag: FilterLookup[str] | None = strawberry_django.filter_field()
    discovered: FilterLookup[bool] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.InventoryItemRole, lookups=True)
class InventoryItemRoleFilter(OrganizationalModelFilter):
    color: BaseFilterLookup[Annotated['ColorEnum', strawberry.lazy('netbox.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.Location, lookups=True)
class LocationFilter(ContactFilterMixin, ImageAttachmentFilterMixin, TenancyFilterMixin, NestedGroupModelFilter):
    site: Annotated['SiteFilter', strawberry.lazy('dcim.graphql.filters')] | None = strawberry_django.filter_field()
    site_id: ID | None = strawberry_django.filter_field()
    status: BaseFilterLookup[Annotated['LocationStatusEnum', strawberry.lazy('dcim.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )
    facility: FilterLookup[str] | None = strawberry_django.filter_field()
    prefixes: Annotated['PrefixFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    vlan_groups: Annotated['VLANGroupFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.Manufacturer, lookups=True)
class ManufacturerFilter(ContactFilterMixin, OrganizationalModelFilter):
    pass


@strawberry_django.filter_type(models.Module, lookups=True)
class ModuleFilter(ConfigContextFilterMixin, PrimaryModelFilter):
    device: Annotated['DeviceFilter', strawberry.lazy('dcim.graphql.filters')] | None = strawberry_django.filter_field()
    device_id: ID | None = strawberry_django.filter_field()
    module_bay: Annotated['ModuleBayFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    module_bay_id: ID | None = strawberry_django.filter_field()
    module_type: Annotated['ModuleTypeFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    module_type_id: ID | None = strawberry_django.filter_field()
    status: BaseFilterLookup[Annotated['ModuleStatusEnum', strawberry.lazy('dcim.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )
    serial: FilterLookup[str] | None = strawberry_django.filter_field()
    asset_tag: FilterLookup[str] | None = strawberry_django.filter_field()
    console_ports: Annotated['ConsolePortFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    console_server_ports: Annotated['ConsoleServerPortFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    power_outlets: Annotated['PowerOutletFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    power_ports: Annotated['PowerPortFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    interfaces: Annotated['InterfaceFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    front_ports: Annotated['FrontPortFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    rear_ports: Annotated['RearPortFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    device_bays: Annotated['DeviceBayFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    module_bays: Annotated['ModuleBayFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    modules: Annotated['ModuleFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.ModuleBay, lookups=True)
class ModuleBayFilter(ModularComponentFilterMixin, NetBoxModelFilter):
    parent: Annotated['ModuleBayFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    parent_id: ID | None = strawberry_django.filter_field()
    position: FilterLookup[str] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.ModuleBayTemplate, lookups=True)
class ModuleBayTemplateFilter(ModularComponentTemplateFilterMixin, ChangeLoggedModelFilter):
    position: FilterLookup[str] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.ModuleTypeProfile, lookups=True)
class ModuleTypeProfileFilter(PrimaryModelFilter):
    name: FilterLookup[str] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.ModuleType, lookups=True)
class ModuleTypeFilter(ImageAttachmentFilterMixin, WeightFilterMixin, PrimaryModelFilter):
    manufacturer: Annotated['ManufacturerFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    manufacturer_id: ID | None = strawberry_django.filter_field()
    profile: Annotated['ModuleTypeProfileFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    profile_id: ID | None = strawberry_django.filter_field()
    model: FilterLookup[str] | None = strawberry_django.filter_field()
    part_number: FilterLookup[str] | None = strawberry_django.filter_field()
    instances: Annotated['ModuleFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    airflow: BaseFilterLookup[Annotated['ModuleAirflowEnum', strawberry.lazy('dcim.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )
    console_port_templates: (
        Annotated['ConsolePortTemplateFilter', strawberry.lazy('dcim.graphql.filters')] | None
    ) = strawberry_django.filter_field()
    console_server_port_templates: (
        Annotated['ConsoleServerPortTemplateFilter', strawberry.lazy('dcim.graphql.filters')] | None
    ) = strawberry_django.filter_field()
    power_port_templates: (
        Annotated['PowerPortTemplateFilter', strawberry.lazy('dcim.graphql.filters')] | None
    ) = strawberry_django.filter_field()
    power_outlet_templates: (
        Annotated['PowerOutletTemplateFilter', strawberry.lazy('dcim.graphql.filters')] | None
    ) = strawberry_django.filter_field()
    interface_templates: (
        Annotated['InterfaceTemplateFilter', strawberry.lazy('dcim.graphql.filters')] | None
    ) = strawberry_django.filter_field()
    front_port_templates: (
        Annotated['FrontPortTemplateFilter', strawberry.lazy('dcim.graphql.filters')] | None
    ) = strawberry_django.filter_field()
    rear_port_templates: (
        Annotated['RearPortTemplateFilter', strawberry.lazy('dcim.graphql.filters')] | None
    ) = strawberry_django.filter_field()
    device_bay_templates: (
        Annotated['DeviceBayTemplateFilter', strawberry.lazy('dcim.graphql.filters')] | None
    ) = strawberry_django.filter_field()
    module_bay_templates: (
        Annotated['ModuleBayTemplateFilter', strawberry.lazy('dcim.graphql.filters')] | None
    ) = strawberry_django.filter_field()
    inventory_item_templates: (
        Annotated['InventoryItemTemplateFilter', strawberry.lazy('dcim.graphql.filters')] | None
    ) = strawberry_django.filter_field()
    module_count: ComparisonFilterLookup[int] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.Platform, lookups=True)
class PlatformFilter(OrganizationalModelFilter):
    manufacturer: Annotated['ManufacturerFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    manufacturer_id: ID | None = strawberry_django.filter_field()
    config_template: Annotated['ConfigTemplateFilter', strawberry.lazy('extras.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    config_template_id: ID | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.PowerFeed, lookups=True)
class PowerFeedFilter(CabledObjectModelFilterMixin, TenancyFilterMixin, PrimaryModelFilter):
    power_panel: Annotated['PowerPanelFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    power_panel_id: ID | None = strawberry_django.filter_field()
    rack: Annotated['RackFilter', strawberry.lazy('dcim.graphql.filters')] | None = strawberry_django.filter_field()
    rack_id: ID | None = strawberry_django.filter_field()
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    status: BaseFilterLookup[Annotated['PowerFeedStatusEnum', strawberry.lazy('dcim.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )
    type: BaseFilterLookup[Annotated['PowerFeedTypeEnum', strawberry.lazy('dcim.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )
    supply: BaseFilterLookup[Annotated['PowerFeedSupplyEnum', strawberry.lazy('dcim.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )
    phase: BaseFilterLookup[Annotated['PowerFeedPhaseEnum', strawberry.lazy('dcim.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )
    voltage: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    amperage: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    max_utilization: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    available_power: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.PowerOutlet, lookups=True)
class PowerOutletFilter(ModularComponentFilterMixin, CabledObjectModelFilterMixin, NetBoxModelFilter):
    type: BaseFilterLookup[Annotated['PowerOutletTypeEnum', strawberry.lazy('dcim.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )
    power_port: Annotated['PowerPortFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    power_port_id: ID | None = strawberry_django.filter_field()
    feed_leg: BaseFilterLookup[Annotated['PowerOutletFeedLegEnum', strawberry.lazy('dcim.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )
    color: BaseFilterLookup[Annotated['ColorEnum', strawberry.lazy('netbox.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )
    status: BaseFilterLookup[Annotated['PowerOutletStatusEnum', strawberry.lazy('dcim.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.PowerOutletTemplate, lookups=True)
class PowerOutletTemplateFilter(ModularComponentTemplateFilterMixin, ChangeLoggedModelFilter):
    type: BaseFilterLookup[Annotated['PowerOutletTypeEnum', strawberry.lazy('dcim.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )
    power_port: Annotated['PowerPortTemplateFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    power_port_id: ID | None = strawberry_django.filter_field()
    feed_leg: BaseFilterLookup[Annotated['PowerOutletFeedLegEnum', strawberry.lazy('dcim.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.PowerPanel, lookups=True)
class PowerPanelFilter(ContactFilterMixin, ImageAttachmentFilterMixin, PrimaryModelFilter):
    site: Annotated['SiteFilter', strawberry.lazy('dcim.graphql.filters')] | None = strawberry_django.filter_field()
    site_id: ID | None = strawberry_django.filter_field()
    location: Annotated['LocationFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    location_id: Annotated['TreeNodeFilter', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    name: FilterLookup[str] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.PowerPort, lookups=True)
class PowerPortFilter(ModularComponentFilterMixin, CabledObjectModelFilterMixin, NetBoxModelFilter):
    type: BaseFilterLookup[Annotated['PowerPortTypeEnum', strawberry.lazy('dcim.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )
    maximum_draw: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    allocated_draw: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.PowerPortTemplate, lookups=True)
class PowerPortTemplateFilter(ModularComponentTemplateFilterMixin, ChangeLoggedModelFilter):
    type: BaseFilterLookup[Annotated['PowerPortTypeEnum', strawberry.lazy('dcim.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )
    maximum_draw: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    allocated_draw: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.RackType, lookups=True)
class RackTypeFilter(ImageAttachmentFilterMixin, RackFilterMixin, WeightFilterMixin, PrimaryModelFilter):
    form_factor: BaseFilterLookup[Annotated['RackFormFactorEnum', strawberry.lazy('dcim.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )
    manufacturer: Annotated['ManufacturerFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    manufacturer_id: ID | None = strawberry_django.filter_field()
    model: FilterLookup[str] | None = strawberry_django.filter_field()
    slug: FilterLookup[str] | None = strawberry_django.filter_field()
    racks: Annotated['RackFilter', strawberry.lazy('dcim.graphql.filters')] | None = strawberry_django.filter_field()
    rack_count: ComparisonFilterLookup[int] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.Rack, lookups=True)
class RackFilter(
    ContactFilterMixin,
    ImageAttachmentFilterMixin,
    TenancyFilterMixin,
    WeightFilterMixin,
    RackFilterMixin,
    PrimaryModelFilter
):
    form_factor: BaseFilterLookup[Annotated['RackFormFactorEnum', strawberry.lazy('dcim.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )
    rack_type: Annotated['RackTypeFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    rack_type_id: ID | None = strawberry_django.filter_field()
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    facility_id: FilterLookup[str] | None = strawberry_django.filter_field()
    site: Annotated['SiteFilter', strawberry.lazy('dcim.graphql.filters')] | None = strawberry_django.filter_field()
    site_id: ID | None = strawberry_django.filter_field()
    location: Annotated['LocationFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    location_id: Annotated['TreeNodeFilter', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    status: BaseFilterLookup[Annotated['RackStatusEnum', strawberry.lazy('dcim.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )
    role: Annotated['RackRoleFilter', strawberry.lazy('dcim.graphql.filters')] | None = strawberry_django.filter_field()
    role_id: ID | None = strawberry_django.filter_field()
    serial: FilterLookup[str] | None = strawberry_django.filter_field()
    asset_tag: FilterLookup[str] | None = strawberry_django.filter_field()
    airflow: BaseFilterLookup[Annotated['RackAirflowEnum', strawberry.lazy('dcim.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )
    vlan_groups: Annotated['VLANGroupFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.RackReservation, lookups=True)
class RackReservationFilter(TenancyFilterMixin, PrimaryModelFilter):
    rack: Annotated['RackFilter', strawberry.lazy('dcim.graphql.filters')] | None = strawberry_django.filter_field()
    rack_id: ID | None = strawberry_django.filter_field()
    units: Annotated['IntegerArrayLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    user: Annotated['UserFilter', strawberry.lazy('users.graphql.filters')] | None = strawberry_django.filter_field()
    user_id: ID | None = strawberry_django.filter_field()
    description: FilterLookup[str] | None = strawberry_django.filter_field()
    status: BaseFilterLookup[Annotated['RackReservationStatusEnum', strawberry.lazy('dcim.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.RackRole, lookups=True)
class RackRoleFilter(OrganizationalModelFilter):
    color: BaseFilterLookup[Annotated['ColorEnum', strawberry.lazy('netbox.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.RearPort, lookups=True)
class RearPortFilter(ModularComponentFilterMixin, CabledObjectModelFilterMixin, NetBoxModelFilter):
    type: BaseFilterLookup[Annotated['PortTypeEnum', strawberry.lazy('dcim.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )
    color: BaseFilterLookup[Annotated['ColorEnum', strawberry.lazy('netbox.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )
    positions: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.RearPortTemplate, lookups=True)
class RearPortTemplateFilter(ModularComponentTemplateFilterMixin, ChangeLoggedModelFilter):
    type: BaseFilterLookup[Annotated['PortTypeEnum', strawberry.lazy('dcim.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )
    color: BaseFilterLookup[Annotated['ColorEnum', strawberry.lazy('netbox.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )
    positions: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.Region, lookups=True)
class RegionFilter(ContactFilterMixin, NestedGroupModelFilter):
    prefixes: Annotated['PrefixFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    vlan_groups: Annotated['VLANGroupFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.Site, lookups=True)
class SiteFilter(ContactFilterMixin, ImageAttachmentFilterMixin, TenancyFilterMixin, PrimaryModelFilter):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    slug: FilterLookup[str] | None = strawberry_django.filter_field()
    status: BaseFilterLookup[Annotated['SiteStatusEnum', strawberry.lazy('dcim.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )
    region: Annotated['RegionFilter', strawberry.lazy('dcim.graphql.filters')] | None = strawberry_django.filter_field()
    region_id: Annotated['TreeNodeFilter', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    group: Annotated['SiteGroupFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    group_id: Annotated['TreeNodeFilter', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    facility: FilterLookup[str] | None = strawberry_django.filter_field()
    asns: Annotated['ASNFilter', strawberry.lazy('ipam.graphql.filters')] | None = strawberry_django.filter_field()
    time_zone: FilterLookup[str] | None = strawberry_django.filter_field()
    physical_address: FilterLookup[str] | None = strawberry_django.filter_field()
    shipping_address: FilterLookup[str] | None = strawberry_django.filter_field()
    latitude: Annotated['FloatLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    longitude: Annotated['FloatLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    prefixes: Annotated['PrefixFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    vlan_groups: Annotated['VLANGroupFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.SiteGroup, lookups=True)
class SiteGroupFilter(ContactFilterMixin, NestedGroupModelFilter):
    prefixes: Annotated['PrefixFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    vlan_groups: Annotated['VLANGroupFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.VirtualChassis, lookups=True)
class VirtualChassisFilter(PrimaryModelFilter):
    master: Annotated['DeviceFilter', strawberry.lazy('dcim.graphql.filters')] | None = strawberry_django.filter_field()
    master_id: ID | None = strawberry_django.filter_field()
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    domain: FilterLookup[str] | None = strawberry_django.filter_field()
    members: (
        Annotated['DeviceFilter', strawberry.lazy('dcim.graphql.filters')] | None
    ) = strawberry_django.filter_field()
    member_count: FilterLookup[int] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.VirtualDeviceContext, lookups=True)
class VirtualDeviceContextFilter(TenancyFilterMixin, PrimaryModelFilter):
    device: Annotated['DeviceFilter', strawberry.lazy('dcim.graphql.filters')] | None = strawberry_django.filter_field()
    device_id: ID | None = strawberry_django.filter_field()
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    status: (
        BaseFilterLookup[Annotated['VirtualDeviceContextStatusEnum', strawberry.lazy('dcim.graphql.enums')]] | None
    ) = (
        strawberry_django.filter_field()
    )
    identifier: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    primary_ip4: Annotated['IPAddressFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    primary_ip4_id: ID | None = strawberry_django.filter_field()
    primary_ip6: Annotated['IPAddressFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    primary_ip6_id: ID | None = strawberry_django.filter_field()
    comments: FilterLookup[str] | None = strawberry_django.filter_field()
    interfaces: (
        Annotated['InterfaceFilter', strawberry.lazy('dcim.graphql.filters')] | None
    ) = strawberry_django.filter_field()
