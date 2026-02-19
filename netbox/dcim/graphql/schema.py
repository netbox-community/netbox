import strawberry
import strawberry_django

from .types import *


@strawberry.type(name="Query")
class DCIMQuery:
    cable: CableType = strawberry_django.field()
    cable_list: list[CableType] = strawberry_django.field()

    console_port: ConsolePortType = strawberry_django.field()
    console_port_list: list[ConsolePortType] = strawberry_django.field()

    console_port_template: ConsolePortTemplateType = strawberry_django.field()
    console_port_template_list: list[ConsolePortTemplateType] = strawberry_django.field()

    console_server_port: ConsoleServerPortType = strawberry_django.field()
    console_server_port_list: list[ConsoleServerPortType] = strawberry_django.field()

    console_server_port_template: ConsoleServerPortTemplateType = strawberry_django.field()
    console_server_port_template_list: list[ConsoleServerPortTemplateType] = strawberry_django.field()

    device: DeviceType = strawberry_django.field()
    device_list: list[DeviceType] = strawberry_django.field()

    device_bay: DeviceBayType = strawberry_django.field()
    device_bay_list: list[DeviceBayType] = strawberry_django.field()

    device_bay_template: DeviceBayTemplateType = strawberry_django.field()
    device_bay_template_list: list[DeviceBayTemplateType] = strawberry_django.field()

    device_role: DeviceRoleType = strawberry_django.field()
    device_role_list: list[DeviceRoleType] = strawberry_django.field()

    device_type: DeviceTypeType = strawberry_django.field()
    device_type_list: list[DeviceTypeType] = strawberry_django.field()

    front_port: FrontPortType = strawberry_django.field()
    front_port_list: list[FrontPortType] = strawberry_django.field()

    front_port_template: FrontPortTemplateType = strawberry_django.field()
    front_port_template_list: list[FrontPortTemplateType] = strawberry_django.field()

    mac_address: MACAddressType = strawberry_django.field()
    mac_address_list: list[MACAddressType] = strawberry_django.field()

    interface: InterfaceType = strawberry_django.field()
    interface_list: list[InterfaceType] = strawberry_django.field()

    interface_template: InterfaceTemplateType = strawberry_django.field()
    interface_template_list: list[InterfaceTemplateType] = strawberry_django.field()

    inventory_item: InventoryItemType = strawberry_django.field()
    inventory_item_list: list[InventoryItemType] = strawberry_django.field()

    inventory_item_role: InventoryItemRoleType = strawberry_django.field()
    inventory_item_role_list: list[InventoryItemRoleType] = strawberry_django.field()

    inventory_item_template: InventoryItemTemplateType = strawberry_django.field()
    inventory_item_template_list: list[InventoryItemTemplateType] = strawberry_django.field()

    location: LocationType = strawberry_django.field()
    location_list: list[LocationType] = strawberry_django.field()

    manufacturer: ManufacturerType = strawberry_django.field()
    manufacturer_list: list[ManufacturerType] = strawberry_django.field()

    module: ModuleType = strawberry_django.field()
    module_list: list[ModuleType] = strawberry_django.field()

    module_bay: ModuleBayType = strawberry_django.field()
    module_bay_list: list[ModuleBayType] = strawberry_django.field()

    module_bay_template: ModuleBayTemplateType = strawberry_django.field()
    module_bay_template_list: list[ModuleBayTemplateType] = strawberry_django.field()

    module_type_profile: ModuleTypeProfileType = strawberry_django.field()
    module_type_profile_list: list[ModuleTypeProfileType] = strawberry_django.field()

    module_type: ModuleTypeType = strawberry_django.field()
    module_type_list: list[ModuleTypeType] = strawberry_django.field()

    platform: PlatformType = strawberry_django.field()
    platform_list: list[PlatformType] = strawberry_django.field()

    power_feed: PowerFeedType = strawberry_django.field()
    power_feed_list: list[PowerFeedType] = strawberry_django.field()

    power_outlet: PowerOutletType = strawberry_django.field()
    power_outlet_list: list[PowerOutletType] = strawberry_django.field()

    power_outlet_template: PowerOutletTemplateType = strawberry_django.field()
    power_outlet_template_list: list[PowerOutletTemplateType] = strawberry_django.field()

    power_panel: PowerPanelType = strawberry_django.field()
    power_panel_list: list[PowerPanelType] = strawberry_django.field()

    power_port: PowerPortType = strawberry_django.field()
    power_port_list: list[PowerPortType] = strawberry_django.field()

    power_port_template: PowerPortTemplateType = strawberry_django.field()
    power_port_template_list: list[PowerPortTemplateType] = strawberry_django.field()

    rack_type: RackTypeType = strawberry_django.field()
    rack_type_list: list[RackTypeType] = strawberry_django.field()

    rack: RackType = strawberry_django.field()
    rack_list: list[RackType] = strawberry_django.field()

    rack_reservation: RackReservationType = strawberry_django.field()
    rack_reservation_list: list[RackReservationType] = strawberry_django.field()

    rack_role: RackRoleType = strawberry_django.field()
    rack_role_list: list[RackRoleType] = strawberry_django.field()

    rear_port: RearPortType = strawberry_django.field()
    rear_port_list: list[RearPortType] = strawberry_django.field()

    rear_port_template: RearPortTemplateType = strawberry_django.field()
    rear_port_template_list: list[RearPortTemplateType] = strawberry_django.field()

    region: RegionType = strawberry_django.field()
    region_list: list[RegionType] = strawberry_django.field()

    site: SiteType = strawberry_django.field()
    site_list: list[SiteType] = strawberry_django.field()

    site_group: SiteGroupType = strawberry_django.field()
    site_group_list: list[SiteGroupType] = strawberry_django.field()

    virtual_chassis: VirtualChassisType = strawberry_django.field()
    virtual_chassis_list: list[VirtualChassisType] = strawberry_django.field()

    virtual_device_context: VirtualDeviceContextType = strawberry_django.field()
    virtual_device_context_list: list[VirtualDeviceContextType] = strawberry_django.field()
