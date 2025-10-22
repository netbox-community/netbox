from typing import List

import strawberry
import strawberry_django
from strawberry_django.pagination import OffsetPaginated

from .types import *


@strawberry.type(name="Query")
class DCIMQueryV1:
    cable: CableType = strawberry_django.field()
    cable_list: List[CableType] = strawberry_django.field()

    console_port: ConsolePortType = strawberry_django.field()
    console_port_list: List[ConsolePortType] = strawberry_django.field()

    console_port_template: ConsolePortTemplateType = strawberry_django.field()
    console_port_template_list: List[ConsolePortTemplateType] = strawberry_django.field()

    console_server_port: ConsoleServerPortType = strawberry_django.field()
    console_server_port_list: List[ConsoleServerPortType] = strawberry_django.field()

    console_server_port_template: ConsoleServerPortTemplateType = strawberry_django.field()
    console_server_port_template_list: List[ConsoleServerPortTemplateType] = strawberry_django.field()

    device: DeviceType = strawberry_django.field()
    device_list: List[DeviceType] = strawberry_django.field()

    device_bay: DeviceBayType = strawberry_django.field()
    device_bay_list: List[DeviceBayType] = strawberry_django.field()

    device_bay_template: DeviceBayTemplateType = strawberry_django.field()
    device_bay_template_list: List[DeviceBayTemplateType] = strawberry_django.field()

    device_role: DeviceRoleType = strawberry_django.field()
    device_role_list: List[DeviceRoleType] = strawberry_django.field()

    device_type: DeviceTypeType = strawberry_django.field()
    device_type_list: List[DeviceTypeType] = strawberry_django.field()

    front_port: FrontPortType = strawberry_django.field()
    front_port_list: List[FrontPortType] = strawberry_django.field()

    front_port_template: FrontPortTemplateType = strawberry_django.field()
    front_port_template_list: List[FrontPortTemplateType] = strawberry_django.field()

    mac_address: MACAddressType = strawberry_django.field()
    mac_address_list: List[MACAddressType] = strawberry_django.field()

    interface: InterfaceType = strawberry_django.field()
    interface_list: List[InterfaceType] = strawberry_django.field()

    interface_template: InterfaceTemplateType = strawberry_django.field()
    interface_template_list: List[InterfaceTemplateType] = strawberry_django.field()

    inventory_item: InventoryItemType = strawberry_django.field()
    inventory_item_list: List[InventoryItemType] = strawberry_django.field()

    inventory_item_role: InventoryItemRoleType = strawberry_django.field()
    inventory_item_role_list: List[InventoryItemRoleType] = strawberry_django.field()

    inventory_item_template: InventoryItemTemplateType = strawberry_django.field()
    inventory_item_template_list: List[InventoryItemTemplateType] = strawberry_django.field()

    location: LocationType = strawberry_django.field()
    location_list: List[LocationType] = strawberry_django.field()

    manufacturer: ManufacturerType = strawberry_django.field()
    manufacturer_list: List[ManufacturerType] = strawberry_django.field()

    module: ModuleType = strawberry_django.field()
    module_list: List[ModuleType] = strawberry_django.field()

    module_bay: ModuleBayType = strawberry_django.field()
    module_bay_list: List[ModuleBayType] = strawberry_django.field()

    module_bay_template: ModuleBayTemplateType = strawberry_django.field()
    module_bay_template_list: List[ModuleBayTemplateType] = strawberry_django.field()

    module_type_profile: ModuleTypeProfileType = strawberry_django.field()
    module_type_profile_list: List[ModuleTypeProfileType] = strawberry_django.field()

    module_type: ModuleTypeType = strawberry_django.field()
    module_type_list: List[ModuleTypeType] = strawberry_django.field()

    platform: PlatformType = strawberry_django.field()
    platform_list: List[PlatformType] = strawberry_django.field()

    power_feed: PowerFeedType = strawberry_django.field()
    power_feed_list: List[PowerFeedType] = strawberry_django.field()

    power_outlet: PowerOutletType = strawberry_django.field()
    power_outlet_list: List[PowerOutletType] = strawberry_django.field()

    power_outlet_template: PowerOutletTemplateType = strawberry_django.field()
    power_outlet_template_list: List[PowerOutletTemplateType] = strawberry_django.field()

    power_panel: PowerPanelType = strawberry_django.field()
    power_panel_list: List[PowerPanelType] = strawberry_django.field()

    power_port: PowerPortType = strawberry_django.field()
    power_port_list: List[PowerPortType] = strawberry_django.field()

    power_port_template: PowerPortTemplateType = strawberry_django.field()
    power_port_template_list: List[PowerPortTemplateType] = strawberry_django.field()

    rack_type: RackTypeType = strawberry_django.field()
    rack_type_list: List[RackTypeType] = strawberry_django.field()

    rack: RackType = strawberry_django.field()
    rack_list: List[RackType] = strawberry_django.field()

    rack_reservation: RackReservationType = strawberry_django.field()
    rack_reservation_list: List[RackReservationType] = strawberry_django.field()

    rack_role: RackRoleType = strawberry_django.field()
    rack_role_list: List[RackRoleType] = strawberry_django.field()

    rear_port: RearPortType = strawberry_django.field()
    rear_port_list: List[RearPortType] = strawberry_django.field()

    rear_port_template: RearPortTemplateType = strawberry_django.field()
    rear_port_template_list: List[RearPortTemplateType] = strawberry_django.field()

    region: RegionType = strawberry_django.field()
    region_list: List[RegionType] = strawberry_django.field()

    site: SiteType = strawberry_django.field()
    site_list: List[SiteType] = strawberry_django.field()

    site_group: SiteGroupType = strawberry_django.field()
    site_group_list: List[SiteGroupType] = strawberry_django.field()

    virtual_chassis: VirtualChassisType = strawberry_django.field()
    virtual_chassis_list: List[VirtualChassisType] = strawberry_django.field()

    virtual_device_context: VirtualDeviceContextType = strawberry_django.field()
    virtual_device_context_list: List[VirtualDeviceContextType] = strawberry_django.field()


@strawberry.type(name="Query")
class DCIMQuery:
    cable: CableType = strawberry_django.field()
    cable_list: OffsetPaginated[CableType] = strawberry_django.offset_paginated()

    console_port: ConsolePortType = strawberry_django.field()
    console_port_list: OffsetPaginated[ConsolePortType] = strawberry_django.offset_paginated()

    console_port_template: ConsolePortTemplateType = strawberry_django.field()
    console_port_template_list: OffsetPaginated[ConsolePortTemplateType] = strawberry_django.offset_paginated()

    console_server_port: ConsoleServerPortType = strawberry_django.field()
    console_server_port_list: OffsetPaginated[ConsoleServerPortType] = strawberry_django.offset_paginated()

    console_server_port_template: ConsoleServerPortTemplateType = strawberry_django.field()
    console_server_port_template_list: OffsetPaginated[ConsoleServerPortTemplateType] = (
        strawberry_django.offset_paginated()
    )

    device: DeviceType = strawberry_django.field()
    device_list: OffsetPaginated[DeviceType] = strawberry_django.offset_paginated()

    device_bay: DeviceBayType = strawberry_django.field()
    device_bay_list: OffsetPaginated[DeviceBayType] = strawberry_django.offset_paginated()

    device_bay_template: DeviceBayTemplateType = strawberry_django.field()
    device_bay_template_list: OffsetPaginated[DeviceBayTemplateType] = strawberry_django.offset_paginated()

    device_role: DeviceRoleType = strawberry_django.field()
    device_role_list: OffsetPaginated[DeviceRoleType] = strawberry_django.offset_paginated()

    device_type: DeviceTypeType = strawberry_django.field()
    device_type_list: OffsetPaginated[DeviceTypeType] = strawberry_django.offset_paginated()

    front_port: FrontPortType = strawberry_django.field()
    front_port_list: OffsetPaginated[FrontPortType] = strawberry_django.offset_paginated()

    front_port_template: FrontPortTemplateType = strawberry_django.field()
    front_port_template_list: OffsetPaginated[FrontPortTemplateType] = strawberry_django.offset_paginated()

    mac_address: MACAddressType = strawberry_django.field()
    mac_address_list: OffsetPaginated[MACAddressType] = strawberry_django.offset_paginated()

    interface: InterfaceType = strawberry_django.field()
    interface_list: OffsetPaginated[InterfaceType] = strawberry_django.offset_paginated()

    interface_template: InterfaceTemplateType = strawberry_django.field()
    interface_template_list: OffsetPaginated[InterfaceTemplateType] = strawberry_django.offset_paginated()

    inventory_item: InventoryItemType = strawberry_django.field()
    inventory_item_list: OffsetPaginated[InventoryItemType] = strawberry_django.offset_paginated()

    inventory_item_role: InventoryItemRoleType = strawberry_django.field()
    inventory_item_role_list: OffsetPaginated[InventoryItemRoleType] = strawberry_django.offset_paginated()

    inventory_item_template: InventoryItemTemplateType = strawberry_django.field()
    inventory_item_template_list: OffsetPaginated[InventoryItemTemplateType] = strawberry_django.offset_paginated()

    location: LocationType = strawberry_django.field()
    location_list: OffsetPaginated[LocationType] = strawberry_django.offset_paginated()

    manufacturer: ManufacturerType = strawberry_django.field()
    manufacturer_list: OffsetPaginated[ManufacturerType] = strawberry_django.offset_paginated()

    module: ModuleType = strawberry_django.field()
    module_list: OffsetPaginated[ModuleType] = strawberry_django.offset_paginated()

    module_bay: ModuleBayType = strawberry_django.field()
    module_bay_list: OffsetPaginated[ModuleBayType] = strawberry_django.offset_paginated()

    module_bay_template: ModuleBayTemplateType = strawberry_django.field()
    module_bay_template_list: OffsetPaginated[ModuleBayTemplateType] = strawberry_django.offset_paginated()

    module_type_profile: ModuleTypeProfileType = strawberry_django.field()
    module_type_profile_list: OffsetPaginated[ModuleTypeProfileType] = strawberry_django.offset_paginated()

    module_type: ModuleTypeType = strawberry_django.field()
    module_type_list: OffsetPaginated[ModuleTypeType] = strawberry_django.offset_paginated()

    platform: PlatformType = strawberry_django.field()
    platform_list: OffsetPaginated[PlatformType] = strawberry_django.offset_paginated()

    power_feed: PowerFeedType = strawberry_django.field()
    power_feed_list: OffsetPaginated[PowerFeedType] = strawberry_django.offset_paginated()

    power_outlet: PowerOutletType = strawberry_django.field()
    power_outlet_list: OffsetPaginated[PowerOutletType] = strawberry_django.offset_paginated()

    power_outlet_template: PowerOutletTemplateType = strawberry_django.field()
    power_outlet_template_list: OffsetPaginated[PowerOutletTemplateType] = strawberry_django.offset_paginated()

    power_panel: PowerPanelType = strawberry_django.field()
    power_panel_list: OffsetPaginated[PowerPanelType] = strawberry_django.offset_paginated()

    power_port: PowerPortType = strawberry_django.field()
    power_port_list: OffsetPaginated[PowerPortType] = strawberry_django.offset_paginated()

    power_port_template: PowerPortTemplateType = strawberry_django.field()
    power_port_template_list: OffsetPaginated[PowerPortTemplateType] = strawberry_django.offset_paginated()

    rack_type: RackTypeType = strawberry_django.field()
    rack_type_list: OffsetPaginated[RackTypeType] = strawberry_django.offset_paginated()

    rack: RackType = strawberry_django.field()
    rack_list: OffsetPaginated[RackType] = strawberry_django.offset_paginated()

    rack_reservation: RackReservationType = strawberry_django.field()
    rack_reservation_list: OffsetPaginated[RackReservationType] = strawberry_django.offset_paginated()

    rack_role: RackRoleType = strawberry_django.field()
    rack_role_list: OffsetPaginated[RackRoleType] = strawberry_django.offset_paginated()

    rear_port: RearPortType = strawberry_django.field()
    rear_port_list: OffsetPaginated[RearPortType] = strawberry_django.offset_paginated()

    rear_port_template: RearPortTemplateType = strawberry_django.field()
    rear_port_template_list: OffsetPaginated[RearPortTemplateType] = strawberry_django.offset_paginated()

    region: RegionType = strawberry_django.field()
    region_list: OffsetPaginated[RegionType] = strawberry_django.offset_paginated()

    site: SiteType = strawberry_django.field()
    site_list: OffsetPaginated[SiteType] = strawberry_django.offset_paginated()

    site_group: SiteGroupType = strawberry_django.field()
    site_group_list: OffsetPaginated[SiteGroupType] = strawberry_django.offset_paginated()

    virtual_chassis: VirtualChassisType = strawberry_django.field()
    virtual_chassis_list: OffsetPaginated[VirtualChassisType] = strawberry_django.offset_paginated()

    virtual_device_context: VirtualDeviceContextType = strawberry_django.field()
    virtual_device_context_list: OffsetPaginated[VirtualDeviceContextType] = strawberry_django.offset_paginated()
