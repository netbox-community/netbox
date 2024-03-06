from typing import List
import strawberry
import strawberry_django

from circuits import models
from .types import *


@strawberry.type
class DCIMQuery:
    @strawberry.field
    def cable(self, id: int) -> CableType:
        return models.Cable.objects.get(id=id)
    cable_list: List[CableType] = strawberry_django.field()

    @strawberry.field
    def console_port(self, id: int) -> ConsolePortType:
        return models.ConsolePort.objects.get(id=id)
    console_port_list: List[ConsolePortType] = strawberry_django.field()

    @strawberry.field
    def console_port_template(self, id: int) -> ConsolePortTemplateType:
        return models.ConsolePortTemplate.objects.get(id=id)
    console_port_template_list: List[ConsolePortTemplateType] = strawberry_django.field()

    @strawberry.field
    def console_server_port(self, id: int) -> ConsoleServerPortType:
        return models.ConsoleServerPort.objects.get(id=id)
    console_server_port_list: List[ConsoleServerPortType] = strawberry_django.field()

    @strawberry.field
    def console_server_port_template(self, id: int) -> ConsoleServerPortTemplateType:
        return models.ConsoleServerPortTemplate.objects.get(id=id)
    console_server_port_template_list: List[ConsoleServerPortTemplateType] = strawberry_django.field()

    @strawberry.field
    def device(self, id: int) -> DeviceType:
        return models.Device.objects.get(id=id)
    device_list: List[DeviceType] = strawberry_django.field()

    @strawberry.field
    def device_bay(self, id: int) -> DeviceBayType:
        return models.DeviceBay.objects.get(id=id)
    device_bay_list: List[DeviceBayType] = strawberry_django.field()

    @strawberry.field
    def device_bay_template(self, id: int) -> DeviceBayTemplateType:
        return models.DeviceBayTemplate.objects.get(id=id)
    device_bay_template_list: List[DeviceBayTemplateType] = strawberry_django.field()

    @strawberry.field
    def device_role(self, id: int) -> DeviceRoleType:
        return models.DeviceRole.objects.get(id=id)
    device_role_list: List[DeviceRoleType] = strawberry_django.field()

    @strawberry.field
    def device_type(self, id: int) -> DeviceTypeType:
        return models.DeviceType.objects.get(id=id)
    device_type_list: List[DeviceTypeType] = strawberry_django.field()

    @strawberry.field
    def front_port(self, id: int) -> FrontPortType:
        return models.FrontPort.objects.get(id=id)
    front_port_list: List[FrontPortType] = strawberry_django.field()

    @strawberry.field
    def front_port_template(self, id: int) -> FrontPortTemplateType:
        return models.FrontPortTemplate.objects.get(id=id)
    front_port_template_list: List[FrontPortTemplateType] = strawberry_django.field()

    @strawberry.field
    def interface(self, id: int) -> InterfaceType:
        return models.Interface.objects.get(id=id)
    interface_list: List[InterfaceType] = strawberry_django.field()

    @strawberry.field
    def interface_template(self, id: int) -> InterfaceTemplateType:
        return models.InterfaceTemplate.objects.get(id=id)
    interface_template_list: List[InterfaceTemplateType] = strawberry_django.field()

    @strawberry.field
    def inventory_item(self, id: int) -> InventoryItemType:
        return models.InventoryItem.objects.get(id=id)
    inventory_item_list: List[InventoryItemType] = strawberry_django.field()

    @strawberry.field
    def inventory_item_role(self, id: int) -> InventoryItemRoleType:
        return models.InventoryItemRole.objects.get(id=id)
    inventory_item_role_list: List[InventoryItemRoleType] = strawberry_django.field()

    @strawberry.field
    def inventory_item_template(self, id: int) -> InventoryItemTemplateType:
        return models.InventoryItemTemplate.objects.get(id=id)
    inventory_item_template_list: List[InventoryItemTemplateType] = strawberry_django.field()

    @strawberry.field
    def location(self, id: int) -> LocationType:
        return models.Location.objects.get(id=id)
    location_list: List[LocationType] = strawberry_django.field()

    @strawberry.field
    def manufacturer(self, id: int) -> ManufacturerType:
        return models.Manufacturer.objects.get(id=id)
    manufacturer_list: List[ManufacturerType] = strawberry_django.field()

    @strawberry.field
    def module(self, id: int) -> ModuleType:
        return models.Module.objects.get(id=id)
    module_list: List[ModuleType] = strawberry_django.field()

    @strawberry.field
    def module_bay(self, id: int) -> ModuleBayType:
        return models.ModuleBay.objects.get(id=id)
    module_bay_list: List[ModuleBayType] = strawberry_django.field()

    @strawberry.field
    def module_bay_template(self, id: int) -> ModuleBayTemplateType:
        return models.ModuleBayTemplate.objects.get(id=id)
    module_bay_template_list: List[ModuleBayTemplateType] = strawberry_django.field()

    @strawberry.field
    def module_type(self, id: int) -> ModuleTypeType:
        return models.ModuleType.objects.get(id=id)
    module_type_list: List[ModuleTypeType] = strawberry_django.field()

    @strawberry.field
    def platform(self, id: int) -> PlatformType:
        return models.Platform.objects.get(id=id)
    platform_list: List[PlatformType] = strawberry_django.field()

    @strawberry.field
    def power_feed(self, id: int) -> PowerFeedType:
        return models.PowerFeed.objects.get(id=id)
    power_feed_list: List[PowerFeedType] = strawberry_django.field()

    @strawberry.field
    def power_outlet(self, id: int) -> PowerOutletType:
        return models.PowerOutlet.objects.get(id=id)
    power_outlet_list: List[PowerOutletType] = strawberry_django.field()

    @strawberry.field
    def power_outlet_template(self, id: int) -> PowerOutletTemplateType:
        return models.PowerOutletTemplate.objects.get(id=id)
    power_outlet_template_list: List[PowerOutletTemplateType] = strawberry_django.field()

    @strawberry.field
    def power_panel(self, id: int) -> PowerPanelType:
        return models.PowerPanel.objects.get(id=id)
    power_panel_list: List[PowerPanelType] = strawberry_django.field()

    @strawberry.field
    def power_port(self, id: int) -> PowerPortType:
        return models.PowerPort.objects.get(id=id)
    power_port_list: List[PowerPortType] = strawberry_django.field()

    @strawberry.field
    def power_port_template(self, id: int) -> PowerPortTemplateType:
        return models.PowerPortTemplate.objects.get(id=id)
    power_port_template_list: List[PowerPortTemplateType] = strawberry_django.field()

    @strawberry.field
    def rack(self, id: int) -> RackType:
        return models.Rack.objects.get(id=id)
    rack_list: List[RackType] = strawberry_django.field()

    @strawberry.field
    def rack_reservation(self, id: int) -> RackReservationType:
        return models.RackReservation.objects.get(id=id)
    rack_reservation_list: List[RackReservationType] = strawberry_django.field()

    @strawberry.field
    def rack_role(self, id: int) -> RackRoleType:
        return models.RackRole.objects.get(id=id)
    rack_role_list: List[RackRoleType] = strawberry_django.field()

    @strawberry.field
    def rear_port(self, id: int) -> RearPortType:
        return models.RearPort.objects.get(id=id)
    rear_port_list: List[RearPortType] = strawberry_django.field()

    @strawberry.field
    def rear_port_template(self, id: int) -> RearPortTemplateType:
        return models.RearPortTemplate.objects.get(id=id)
    rear_port_template_list: List[RearPortTemplateType] = strawberry_django.field()

    @strawberry.field
    def region(self, id: int) -> RegionType:
        return models.Region.objects.get(id=id)
    region_list: List[RegionType] = strawberry_django.field()

    @strawberry.field
    def site(self, id: int) -> SiteType:
        return models.Site.objects.get(id=id)
    site_list: List[SiteType] = strawberry_django.field()

    @strawberry.field
    def site_group(self, id: int) -> SiteGroupType:
        return models.SiteGroup.objects.get(id=id)
    site_group_list: List[SiteGroupType] = strawberry_django.field()

    @strawberry.field
    def virtual_chassis(self, id: int) -> VirtualChassisType:
        return models.VirtualChassis.objects.get(id=id)
    virtual_chassis_list: List[VirtualChassisType] = strawberry_django.field()

    @strawberry.field
    def virtual_device_context(self, id: int) -> VirtualDeviceContextType:
        return models.VirtualDeviceContext.objects.get(id=id)
    virtual_device_context_list: List[VirtualDeviceContextType] = strawberry_django.field()
