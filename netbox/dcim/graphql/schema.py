import graphene

from netbox.graphql.fields import ObjectField, ObjectListField
from .types import *
from dcim import models
from .types import VirtualDeviceContextType
from utilities.graphql_optimizer import gql_query_optimizer


class DCIMQuery(graphene.ObjectType):
    cable = ObjectField(CableType)
    cable_list = ObjectListField(CableType)

    def resolve_cable_list(root, info, **kwargs):
        return gql_query_optimizer(models.Cable.objects.all(), info)

    console_port = ObjectField(ConsolePortType)
    console_port_list = ObjectListField(ConsolePortType)

    def resolve_console_port_list(root, info, **kwargs):
        return gql_query_optimizer(models.ConsolePort.objects.all(), info)

    console_port_template = ObjectField(ConsolePortTemplateType)
    console_port_template_list = ObjectListField(ConsolePortTemplateType)

    def resolve_console_port_template_list(root, info, **kwargs):
        return gql_query_optimizer(models.ConsolePortTemplate.objects.all(), info)

    console_server_port = ObjectField(ConsoleServerPortType)
    console_server_port_list = ObjectListField(ConsoleServerPortType)

    def resolve_console_server_port_list(root, info, **kwargs):
        return gql_query_optimizer(models.ConsoleServerPort.objects.all(), info)

    console_server_port_template = ObjectField(ConsoleServerPortTemplateType)
    console_server_port_template_list = ObjectListField(ConsoleServerPortTemplateType)

    def resolve_console_server_port_template_list(root, info, **kwargs):
        return gql_query_optimizer(models.ConsoleServerPortTemplate.objects.all(), info)

    device = ObjectField(DeviceType)
    device_list = ObjectListField(DeviceType)

    def resolve_device_list(root, info, **kwargs):
        return gql_query_optimizer(models.Device.objects.all(), info)

    device_bay = ObjectField(DeviceBayType)
    device_bay_list = ObjectListField(DeviceBayType)

    def resolve_device_bay_list(root, info, **kwargs):
        return gql_query_optimizer(models.DeviceBay.objects.all(), info)

    device_bay_template = ObjectField(DeviceBayTemplateType)
    device_bay_template_list = ObjectListField(DeviceBayTemplateType)

    def resolve_device_bay_template_list(root, info, **kwargs):
        return gql_query_optimizer(models.DeviceBayTemplate.objects.all(), info)

    device_role = ObjectField(DeviceRoleType)
    device_role_list = ObjectListField(DeviceRoleType)

    def resolve_device_role_list(root, info, **kwargs):
        return gql_query_optimizer(models.DeviceRole.objects.all(), info)

    device_type = ObjectField(DeviceTypeType)
    device_type_list = ObjectListField(DeviceTypeType)

    def resolve_device_type_list(root, info, **kwargs):
        return gql_query_optimizer(models.DeviceType.objects.all(), info)

    front_port = ObjectField(FrontPortType)
    front_port_list = ObjectListField(FrontPortType)

    def resolve_front_port_list(root, info, **kwargs):
        return gql_query_optimizer(models.FrontPort.objects.all(), info)

    front_port_template = ObjectField(FrontPortTemplateType)
    front_port_template_list = ObjectListField(FrontPortTemplateType)

    def resolve_front_port_template_list(root, info, **kwargs):
        return gql_query_optimizer(models.FrontPortTemplate.objects.all(), info)

    interface = ObjectField(InterfaceType)
    interface_list = ObjectListField(InterfaceType)

    def resolve_interface_list(root, info, **kwargs):
        return gql_query_optimizer(models.Interface.objects.all(), info)

    interface_template = ObjectField(InterfaceTemplateType)
    interface_template_list = ObjectListField(InterfaceTemplateType)

    def resolve_interface_template_list(root, info, **kwargs):
        return gql_query_optimizer(models.InterfaceTemplate.objects.all(), info)

    inventory_item = ObjectField(InventoryItemType)
    inventory_item_list = ObjectListField(InventoryItemType)

    def resolve_inventory_item_list(root, info, **kwargs):
        return gql_query_optimizer(models.InventoryItem.objects.all(), info)

    inventory_item_role = ObjectField(InventoryItemRoleType)
    inventory_item_role_list = ObjectListField(InventoryItemRoleType)

    def resolve_inventory_item_role_list(root, info, **kwargs):
        return gql_query_optimizer(models.InventoryItemRole.objects.all(), info)

    inventory_item_template = ObjectField(InventoryItemTemplateType)
    inventory_item_template_list = ObjectListField(InventoryItemTemplateType)

    def resolve_inventory_item_template_list(root, info, **kwargs):
        return gql_query_optimizer(models.InventoryItemTemplate.objects.all(), info)

    location = ObjectField(LocationType)
    location_list = ObjectListField(LocationType)

    def resolve_location_list(root, info, **kwargs):
        return gql_query_optimizer(models.Location.objects.all(), info)

    manufacturer = ObjectField(ManufacturerType)
    manufacturer_list = ObjectListField(ManufacturerType)

    def resolve_manufacturer_list(root, info, **kwargs):
        return gql_query_optimizer(models.Manufacturer.objects.all(), info)

    module = ObjectField(ModuleType)
    module_list = ObjectListField(ModuleType)

    def resolve_module_list(root, info, **kwargs):
        return gql_query_optimizer(models.Module.objects.all(), info)

    module_bay = ObjectField(ModuleBayType)
    module_bay_list = ObjectListField(ModuleBayType)

    def resolve_module_bay_list(root, info, **kwargs):
        return gql_query_optimizer(models.ModuleBay.objects.all(), info)

    module_bay_template = ObjectField(ModuleBayTemplateType)
    module_bay_template_list = ObjectListField(ModuleBayTemplateType)

    def resolve_module_bay_template_list(root, info, **kwargs):
        return gql_query_optimizer(models.ModuleBayTemplate.objects.all(), info)

    module_type = ObjectField(ModuleTypeType)
    module_type_list = ObjectListField(ModuleTypeType)

    def resolve_module_type_list(root, info, **kwargs):
        return gql_query_optimizer(models.ModuleType.objects.all(), info)

    platform = ObjectField(PlatformType)
    platform_list = ObjectListField(PlatformType)

    def resolve_platform_list(root, info, **kwargs):
        return gql_query_optimizer(models.Platform.objects.all(), info)

    power_feed = ObjectField(PowerFeedType)
    power_feed_list = ObjectListField(PowerFeedType)

    def resolve_power_feed_list(root, info, **kwargs):
        return gql_query_optimizer(models.PowerFeed.objects.all(), info)

    power_outlet = ObjectField(PowerOutletType)
    power_outlet_list = ObjectListField(PowerOutletType)

    def resolve_power_outlet_list(root, info, **kwargs):
        return gql_query_optimizer(models.PowerOutlet.objects.all(), info)

    power_outlet_template = ObjectField(PowerOutletTemplateType)
    power_outlet_template_list = ObjectListField(PowerOutletTemplateType)

    def resolve_power_outlet_template_list(root, info, **kwargs):
        return gql_query_optimizer(models.PowerOutletTemplate.objects.all(), info)

    power_panel = ObjectField(PowerPanelType)
    power_panel_list = ObjectListField(PowerPanelType)

    def resolve_power_panel_list(root, info, **kwargs):
        return gql_query_optimizer(models.PowerPanel.objects.all(), info)

    power_port = ObjectField(PowerPortType)
    power_port_list = ObjectListField(PowerPortType)

    def resolve_power_port_list(root, info, **kwargs):
        return gql_query_optimizer(models.PowerPort.objects.all(), info)

    power_port_template = ObjectField(PowerPortTemplateType)
    power_port_template_list = ObjectListField(PowerPortTemplateType)

    def resolve_power_port_template_list(root, info, **kwargs):
        return gql_query_optimizer(models.PowerPortTemplate.objects.all(), info)

    rack = ObjectField(RackType)
    rack_list = ObjectListField(RackType)

    def resolve_rack_list(root, info, **kwargs):
        return gql_query_optimizer(models.Rack.objects.all(), info)

    rack_reservation = ObjectField(RackReservationType)
    rack_reservation_list = ObjectListField(RackReservationType)

    def resolve_rack_reservation_list(root, info, **kwargs):
        return gql_query_optimizer(models.RackReservation.objects.all(), info)

    rack_role = ObjectField(RackRoleType)
    rack_role_list = ObjectListField(RackRoleType)

    def resolve_rack_role_list(root, info, **kwargs):
        return gql_query_optimizer(models.RackRole.objects.all(), info)

    rear_port = ObjectField(RearPortType)
    rear_port_list = ObjectListField(RearPortType)

    def resolve_rear_port_list(root, info, **kwargs):
        return gql_query_optimizer(models.RearPort.objects.all(), info)

    rear_port_template = ObjectField(RearPortTemplateType)
    rear_port_template_list = ObjectListField(RearPortTemplateType)

    def resolve_rear_port_template_list(root, info, **kwargs):
        return gql_query_optimizer(models.RearPortTemplate.objects.all(), info)

    region = ObjectField(RegionType)
    region_list = ObjectListField(RegionType)

    def resolve_region_list(root, info, **kwargs):
        return gql_query_optimizer(models.Region.objects.all(), info)

    site = ObjectField(SiteType)
    site_list = ObjectListField(SiteType)

    def resolve_site_list(root, info, **kwargs):
        return gql_query_optimizer(models.Site.objects.all(), info)

    site_group = ObjectField(SiteGroupType)
    site_group_list = ObjectListField(SiteGroupType)

    def resolve_site_group_list(root, info, **kwargs):
        return gql_query_optimizer(models.SiteGroup.objects.all(), info)

    virtual_chassis = ObjectField(VirtualChassisType)
    virtual_chassis_list = ObjectListField(VirtualChassisType)

    def resolve_virtual_chassis_list(root, info, **kwargs):
        return gql_query_optimizer(models.VirtualChassis.objects.all(), info)

    virtual_device_context = ObjectField(VirtualDeviceContextType)
    virtual_device_context_list = ObjectListField(VirtualDeviceContextType)

    def resolve_virtual_device_context_list(root, info, **kwargs):
        return gql_query_optimizer(models.VirtualDeviceContext.objects.all(), info)
