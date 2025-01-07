from typing import Annotated, TYPE_CHECKING
import strawberry
from strawberry.scalars import ID
import strawberry_django
from strawberry_django import (
    FilterLookup,
)
from extras.graphql.filter_mixins import (
    ConfigContextFilterMixin,
)
from netbox.graphql.filter_mixins import (
    PrimaryModelFilterMixin,
    OrganizationalModelFilterMixin,
    NestedGroupModelFilterMixin,
    ImageAttachmentFilterMixin,
    WeightFilterMixin,
)
from .filter_mixins import *
from dcim import models
from core.graphql.filter_mixins import *
from tenancy.graphql.filter_mixins import TenancyFilterMixin, ContactFilterMixin

if TYPE_CHECKING:
    from .enums import *
    from netbox.graphql.enums import *
    from wireless.graphql.enums import *
    from core.graphql.filter_lookups import *
    from core.graphql.filters import *
    from extras.graphql.filters import *
    from circuits.graphql.filters import *
    from dcim.graphql.filters import *
    from ipam.graphql.filters import *
    from tenancy.graphql.filters import *
    from wireless.graphql.filters import *
    from users.graphql.filters import *
    from virtualization.graphql.filters import *
    from vpn.graphql.filters import *


__all__ = (
    'CableFilter',
    'CableTerminationFilter',
    'ConsolePortFilter',
    'ConsolePortTemplateFilter',
    'ConsoleServerPortFilter',
    'ConsoleServerPortTemplateFilter',
    'DeviceFilter',
    'DeviceBayFilter',
    'DeviceBayTemplateFilter',
    'InventoryItemTemplateFilter',
    'DeviceRoleFilter',
    'DeviceTypeFilter',
    'FrontPortFilter',
    'FrontPortTemplateFilter',
    'InterfaceFilter',
    'InterfaceTemplateFilter',
    'InventoryItemFilter',
    'InventoryItemRoleFilter',
    'LocationFilter',
    'MACAddressFilter',
    'ManufacturerFilter',
    'ModuleFilter',
    'ModuleBayFilter',
    'ModuleBayTemplateFilter',
    'ModuleTypeFilter',
    'PlatformFilter',
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


@strawberry_django.filter(models.Cable, lookups=True)
class CableFilter(PrimaryModelFilterMixin, TenancyFilterMixin):
    type: Annotated['CableTypeEnum', strawberry.lazy('dcim.graphql.enums')] | None = strawberry_django.filter_field()
    status: Annotated['LinkStatusEnum', strawberry.lazy('dcim.graphql.enums')] | None = strawberry_django.filter_field()
    label: FilterLookup[str] | None = strawberry_django.filter_field()
    color: Annotated['ColorEnum', strawberry.lazy('netbox.graphql.enums')] | None = strawberry_django.filter_field()
    length: Annotated['FloatLookup', strawberry.lazy('core.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    length_unit: Annotated['CableLengthUnitEnum', strawberry.lazy('dcim.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    terminations: Annotated['CableTerminationFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter(models.CableTermination, lookups=True)
class CableTerminationFilter(ChangeLogFilterMixin):
    cable: Annotated['CableFilter', strawberry.lazy('dcim.graphql.filters')] | None = strawberry_django.filter_field()
    cable_id: ID | None = strawberry_django.filter_field()
    cable_end: Annotated['CableEndEnum', strawberry.lazy('dcim.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    termination_type: Annotated['CableTerminationFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    termination_id: ID | None = strawberry_django.filter_field()


@strawberry_django.filter(models.ConsolePort, lookups=True)
class ConsolePortFilter(ModularComponentModelFilterMixin, CabledObjectModelFilterMixin):
    type: Annotated['ConsolePortTypeEnum', strawberry.lazy('dcim.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    speed: Annotated['ConsolePortSpeedEnum', strawberry.lazy('dcim.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter(models.ConsolePortTemplate, lookups=True)
class ConsolePortTemplateFilter(ModularComponentTemplateFilterMixin):
    type: Annotated['ConsolePortTypeEnum', strawberry.lazy('dcim.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter(models.ConsoleServerPort, lookups=True)
class ConsoleServerPortFilter(ModularComponentModelFilterMixin, CabledObjectModelFilterMixin):
    type: Annotated['ConsolePortTypeEnum', strawberry.lazy('dcim.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    speed: Annotated['ConsolePortSpeedEnum', strawberry.lazy('dcim.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter(models.ConsoleServerPortTemplate, lookups=True)
class ConsoleServerPortTemplateFilter(ModularComponentTemplateFilterMixin):
    type: Annotated['ConsolePortTypeEnum', strawberry.lazy('dcim.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter(models.Device, lookups=True)
class DeviceFilter(
    ContactFilterMixin,
    TenancyFilterMixin,
    ImageAttachmentFilterMixin,
    RenderConfigFilterMixin,
    ConfigContextFilterMixin,
    PrimaryModelFilterMixin,
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
    location_id: Annotated['TreeNodeFilter', strawberry.lazy('core.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    rack: Annotated['RackFilter', strawberry.lazy('dcim.graphql.filters')] | None = strawberry_django.filter_field()
    rack_id: ID | None = strawberry_django.filter_field()
    position: Annotated['FloatLookup', strawberry.lazy('core.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    face: Annotated['DeviceFaceEnum', strawberry.lazy('dcim.graphql.enums')] | None = strawberry_django.filter_field()
    status: Annotated['DeviceStatusEnum', strawberry.lazy('dcim.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    airflow: Annotated['DeviceAirflowEnum', strawberry.lazy('dcim.graphql.enums')] | None = (
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
    vc_position: Annotated['IntegerLookup', strawberry.lazy('core.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    vc_priority: Annotated['IntegerLookup', strawberry.lazy('core.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    latitude: Annotated['FloatLookup', strawberry.lazy('core.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    longitude: Annotated['FloatLookup', strawberry.lazy('core.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    interfaces: Annotated['InterfaceFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    consoleports: Annotated['ConsolePortFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    consoleserverports: Annotated['ConsoleServerPortFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    poweroutlets: Annotated['PowerOutletFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    powerports: Annotated['PowerPortFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    devicebays: Annotated['DeviceBayFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    frontports: Annotated['FrontPortFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    rearports: Annotated['RearPortFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    modulebays: Annotated['ModuleBayFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    modules: Annotated['ModuleFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter(models.DeviceBay, lookups=True)
class DeviceBayFilter(ComponentModelFilterMixin):
    installed_device: Annotated['DeviceFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    installed_device_id: ID | None = strawberry_django.filter_field()


@strawberry_django.filter(models.DeviceBayTemplate, lookups=True)
class DeviceBayTemplateFilter(ComponentTemplateFilterMixin):
    pass


@strawberry_django.filter(models.InventoryItemTemplate, lookups=True)
class InventoryItemTemplateFilter(ComponentTemplateFilterMixin):
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


@strawberry_django.filter(models.DeviceRole, lookups=True)
class DeviceRoleFilter(OrganizationalModelFilterMixin, RenderConfigFilterMixin):
    color: Annotated['ColorEnum', strawberry.lazy('netbox.graphql.enums')] | None = strawberry_django.filter_field()
    vm_role: FilterLookup[bool] | None = strawberry_django.filter_field()


@strawberry_django.filter(models.DeviceType, lookups=True)
class DeviceTypeFilter(ImageAttachmentFilterMixin, PrimaryModelFilterMixin, WeightFilterMixin):
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
    u_height: Annotated['FloatLookup', strawberry.lazy('core.graphql.filter_lookups')] | None = (
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
    front_image: Annotated['ImageAttachmentFilter', strawberry.lazy('extras.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    rear_image: Annotated['ImageAttachmentFilter', strawberry.lazy('extras.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter(models.FrontPort, lookups=True)
class FrontPortFilter(ModularComponentModelFilterMixin, CabledObjectModelFilterMixin):
    type: Annotated['PortTypeEnum', strawberry.lazy('dcim.graphql.enums')] | None = strawberry_django.filter_field()
    color: Annotated['ColorEnum', strawberry.lazy('netbox.graphql.enums')] | None = strawberry_django.filter_field()
    rear_port: Annotated['RearPortFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    rear_port_id: ID | None = strawberry_django.filter_field()
    rear_port_position: Annotated['IntegerLookup', strawberry.lazy('core.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter(models.FrontPortTemplate, lookups=True)
class FrontPortTemplateFilter(ModularComponentTemplateFilterMixin):
    type: Annotated['PortTypeEnum', strawberry.lazy('dcim.graphql.enums')] | None = strawberry_django.filter_field()
    color: Annotated['ColorEnum', strawberry.lazy('netbox.graphql.enums')] | None = strawberry_django.filter_field()
    rear_port: Annotated['RearPortTemplateFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    rear_port_id: ID | None = strawberry_django.filter_field()
    rear_port_position: Annotated['IntegerLookup', strawberry.lazy('core.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter(models.MACAddress, lookups=True)
class MACAddressFilter(PrimaryModelFilterMixin):
    mac_address: FilterLookup[str] | None = strawberry_django.filter_field()
    assigned_object_type: Annotated['ContentTypeFilter', strawberry.lazy('core.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    assigned_object_id: ID | None = strawberry_django.filter_field()


@strawberry_django.filter(models.Interface, lookups=True)
class InterfaceFilter(ModularComponentModelFilterMixin, InterfaceBaseFilterMixin, CabledObjectModelFilterMixin):
    vcdcs: Annotated['VirtualDeviceContextFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    lag: Annotated['InterfaceFilter', strawberry.lazy('dcim.graphql.filters')] | None = strawberry_django.filter_field()
    lag_id: ID | None = strawberry_django.filter_field()
    type: Annotated['InterfaceTypeEnum', strawberry.lazy('dcim.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    mgmt_only: FilterLookup[bool] | None = strawberry_django.filter_field()
    speed: Annotated['IntegerLookup', strawberry.lazy('core.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    duplex: Annotated['InterfaceDuplexEnum', strawberry.lazy('dcim.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    wwn: FilterLookup[str] | None = strawberry_django.filter_field()
    rf_role: Annotated['WirelessRoleEnum', strawberry.lazy('wireless.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    rf_channel: Annotated['WirelessChannelEnum', strawberry.lazy('wireless.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    rf_channel_frequency: Annotated['FloatLookup', strawberry.lazy('core.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    rf_channel_width: Annotated['FloatLookup', strawberry.lazy('core.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    tx_power: Annotated['IntegerLookup', strawberry.lazy('core.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    poe_mode: Annotated['InterfacePoEModeEnum', strawberry.lazy('dcim.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    poe_type: Annotated['InterfacePoETypeEnum', strawberry.lazy('dcim.graphql.enums')] | None = (
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


@strawberry_django.filter(models.InterfaceTemplate, lookups=True)
class InterfaceTemplateFilter(ModularComponentTemplateFilterMixin):
    type: Annotated['InterfaceTypeEnum', strawberry.lazy('dcim.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    enabled: FilterLookup[bool] | None = strawberry_django.filter_field()
    mgmt_only: FilterLookup[bool] | None = strawberry_django.filter_field()
    bridge: Annotated['InterfaceTemplateFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
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


@strawberry_django.filter(models.InventoryItem, lookups=True)
class InventoryItemFilter(ComponentModelFilterMixin):
    parent: Annotated['InventoryItemFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    parent_id: ID | None = strawberry_django.filter_field()
    component_type: Annotated['ContentTypeFilter', strawberry.lazy('core.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    component_id: ID | None = strawberry_django.filter_field()
    status: Annotated['InventoryItemStatusEnum', strawberry.lazy('dcim.graphql.enums')] | None = (
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


@strawberry_django.filter(models.InventoryItemRole, lookups=True)
class InventoryItemRoleFilter(OrganizationalModelFilterMixin):
    color: Annotated['ColorEnum', strawberry.lazy('netbox.graphql.enums')] | None = strawberry_django.filter_field()


@strawberry_django.filter(models.Location, lookups=True)
class LocationFilter(ContactFilterMixin, ImageAttachmentFilterMixin, NestedGroupModelFilterMixin):
    site: Annotated['SiteFilter', strawberry.lazy('dcim.graphql.filters')] | None = strawberry_django.filter_field()
    site_id: ID | None = strawberry_django.filter_field()
    status: Annotated['LocationStatusEnum', strawberry.lazy('dcim.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    tenant: Annotated['TenantFilter', strawberry.lazy('tenancy.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    tenant_id: ID | None = strawberry_django.filter_field()
    facility: FilterLookup[str] | None = strawberry_django.filter_field()
    prefixes: Annotated['PrefixFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    vlan_groups: Annotated['VLANGroupFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter(models.Manufacturer, lookups=True)
class ManufacturerFilter(ContactFilterMixin, OrganizationalModelFilterMixin):
    pass


@strawberry_django.filter(models.Module, lookups=True)
class ModuleFilter(PrimaryModelFilterMixin, ConfigContextFilterMixin):
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
    status: Annotated['ModuleStatusEnum', strawberry.lazy('dcim.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    serial: FilterLookup[str] | None = strawberry_django.filter_field()
    asset_tag: FilterLookup[str] | None = strawberry_django.filter_field()


@strawberry_django.filter(models.ModuleBay, lookups=True)
class ModuleBayFilter(ModularComponentModelFilterMixin):
    parent: Annotated['ModuleBayFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    parent_id: ID | None = strawberry_django.filter_field()
    position: FilterLookup[str] | None = strawberry_django.filter_field()


@strawberry_django.filter(models.ModuleBayTemplate, lookups=True)
class ModuleBayTemplateFilter(ModularComponentTemplateFilterMixin):
    position: FilterLookup[str] | None = strawberry_django.filter_field()


@strawberry_django.filter(models.ModuleType, lookups=True)
class ModuleTypeFilter(ImageAttachmentFilterMixin, PrimaryModelFilterMixin, WeightFilterMixin):
    manufacturer: Annotated['ManufacturerFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    manufacturer_id: ID | None = strawberry_django.filter_field()
    model: FilterLookup[str] | None = strawberry_django.filter_field()
    part_number: FilterLookup[str] | None = strawberry_django.filter_field()
    airflow: Annotated['ModuleAirflowEnum', strawberry.lazy('dcim.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter(models.Platform, lookups=True)
class PlatformFilter(OrganizationalModelFilterMixin):
    manufacturer: Annotated['ManufacturerFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    manufacturer_id: ID | None = strawberry_django.filter_field()
    config_template: Annotated['ConfigTemplateFilter', strawberry.lazy('extras.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    config_template_id: ID | None = strawberry_django.filter_field()


@strawberry_django.filter(models.PowerFeed, lookups=True)
class PowerFeedFilter(PrimaryModelFilterMixin, CabledObjectModelFilterMixin):
    power_panel: Annotated['PowerPanelFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    power_panel_id: ID | None = strawberry_django.filter_field()
    rack: Annotated['RackFilter', strawberry.lazy('dcim.graphql.filters')] | None = strawberry_django.filter_field()
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
    voltage: Annotated['IntegerLookup', strawberry.lazy('core.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    amperage: Annotated['IntegerLookup', strawberry.lazy('core.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    max_utilization: Annotated['IntegerLookup', strawberry.lazy('core.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    available_power: Annotated['IntegerLookup', strawberry.lazy('core.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    tenant: Annotated['TenantFilter', strawberry.lazy('tenancy.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    tenant_id: ID | None = strawberry_django.filter_field()


@strawberry_django.filter(models.PowerOutlet, lookups=True)
class PowerOutletFilter(ModularComponentModelFilterMixin, CabledObjectModelFilterMixin):
    type: Annotated['PowerOutletTypeEnum', strawberry.lazy('dcim.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    power_port: Annotated['PowerPortFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    power_port_id: ID | None = strawberry_django.filter_field()
    feed_leg: Annotated['PowerOutletFeedLegEnum', strawberry.lazy('dcim.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    color: Annotated['ColorEnum', strawberry.lazy('netbox.graphql.enums')] | None = strawberry_django.filter_field()


@strawberry_django.filter(models.PowerOutletTemplate, lookups=True)
class PowerOutletTemplateFilter(ModularComponentModelFilterMixin):
    type: Annotated['PowerOutletTypeEnum', strawberry.lazy('dcim.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    power_port: Annotated['PowerPortTemplateFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    power_port_id: ID | None = strawberry_django.filter_field()
    feed_leg: Annotated['PowerOutletFeedLegEnum', strawberry.lazy('dcim.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter(models.PowerPanel, lookups=True)
class PowerPanelFilter(ContactFilterMixin, ImageAttachmentFilterMixin, PrimaryModelFilterMixin):
    site: Annotated['SiteFilter', strawberry.lazy('dcim.graphql.filters')] | None = strawberry_django.filter_field()
    site_id: ID | None = strawberry_django.filter_field()
    location: Annotated['LocationFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    location_id: Annotated['TreeNodeFilter', strawberry.lazy('core.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    name: FilterLookup[str] | None = strawberry_django.filter_field()


@strawberry_django.filter(models.PowerPort, lookups=True)
class PowerPortFilter(ModularComponentModelFilterMixin, CabledObjectModelFilterMixin):
    type: Annotated['PowerPortTypeEnum', strawberry.lazy('dcim.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    maximum_draw: Annotated['IntegerLookup', strawberry.lazy('core.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    allocated_draw: Annotated['IntegerLookup', strawberry.lazy('core.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter(models.PowerPortTemplate, lookups=True)
class PowerPortTemplateFilter(ModularComponentTemplateFilterMixin):
    type: Annotated['PowerPortTypeEnum', strawberry.lazy('dcim.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    maximum_draw: Annotated['IntegerLookup', strawberry.lazy('core.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    allocated_draw: Annotated['IntegerLookup', strawberry.lazy('core.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter(models.RackType, lookups=True)
class RackTypeFilter(RackBaseFilterMixin):
    form_factor: Annotated['RackFormFactorEnum', strawberry.lazy('dcim.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    manufacturer: Annotated['ManufacturerFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    manufacturer_id: ID | None = strawberry_django.filter_field()
    model: FilterLookup[str] | None = strawberry_django.filter_field()
    slug: FilterLookup[str] | None = strawberry_django.filter_field()


@strawberry_django.filter(models.Rack, lookups=True)
class RackFilter(ContactFilterMixin, ImageAttachmentFilterMixin, RackBaseFilterMixin):
    form_factor: Annotated['RackFormFactorEnum', strawberry.lazy('dcim.graphql.enums')] | None = (
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
    location_id: Annotated['TreeNodeFilter', strawberry.lazy('core.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    tenant: Annotated['TenantFilter', strawberry.lazy('tenancy.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    tenant_id: ID | None = strawberry_django.filter_field()
    status: Annotated['RackStatusEnum', strawberry.lazy('dcim.graphql.enums')] | None = strawberry_django.filter_field()
    role: Annotated['RackRoleFilter', strawberry.lazy('dcim.graphql.filters')] | None = strawberry_django.filter_field()
    role_id: ID | None = strawberry_django.filter_field()
    serial: FilterLookup[str] | None = strawberry_django.filter_field()
    asset_tag: FilterLookup[str] | None = strawberry_django.filter_field()
    airflow: Annotated['RackAirflowEnum', strawberry.lazy('dcim.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    vlan_groups: Annotated['VLANGroupFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter(models.RackReservation, lookups=True)
class RackReservationFilter(PrimaryModelFilterMixin):
    rack: Annotated['RackFilter', strawberry.lazy('dcim.graphql.filters')] | None = strawberry_django.filter_field()
    rack_id: ID | None = strawberry_django.filter_field()
    units: Annotated['IntegerArrayLookup', strawberry.lazy('core.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    tenant: Annotated['TenantFilter', strawberry.lazy('tenancy.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    tenant_id: ID | None = strawberry_django.filter_field()
    user: Annotated['UserFilter', strawberry.lazy('users.graphql.filters')] | None = strawberry_django.filter_field()
    user_id: ID | None = strawberry_django.filter_field()
    description: FilterLookup[str] | None = strawberry_django.filter_field()


@strawberry_django.filter(models.RackRole, lookups=True)
class RackRoleFilter(OrganizationalModelFilterMixin):
    color: Annotated['ColorEnum', strawberry.lazy('netbox.graphql.enums')] | None = strawberry_django.filter_field()


@strawberry_django.filter(models.RearPort, lookups=True)
class RearPortFilter(ModularComponentModelFilterMixin, CabledObjectModelFilterMixin):
    type: Annotated['PortTypeEnum', strawberry.lazy('dcim.graphql.enums')] | None = strawberry_django.filter_field()
    color: Annotated['ColorEnum', strawberry.lazy('netbox.graphql.enums')] | None = strawberry_django.filter_field()
    positions: Annotated['IntegerLookup', strawberry.lazy('core.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter(models.RearPortTemplate, lookups=True)
class RearPortTemplateFilter(ModularComponentTemplateFilterMixin):
    type: Annotated['PortTypeEnum', strawberry.lazy('dcim.graphql.enums')] | None = strawberry_django.filter_field()
    color: Annotated['ColorEnum', strawberry.lazy('netbox.graphql.enums')] | None = strawberry_django.filter_field()
    positions: Annotated['IntegerLookup', strawberry.lazy('core.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter(models.Region, lookups=True)
class RegionFilter(ContactFilterMixin, NestedGroupModelFilterMixin):
    prefixes: Annotated['PrefixFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    vlan_groups: Annotated['VLANGroupFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter(models.Site, lookups=True)
class SiteFilter(ContactFilterMixin, ImageAttachmentFilterMixin, PrimaryModelFilterMixin):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    slug: FilterLookup[str] | None = strawberry_django.filter_field()
    status: Annotated['SiteStatusEnum', strawberry.lazy('dcim.graphql.enums')] | None = strawberry_django.filter_field()
    region: Annotated['RegionFilter', strawberry.lazy('dcim.graphql.filters')] | None = strawberry_django.filter_field()
    region_id: Annotated['TreeNodeFilter', strawberry.lazy('core.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    group: Annotated['SiteGroupFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    group_id: Annotated['TreeNodeFilter', strawberry.lazy('core.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    tenant: Annotated['TenantFilter', strawberry.lazy('tenancy.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    tenant_id: ID | None = strawberry_django.filter_field()
    facility: FilterLookup[str] | None = strawberry_django.filter_field()
    asns: Annotated['ASNFilter', strawberry.lazy('ipam.graphql.filters')] | None = strawberry_django.filter_field()
    time_zone: FilterLookup[str] | None = strawberry_django.filter_field()
    physical_address: FilterLookup[str] | None = strawberry_django.filter_field()
    shipping_address: FilterLookup[str] | None = strawberry_django.filter_field()
    latitude: Annotated['FloatLookup', strawberry.lazy('core.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    longitude: Annotated['FloatLookup', strawberry.lazy('core.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    prefixes: Annotated['PrefixFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    vlan_groups: Annotated['VLANGroupFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter(models.SiteGroup, lookups=True)
class SiteGroupFilter(ContactFilterMixin, NestedGroupModelFilterMixin):
    prefixes: Annotated['PrefixFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    vlan_groups: Annotated['VLANGroupFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter(models.VirtualChassis, lookups=True)
class VirtualChassisFilter(PrimaryModelFilterMixin):
    master: Annotated['DeviceFilter', strawberry.lazy('dcim.graphql.filters')] | None = strawberry_django.filter_field()
    master_id: ID | None = strawberry_django.filter_field()
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    domain: FilterLookup[str] | None = strawberry_django.filter_field()


@strawberry_django.filter(models.VirtualDeviceContext, lookups=True)
class VirtualDeviceContextFilter(PrimaryModelFilterMixin):
    device: Annotated['DeviceFilter', strawberry.lazy('dcim.graphql.filters')] | None = strawberry_django.filter_field()
    device_id: ID | None = strawberry_django.filter_field()
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    status: Annotated['VirtualDeviceContextStatusEnum', strawberry.lazy('dcim.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    identifier: Annotated['IntegerLookup', strawberry.lazy('core.graphql.filter_lookups')] | None = (
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
    tenant: Annotated['TenantFilter', strawberry.lazy('tenancy.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    tenant_id: ID | None = strawberry_django.filter_field()
    comments: FilterLookup[str] | None = strawberry_django.filter_field()
