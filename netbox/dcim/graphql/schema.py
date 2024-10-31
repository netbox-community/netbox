from typing import List

import strawberry
import strawberry_django

from .types import *


@strawberry.type(name="Query")
class DCIMQuery:
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
