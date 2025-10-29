from typing import Annotated, TYPE_CHECKING

from django.db.models import Q
import strawberry
import strawberry_django
from strawberry.scalars import ID
from strawberry_django import FilterLookup

from core.graphql.filter_mixins_v1 import ChangeLogFilterMixinV1
from dcim import models
from dcim.constants import *
from dcim.graphql.enums import InterfaceKindEnum
from extras.graphql.filter_mixins_v1 import ConfigContextFilterMixinV1
from netbox.graphql.filter_mixins_v1 import (
    PrimaryModelFilterMixinV1,
    OrganizationalModelFilterMixinV1,
    NestedGroupModelFilterMixinV1,
    ImageAttachmentFilterMixinV1,
    WeightFilterMixinV1,
)
from tenancy.graphql.filter_mixins_v1 import TenancyFilterMixinV1, ContactFilterMixinV1
from .filter_mixins_v1 import (
    CabledObjectModelFilterMixinV1,
    ComponentModelFilterMixinV1,
    ComponentTemplateFilterMixinV1,
    InterfaceBaseFilterMixinV1,
    ModularComponentModelFilterMixinV1,
    ModularComponentTemplateFilterMixinV1,
    RackBaseFilterMixinV1,
    RenderConfigFilterMixinV1,
)

if TYPE_CHECKING:
    from core.graphql.filters_v1 import ContentTypeFilterV1
    from extras.graphql.filters_v1 import ConfigTemplateFilterV1, ImageAttachmentFilterV1
    from ipam.graphql.filters_v1 import (
        ASNFilterV1, FHRPGroupAssignmentFilterV1, IPAddressFilterV1, PrefixFilterV1, VLANGroupFilterV1, VRFFilterV1,
    )
    from netbox.graphql.enums import ColorEnum
    from netbox.graphql.filter_lookups import FloatLookup, IntegerArrayLookup, IntegerLookup, TreeNodeFilter
    from users.graphql.filters_v1 import UserFilterV1
    from virtualization.graphql.filters_v1 import ClusterFilterV1
    from vpn.graphql.filters_v1 import L2VPNFilterV1, TunnelTerminationFilterV1
    from wireless.graphql.enums import WirelessChannelEnum, WirelessRoleEnum
    from wireless.graphql.filters_v1 import WirelessLANFilterV1, WirelessLinkFilterV1
    from .enums import *

__all__ = (
    'CableFilterV1',
    'CableTerminationFilterV1',
    'ConsolePortFilterV1',
    'ConsolePortTemplateFilterV1',
    'ConsoleServerPortFilterV1',
    'ConsoleServerPortTemplateFilterV1',
    'DeviceFilterV1',
    'DeviceBayFilterV1',
    'DeviceBayTemplateFilterV1',
    'DeviceRoleFilterV1',
    'DeviceTypeFilterV1',
    'FrontPortFilterV1',
    'FrontPortTemplateFilterV1',
    'InterfaceFilterV1',
    'InterfaceTemplateFilterV1',
    'InventoryItemFilterV1',
    'InventoryItemRoleFilterV1',
    'InventoryItemTemplateFilterV1',
    'LocationFilterV1',
    'MACAddressFilterV1',
    'ManufacturerFilterV1',
    'ModuleFilterV1',
    'ModuleBayFilterV1',
    'ModuleBayTemplateFilterV1',
    'ModuleTypeFilterV1',
    'ModuleTypeProfileFilterV1',
    'PlatformFilterV1',
    'PowerFeedFilterV1',
    'PowerOutletFilterV1',
    'PowerOutletTemplateFilterV1',
    'PowerPanelFilterV1',
    'PowerPortFilterV1',
    'PowerPortTemplateFilterV1',
    'RackFilterV1',
    'RackReservationFilterV1',
    'RackRoleFilterV1',
    'RackTypeFilterV1',
    'RearPortFilterV1',
    'RearPortTemplateFilterV1',
    'RegionFilterV1',
    'SiteFilterV1',
    'SiteGroupFilterV1',
    'VirtualChassisFilterV1',
    'VirtualDeviceContextFilterV1',
)


@strawberry_django.filter_type(models.Cable, lookups=True)
class CableFilterV1(PrimaryModelFilterMixinV1, TenancyFilterMixinV1):
    type: Annotated['CableTypeEnum', strawberry.lazy('dcim.graphql.enums')] | None = strawberry_django.filter_field()
    status: Annotated['LinkStatusEnum', strawberry.lazy('dcim.graphql.enums')] | None = strawberry_django.filter_field()
    label: FilterLookup[str] | None = strawberry_django.filter_field()
    color: Annotated['ColorEnum', strawberry.lazy('netbox.graphql.enums')] | None = strawberry_django.filter_field()
    length: Annotated['FloatLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    length_unit: Annotated['CableLengthUnitEnum', strawberry.lazy('dcim.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    terminations: Annotated['CableTerminationFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.CableTermination, lookups=True)
class CableTerminationFilterV1(ChangeLogFilterMixinV1):
    cable: Annotated['CableFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    cable_id: ID | None = strawberry_django.filter_field()
    cable_end: Annotated['CableEndEnum', strawberry.lazy('dcim.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    termination_type: Annotated['CableTerminationFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    termination_id: ID | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.ConsolePort, lookups=True)
class ConsolePortFilterV1(ModularComponentModelFilterMixinV1, CabledObjectModelFilterMixinV1):
    type: Annotated['ConsolePortTypeEnum', strawberry.lazy('dcim.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    speed: Annotated['ConsolePortSpeedEnum', strawberry.lazy('dcim.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.ConsolePortTemplate, lookups=True)
class ConsolePortTemplateFilterV1(ModularComponentTemplateFilterMixinV1):
    type: Annotated['ConsolePortTypeEnum', strawberry.lazy('dcim.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.ConsoleServerPort, lookups=True)
class ConsoleServerPortFilterV1(ModularComponentModelFilterMixinV1, CabledObjectModelFilterMixinV1):
    type: Annotated['ConsolePortTypeEnum', strawberry.lazy('dcim.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    speed: Annotated['ConsolePortSpeedEnum', strawberry.lazy('dcim.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.ConsoleServerPortTemplate, lookups=True)
class ConsoleServerPortTemplateFilterV1(ModularComponentTemplateFilterMixinV1):
    type: Annotated['ConsolePortTypeEnum', strawberry.lazy('dcim.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.Device, lookups=True)
class DeviceFilterV1(
    ContactFilterMixinV1,
    TenancyFilterMixinV1,
    ImageAttachmentFilterMixinV1,
    RenderConfigFilterMixinV1,
    ConfigContextFilterMixinV1,
    PrimaryModelFilterMixinV1,
):
    device_type: Annotated['DeviceTypeFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    device_type_id: ID | None = strawberry_django.filter_field()
    role: Annotated['DeviceRoleFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    role_id: ID | None = strawberry_django.filter_field()
    platform: Annotated['PlatformFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    serial: FilterLookup[str] | None = strawberry_django.filter_field()
    asset_tag: FilterLookup[str] | None = strawberry_django.filter_field()
    site: Annotated['SiteFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    site_id: ID | None = strawberry_django.filter_field()
    location: Annotated['LocationFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    location_id: Annotated['TreeNodeFilter', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    rack: Annotated['RackFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    rack_id: ID | None = strawberry_django.filter_field()
    position: Annotated['FloatLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    face: Annotated['DeviceFaceEnum', strawberry.lazy('dcim.graphql.enums')] | None = strawberry_django.filter_field()
    status: Annotated['DeviceStatusEnum', strawberry.lazy('dcim.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    airflow: Annotated['DeviceAirflowEnum', strawberry.lazy('dcim.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    primary_ip4: Annotated['IPAddressFilterV1', strawberry.lazy('ipam.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    primary_ip4_id: ID | None = strawberry_django.filter_field()
    primary_ip6: Annotated['IPAddressFilterV1', strawberry.lazy('ipam.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    primary_ip6_id: ID | None = strawberry_django.filter_field()
    oob_ip: Annotated['IPAddressFilterV1', strawberry.lazy('ipam.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    oob_ip_id: ID | None = strawberry_django.filter_field()
    cluster: Annotated['ClusterFilterV1', strawberry.lazy('virtualization.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    cluster_id: ID | None = strawberry_django.filter_field()
    virtual_chassis: Annotated['VirtualChassisFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
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
    console_ports: Annotated['ConsolePortFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    console_server_ports: Annotated['ConsoleServerPortFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    power_outlets: Annotated['PowerOutletFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    power_ports: Annotated['PowerPortFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    interfaces: Annotated['InterfaceFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    front_ports: Annotated['FrontPortFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    rear_ports: Annotated['RearPortFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    device_bays: Annotated['DeviceBayFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    module_bays: Annotated['ModuleBayFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    modules: Annotated['ModuleFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
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
class DeviceBayFilterV1(ComponentModelFilterMixinV1):
    installed_device: Annotated['DeviceFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    installed_device_id: ID | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.DeviceBayTemplate, lookups=True)
class DeviceBayTemplateFilterV1(ComponentTemplateFilterMixinV1):
    pass


@strawberry_django.filter_type(models.InventoryItemTemplate, lookups=True)
class InventoryItemTemplateFilterV1(ComponentTemplateFilterMixinV1):
    parent: Annotated['InventoryItemTemplateFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    component_type: Annotated['ContentTypeFilterV1', strawberry.lazy('core.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    component_id: ID | None = strawberry_django.filter_field()
    role: Annotated['InventoryItemRoleFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    role_id: ID | None = strawberry_django.filter_field()
    manufacturer: Annotated['ManufacturerFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    manufacturer_id: ID | None = strawberry_django.filter_field()
    part_id: FilterLookup[str] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.DeviceRole, lookups=True)
class DeviceRoleFilterV1(OrganizationalModelFilterMixinV1, RenderConfigFilterMixinV1):
    color: Annotated['ColorEnum', strawberry.lazy('netbox.graphql.enums')] | None = strawberry_django.filter_field()
    vm_role: FilterLookup[bool] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.DeviceType, lookups=True)
class DeviceTypeFilterV1(ImageAttachmentFilterMixinV1, PrimaryModelFilterMixinV1, WeightFilterMixinV1):
    manufacturer: Annotated['ManufacturerFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    manufacturer_id: ID | None = strawberry_django.filter_field()
    model: FilterLookup[str] | None = strawberry_django.filter_field()
    slug: FilterLookup[str] | None = strawberry_django.filter_field()
    default_platform: Annotated['PlatformFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    default_platform_id: ID | None = strawberry_django.filter_field()
    part_number: FilterLookup[str] | None = strawberry_django.filter_field()
    u_height: Annotated['FloatLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    exclude_from_utilization: FilterLookup[bool] | None = strawberry_django.filter_field()
    is_full_depth: FilterLookup[bool] | None = strawberry_django.filter_field()
    subdevice_role: Annotated['SubdeviceRoleEnum', strawberry.lazy('dcim.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    airflow: Annotated['DeviceAirflowEnum', strawberry.lazy('dcim.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    front_image: Annotated['ImageAttachmentFilterV1', strawberry.lazy('extras.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    rear_image: Annotated['ImageAttachmentFilterV1', strawberry.lazy('extras.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    console_port_templates: (
        Annotated['ConsolePortTemplateFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None
    ) = strawberry_django.filter_field()
    console_server_port_templates: (
        Annotated['ConsoleServerPortTemplateFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None
    ) = strawberry_django.filter_field()
    power_port_templates: (
        Annotated['PowerPortTemplateFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None
    ) = strawberry_django.filter_field()
    power_outlet_templates: (
        Annotated['PowerOutletTemplateFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None
    ) = strawberry_django.filter_field()
    interface_templates: (
        Annotated['InterfaceTemplateFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None
    ) = strawberry_django.filter_field()
    front_port_templates: (
        Annotated['FrontPortTemplateFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None
    ) = strawberry_django.filter_field()
    rear_port_templates: (
        Annotated['RearPortTemplateFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None
    ) = strawberry_django.filter_field()
    device_bay_templates: (
        Annotated['DeviceBayTemplateFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None
    ) = strawberry_django.filter_field()
    module_bay_templates: (
        Annotated['ModuleBayTemplateFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None
    ) = strawberry_django.filter_field()
    inventory_item_templates: (
        Annotated['InventoryItemTemplateFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None
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


@strawberry_django.filter_type(models.FrontPort, lookups=True)
class FrontPortFilterV1(ModularComponentModelFilterMixinV1, CabledObjectModelFilterMixinV1):
    type: Annotated['PortTypeEnum', strawberry.lazy('dcim.graphql.enums')] | None = strawberry_django.filter_field()
    color: Annotated['ColorEnum', strawberry.lazy('netbox.graphql.enums')] | None = strawberry_django.filter_field()
    rear_port: Annotated['RearPortFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    rear_port_id: ID | None = strawberry_django.filter_field()
    rear_port_position: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.FrontPortTemplate, lookups=True)
class FrontPortTemplateFilterV1(ModularComponentTemplateFilterMixinV1):
    type: Annotated['PortTypeEnum', strawberry.lazy('dcim.graphql.enums')] | None = strawberry_django.filter_field()
    color: Annotated['ColorEnum', strawberry.lazy('netbox.graphql.enums')] | None = strawberry_django.filter_field()
    rear_port: Annotated['RearPortTemplateFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    rear_port_id: ID | None = strawberry_django.filter_field()
    rear_port_position: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.MACAddress, lookups=True)
class MACAddressFilterV1(PrimaryModelFilterMixinV1):
    mac_address: FilterLookup[str] | None = strawberry_django.filter_field()
    assigned_object_type: Annotated['ContentTypeFilterV1', strawberry.lazy('core.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    assigned_object_id: ID | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.Interface, lookups=True)
class InterfaceFilterV1(ModularComponentModelFilterMixinV1, InterfaceBaseFilterMixinV1, CabledObjectModelFilterMixinV1):
    vcdcs: Annotated['VirtualDeviceContextFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    lag: Annotated['InterfaceFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    lag_id: ID | None = strawberry_django.filter_field()
    type: Annotated['InterfaceTypeEnum', strawberry.lazy('dcim.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    mgmt_only: FilterLookup[bool] | None = strawberry_django.filter_field()
    speed: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    duplex: Annotated['InterfaceDuplexEnum', strawberry.lazy('dcim.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    wwn: FilterLookup[str] | None = strawberry_django.filter_field()
    parent: Annotated['InterfaceFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    parent_id: ID | None = strawberry_django.filter_field()
    rf_role: Annotated['WirelessRoleEnum', strawberry.lazy('wireless.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    rf_channel: Annotated['WirelessChannelEnum', strawberry.lazy('wireless.graphql.enums')] | None = (
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
    poe_mode: Annotated['InterfacePoEModeEnum', strawberry.lazy('dcim.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    poe_type: Annotated['InterfacePoETypeEnum', strawberry.lazy('dcim.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    wireless_link: Annotated['WirelessLinkFilterV1', strawberry.lazy('wireless.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    wireless_link_id: ID | None = strawberry_django.filter_field()
    wireless_lans: Annotated['WirelessLANFilterV1', strawberry.lazy('wireless.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    vrf: Annotated['VRFFilterV1', strawberry.lazy('ipam.graphql.filters_v1')] | None = strawberry_django.filter_field()
    vrf_id: ID | None = strawberry_django.filter_field()
    ip_addresses: Annotated['IPAddressFilterV1', strawberry.lazy('ipam.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    mac_addresses: Annotated['MACAddressFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    fhrp_group_assignments: Annotated[
        'FHRPGroupAssignmentFilterV1', strawberry.lazy('ipam.graphql.filters_v1')
    ] | None = (
        strawberry_django.filter_field()
    )
    tunnel_terminations: Annotated['TunnelTerminationFilterV1', strawberry.lazy('vpn.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    l2vpn_terminations: Annotated['L2VPNFilterV1', strawberry.lazy('vpn.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )

    @strawberry_django.filter_field
    def connected(self, queryset, value: bool, prefix: str):
        if value is True:
            return queryset, Q(**{f"{prefix}_path__is_active": True})
        else:
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
        elif value == InterfaceKindEnum.KIND_VIRTUAL:
            return queryset, Q(**{f"{prefix}type__in": VIRTUAL_IFACE_TYPES})
        elif value == InterfaceKindEnum.KIND_WIRELESS:
            return queryset, Q(**{f"{prefix}type__in": WIRELESS_IFACE_TYPES})


@strawberry_django.filter_type(models.InterfaceTemplate, lookups=True)
class InterfaceTemplateFilterV1(ModularComponentTemplateFilterMixinV1):
    type: Annotated['InterfaceTypeEnum', strawberry.lazy('dcim.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    enabled: FilterLookup[bool] | None = strawberry_django.filter_field()
    mgmt_only: FilterLookup[bool] | None = strawberry_django.filter_field()
    bridge: Annotated['InterfaceTemplateFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    bridge_id: ID | None = strawberry_django.filter_field()
    poe_mode: Annotated['InterfacePoEModeEnum', strawberry.lazy('dcim.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    poe_type: Annotated['InterfacePoETypeEnum', strawberry.lazy('dcim.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    rf_role: Annotated['WirelessRoleEnum', strawberry.lazy('wireless.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.InventoryItem, lookups=True)
class InventoryItemFilterV1(ComponentModelFilterMixinV1):
    parent: Annotated['InventoryItemFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    parent_id: ID | None = strawberry_django.filter_field()
    component_type: Annotated['ContentTypeFilterV1', strawberry.lazy('core.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    component_id: ID | None = strawberry_django.filter_field()
    status: Annotated['InventoryItemStatusEnum', strawberry.lazy('dcim.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    role: Annotated['InventoryItemRoleFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    role_id: ID | None = strawberry_django.filter_field()
    manufacturer: Annotated['ManufacturerFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    manufacturer_id: ID | None = strawberry_django.filter_field()
    part_id: FilterLookup[str] | None = strawberry_django.filter_field()
    serial: FilterLookup[str] | None = strawberry_django.filter_field()
    asset_tag: FilterLookup[str] | None = strawberry_django.filter_field()
    discovered: FilterLookup[bool] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.InventoryItemRole, lookups=True)
class InventoryItemRoleFilterV1(OrganizationalModelFilterMixinV1):
    color: Annotated['ColorEnum', strawberry.lazy('netbox.graphql.enums')] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.Location, lookups=True)
class LocationFilterV1(
    ContactFilterMixinV1, ImageAttachmentFilterMixinV1, TenancyFilterMixinV1, NestedGroupModelFilterMixinV1
):
    site: Annotated['SiteFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    site_id: ID | None = strawberry_django.filter_field()
    status: Annotated['LocationStatusEnum', strawberry.lazy('dcim.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    facility: FilterLookup[str] | None = strawberry_django.filter_field()
    prefixes: Annotated['PrefixFilterV1', strawberry.lazy('ipam.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    vlan_groups: Annotated['VLANGroupFilterV1', strawberry.lazy('ipam.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.Manufacturer, lookups=True)
class ManufacturerFilterV1(ContactFilterMixinV1, OrganizationalModelFilterMixinV1):
    pass


@strawberry_django.filter_type(models.Module, lookups=True)
class ModuleFilterV1(PrimaryModelFilterMixinV1, ConfigContextFilterMixinV1):
    device: Annotated['DeviceFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    device_id: ID | None = strawberry_django.filter_field()
    module_bay: Annotated['ModuleBayFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    module_bay_id: ID | None = strawberry_django.filter_field()
    module_type: Annotated['ModuleTypeFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    module_type_id: ID | None = strawberry_django.filter_field()
    status: Annotated['ModuleStatusEnum', strawberry.lazy('dcim.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    serial: FilterLookup[str] | None = strawberry_django.filter_field()
    asset_tag: FilterLookup[str] | None = strawberry_django.filter_field()
    console_ports: Annotated['ConsolePortFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    console_server_ports: Annotated['ConsoleServerPortFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    power_outlets: Annotated['PowerOutletFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    power_ports: Annotated['PowerPortFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    interfaces: Annotated['InterfaceFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    front_ports: Annotated['FrontPortFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    rear_ports: Annotated['RearPortFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    device_bays: Annotated['DeviceBayFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    module_bays: Annotated['ModuleBayFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    modules: Annotated['ModuleFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.ModuleBay, lookups=True)
class ModuleBayFilterV1(ModularComponentModelFilterMixinV1):
    parent: Annotated['ModuleBayFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    parent_id: ID | None = strawberry_django.filter_field()
    position: FilterLookup[str] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.ModuleBayTemplate, lookups=True)
class ModuleBayTemplateFilterV1(ModularComponentTemplateFilterMixinV1):
    position: FilterLookup[str] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.ModuleTypeProfile, lookups=True)
class ModuleTypeProfileFilterV1(PrimaryModelFilterMixinV1):
    name: FilterLookup[str] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.ModuleType, lookups=True)
class ModuleTypeFilterV1(ImageAttachmentFilterMixinV1, PrimaryModelFilterMixinV1, WeightFilterMixinV1):
    manufacturer: Annotated['ManufacturerFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    manufacturer_id: ID | None = strawberry_django.filter_field()
    profile: Annotated['ModuleTypeProfileFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    profile_id: ID | None = strawberry_django.filter_field()
    model: FilterLookup[str] | None = strawberry_django.filter_field()
    part_number: FilterLookup[str] | None = strawberry_django.filter_field()
    airflow: Annotated['ModuleAirflowEnum', strawberry.lazy('dcim.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    console_port_templates: (
        Annotated['ConsolePortTemplateFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None
    ) = strawberry_django.filter_field()
    console_server_port_templates: (
        Annotated['ConsoleServerPortTemplateFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None
    ) = strawberry_django.filter_field()
    power_port_templates: (
        Annotated['PowerPortTemplateFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None
    ) = strawberry_django.filter_field()
    power_outlet_templates: (
        Annotated['PowerOutletTemplateFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None
    ) = strawberry_django.filter_field()
    interface_templates: (
        Annotated['InterfaceTemplateFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None
    ) = strawberry_django.filter_field()
    front_port_templates: (
        Annotated['FrontPortTemplateFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None
    ) = strawberry_django.filter_field()
    rear_port_templates: (
        Annotated['RearPortTemplateFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None
    ) = strawberry_django.filter_field()
    device_bay_templates: (
        Annotated['DeviceBayTemplateFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None
    ) = strawberry_django.filter_field()
    module_bay_templates: (
        Annotated['ModuleBayTemplateFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None
    ) = strawberry_django.filter_field()
    inventory_item_templates: (
        Annotated['InventoryItemTemplateFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None
    ) = strawberry_django.filter_field()


@strawberry_django.filter_type(models.Platform, lookups=True)
class PlatformFilterV1(OrganizationalModelFilterMixinV1):
    manufacturer: Annotated['ManufacturerFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    manufacturer_id: ID | None = strawberry_django.filter_field()
    config_template: Annotated['ConfigTemplateFilterV1', strawberry.lazy('extras.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    config_template_id: ID | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.PowerFeed, lookups=True)
class PowerFeedFilterV1(CabledObjectModelFilterMixinV1, TenancyFilterMixinV1, PrimaryModelFilterMixinV1):
    power_panel: Annotated['PowerPanelFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    power_panel_id: ID | None = strawberry_django.filter_field()
    rack: Annotated['RackFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    rack_id: ID | None = strawberry_django.filter_field()
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    status: Annotated['PowerFeedStatusEnum', strawberry.lazy('dcim.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    type: Annotated['PowerFeedTypeEnum', strawberry.lazy('dcim.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    supply: Annotated['PowerFeedSupplyEnum', strawberry.lazy('dcim.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    phase: Annotated['PowerFeedPhaseEnum', strawberry.lazy('dcim.graphql.enums')] | None = (
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
class PowerOutletFilterV1(ModularComponentModelFilterMixinV1, CabledObjectModelFilterMixinV1):
    type: Annotated['PowerOutletTypeEnum', strawberry.lazy('dcim.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    power_port: Annotated['PowerPortFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    power_port_id: ID | None = strawberry_django.filter_field()
    feed_leg: Annotated['PowerOutletFeedLegEnum', strawberry.lazy('dcim.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    color: Annotated['ColorEnum', strawberry.lazy('netbox.graphql.enums')] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.PowerOutletTemplate, lookups=True)
class PowerOutletTemplateFilterV1(ModularComponentModelFilterMixinV1):
    type: Annotated['PowerOutletTypeEnum', strawberry.lazy('dcim.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    power_port: Annotated['PowerPortTemplateFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    power_port_id: ID | None = strawberry_django.filter_field()
    feed_leg: Annotated['PowerOutletFeedLegEnum', strawberry.lazy('dcim.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.PowerPanel, lookups=True)
class PowerPanelFilterV1(ContactFilterMixinV1, ImageAttachmentFilterMixinV1, PrimaryModelFilterMixinV1):
    site: Annotated['SiteFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    site_id: ID | None = strawberry_django.filter_field()
    location: Annotated['LocationFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    location_id: Annotated['TreeNodeFilter', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    name: FilterLookup[str] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.PowerPort, lookups=True)
class PowerPortFilterV1(ModularComponentModelFilterMixinV1, CabledObjectModelFilterMixinV1):
    type: Annotated['PowerPortTypeEnum', strawberry.lazy('dcim.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    maximum_draw: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    allocated_draw: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.PowerPortTemplate, lookups=True)
class PowerPortTemplateFilterV1(ModularComponentTemplateFilterMixinV1):
    type: Annotated['PowerPortTypeEnum', strawberry.lazy('dcim.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    maximum_draw: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    allocated_draw: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.RackType, lookups=True)
class RackTypeFilterV1(RackBaseFilterMixinV1):
    form_factor: Annotated['RackFormFactorEnum', strawberry.lazy('dcim.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    manufacturer: Annotated['ManufacturerFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    manufacturer_id: ID | None = strawberry_django.filter_field()
    model: FilterLookup[str] | None = strawberry_django.filter_field()
    slug: FilterLookup[str] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.Rack, lookups=True)
class RackFilterV1(ContactFilterMixinV1, ImageAttachmentFilterMixinV1, TenancyFilterMixinV1, RackBaseFilterMixinV1):
    form_factor: Annotated['RackFormFactorEnum', strawberry.lazy('dcim.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    rack_type: Annotated['RackTypeFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    rack_type_id: ID | None = strawberry_django.filter_field()
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    facility_id: FilterLookup[str] | None = strawberry_django.filter_field()
    site: Annotated['SiteFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    site_id: ID | None = strawberry_django.filter_field()
    location: Annotated['LocationFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    location_id: Annotated['TreeNodeFilter', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    status: Annotated['RackStatusEnum', strawberry.lazy('dcim.graphql.enums')] | None = strawberry_django.filter_field()
    role: Annotated['RackRoleFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    role_id: ID | None = strawberry_django.filter_field()
    serial: FilterLookup[str] | None = strawberry_django.filter_field()
    asset_tag: FilterLookup[str] | None = strawberry_django.filter_field()
    airflow: Annotated['RackAirflowEnum', strawberry.lazy('dcim.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    vlan_groups: Annotated['VLANGroupFilterV1', strawberry.lazy('ipam.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.RackReservation, lookups=True)
class RackReservationFilterV1(TenancyFilterMixinV1, PrimaryModelFilterMixinV1):
    rack: Annotated['RackFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    rack_id: ID | None = strawberry_django.filter_field()
    units: Annotated['IntegerArrayLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    user: Annotated['UserFilterV1', strawberry.lazy('users.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    user_id: ID | None = strawberry_django.filter_field()
    description: FilterLookup[str] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.RackRole, lookups=True)
class RackRoleFilterV1(OrganizationalModelFilterMixinV1):
    color: Annotated['ColorEnum', strawberry.lazy('netbox.graphql.enums')] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.RearPort, lookups=True)
class RearPortFilterV1(ModularComponentModelFilterMixinV1, CabledObjectModelFilterMixinV1):
    type: Annotated['PortTypeEnum', strawberry.lazy('dcim.graphql.enums')] | None = strawberry_django.filter_field()
    color: Annotated['ColorEnum', strawberry.lazy('netbox.graphql.enums')] | None = strawberry_django.filter_field()
    positions: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.RearPortTemplate, lookups=True)
class RearPortTemplateFilterV1(ModularComponentTemplateFilterMixinV1):
    type: Annotated['PortTypeEnum', strawberry.lazy('dcim.graphql.enums')] | None = strawberry_django.filter_field()
    color: Annotated['ColorEnum', strawberry.lazy('netbox.graphql.enums')] | None = strawberry_django.filter_field()
    positions: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.Region, lookups=True)
class RegionFilterV1(ContactFilterMixinV1, NestedGroupModelFilterMixinV1):
    prefixes: Annotated['PrefixFilterV1', strawberry.lazy('ipam.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    vlan_groups: Annotated['VLANGroupFilterV1', strawberry.lazy('ipam.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.Site, lookups=True)
class SiteFilterV1(ContactFilterMixinV1, ImageAttachmentFilterMixinV1, TenancyFilterMixinV1, PrimaryModelFilterMixinV1):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    slug: FilterLookup[str] | None = strawberry_django.filter_field()
    status: Annotated['SiteStatusEnum', strawberry.lazy('dcim.graphql.enums')] | None = strawberry_django.filter_field()
    region: Annotated['RegionFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    region_id: Annotated['TreeNodeFilter', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    group: Annotated['SiteGroupFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    group_id: Annotated['TreeNodeFilter', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    facility: FilterLookup[str] | None = strawberry_django.filter_field()
    asns: Annotated['ASNFilterV1', strawberry.lazy('ipam.graphql.filters_v1')] | None = strawberry_django.filter_field()
    time_zone: FilterLookup[str] | None = strawberry_django.filter_field()
    physical_address: FilterLookup[str] | None = strawberry_django.filter_field()
    shipping_address: FilterLookup[str] | None = strawberry_django.filter_field()
    latitude: Annotated['FloatLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    longitude: Annotated['FloatLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    prefixes: Annotated['PrefixFilterV1', strawberry.lazy('ipam.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    vlan_groups: Annotated['VLANGroupFilterV1', strawberry.lazy('ipam.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.SiteGroup, lookups=True)
class SiteGroupFilterV1(ContactFilterMixinV1, NestedGroupModelFilterMixinV1):
    prefixes: Annotated['PrefixFilterV1', strawberry.lazy('ipam.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    vlan_groups: Annotated['VLANGroupFilterV1', strawberry.lazy('ipam.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.VirtualChassis, lookups=True)
class VirtualChassisFilterV1(PrimaryModelFilterMixinV1):
    master: Annotated['DeviceFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    master_id: ID | None = strawberry_django.filter_field()
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    domain: FilterLookup[str] | None = strawberry_django.filter_field()
    members: (
        Annotated['DeviceFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None
    ) = strawberry_django.filter_field()
    member_count: FilterLookup[int] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.VirtualDeviceContext, lookups=True)
class VirtualDeviceContextFilterV1(TenancyFilterMixinV1, PrimaryModelFilterMixinV1):
    device: Annotated['DeviceFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    device_id: ID | None = strawberry_django.filter_field()
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    status: Annotated['VirtualDeviceContextStatusEnum', strawberry.lazy('dcim.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    identifier: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    primary_ip4: Annotated['IPAddressFilterV1', strawberry.lazy('ipam.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    primary_ip4_id: ID | None = strawberry_django.filter_field()
    primary_ip6: Annotated['IPAddressFilterV1', strawberry.lazy('ipam.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    primary_ip6_id: ID | None = strawberry_django.filter_field()
    comments: FilterLookup[str] | None = strawberry_django.filter_field()
    interfaces: (
        Annotated['InterfaceFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None
    ) = strawberry_django.filter_field()
