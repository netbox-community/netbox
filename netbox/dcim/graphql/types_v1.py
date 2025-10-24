from typing import Annotated, List, TYPE_CHECKING, Union

import strawberry
import strawberry_django

from core.graphql.mixins_v1 import ChangelogMixinV1
from dcim import models
from extras.graphql.mixins_v1 import (
    ConfigContextMixinV1,
    ContactsMixinV1,
    CustomFieldsMixinV1,
    ImageAttachmentsMixinV1,
    TagsMixinV1,
)
from ipam.graphql.mixins_v1 import IPAddressesMixinV1, VLANGroupsMixinV1
from netbox.graphql.scalars import BigInt
from netbox.graphql.types_v1 import BaseObjectTypeV1, NetBoxObjectTypeV1, OrganizationalObjectTypeV1
from .filters_v1 import *
from .mixins_v1 import CabledObjectMixinV1, PathEndpointMixinV1

if TYPE_CHECKING:
    from circuits.graphql.types_v1 import CircuitTerminationTypeV1
    from extras.graphql.types_v1 import ConfigTemplateTypeV1
    from ipam.graphql.types_v1 import (
        ASNTypeV1,
        IPAddressTypeV1,
        PrefixTypeV1,
        ServiceTypeV1,
        VLANTranslationPolicyTypeV1,
        VLANTypeV1,
        VRFTypeV1,
    )
    from tenancy.graphql.types_v1 import TenantTypeV1
    from users.graphql.types_v1 import UserTypeV1
    from virtualization.graphql.types_v1 import ClusterTypeV1, VMInterfaceTypeV1, VirtualMachineTypeV1
    from vpn.graphql.types_v1 import L2VPNTerminationTypeV1
    from wireless.graphql.types_v1 import WirelessLANTypeV1, WirelessLinkTypeV1

__all__ = (
    'CableTypeV1',
    'ComponentTypeV1',
    'ConsolePortTypeV1',
    'ConsolePortTemplateTypeV1',
    'ConsoleServerPortTypeV1',
    'ConsoleServerPortTemplateTypeV1',
    'DeviceTypeV1',
    'DeviceBayTypeV1',
    'DeviceBayTemplateTypeV1',
    'DeviceRoleTypeV1',
    'DeviceTypeTypeV1',
    'FrontPortTypeV1',
    'FrontPortTemplateTypeV1',
    'InterfaceTypeV1',
    'InterfaceTemplateTypeV1',
    'InventoryItemTypeV1',
    'InventoryItemRoleTypeV1',
    'InventoryItemTemplateTypeV1',
    'LocationTypeV1',
    'MACAddressTypeV1',
    'ManufacturerTypeV1',
    'ModularComponentTypeV1',
    'ModuleTypeV1',
    'ModuleBayTypeV1',
    'ModuleBayTemplateTypeV1',
    'ModuleTypeProfileTypeV1',
    'ModuleTypeTypeV1',
    'PlatformTypeV1',
    'PowerFeedTypeV1',
    'PowerOutletTypeV1',
    'PowerOutletTemplateTypeV1',
    'PowerPanelTypeV1',
    'PowerPortTypeV1',
    'PowerPortTemplateTypeV1',
    'RackTypeV1',
    'RackReservationTypeV1',
    'RackRoleTypeV1',
    'RackTypeTypeV1',
    'RearPortTypeV1',
    'RearPortTemplateTypeV1',
    'RegionTypeV1',
    'SiteTypeV1',
    'SiteGroupTypeV1',
    'VirtualChassisTypeV1',
    'VirtualDeviceContextTypeV1',
)


#
# Base types
#


@strawberry.type
class ComponentTypeV1(
    ChangelogMixinV1,
    CustomFieldsMixinV1,
    TagsMixinV1,
    BaseObjectTypeV1
):
    """
    Base type for device/VM components
    """
    device: Annotated["DeviceTypeV1", strawberry.lazy('dcim.graphql.types_v1')]


@strawberry.type
class ModularComponentTypeV1(ComponentTypeV1):
    module: Annotated["ModuleTypeV1", strawberry.lazy('dcim.graphql.types_v1')] | None


@strawberry.type
class ComponentTemplateTypeV1(
    ChangelogMixinV1,
    BaseObjectTypeV1
):
    """
    Base type for device/VM components
    """
    device_type: Annotated["DeviceTypeTypeV1", strawberry.lazy('dcim.graphql.types_v1')]


@strawberry.type
class ModularComponentTemplateTypeV1(ComponentTemplateTypeV1):
    """
    Base type for ComponentTemplateModel which supports optional assignment to a ModuleType.
    """
    device_type: Annotated["DeviceTypeTypeV1", strawberry.lazy('dcim.graphql.types_v1')] | None
    module_type: Annotated["ModuleTypeTypeV1", strawberry.lazy('dcim.graphql.types_v1')] | None

#
# Model types
#


@strawberry_django.type(
    models.CableTermination,
    exclude=['termination_type', 'termination_id', '_device', '_rack', '_location', '_site'],
    filters=CableTerminationFilterV1,
    pagination=True
)
class CableTerminationTypeV1(NetBoxObjectTypeV1):
    cable: Annotated["CableTypeV1", strawberry.lazy('dcim.graphql.types_v1')] | None
    termination: Annotated[Union[
        Annotated["CircuitTerminationTypeV1", strawberry.lazy('circuits.graphql.types_v1')],
        Annotated["ConsolePortTypeV1", strawberry.lazy('dcim.graphql.types_v1')],
        Annotated["ConsoleServerPortTypeV1", strawberry.lazy('dcim.graphql.types_v1')],
        Annotated["FrontPortTypeV1", strawberry.lazy('dcim.graphql.types_v1')],
        Annotated["InterfaceTypeV1", strawberry.lazy('dcim.graphql.types_v1')],
        Annotated["PowerFeedTypeV1", strawberry.lazy('dcim.graphql.types_v1')],
        Annotated["PowerOutletTypeV1", strawberry.lazy('dcim.graphql.types_v1')],
        Annotated["PowerPortTypeV1", strawberry.lazy('dcim.graphql.types_v1')],
        Annotated["RearPortTypeV1", strawberry.lazy('dcim.graphql.types_v1')],
    ], strawberry.union("CableTerminationTerminationTypeV1")] | None


@strawberry_django.type(
    models.Cable,
    fields='__all__',
    filters=CableFilterV1,
    pagination=True
)
class CableTypeV1(NetBoxObjectTypeV1):
    color: str
    tenant: Annotated["TenantTypeV1", strawberry.lazy('tenancy.graphql.types_v1')] | None

    terminations: List[CableTerminationTypeV1]

    a_terminations: List[Annotated[Union[
        Annotated["CircuitTerminationTypeV1", strawberry.lazy('circuits.graphql.types_v1')],
        Annotated["ConsolePortTypeV1", strawberry.lazy('dcim.graphql.types_v1')],
        Annotated["ConsoleServerPortTypeV1", strawberry.lazy('dcim.graphql.types_v1')],
        Annotated["FrontPortTypeV1", strawberry.lazy('dcim.graphql.types_v1')],
        Annotated["InterfaceTypeV1", strawberry.lazy('dcim.graphql.types_v1')],
        Annotated["PowerFeedTypeV1", strawberry.lazy('dcim.graphql.types_v1')],
        Annotated["PowerOutletTypeV1", strawberry.lazy('dcim.graphql.types_v1')],
        Annotated["PowerPortTypeV1", strawberry.lazy('dcim.graphql.types_v1')],
        Annotated["RearPortTypeV1", strawberry.lazy('dcim.graphql.types_v1')],
    ], strawberry.union("CableTerminationTerminationTypeV1")]]

    b_terminations: List[Annotated[Union[
        Annotated["CircuitTerminationTypeV1", strawberry.lazy('circuits.graphql.types_v1')],
        Annotated["ConsolePortTypeV1", strawberry.lazy('dcim.graphql.types_v1')],
        Annotated["ConsoleServerPortTypeV1", strawberry.lazy('dcim.graphql.types_v1')],
        Annotated["FrontPortTypeV1", strawberry.lazy('dcim.graphql.types_v1')],
        Annotated["InterfaceTypeV1", strawberry.lazy('dcim.graphql.types_v1')],
        Annotated["PowerFeedTypeV1", strawberry.lazy('dcim.graphql.types_v1')],
        Annotated["PowerOutletTypeV1", strawberry.lazy('dcim.graphql.types_v1')],
        Annotated["PowerPortTypeV1", strawberry.lazy('dcim.graphql.types_v1')],
        Annotated["RearPortTypeV1", strawberry.lazy('dcim.graphql.types_v1')],
    ], strawberry.union("CableTerminationTerminationTypeV1")]]


@strawberry_django.type(
    models.ConsolePort,
    exclude=['_path'],
    filters=ConsolePortFilterV1,
    pagination=True
)
class ConsolePortTypeV1(ModularComponentTypeV1, CabledObjectMixinV1, PathEndpointMixinV1):
    pass


@strawberry_django.type(
    models.ConsolePortTemplate,
    fields='__all__',
    filters=ConsolePortTemplateFilterV1,
    pagination=True
)
class ConsolePortTemplateTypeV1(ModularComponentTemplateTypeV1):
    pass


@strawberry_django.type(
    models.ConsoleServerPort,
    exclude=['_path'],
    filters=ConsoleServerPortFilterV1,
    pagination=True
)
class ConsoleServerPortTypeV1(ModularComponentTypeV1, CabledObjectMixinV1, PathEndpointMixinV1):
    pass


@strawberry_django.type(
    models.ConsoleServerPortTemplate,
    fields='__all__',
    filters=ConsoleServerPortTemplateFilterV1,
    pagination=True
)
class ConsoleServerPortTemplateTypeV1(ModularComponentTemplateTypeV1):
    pass


@strawberry_django.type(
    models.Device,
    fields='__all__',
    filters=DeviceFilterV1,
    pagination=True
)
class DeviceTypeV1(ConfigContextMixinV1, ImageAttachmentsMixinV1, ContactsMixinV1, NetBoxObjectTypeV1):
    console_port_count: BigInt
    console_server_port_count: BigInt
    power_port_count: BigInt
    power_outlet_count: BigInt
    interface_count: BigInt
    front_port_count: BigInt
    rear_port_count: BigInt
    device_bay_count: BigInt
    module_bay_count: BigInt
    inventory_item_count: BigInt
    config_template: Annotated["ConfigTemplateTypeV1", strawberry.lazy('extras.graphql.types_v1')] | None
    device_type: Annotated["DeviceTypeTypeV1", strawberry.lazy('dcim.graphql.types_v1')]
    role: Annotated["DeviceRoleTypeV1", strawberry.lazy('dcim.graphql.types_v1')]
    tenant: Annotated["TenantTypeV1", strawberry.lazy('tenancy.graphql.types_v1')] | None
    platform: Annotated["PlatformTypeV1", strawberry.lazy('dcim.graphql.types_v1')] | None
    site: Annotated["SiteTypeV1", strawberry.lazy('dcim.graphql.types_v1')]
    location: Annotated["LocationTypeV1", strawberry.lazy('dcim.graphql.types_v1')] | None
    rack: Annotated["RackTypeV1", strawberry.lazy('dcim.graphql.types_v1')] | None
    primary_ip4: Annotated["IPAddressTypeV1", strawberry.lazy('ipam.graphql.types_v1')] | None
    primary_ip6: Annotated["IPAddressTypeV1", strawberry.lazy('ipam.graphql.types_v1')] | None
    oob_ip: Annotated["IPAddressTypeV1", strawberry.lazy('ipam.graphql.types_v1')] | None
    cluster: Annotated["ClusterTypeV1", strawberry.lazy('virtualization.graphql.types_v1')] | None
    virtual_chassis: Annotated["VirtualChassisTypeV1", strawberry.lazy('dcim.graphql.types_v1')] | None

    virtual_machines: List[Annotated["VirtualMachineTypeV1", strawberry.lazy('virtualization.graphql.types_v1')]]
    modules: List[Annotated["ModuleTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]
    interfaces: List[Annotated["InterfaceTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]
    rearports: List[Annotated["RearPortTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]
    consoleports: List[Annotated["ConsolePortTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]
    powerports: List[Annotated["PowerPortTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]
    cabletermination_set: List[Annotated["CableTerminationTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]
    consoleserverports: List[Annotated["ConsoleServerPortTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]
    poweroutlets: List[Annotated["PowerOutletTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]
    frontports: List[Annotated["FrontPortTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]
    devicebays: List[Annotated["DeviceBayTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]
    modulebays: List[Annotated["ModuleBayTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]
    services: List[Annotated["ServiceTypeV1", strawberry.lazy('ipam.graphql.types_v1')]]
    inventoryitems: List[Annotated["InventoryItemTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]
    vdcs: List[Annotated["VirtualDeviceContextTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]

    @strawberry_django.field
    def vc_master_for(self) -> Annotated["VirtualChassisTypeV1", strawberry.lazy('dcim.graphql.types_v1')] | None:
        return self.vc_master_for if hasattr(self, 'vc_master_for') else None

    @strawberry_django.field
    def parent_bay(self) -> Annotated["DeviceBayTypeV1", strawberry.lazy('dcim.graphql.types_v1')] | None:
        return self.parent_bay if hasattr(self, 'parent_bay') else None


@strawberry_django.type(
    models.DeviceBay,
    fields='__all__',
    filters=DeviceBayFilterV1,
    pagination=True
)
class DeviceBayTypeV1(ComponentTypeV1):
    installed_device: Annotated["DeviceTypeV1", strawberry.lazy('dcim.graphql.types_v1')] | None


@strawberry_django.type(
    models.DeviceBayTemplate,
    fields='__all__',
    filters=DeviceBayTemplateFilterV1,
    pagination=True
)
class DeviceBayTemplateTypeV1(ComponentTemplateTypeV1):
    pass


@strawberry_django.type(
    models.InventoryItemTemplate,
    exclude=['component_type', 'component_id', 'parent'],
    filters=InventoryItemTemplateFilterV1,
    pagination=True
)
class InventoryItemTemplateTypeV1(ComponentTemplateTypeV1):
    role: Annotated["InventoryItemRoleTypeV1", strawberry.lazy('dcim.graphql.types_v1')] | None
    manufacturer: Annotated["ManufacturerTypeV1", strawberry.lazy('dcim.graphql.types_v1')]

    @strawberry_django.field
    def parent(self) -> Annotated["InventoryItemTemplateTypeV1", strawberry.lazy('dcim.graphql.types_v1')] | None:
        return self.parent

    child_items: List[Annotated["InventoryItemTemplateTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]

    component: Annotated[Union[
        Annotated["ConsolePortTypeV1", strawberry.lazy('dcim.graphql.types_v1')],
        Annotated["ConsoleServerPortTypeV1", strawberry.lazy('dcim.graphql.types_v1')],
        Annotated["FrontPortTypeV1", strawberry.lazy('dcim.graphql.types_v1')],
        Annotated["InterfaceTypeV1", strawberry.lazy('dcim.graphql.types_v1')],
        Annotated["PowerOutletTypeV1", strawberry.lazy('dcim.graphql.types_v1')],
        Annotated["PowerPortTypeV1", strawberry.lazy('dcim.graphql.types_v1')],
        Annotated["RearPortTypeV1", strawberry.lazy('dcim.graphql.types_v1')],
    ], strawberry.union("InventoryItemTemplateComponentTypeV1")] | None


@strawberry_django.type(
    models.DeviceRole,
    fields='__all__',
    filters=DeviceRoleFilterV1,
    pagination=True
)
class DeviceRoleTypeV1(OrganizationalObjectTypeV1):
    parent: Annotated['DeviceRoleTypeV1', strawberry.lazy('dcim.graphql.types_v1')] | None
    children: List[Annotated['DeviceRoleTypeV1', strawberry.lazy('dcim.graphql.types_v1')]]
    color: str
    config_template: Annotated["ConfigTemplateTypeV1", strawberry.lazy('extras.graphql.types_v1')] | None

    virtual_machines: List[Annotated["VirtualMachineTypeV1", strawberry.lazy('virtualization.graphql.types_v1')]]
    devices: List[Annotated["DeviceTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]


@strawberry_django.type(
    models.DeviceType,
    fields='__all__',
    filters=DeviceTypeFilterV1,
    pagination=True
)
class DeviceTypeTypeV1(NetBoxObjectTypeV1):
    console_port_template_count: BigInt
    console_server_port_template_count: BigInt
    power_port_template_count: BigInt
    power_outlet_template_count: BigInt
    interface_template_count: BigInt
    front_port_template_count: BigInt
    rear_port_template_count: BigInt
    device_bay_template_count: BigInt
    module_bay_template_count: BigInt
    inventory_item_template_count: BigInt
    front_image: strawberry_django.fields.types.DjangoImageType | None
    rear_image: strawberry_django.fields.types.DjangoImageType | None
    manufacturer: Annotated["ManufacturerTypeV1", strawberry.lazy('dcim.graphql.types_v1')]
    default_platform: Annotated["PlatformTypeV1", strawberry.lazy('dcim.graphql.types_v1')] | None

    frontporttemplates: List[Annotated["FrontPortTemplateTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]
    modulebaytemplates: List[Annotated["ModuleBayTemplateTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]
    instances: List[Annotated["DeviceTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]
    poweroutlettemplates: List[Annotated["PowerOutletTemplateTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]
    powerporttemplates: List[Annotated["PowerPortTemplateTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]
    inventoryitemtemplates: List[Annotated["InventoryItemTemplateTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]
    rearporttemplates: List[Annotated["RearPortTemplateTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]
    consoleserverporttemplates: List[
        Annotated["ConsoleServerPortTemplateTypeV1", strawberry.lazy('dcim.graphql.types_v1')]
    ]
    interfacetemplates: List[Annotated["InterfaceTemplateTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]
    devicebaytemplates: List[Annotated["DeviceBayTemplateTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]
    consoleporttemplates: List[Annotated["ConsolePortTemplateTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]


@strawberry_django.type(
    models.FrontPort,
    fields='__all__',
    filters=FrontPortFilterV1,
    pagination=True
)
class FrontPortTypeV1(ModularComponentTypeV1, CabledObjectMixinV1):
    color: str
    rear_port: Annotated["RearPortTypeV1", strawberry.lazy('dcim.graphql.types_v1')]


@strawberry_django.type(
    models.FrontPortTemplate,
    fields='__all__',
    filters=FrontPortTemplateFilterV1,
    pagination=True
)
class FrontPortTemplateTypeV1(ModularComponentTemplateTypeV1):
    color: str
    rear_port: Annotated["RearPortTemplateTypeV1", strawberry.lazy('dcim.graphql.types_v1')]


@strawberry_django.type(
    models.MACAddress,
    exclude=['assigned_object_type', 'assigned_object_id'],
    filters=MACAddressFilterV1,
    pagination=True
)
class MACAddressTypeV1(NetBoxObjectTypeV1):
    mac_address: str

    @strawberry_django.field
    def assigned_object(self) -> Annotated[Union[
        Annotated["InterfaceTypeV1", strawberry.lazy('dcim.graphql.types_v1')],
        Annotated["VMInterfaceTypeV1", strawberry.lazy('virtualization.graphql.types_v1')],
    ], strawberry.union("MACAddressAssignmentTypeV1")] | None:
        return self.assigned_object


@strawberry_django.type(
    models.Interface,
    exclude=['_path'],
    filters=InterfaceFilterV1,
    pagination=True
)
class InterfaceTypeV1(IPAddressesMixinV1, ModularComponentTypeV1, CabledObjectMixinV1, PathEndpointMixinV1):
    _name: str
    wwn: str | None
    parent: Annotated["InterfaceTypeV1", strawberry.lazy('dcim.graphql.types_v1')] | None
    bridge: Annotated["InterfaceTypeV1", strawberry.lazy('dcim.graphql.types_v1')] | None
    lag: Annotated["InterfaceTypeV1", strawberry.lazy('dcim.graphql.types_v1')] | None
    wireless_link: Annotated["WirelessLinkTypeV1", strawberry.lazy('wireless.graphql.types_v1')] | None
    untagged_vlan: Annotated["VLANTypeV1", strawberry.lazy('ipam.graphql.types_v1')] | None
    vrf: Annotated["VRFTypeV1", strawberry.lazy('ipam.graphql.types_v1')] | None
    primary_mac_address: Annotated["MACAddressTypeV1", strawberry.lazy('dcim.graphql.types_v1')] | None
    qinq_svlan: Annotated["VLANTypeV1", strawberry.lazy('ipam.graphql.types_v1')] | None
    vlan_translation_policy: Annotated["VLANTranslationPolicyTypeV1", strawberry.lazy('ipam.graphql.types_v1')] | None
    l2vpn_termination: Annotated["L2VPNTerminationTypeV1", strawberry.lazy('vpn.graphql.types_v1')] | None

    vdcs: List[Annotated["VirtualDeviceContextTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]
    tagged_vlans: List[Annotated["VLANTypeV1", strawberry.lazy('ipam.graphql.types_v1')]]
    bridge_interfaces: List[Annotated["InterfaceTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]
    wireless_lans: List[Annotated["WirelessLANTypeV1", strawberry.lazy('wireless.graphql.types_v1')]]
    member_interfaces: List[Annotated["InterfaceTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]
    child_interfaces: List[Annotated["InterfaceTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]
    mac_addresses: List[Annotated["MACAddressTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]


@strawberry_django.type(
    models.InterfaceTemplate,
    fields='__all__',
    filters=InterfaceTemplateFilterV1,
    pagination=True
)
class InterfaceTemplateTypeV1(ModularComponentTemplateTypeV1):
    _name: str
    bridge: Annotated["InterfaceTemplateTypeV1", strawberry.lazy('dcim.graphql.types_v1')] | None

    bridge_interfaces: List[Annotated["InterfaceTemplateTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]


@strawberry_django.type(
    models.InventoryItem,
    exclude=['component_type', 'component_id', 'parent'],
    filters=InventoryItemFilterV1,
    pagination=True
)
class InventoryItemTypeV1(ComponentTypeV1):
    role: Annotated["InventoryItemRoleTypeV1", strawberry.lazy('dcim.graphql.types_v1')] | None
    manufacturer: Annotated["ManufacturerTypeV1", strawberry.lazy('dcim.graphql.types_v1')] | None

    child_items: List[Annotated["InventoryItemTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]

    @strawberry_django.field
    def parent(self) -> Annotated["InventoryItemTypeV1", strawberry.lazy('dcim.graphql.types_v1')] | None:
        return self.parent

    component: Annotated[Union[
        Annotated["ConsolePortTypeV1", strawberry.lazy('dcim.graphql.types_v1')],
        Annotated["ConsoleServerPortTypeV1", strawberry.lazy('dcim.graphql.types_v1')],
        Annotated["FrontPortTypeV1", strawberry.lazy('dcim.graphql.types_v1')],
        Annotated["InterfaceTypeV1", strawberry.lazy('dcim.graphql.types_v1')],
        Annotated["PowerOutletTypeV1", strawberry.lazy('dcim.graphql.types_v1')],
        Annotated["PowerPortTypeV1", strawberry.lazy('dcim.graphql.types_v1')],
        Annotated["RearPortTypeV1", strawberry.lazy('dcim.graphql.types_v1')],
    ], strawberry.union("InventoryItemComponentTypeV1")] | None


@strawberry_django.type(
    models.InventoryItemRole,
    fields='__all__',
    filters=InventoryItemRoleFilterV1,
    pagination=True
)
class InventoryItemRoleTypeV1(OrganizationalObjectTypeV1):
    color: str

    inventory_items: List[Annotated["InventoryItemTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]
    inventory_item_templates: List[Annotated["InventoryItemTemplateTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]


@strawberry_django.type(
    models.Location,
    # fields='__all__',
    exclude=['parent'],  # bug - temp
    filters=LocationFilterV1,
    pagination=True
)
class LocationTypeV1(VLANGroupsMixinV1, ImageAttachmentsMixinV1, ContactsMixinV1, OrganizationalObjectTypeV1):
    site: Annotated["SiteTypeV1", strawberry.lazy('dcim.graphql.types_v1')]
    tenant: Annotated["TenantTypeV1", strawberry.lazy('tenancy.graphql.types_v1')] | None
    parent: Annotated["LocationTypeV1", strawberry.lazy('dcim.graphql.types_v1')] | None

    powerpanel_set: List[Annotated["PowerPanelTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]
    cabletermination_set: List[Annotated["CableTerminationTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]
    racks: List[Annotated["RackTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]
    devices: List[Annotated["DeviceTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]
    children: List[Annotated["LocationTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]

    @strawberry_django.field
    def clusters(self) -> List[Annotated["ClusterTypeV1", strawberry.lazy('virtualization.graphql.types_v1')]]:
        return self.cluster_set.all()

    @strawberry_django.field
    def circuit_terminations(self) -> List[
        Annotated["CircuitTerminationTypeV1", strawberry.lazy('circuits.graphql.types_v1')]
    ]:
        return self.circuit_terminations.all()


@strawberry_django.type(
    models.Manufacturer,
    fields='__all__',
    filters=ManufacturerFilterV1,
    pagination=True
)
class ManufacturerTypeV1(OrganizationalObjectTypeV1, ContactsMixinV1):

    platforms: List[Annotated["PlatformTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]
    device_types: List[Annotated["DeviceTypeTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]
    inventory_item_templates: List[Annotated["InventoryItemTemplateTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]
    inventory_items: List[Annotated["InventoryItemTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]
    module_types: List[Annotated["ModuleTypeTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]


@strawberry_django.type(
    models.Module,
    fields='__all__',
    filters=ModuleFilterV1,
    pagination=True
)
class ModuleTypeV1(NetBoxObjectTypeV1):
    device: Annotated["DeviceTypeV1", strawberry.lazy('dcim.graphql.types_v1')]
    module_bay: Annotated["ModuleBayTypeV1", strawberry.lazy('dcim.graphql.types_v1')]
    module_type: Annotated["ModuleTypeTypeV1", strawberry.lazy('dcim.graphql.types_v1')]

    interfaces: List[Annotated["InterfaceTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]
    powerports: List[Annotated["PowerPortTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]
    consoleserverports: List[Annotated["ConsoleServerPortTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]
    consoleports: List[Annotated["ConsolePortTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]
    poweroutlets: List[Annotated["PowerOutletTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]
    rearports: List[Annotated["RearPortTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]
    frontports: List[Annotated["FrontPortTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]


@strawberry_django.type(
    models.ModuleBay,
    # fields='__all__',
    exclude=['parent'],
    filters=ModuleBayFilterV1,
    pagination=True
)
class ModuleBayTypeV1(ModularComponentTypeV1):

    installed_module: Annotated["ModuleTypeV1", strawberry.lazy('dcim.graphql.types_v1')] | None
    children: List[Annotated["ModuleBayTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]

    @strawberry_django.field
    def parent(self) -> Annotated["ModuleBayTypeV1", strawberry.lazy('dcim.graphql.types_v1')] | None:
        return self.parent


@strawberry_django.type(
    models.ModuleBayTemplate,
    fields='__all__',
    filters=ModuleBayTemplateFilterV1,
    pagination=True
)
class ModuleBayTemplateTypeV1(ModularComponentTemplateTypeV1):
    pass


@strawberry_django.type(
    models.ModuleTypeProfile,
    fields='__all__',
    filters=ModuleTypeProfileFilterV1,
    pagination=True
)
class ModuleTypeProfileTypeV1(NetBoxObjectTypeV1):
    module_types: List[Annotated["ModuleTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]


@strawberry_django.type(
    models.ModuleType,
    fields='__all__',
    filters=ModuleTypeFilterV1,
    pagination=True
)
class ModuleTypeTypeV1(NetBoxObjectTypeV1):
    profile: Annotated["ModuleTypeProfileTypeV1", strawberry.lazy('dcim.graphql.types_v1')] | None
    manufacturer: Annotated["ManufacturerTypeV1", strawberry.lazy('dcim.graphql.types_v1')]

    frontporttemplates: List[Annotated["FrontPortTemplateTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]
    consoleserverporttemplates: List[
        Annotated["ConsoleServerPortTemplateTypeV1", strawberry.lazy('dcim.graphql.types_v1')]
    ]
    interfacetemplates: List[Annotated["InterfaceTemplateTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]
    powerporttemplates: List[Annotated["PowerPortTemplateTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]
    poweroutlettemplates: List[Annotated["PowerOutletTemplateTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]
    rearporttemplates: List[Annotated["RearPortTemplateTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]
    instances: List[Annotated["ModuleTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]
    consoleporttemplates: List[Annotated["ConsolePortTemplateTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]


@strawberry_django.type(
    models.Platform,
    fields='__all__',
    filters=PlatformFilterV1,
    pagination=True
)
class PlatformTypeV1(OrganizationalObjectTypeV1):
    parent: Annotated['PlatformTypeV1', strawberry.lazy('dcim.graphql.types_v1')] | None
    children: List[Annotated['PlatformTypeV1', strawberry.lazy('dcim.graphql.types_v1')]]
    manufacturer: Annotated["ManufacturerTypeV1", strawberry.lazy('dcim.graphql.types_v1')] | None
    config_template: Annotated["ConfigTemplateTypeV1", strawberry.lazy('extras.graphql.types_v1')] | None

    virtual_machines: List[Annotated["VirtualMachineTypeV1", strawberry.lazy('virtualization.graphql.types_v1')]]
    devices: List[Annotated["DeviceTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]


@strawberry_django.type(
    models.PowerFeed,
    exclude=['_path'],
    filters=PowerFeedFilterV1,
    pagination=True
)
class PowerFeedTypeV1(NetBoxObjectTypeV1, CabledObjectMixinV1, PathEndpointMixinV1):
    power_panel: Annotated["PowerPanelTypeV1", strawberry.lazy('dcim.graphql.types_v1')]
    rack: Annotated["RackTypeV1", strawberry.lazy('dcim.graphql.types_v1')] | None
    tenant: Annotated["TenantTypeV1", strawberry.lazy('tenancy.graphql.types_v1')] | None


@strawberry_django.type(
    models.PowerOutlet,
    exclude=['_path'],
    filters=PowerOutletFilterV1,
    pagination=True
)
class PowerOutletTypeV1(ModularComponentTypeV1, CabledObjectMixinV1, PathEndpointMixinV1):
    power_port: Annotated["PowerPortTypeV1", strawberry.lazy('dcim.graphql.types_v1')] | None
    color: str


@strawberry_django.type(
    models.PowerOutletTemplate,
    fields='__all__',
    filters=PowerOutletTemplateFilterV1,
    pagination=True
)
class PowerOutletTemplateTypeV1(ModularComponentTemplateTypeV1):
    power_port: Annotated["PowerPortTemplateTypeV1", strawberry.lazy('dcim.graphql.types_v1')] | None


@strawberry_django.type(
    models.PowerPanel,
    fields='__all__',
    filters=PowerPanelFilterV1,
    pagination=True
)
class PowerPanelTypeV1(NetBoxObjectTypeV1, ContactsMixinV1):
    site: Annotated["SiteTypeV1", strawberry.lazy('dcim.graphql.types_v1')]
    location: Annotated["LocationTypeV1", strawberry.lazy('dcim.graphql.types_v1')] | None

    powerfeeds: List[Annotated["PowerFeedTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]


@strawberry_django.type(
    models.PowerPort,
    exclude=['_path'],
    filters=PowerPortFilterV1,
    pagination=True
)
class PowerPortTypeV1(ModularComponentTypeV1, CabledObjectMixinV1, PathEndpointMixinV1):

    poweroutlets: List[Annotated["PowerOutletTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]


@strawberry_django.type(
    models.PowerPortTemplate,
    fields='__all__',
    filters=PowerPortTemplateFilterV1,
    pagination=True
)
class PowerPortTemplateTypeV1(ModularComponentTemplateTypeV1):
    poweroutlet_templates: List[Annotated["PowerOutletTemplateTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]


@strawberry_django.type(
    models.RackType,
    fields='__all__',
    filters=RackTypeFilterV1,
    pagination=True
)
class RackTypeTypeV1(NetBoxObjectTypeV1):
    manufacturer: Annotated["ManufacturerTypeV1", strawberry.lazy('dcim.graphql.types_v1')]


@strawberry_django.type(
    models.Rack,
    fields='__all__',
    filters=RackFilterV1,
    pagination=True
)
class RackTypeV1(VLANGroupsMixinV1, ImageAttachmentsMixinV1, ContactsMixinV1, NetBoxObjectTypeV1):
    site: Annotated["SiteTypeV1", strawberry.lazy('dcim.graphql.types_v1')]
    location: Annotated["LocationTypeV1", strawberry.lazy('dcim.graphql.types_v1')] | None
    tenant: Annotated["TenantTypeV1", strawberry.lazy('tenancy.graphql.types_v1')] | None
    role: Annotated["RackRoleTypeV1", strawberry.lazy('dcim.graphql.types_v1')] | None

    rack_type: Annotated["RackTypeTypeV1", strawberry.lazy('dcim.graphql.types_v1')] | None
    reservations: List[Annotated["RackReservationTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]
    devices: List[Annotated["DeviceTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]
    powerfeeds: List[Annotated["PowerFeedTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]
    cabletermination_set: List[Annotated["CableTerminationTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]


@strawberry_django.type(
    models.RackReservation,
    fields='__all__',
    filters=RackReservationFilterV1,
    pagination=True
)
class RackReservationTypeV1(NetBoxObjectTypeV1):
    units: List[int]
    rack: Annotated["RackTypeV1", strawberry.lazy('dcim.graphql.types_v1')]
    tenant: Annotated["TenantTypeV1", strawberry.lazy('tenancy.graphql.types_v1')] | None
    user: Annotated["UserTypeV1", strawberry.lazy('users.graphql.types_v1')]


@strawberry_django.type(
    models.RackRole,
    fields='__all__',
    filters=RackRoleFilterV1,
    pagination=True
)
class RackRoleTypeV1(OrganizationalObjectTypeV1):
    color: str

    racks: List[Annotated["RackTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]


@strawberry_django.type(
    models.RearPort,
    fields='__all__',
    filters=RearPortFilterV1,
    pagination=True
)
class RearPortTypeV1(ModularComponentTypeV1, CabledObjectMixinV1):
    color: str

    frontports: List[Annotated["FrontPortTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]


@strawberry_django.type(
    models.RearPortTemplate,
    fields='__all__',
    filters=RearPortTemplateFilterV1,
    pagination=True
)
class RearPortTemplateTypeV1(ModularComponentTemplateTypeV1):
    color: str

    frontport_templates: List[Annotated["FrontPortTemplateTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]


@strawberry_django.type(
    models.Region,
    exclude=['parent'],
    filters=RegionFilterV1,
    pagination=True
)
class RegionTypeV1(VLANGroupsMixinV1, ContactsMixinV1, OrganizationalObjectTypeV1):

    sites: List[Annotated["SiteTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]
    children: List[Annotated["RegionTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]

    @strawberry_django.field
    def parent(self) -> Annotated["RegionTypeV1", strawberry.lazy('dcim.graphql.types_v1')] | None:
        return self.parent

    @strawberry_django.field
    def clusters(self) -> List[Annotated["ClusterTypeV1", strawberry.lazy('virtualization.graphql.types_v1')]]:
        return self.cluster_set.all()

    @strawberry_django.field
    def circuit_terminations(self) -> List[
        Annotated["CircuitTerminationTypeV1", strawberry.lazy('circuits.graphql.types_v1')]
    ]:
        return self.circuit_terminations.all()


@strawberry_django.type(
    models.Site,
    fields='__all__',
    filters=SiteFilterV1,
    pagination=True
)
class SiteTypeV1(VLANGroupsMixinV1, ImageAttachmentsMixinV1, ContactsMixinV1, NetBoxObjectTypeV1):
    time_zone: str | None
    region: Annotated["RegionTypeV1", strawberry.lazy('dcim.graphql.types_v1')] | None
    group: Annotated["SiteGroupTypeV1", strawberry.lazy('dcim.graphql.types_v1')] | None
    tenant: Annotated["TenantTypeV1", strawberry.lazy('tenancy.graphql.types_v1')] | None

    prefixes: List[Annotated["PrefixTypeV1", strawberry.lazy('ipam.graphql.types_v1')]]
    virtual_machines: List[Annotated["VirtualMachineTypeV1", strawberry.lazy('virtualization.graphql.types_v1')]]
    racks: List[Annotated["RackTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]
    cabletermination_set: List[Annotated["CableTerminationTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]
    powerpanel_set: List[Annotated["PowerPanelTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]
    devices: List[Annotated["DeviceTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]
    locations: List[Annotated["LocationTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]
    asns: List[Annotated["ASNTypeV1", strawberry.lazy('ipam.graphql.types_v1')]]
    circuit_terminations: List[Annotated["CircuitTerminationTypeV1", strawberry.lazy('circuits.graphql.types_v1')]]
    clusters: List[Annotated["ClusterTypeV1", strawberry.lazy('virtualization.graphql.types_v1')]]
    vlans: List[Annotated["VLANTypeV1", strawberry.lazy('ipam.graphql.types_v1')]]

    @strawberry_django.field
    def clusters(self) -> List[Annotated["ClusterTypeV1", strawberry.lazy('virtualization.graphql.types_v1')]]:
        return self.cluster_set.all()

    @strawberry_django.field
    def circuit_terminations(self) -> List[
        Annotated["CircuitTerminationTypeV1", strawberry.lazy('circuits.graphql.types_v1')]
    ]:
        return self.circuit_terminations.all()


@strawberry_django.type(
    models.SiteGroup,
    exclude=['parent'],  # bug - temp
    filters=SiteGroupFilterV1,
    pagination=True
)
class SiteGroupTypeV1(VLANGroupsMixinV1, ContactsMixinV1, OrganizationalObjectTypeV1):

    sites: List[Annotated["SiteTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]
    children: List[Annotated["SiteGroupTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]

    @strawberry_django.field
    def parent(self) -> Annotated["SiteGroupTypeV1", strawberry.lazy('dcim.graphql.types_v1')] | None:
        return self.parent

    @strawberry_django.field
    def clusters(self) -> List[Annotated["ClusterTypeV1", strawberry.lazy('virtualization.graphql.types_v1')]]:
        return self.cluster_set.all()

    @strawberry_django.field
    def circuit_terminations(self) -> List[
        Annotated["CircuitTerminationTypeV1", strawberry.lazy('circuits.graphql.types_v1')]
    ]:
        return self.circuit_terminations.all()


@strawberry_django.type(
    models.VirtualChassis,
    fields='__all__',
    filters=VirtualChassisFilterV1,
    pagination=True
)
class VirtualChassisTypeV1(NetBoxObjectTypeV1):
    member_count: BigInt
    master: Annotated["DeviceTypeV1", strawberry.lazy('dcim.graphql.types_v1')] | None

    members: List[Annotated["DeviceTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]


@strawberry_django.type(
    models.VirtualDeviceContext,
    fields='__all__',
    filters=VirtualDeviceContextFilterV1,
    pagination=True
)
class VirtualDeviceContextTypeV1(NetBoxObjectTypeV1):
    device: Annotated["DeviceTypeV1", strawberry.lazy('dcim.graphql.types_v1')] | None
    primary_ip4: Annotated["IPAddressTypeV1", strawberry.lazy('ipam.graphql.types_v1')] | None
    primary_ip6: Annotated["IPAddressTypeV1", strawberry.lazy('ipam.graphql.types_v1')] | None
    tenant: Annotated["TenantTypeV1", strawberry.lazy('tenancy.graphql.types_v1')] | None

    interfaces: List[Annotated["InterfaceTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]
