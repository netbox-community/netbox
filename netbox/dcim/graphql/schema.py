import graphene

from netbox.graphql.fields import ObjectField, ObjectListField
from .types import *


class DCIMQuery(graphene.ObjectType):
    cable = ObjectField(CableType)
    cable_list = ObjectListField(CableType)

    console_port = ObjectField(ConsolePortType)
    console_port_list = ObjectListField(ConsolePortType)

    console_port_template = ObjectField(ConsolePortTemplateType)
    console_port_template_list = ObjectListField(ConsolePortTemplateType)

    console_server_port = ObjectField(ConsoleServerPortType)
    console_server_port_list = ObjectListField(ConsoleServerPortType)

    console_server_port_template = ObjectField(ConsoleServerPortTemplateType)
    console_server_port_template_list = ObjectListField(ConsoleServerPortTemplateType)

    device = ObjectField(DeviceType)
    device_list = ObjectListField(DeviceType)

    device_bay = ObjectField(DeviceBayType)
    device_bay_list = ObjectListField(DeviceBayType)

    device_bay_template = ObjectField(DeviceBayTemplateType)
    device_bay_template_list = ObjectListField(DeviceBayTemplateType)

    device_role = ObjectField(DeviceRoleType)
    device_role_list = ObjectListField(DeviceRoleType)

    device_type = ObjectField(DeviceTypeType)
    device_type_list = ObjectListField(DeviceTypeType)

    front_port = ObjectField(FrontPortType)
    front_port_list = ObjectListField(FrontPortType)

    front_port_template = ObjectField(FrontPortTemplateType)
    front_port_template_list = ObjectListField(FrontPortTemplateType)

    interface = ObjectField(InterfaceType)
    interface_list = ObjectListField(InterfaceType)

    interface_template = ObjectField(InterfaceTemplateType)
    interface_template_list = ObjectListField(InterfaceTemplateType)

    inventory_item = ObjectField(InventoryItemType)
    inventory_item_list = ObjectListField(InventoryItemType)

    location = ObjectField(LocationType)
    location_list = ObjectListField(LocationType)

    manufacturer = ObjectField(ManufacturerType)
    manufacturer_list = ObjectListField(ManufacturerType)

    platform = ObjectField(PlatformType)
    platform_list = ObjectListField(PlatformType)

    power_feed = ObjectField(PowerFeedType)
    power_feed_list = ObjectListField(PowerFeedType)

    power_outlet = ObjectField(PowerOutletType)
    power_outlet_list = ObjectListField(PowerOutletType)

    power_outlet_template = ObjectField(PowerOutletTemplateType)
    power_outlet_template_list = ObjectListField(PowerOutletTemplateType)

    power_panel = ObjectField(PowerPanelType)
    power_panel_list = ObjectListField(PowerPanelType)

    power_port = ObjectField(PowerPortType)
    power_port_list = ObjectListField(PowerPortType)

    power_port_template = ObjectField(PowerPortTemplateType)
    power_port_template_list = ObjectListField(PowerPortTemplateType)

    rack = ObjectField(RackType)
    rack_list = ObjectListField(RackType)

    rack_reservation = ObjectField(RackReservationType)
    rack_reservation_list = ObjectListField(RackReservationType)

    rack_role = ObjectField(RackRoleType)
    rack_role_list = ObjectListField(RackRoleType)

    rear_port = ObjectField(RearPortType)
    rear_port_list = ObjectListField(RearPortType)

    rear_port_template = ObjectField(RearPortTemplateType)
    rear_port_template_list = ObjectListField(RearPortTemplateType)

    region = ObjectField(RegionType)
    region_list = ObjectListField(RegionType)

    site = ObjectField(SiteType)
    site_list = ObjectListField(SiteType)

    site_group = ObjectField(SiteGroupType)
    site_group_list = ObjectListField(SiteGroupType)

    virtual_chassis = ObjectField(VirtualChassisType)
    virtual_chassis_list = ObjectListField(VirtualChassisType)
