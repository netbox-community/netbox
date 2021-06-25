import graphene

from netbox.graphql.fields import ObjectField, ObjectListField
from .types import *


class DCIMQuery(graphene.ObjectType):
    cable = ObjectField(CableType)
    cables = ObjectListField(CableType)

    console_port = ObjectField(ConsolePortType)
    console_ports = ObjectListField(ConsolePortType)

    console_port_template = ObjectField(ConsolePortTemplateType)
    console_port_templates = ObjectListField(ConsolePortTemplateType)

    console_server_port = ObjectField(ConsoleServerPortType)
    console_server_ports = ObjectListField(ConsoleServerPortType)

    console_server_port_template = ObjectField(ConsoleServerPortTemplateType)
    console_server_port_templates = ObjectListField(ConsoleServerPortTemplateType)

    device = ObjectField(DeviceType)
    devices = ObjectListField(DeviceType)

    device_bay = ObjectField(DeviceBayType)
    device_bays = ObjectListField(DeviceBayType)

    device_bay_template = ObjectField(DeviceBayTemplateType)
    device_bay_templates = ObjectListField(DeviceBayTemplateType)

    device_role = ObjectField(DeviceRoleType)
    device_roles = ObjectListField(DeviceRoleType)

    device_type = ObjectField(DeviceTypeType)
    device_types = ObjectListField(DeviceTypeType)

    front_port = ObjectField(FrontPortType)
    front_ports = ObjectListField(FrontPortType)

    front_port_template = ObjectField(FrontPortTemplateType)
    front_port_templates = ObjectListField(FrontPortTemplateType)

    interface = ObjectField(InterfaceType)
    interfaces = ObjectListField(InterfaceType)

    interface_template = ObjectField(InterfaceTemplateType)
    interface_templates = ObjectListField(InterfaceTemplateType)

    inventory_item = ObjectField(InventoryItemType)
    inventory_items = ObjectListField(InventoryItemType)

    location = ObjectField(LocationType)
    locations = ObjectListField(LocationType)

    manufacturer = ObjectField(ManufacturerType)
    manufacturers = ObjectListField(ManufacturerType)

    platform = ObjectField(PlatformType)
    platforms = ObjectListField(PlatformType)

    power_feed = ObjectField(PowerFeedType)
    power_feeds = ObjectListField(PowerFeedType)

    power_outlet = ObjectField(PowerOutletType)
    power_outlets = ObjectListField(PowerOutletType)

    power_outlet_template = ObjectField(PowerOutletTemplateType)
    power_outlet_templates = ObjectListField(PowerOutletTemplateType)

    power_panel = ObjectField(PowerPanelType)
    power_panels = ObjectListField(PowerPanelType)

    power_port = ObjectField(PowerPortType)
    power_ports = ObjectListField(PowerPortType)

    power_port_template = ObjectField(PowerPortTemplateType)
    power_port_templates = ObjectListField(PowerPortTemplateType)

    rack = ObjectField(RackType)
    racks = ObjectListField(RackType)

    rack_reservation = ObjectField(RackReservationType)
    rack_reservations = ObjectListField(RackReservationType)

    rack_role = ObjectField(RackRoleType)
    rack_roles = ObjectListField(RackRoleType)

    rear_port = ObjectField(RearPortType)
    rear_ports = ObjectListField(RearPortType)

    rear_port_template = ObjectField(RearPortTemplateType)
    rear_port_templates = ObjectListField(RearPortTemplateType)

    region = ObjectField(RegionType)
    regions = ObjectListField(RegionType)

    site = ObjectField(SiteType)
    sites = ObjectListField(SiteType)

    site_group = ObjectField(SiteGroupType)
    site_groups = ObjectListField(SiteGroupType)

    virtual_chassis = ObjectField(VirtualChassisType)
    # TODO: Rectify list field name
    virtual_chassis_list = ObjectListField(VirtualChassisType)
