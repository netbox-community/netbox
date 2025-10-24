from typing import List

import strawberry
import strawberry_django

from .types_v1 import *


@strawberry.type(name="Query")
class DCIMQueryV1:
    cable: CableTypeV1 = strawberry_django.field()
    cable_list: List[CableTypeV1] = strawberry_django.field()

    console_port: ConsolePortTypeV1 = strawberry_django.field()
    console_port_list: List[ConsolePortTypeV1] = strawberry_django.field()

    console_port_template: ConsolePortTemplateTypeV1 = strawberry_django.field()
    console_port_template_list: List[ConsolePortTemplateTypeV1] = strawberry_django.field()

    console_server_port: ConsoleServerPortTypeV1 = strawberry_django.field()
    console_server_port_list: List[ConsoleServerPortTypeV1] = strawberry_django.field()

    console_server_port_template: ConsoleServerPortTemplateTypeV1 = strawberry_django.field()
    console_server_port_template_list: List[ConsoleServerPortTemplateTypeV1] = strawberry_django.field()

    device: DeviceTypeV1 = strawberry_django.field()
    device_list: List[DeviceTypeV1] = strawberry_django.field()

    device_bay: DeviceBayTypeV1 = strawberry_django.field()
    device_bay_list: List[DeviceBayTypeV1] = strawberry_django.field()

    device_bay_template: DeviceBayTemplateTypeV1 = strawberry_django.field()
    device_bay_template_list: List[DeviceBayTemplateTypeV1] = strawberry_django.field()

    device_role: DeviceRoleTypeV1 = strawberry_django.field()
    device_role_list: List[DeviceRoleTypeV1] = strawberry_django.field()

    device_type: DeviceTypeTypeV1 = strawberry_django.field()
    device_type_list: List[DeviceTypeTypeV1] = strawberry_django.field()

    front_port: FrontPortTypeV1 = strawberry_django.field()
    front_port_list: List[FrontPortTypeV1] = strawberry_django.field()

    front_port_template: FrontPortTemplateTypeV1 = strawberry_django.field()
    front_port_template_list: List[FrontPortTemplateTypeV1] = strawberry_django.field()

    mac_address: MACAddressTypeV1 = strawberry_django.field()
    mac_address_list: List[MACAddressTypeV1] = strawberry_django.field()

    interface: InterfaceTypeV1 = strawberry_django.field()
    interface_list: List[InterfaceTypeV1] = strawberry_django.field()

    interface_template: InterfaceTemplateTypeV1 = strawberry_django.field()
    interface_template_list: List[InterfaceTemplateTypeV1] = strawberry_django.field()

    inventory_item: InventoryItemTypeV1 = strawberry_django.field()
    inventory_item_list: List[InventoryItemTypeV1] = strawberry_django.field()

    inventory_item_role: InventoryItemRoleTypeV1 = strawberry_django.field()
    inventory_item_role_list: List[InventoryItemRoleTypeV1] = strawberry_django.field()

    inventory_item_template: InventoryItemTemplateTypeV1 = strawberry_django.field()
    inventory_item_template_list: List[InventoryItemTemplateTypeV1] = strawberry_django.field()

    location: LocationTypeV1 = strawberry_django.field()
    location_list: List[LocationTypeV1] = strawberry_django.field()

    manufacturer: ManufacturerTypeV1 = strawberry_django.field()
    manufacturer_list: List[ManufacturerTypeV1] = strawberry_django.field()

    module: ModuleTypeV1 = strawberry_django.field()
    module_list: List[ModuleTypeV1] = strawberry_django.field()

    module_bay: ModuleBayTypeV1 = strawberry_django.field()
    module_bay_list: List[ModuleBayTypeV1] = strawberry_django.field()

    module_bay_template: ModuleBayTemplateTypeV1 = strawberry_django.field()
    module_bay_template_list: List[ModuleBayTemplateTypeV1] = strawberry_django.field()

    module_type_profile: ModuleTypeProfileTypeV1 = strawberry_django.field()
    module_type_profile_list: List[ModuleTypeProfileTypeV1] = strawberry_django.field()

    module_type: ModuleTypeTypeV1 = strawberry_django.field()
    module_type_list: List[ModuleTypeTypeV1] = strawberry_django.field()

    platform: PlatformTypeV1 = strawberry_django.field()
    platform_list: List[PlatformTypeV1] = strawberry_django.field()

    power_feed: PowerFeedTypeV1 = strawberry_django.field()
    power_feed_list: List[PowerFeedTypeV1] = strawberry_django.field()

    power_outlet: PowerOutletTypeV1 = strawberry_django.field()
    power_outlet_list: List[PowerOutletTypeV1] = strawberry_django.field()

    power_outlet_template: PowerOutletTemplateTypeV1 = strawberry_django.field()
    power_outlet_template_list: List[PowerOutletTemplateTypeV1] = strawberry_django.field()

    power_panel: PowerPanelTypeV1 = strawberry_django.field()
    power_panel_list: List[PowerPanelTypeV1] = strawberry_django.field()

    power_port: PowerPortTypeV1 = strawberry_django.field()
    power_port_list: List[PowerPortTypeV1] = strawberry_django.field()

    power_port_template: PowerPortTemplateTypeV1 = strawberry_django.field()
    power_port_template_list: List[PowerPortTemplateTypeV1] = strawberry_django.field()

    rack_type: RackTypeTypeV1 = strawberry_django.field()
    rack_type_list: List[RackTypeTypeV1] = strawberry_django.field()

    rack: RackTypeV1 = strawberry_django.field()
    rack_list: List[RackTypeV1] = strawberry_django.field()

    rack_reservation: RackReservationTypeV1 = strawberry_django.field()
    rack_reservation_list: List[RackReservationTypeV1] = strawberry_django.field()

    rack_role: RackRoleTypeV1 = strawberry_django.field()
    rack_role_list: List[RackRoleTypeV1] = strawberry_django.field()

    rear_port: RearPortTypeV1 = strawberry_django.field()
    rear_port_list: List[RearPortTypeV1] = strawberry_django.field()

    rear_port_template: RearPortTemplateTypeV1 = strawberry_django.field()
    rear_port_template_list: List[RearPortTemplateTypeV1] = strawberry_django.field()

    region: RegionTypeV1 = strawberry_django.field()
    region_list: List[RegionTypeV1] = strawberry_django.field()

    site: SiteTypeV1 = strawberry_django.field()
    site_list: List[SiteTypeV1] = strawberry_django.field()

    site_group: SiteGroupTypeV1 = strawberry_django.field()
    site_group_list: List[SiteGroupTypeV1] = strawberry_django.field()

    virtual_chassis: VirtualChassisTypeV1 = strawberry_django.field()
    virtual_chassis_list: List[VirtualChassisTypeV1] = strawberry_django.field()

    virtual_device_context: VirtualDeviceContextTypeV1 = strawberry_django.field()
    virtual_device_context_list: List[VirtualDeviceContextTypeV1] = strawberry_django.field()
