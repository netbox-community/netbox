from typing import Annotated, List, Union

import strawberry
import strawberry_django
from dcim import models
from extras.graphql.mixins import (
    ChangelogMixin,
    ConfigContextMixin,
    ContactsMixin,
    CustomFieldsMixin,
    ImageAttachmentsMixin,
    TagsMixin,
)
from ipam.graphql.mixins import IPAddressesMixin, VLANGroupsMixin

from netbox.graphql.scalars import BigInt
from netbox.graphql.types import (
    BaseObjectType,
    NetBoxObjectType,
    OrganizationalObjectType,
)

from .filters import *
from .mixins import CabledObjectMixin, PathEndpointMixin

__all__ = (
    'CableType',
    'ComponentObjectType',
    'ConsolePortType',
    'ConsolePortTemplateType',
    'ConsoleServerPortType',
    'ConsoleServerPortTemplateType',
    'DeviceType',
    'DeviceBayType',
    'DeviceBayTemplateType',
    'DeviceRoleType',
    'DeviceTypeType',
    'FrontPortType',
    'FrontPortTemplateType',
    'InterfaceType',
    'InterfaceTemplateType',
    'InventoryItemType',
    'InventoryItemRoleType',
    'InventoryItemTemplateType',
    'LocationType',
    'ManufacturerType',
    'ModuleType',
    'ModuleBayType',
    'ModuleBayTemplateType',
    'ModuleTypeType',
    'PlatformType',
    'PowerFeedType',
    'PowerOutletType',
    'PowerOutletTemplateType',
    'PowerPanelType',
    'PowerPortType',
    'PowerPortTemplateType',
    'RackType',
    'RackReservationType',
    'RackRoleType',
    'RearPortType',
    'RearPortTemplateType',
    'RegionType',
    'SiteType',
    'SiteGroupType',
    'VirtualChassisType',
    'VirtualDeviceContextType',
)


#
# Base types
#


@strawberry.type
class ComponentObjectType(
    ChangelogMixin,
    CustomFieldsMixin,
    TagsMixin,
    BaseObjectType
):
    """
    Base type for device/VM components
    """
    _name: str


class ComponentTemplateObjectType(
    ChangelogMixin,
    BaseObjectType
):
    """
    Base type for device/VM components
    """
    _name: str


#
# Model types
#

@strawberry_django.type(
    models.CableTermination,
    exclude=('termination_type', 'termination_id'),
    filters=CableTerminationFilter
)
class CableTerminationType(NetBoxObjectType):

    @strawberry_django.field
    def termination(self) -> List[Annotated[Union[
        Annotated["CircuitTerminationType", strawberry.lazy('circuits.graphql.types')],
        Annotated["ConsolePortType", strawberry.lazy('dcim.graphql.types')],
        Annotated["ConsoleServerPortType", strawberry.lazy('dcim.graphql.types')],
        Annotated["FrontPortType", strawberry.lazy('dcim.graphql.types')],
        Annotated["InterfaceType", strawberry.lazy('dcim.graphql.types')],
        Annotated["PowerFeedType", strawberry.lazy('dcim.graphql.types')],
        Annotated["PowerOutletType", strawberry.lazy('dcim.graphql.types')],
        Annotated["PowerPortType", strawberry.lazy('dcim.graphql.types')],
        Annotated["RearPortType", strawberry.lazy('dcim.graphql.types')],
    ], strawberry.union("CableTerminationTerminationType")]]:
        return self.termination


@strawberry_django.type(
    models.Cable,
    fields='__all__',
    filters=CableFilter
)
class CableType(NetBoxObjectType):
    color: str

    @strawberry_django.field
    def terminations(self) -> List[CableTerminationType]:
        return self.terminations.all()

    @strawberry_django.field
    def a_terminations(self) -> List[Annotated[Union[
        Annotated["CircuitTerminationType", strawberry.lazy('circuits.graphql.types')],
        Annotated["ConsolePortType", strawberry.lazy('dcim.graphql.types')],
        Annotated["ConsoleServerPortType", strawberry.lazy('dcim.graphql.types')],
        Annotated["FrontPortType", strawberry.lazy('dcim.graphql.types')],
        Annotated["InterfaceType", strawberry.lazy('dcim.graphql.types')],
        Annotated["PowerFeedType", strawberry.lazy('dcim.graphql.types')],
        Annotated["PowerOutletType", strawberry.lazy('dcim.graphql.types')],
        Annotated["PowerPortType", strawberry.lazy('dcim.graphql.types')],
        Annotated["RearPortType", strawberry.lazy('dcim.graphql.types')],
    ], strawberry.union("CableTerminationTerminationType")]]:
        return self.a_terminations

    @strawberry_django.field
    def b_terminations(self) -> List[Annotated[Union[
        Annotated["CircuitTerminationType", strawberry.lazy('circuits.graphql.types')],
        Annotated["ConsolePortType", strawberry.lazy('dcim.graphql.types')],
        Annotated["ConsoleServerPortType", strawberry.lazy('dcim.graphql.types')],
        Annotated["FrontPortType", strawberry.lazy('dcim.graphql.types')],
        Annotated["InterfaceType", strawberry.lazy('dcim.graphql.types')],
        Annotated["PowerFeedType", strawberry.lazy('dcim.graphql.types')],
        Annotated["PowerOutletType", strawberry.lazy('dcim.graphql.types')],
        Annotated["PowerPortType", strawberry.lazy('dcim.graphql.types')],
        Annotated["RearPortType", strawberry.lazy('dcim.graphql.types')],
    ], strawberry.union("CableTerminationTerminationType")]]:
        return self.b_terminations


@strawberry_django.type(
    models.ConsolePort,
    exclude=('_path',),
    filters=ConsolePortFilter
)
class ConsolePortType(ComponentObjectType, CabledObjectMixin, PathEndpointMixin):
    pass


@strawberry_django.type(
    models.ConsolePortTemplate,
    fields='__all__',
    filters=ConsolePortTemplateFilter
)
class ConsolePortTemplateType(ComponentTemplateObjectType):
    _name: str


@strawberry_django.type(
    models.ConsoleServerPort,
    exclude=('_path',),
    filters=ConsoleServerPortFilter
)
class ConsoleServerPortType(ComponentObjectType, CabledObjectMixin, PathEndpointMixin):
    pass


@strawberry_django.type(
    models.ConsoleServerPortTemplate,
    fields='__all__',
    filters=ConsoleServerPortTemplateFilter
)
class ConsoleServerPortTemplateType(ComponentTemplateObjectType):
    _name: str


@strawberry_django.type(
    models.Device,
    fields='__all__',
    filters=DeviceFilter
)
class DeviceType(ConfigContextMixin, ImageAttachmentsMixin, ContactsMixin, NetBoxObjectType):
    _name: str
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

    @strawberry_django.field
    def vc_master_for(self) -> Annotated["VirtualChassisType", strawberry.lazy('dcim.graphql.types')] | None:
        return self.vc_master_for if hasattr(self, 'vc_master_for') else None

    @strawberry_django.field
    def virtual_machines(self) -> List[Annotated["VirtualMachineType", strawberry.lazy('virtualization.graphql.types')]]:
        return self.virtual_machines.all()

    @strawberry_django.field
    def modules(self) -> List[Annotated["ModuleType", strawberry.lazy('dcim.graphql.types')]]:
        return self.modules.all()

    @strawberry_django.field
    def parent_bay(self) -> Annotated["DeviceBayType", strawberry.lazy('dcim.graphql.types')] | None:
        return self.parent_bay if hasattr(self, 'parent_bay') else None

    @strawberry_django.field
    def interfaces(self) -> List[Annotated["InterfaceType", strawberry.lazy('dcim.graphql.types')]]:
        return self.interfaces.all()

    @strawberry_django.field
    def rearports(self) -> List[Annotated["RearPortType", strawberry.lazy('dcim.graphql.types')]]:
        return self.rearports.all()

    @strawberry_django.field
    def consoleports(self) -> List[Annotated["ConsolePortType", strawberry.lazy('dcim.graphql.types')]]:
        return self.consoleports.all()

    @strawberry_django.field
    def powerports(self) -> List[Annotated["PowerPortType", strawberry.lazy('dcim.graphql.types')]]:
        return self.powerports.all()

    @strawberry_django.field
    def cabletermination_set(self) -> List[Annotated["CableTerminationType", strawberry.lazy('dcim.graphql.types')]]:
        return self.cabletermination_set.all()

    @strawberry_django.field
    def consoleserverports(self) -> List[Annotated["ConsoleServerPortType", strawberry.lazy('dcim.graphql.types')]]:
        return self.consoleserverports.all()

    @strawberry_django.field
    def poweroutlets(self) -> List[Annotated["PowerOutletType", strawberry.lazy('dcim.graphql.types')]]:
        return self.poweroutlets.all()

    @strawberry_django.field
    def frontports(self) -> List[Annotated["FrontPortType", strawberry.lazy('dcim.graphql.types')]]:
        return self.frontports.all()

    @strawberry_django.field
    def modulebays(self) -> List[Annotated["ModuleBayType", strawberry.lazy('dcim.graphql.types')]]:
        return self.modulebays.all()

    @strawberry_django.field
    def services(self) -> List[Annotated["ServiceType", strawberry.lazy('ipam.graphql.types')]]:
        return self.services.all()

    @strawberry_django.field
    def inventoryitems(self) -> List[Annotated["InventoryItemType", strawberry.lazy('dcim.graphql.types')]]:
        return self.inventoryitems.all()

    @strawberry_django.field
    def vdcs(self) -> List[Annotated["VirtualDeviceContextType", strawberry.lazy('dcim.graphql.types')]]:
        return self.vdcs.all()


@strawberry_django.type(
    models.DeviceBay,
    fields='__all__',
    filters=DeviceBayFilter
)
class DeviceBayType(ComponentObjectType):
    pass


@strawberry_django.type(
    models.DeviceBayTemplate,
    fields='__all__',
    filters=DeviceBayTemplateFilter
)
class DeviceBayTemplateType(ComponentTemplateObjectType):
    _name: str


@strawberry_django.type(
    models.InventoryItemTemplate,
    exclude=('component_type', 'component_id', 'parent'),
    filters=InventoryItemTemplateFilter
)
class InventoryItemTemplateType(ComponentTemplateObjectType):
    _name: str

    @strawberry_django.field
    def parent(self) -> Annotated["InventoryItemTemplateType", strawberry.lazy('dcim.graphql.types')] | None:
        return self.parent

    @strawberry_django.field
    def child_items(self) -> List[Annotated["InventoryItemTemplateType", strawberry.lazy('dcim.graphql.types')]]:
        return self.child_items.all()

    @strawberry_django.field
    def component(self) -> List[Annotated[Union[
        Annotated["ConsolePortType", strawberry.lazy('dcim.graphql.types')],
        Annotated["ConsoleServerPortType", strawberry.lazy('dcim.graphql.types')],
        Annotated["FrontPortType", strawberry.lazy('dcim.graphql.types')],
        Annotated["InterfaceType", strawberry.lazy('dcim.graphql.types')],
        Annotated["PowerOutletType", strawberry.lazy('dcim.graphql.types')],
        Annotated["PowerPortType", strawberry.lazy('dcim.graphql.types')],
        Annotated["RearPortType", strawberry.lazy('dcim.graphql.types')],
    ], strawberry.union("InventoryItemTemplateComponentType")]]:
        return self.component


@strawberry_django.type(
    models.DeviceRole,
    fields='__all__',
    filters=DeviceRoleFilter
)
class DeviceRoleType(OrganizationalObjectType):
    color: str

    @strawberry_django.field
    def virtual_machines(self) -> List[Annotated["VirtualMachineType", strawberry.lazy('virtualization.graphql.types')]]:
        return self.virtual_machines.all()

    @strawberry_django.field
    def devices(self) -> List[Annotated["DeviceType", strawberry.lazy('dcim.graphql.types')]]:
        return self.devices.all()


@strawberry_django.type(
    models.DeviceType,
    fields='__all__',
    filters=DeviceTypeFilter
)
class DeviceTypeType(NetBoxObjectType):
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

    @strawberry_django.field
    def frontporttemplates(self) -> List[Annotated["FrontPortTemplateType", strawberry.lazy('dcim.graphql.types')]]:
        return self.frontporttemplates.all()

    @strawberry_django.field
    def modulebaytemplates(self) -> List[Annotated["ModuleBayTemplateType", strawberry.lazy('dcim.graphql.types')]]:
        return self.modulebaytemplates.all()

    @strawberry_django.field
    def instances(self) -> List[Annotated["DeviceType", strawberry.lazy('dcim.graphql.types')]]:
        return self.instances.all()

    @strawberry_django.field
    def poweroutlettemplates(self) -> List[Annotated["PowerOutletTemplateType", strawberry.lazy('dcim.graphql.types')]]:
        return self.poweroutlettemplates.all()

    @strawberry_django.field
    def powerporttemplates(self) -> List[Annotated["PowerPortTemplateType", strawberry.lazy('dcim.graphql.types')]]:
        return self.powerporttemplates.all()

    @strawberry_django.field
    def inventoryitemtemplates(self) -> List[Annotated["InventoryItemTemplateType", strawberry.lazy('dcim.graphql.types')]]:
        return self.inventoryitemtemplates.all()

    @strawberry_django.field
    def rearporttemplates(self) -> List[Annotated["RearPortTemplateType", strawberry.lazy('dcim.graphql.types')]]:
        return self.rearporttemplates.all()

    @strawberry_django.field
    def consoleserverporttemplates(self) -> List[Annotated["ConsoleServerPortTemplateType", strawberry.lazy('dcim.graphql.types')]]:
        return self.consoleserverporttemplates.all()

    @strawberry_django.field
    def interfacetemplates(self) -> List[Annotated["InterfaceTemplateType", strawberry.lazy('dcim.graphql.types')]]:
        return self.interfacetemplates.all()

    @strawberry_django.field
    def devicebaytemplates(self) -> List[Annotated["DeviceBayTemplateType", strawberry.lazy('dcim.graphql.types')]]:
        return self.devicebaytemplates.all()

    @strawberry_django.field
    def consoleporttemplates(self) -> List[Annotated["ConsolePortTemplateType", strawberry.lazy('dcim.graphql.types')]]:
        return self.consoleporttemplates.all()


@strawberry_django.type(
    models.FrontPort,
    fields='__all__',
    filters=FrontPortFilter
)
class FrontPortType(ComponentObjectType, CabledObjectMixin):
    color: str


@strawberry_django.type(
    models.FrontPortTemplate,
    fields='__all__',
    filters=FrontPortTemplateFilter
)
class FrontPortTemplateType(ComponentTemplateObjectType):
    _name: str
    color: str


@strawberry_django.type(
    models.Interface,
    fields='__all__',
    filters=InterfaceFilter
)
class InterfaceType(IPAddressesMixin, ComponentObjectType, CabledObjectMixin, PathEndpointMixin):
    mac_address: str | None
    wwn: str | None

    @strawberry_django.field
    def vdcs(self) -> List[Annotated["VirtualDeviceContextType", strawberry.lazy('dcim.graphql.types')]]:
        return self.vdcs.all()

    @strawberry_django.field
    def tagged_vlans(self) -> List[Annotated["VLANType", strawberry.lazy('ipam.graphql.types')]]:
        return self.tagged_vlans.all()

    @strawberry_django.field
    def bridge_interfaces(self) -> List[Annotated["InterfaceType", strawberry.lazy('dcim.graphql.types')]]:
        return self.bridge_interfaces.all()

    @strawberry_django.field
    def wireless_lans(self) -> List[Annotated["WirelessLANType", strawberry.lazy('wireless.graphql.types')]]:
        return self.wireless_lans.all()

    @strawberry_django.field
    def member_interfaces(self) -> List[Annotated["InterfaceType", strawberry.lazy('dcim.graphql.types')]]:
        return self.member_interfaces.all()

    @strawberry_django.field
    def child_interfaces(self) -> List[Annotated["InterfaceType", strawberry.lazy('dcim.graphql.types')]]:
        return self.child_interfaces.all()

    @strawberry_django.field
    def ip_addresses(self) -> List[Annotated["IPAddressType", strawberry.lazy('ipam.graphql.types')]]:
        return self.ip_addresses.all()


@strawberry_django.type(
    models.InterfaceTemplate,
    fields='__all__',
    filters=InterfaceTemplateFilter
)
class InterfaceTemplateType(ComponentTemplateObjectType):
    _name: str

    @strawberry_django.field
    def bridge_interfaces(self) -> List[Annotated["InterfaceTemplateType", strawberry.lazy('dcim.graphql.types')]]:
        return self.bridge_interfaces.all()


@strawberry_django.type(
    models.InventoryItem,
    exclude=('component_type', 'component_id', 'parent'),
    filters=InventoryItemFilter
)
class InventoryItemType(ComponentObjectType):
    _name: str

    @strawberry_django.field
    def parent(self) -> Annotated["InventoryItemType", strawberry.lazy('dcim.graphql.types')] | None:
        return self.parent

    @strawberry_django.field
    def child_items(self) -> List[Annotated["InventoryItemType", strawberry.lazy('dcim.graphql.types')]]:
        return self.child_items.all()

    @strawberry_django.field
    def component(self) -> List[Annotated[Union[
        Annotated["ConsolePortType", strawberry.lazy('dcim.graphql.types')],
        Annotated["ConsoleServerPortType", strawberry.lazy('dcim.graphql.types')],
        Annotated["FrontPortType", strawberry.lazy('dcim.graphql.types')],
        Annotated["InterfaceType", strawberry.lazy('dcim.graphql.types')],
        Annotated["PowerOutletType", strawberry.lazy('dcim.graphql.types')],
        Annotated["PowerPortType", strawberry.lazy('dcim.graphql.types')],
        Annotated["RearPortType", strawberry.lazy('dcim.graphql.types')],
    ], strawberry.union("InventoryItemComponentType")]]:
        return self.component


@strawberry_django.type(
    models.InventoryItemRole,
    fields='__all__',
    filters=InventoryItemRoleFilter
)
class InventoryItemRoleType(OrganizationalObjectType):
    color: str

    @strawberry_django.field
    def inventory_items(self) -> List[Annotated["InventoryItemType", strawberry.lazy('dcim.graphql.types')]]:
        return self.inventory_items.all()

    @strawberry_django.field
    def inventory_item_templates(self) -> List[Annotated["InventoryItemTemplateType", strawberry.lazy('dcim.graphql.types')]]:
        return self.inventory_item_templates.all()


@strawberry_django.type(
    models.Location,
    # fields='__all__',
    exclude=('parent',),  # bug - temp
    filters=LocationFilter
)
class LocationType(VLANGroupsMixin, ImageAttachmentsMixin, ContactsMixin, OrganizationalObjectType):

    @strawberry_django.field
    def powerpanel_set(self) -> List[Annotated["PowerPanelType", strawberry.lazy('dcim.graphql.types')]]:
        return self.powerpanel_set.all()

    @strawberry_django.field
    def cabletermination_set(self) -> List[Annotated["CableTerminationType", strawberry.lazy('dcim.graphql.types')]]:
        return self.cabletermination_set.all()

    @strawberry_django.field
    def racks(self) -> List[Annotated["RackType", strawberry.lazy('dcim.graphql.types')]]:
        return self.racks.all()

    @strawberry_django.field
    def vlan_groups(self) -> List[Annotated["VLANGroupType", strawberry.lazy('ipam.graphql.types')]]:
        return self.vlan_groups.all()

    @strawberry_django.field
    def devices(self) -> List[Annotated["DeviceType", strawberry.lazy('dcim.graphql.types')]]:
        return self.devices.all()

    @strawberry_django.field
    def parent(self) -> Annotated["LocationType", strawberry.lazy('dcim.graphql.types')] | None:
        return self.parent

    @strawberry_django.field
    def children(self) -> List[Annotated["LocationType", strawberry.lazy('dcim.graphql.types')]]:
        return self.children.all()


@strawberry_django.type(
    models.Manufacturer,
    fields='__all__',
    filters=ManufacturerFilter
)
class ManufacturerType(OrganizationalObjectType, ContactsMixin):

    @strawberry_django.field
    def platforms(self) -> List[Annotated["PlatformType", strawberry.lazy('dcim.graphql.types')]]:
        return self.platforms.all()

    @strawberry_django.field
    def device_types(self) -> List[Annotated["DeviceType", strawberry.lazy('dcim.graphql.types')]]:
        return self.device_types.all()

    @strawberry_django.field
    def inventory_item_templates(self) -> List[Annotated["InventoryItemTemplateType", strawberry.lazy('dcim.graphql.types')]]:
        return self.inventory_item_templates.all()

    @strawberry_django.field
    def inventory_items(self) -> List[Annotated["InventoryItemType", strawberry.lazy('dcim.graphql.types')]]:
        return self.inventory_items.all()

    @strawberry_django.field
    def module_types(self) -> List[Annotated["ModuleType", strawberry.lazy('dcim.graphql.types')]]:
        return self.module_types.all()


@strawberry_django.type(
    models.Module,
    fields='__all__',
    filters=ModuleFilter
)
class ModuleType(ComponentObjectType):

    @strawberry_django.field
    def interfaces(self) -> List[Annotated["InterfaceType", strawberry.lazy('dcim.graphql.types')]]:
        return self.interfaces.all()

    @strawberry_django.field
    def powerports(self) -> List[Annotated["PowerPortType", strawberry.lazy('dcim.graphql.types')]]:
        return self.powerports.all()

    @strawberry_django.field
    def consoleserverports(self) -> List[Annotated["ConsoleServerPortType", strawberry.lazy('dcim.graphql.types')]]:
        return self.consoleserverports.all()

    @strawberry_django.field
    def consoleports(self) -> List[Annotated["ConsolePortType", strawberry.lazy('dcim.graphql.types')]]:
        return self.consoleports.all()

    @strawberry_django.field
    def poweroutlets(self) -> List[Annotated["PowerOutletType", strawberry.lazy('dcim.graphql.types')]]:
        return self.poweroutlets.all()

    @strawberry_django.field
    def rearports(self) -> List[Annotated["RearPortType", strawberry.lazy('dcim.graphql.types')]]:
        return self.rearports.all()

    @strawberry_django.field
    def frontports(self) -> List[Annotated["FrontPortType", strawberry.lazy('dcim.graphql.types')]]:
        return self.frontports.all()


@strawberry_django.type(
    models.ModuleBay,
    fields='__all__',
    filters=ModuleBayFilter
)
class ModuleBayType(ComponentObjectType):

    @strawberry_django.field
    def installed_module(self) -> Annotated["ModuleType", strawberry.lazy('dcim.graphql.types')] | None:
        return self.installed_module if hasattr(self, 'installed_module') else None


@strawberry_django.type(
    models.ModuleBayTemplate,
    fields='__all__',
    filters=ModuleBayTemplateFilter
)
class ModuleBayTemplateType(ComponentTemplateObjectType):
    _name: str


@strawberry_django.type(
    models.ModuleType,
    fields='__all__',
    filters=ModuleTypeFilter
)
class ModuleTypeType(NetBoxObjectType):

    @strawberry_django.field
    def frontporttemplates(self) -> List[Annotated["FrontPortTemplateType", strawberry.lazy('dcim.graphql.types')]]:
        return self.frontporttemplates.all()

    @strawberry_django.field
    def consoleserverporttemplates(self) -> List[Annotated["ConsoleServerPortTemplateType", strawberry.lazy('dcim.graphql.types')]]:
        return self.consoleserverporttemplates.all()

    @strawberry_django.field
    def interfacetemplates(self) -> List[Annotated["InterfaceTemplateType", strawberry.lazy('dcim.graphql.types')]]:
        return self.interfacetemplates.all()

    @strawberry_django.field
    def powerporttemplates(self) -> List[Annotated["PowerOutletTemplateType", strawberry.lazy('dcim.graphql.types')]]:
        return self.powerporttemplates.all()

    @strawberry_django.field
    def poweroutlettemplates(self) -> List[Annotated["PowerOutletTemplateType", strawberry.lazy('dcim.graphql.types')]]:
        return self.poweroutlettemplates.all()

    @strawberry_django.field
    def rearporttemplates(self) -> List[Annotated["RearPortTemplateType", strawberry.lazy('dcim.graphql.types')]]:
        return self.rearporttemplates.all()

    @strawberry_django.field
    def instances(self) -> List[Annotated["InterfaceType", strawberry.lazy('dcim.graphql.types')]]:
        return self.instances.all()

    @strawberry_django.field
    def consoleporttemplates(self) -> List[Annotated["ModuleType", strawberry.lazy('dcim.graphql.types')]]:
        return self.consoleporttemplates.all()


@strawberry_django.type(
    models.Platform,
    fields='__all__',
    filters=PlatformFilter
)
class PlatformType(OrganizationalObjectType):

    @strawberry_django.field
    def virtual_machines(self) -> List[Annotated["VirtualMachineType", strawberry.lazy('virtualization.graphql.types')]]:
        return self.virtual_machines.all()

    @strawberry_django.field
    def devices(self) -> List[Annotated["DeviceType", strawberry.lazy('dcim.graphql.types')]]:
        return self.devices.all()


@strawberry_django.type(
    models.PowerFeed,
    exclude=('_path',),
    filters=PowerFeedFilter
)
class PowerFeedType(NetBoxObjectType, CabledObjectMixin, PathEndpointMixin):
    pass


@strawberry_django.type(
    models.PowerOutlet,
    fields='__all__',
    filters=PowerOutletFilter
)
class PowerOutletType(ComponentObjectType, CabledObjectMixin, PathEndpointMixin):
    pass


@strawberry_django.type(
    models.PowerOutletTemplate,
    fields='__all__',
    filters=PowerOutletTemplateFilter
)
class PowerOutletTemplateType(ComponentTemplateObjectType):
    _name: str


@strawberry_django.type(
    models.PowerPanel,
    fields='__all__',
    filters=PowerPanelFilter
)
class PowerPanelType(NetBoxObjectType, ContactsMixin):

    @strawberry_django.field
    def powerfeeds(self) -> List[Annotated["PowerFeedType", strawberry.lazy('dcim.graphql.types')]]:
        return self.powerfeeds.all()


@strawberry_django.type(
    models.PowerPort,
    exclude=('_path',),
    filters=PowerPortFilter
)
class PowerPortType(ComponentObjectType, CabledObjectMixin, PathEndpointMixin):

    @strawberry_django.field
    def poweroutlets(self) -> List[Annotated["PowerOutletType", strawberry.lazy('dcim.graphql.types')]]:
        return self.poweroutlets.all()


@strawberry_django.type(
    models.PowerPortTemplate,
    fields='__all__',
    filters=PowerPortTemplateFilter
)
class PowerPortTemplateType(ComponentTemplateObjectType):
    _name: str

    @strawberry_django.field
    def poweroutlet_templates(self) -> List[Annotated["PowerOutletTemplateType", strawberry.lazy('dcim.graphql.types')]]:
        return self.poweroutlet_templates.all()


@strawberry_django.type(
    models.Rack,
    fields='__all__',
    filters=RackFilter
)
class RackType(VLANGroupsMixin, ImageAttachmentsMixin, ContactsMixin, NetBoxObjectType):
    _name: str

    @strawberry_django.field
    def reservations(self) -> List[Annotated["RackReservationType", strawberry.lazy('dcim.graphql.types')]]:
        return self.reservations.all()

    @strawberry_django.field
    def devices(self) -> List[Annotated["DeviceType", strawberry.lazy('dcim.graphql.types')]]:
        return self.devices.all()

    @strawberry_django.field
    def powerfeeds(self) -> List[Annotated["PowerFeedType", strawberry.lazy('dcim.graphql.types')]]:
        return self.powerfeeds.all()

    @strawberry_django.field
    def cabletermination_set(self) -> List[Annotated["CableTerminationType", strawberry.lazy('dcim.graphql.types')]]:
        return self.cabletermination_set.all()

    @strawberry_django.field
    def vlan_groups(self) -> List[Annotated["VLANGroupType", strawberry.lazy('ipam.graphql.types')]]:
        return self.vlan_groups.all()


@strawberry_django.type(
    models.RackReservation,
    fields='__all__',
    filters=RackReservationFilter
)
class RackReservationType(NetBoxObjectType):
    units: List[int]


@strawberry_django.type(
    models.RackRole,
    fields='__all__',
    filters=RackRoleFilter
)
class RackRoleType(OrganizationalObjectType):
    color: str

    @strawberry_django.field
    def racks(self) -> List[Annotated["RackType", strawberry.lazy('dcim.graphql.types')]]:
        return self.racks.all()


@strawberry_django.type(
    models.RearPort,
    fields='__all__',
    filters=RearPortFilter
)
class RearPortType(ComponentObjectType, CabledObjectMixin):
    color: str

    @strawberry_django.field
    def frontports(self) -> List[Annotated["FrontPortType", strawberry.lazy('dcim.graphql.types')]]:
        return self.frontports.all()


@strawberry_django.type(
    models.RearPortTemplate,
    fields='__all__',
    filters=RearPortTemplateFilter
)
class RearPortTemplateType(ComponentTemplateObjectType):
    _name: str
    color: str

    @strawberry_django.field
    def frontport_templates(self) -> List[Annotated["FrontPortTemplateType", strawberry.lazy('dcim.graphql.types')]]:
        return self.frontport_templates.all()


@strawberry_django.type(
    models.Region,
    exclude=('parent',),
    # fields='__all__',
    filters=RegionFilter
)
class RegionType(VLANGroupsMixin, ContactsMixin, OrganizationalObjectType):

    @strawberry_django.field
    def sites(self) -> List[Annotated["SiteType", strawberry.lazy('dcim.graphql.types')]]:
        return self.sites.all()

    @strawberry_django.field
    def vlan_groups(self) -> List[Annotated["VLANGroupType", strawberry.lazy('ipam.graphql.types')]]:
        return self.vlan_groups.all()

    @strawberry_django.field
    def parent(self) -> Annotated["RegionType", strawberry.lazy('dcim.graphql.types')] | None:
        return self.parent

    @strawberry_django.field
    def children(self) -> List[Annotated["RegionType", strawberry.lazy('dcim.graphql.types')]]:
        return self.children.all()


@strawberry_django.type(
    models.Site,
    fields='__all__',
    filters=SiteFilter
)
class SiteType(VLANGroupsMixin, ImageAttachmentsMixin, ContactsMixin, NetBoxObjectType):
    _name: str
    time_zone: str | None

    @strawberry_django.field
    def prefixes(self) -> List[Annotated["PrefixType", strawberry.lazy('ipam.graphql.types')]]:
        return self.prefixes.all()

    @strawberry_django.field
    def virtual_machines(self) -> List[Annotated["VirtualMachineType", strawberry.lazy('virtualization.graphql.types')]]:
        return self.virtual_machines.all()

    @strawberry_django.field
    def racks(self) -> List[Annotated["RackType", strawberry.lazy('dcim.graphql.types')]]:
        return self.racks.all()

    @strawberry_django.field
    def cabletermination_set(self) -> List[Annotated["CableTerminationType", strawberry.lazy('dcim.graphql.types')]]:
        return self.cabletermination_set.all()

    @strawberry_django.field
    def powerpanel_set(self) -> List[Annotated["PowerPanelType", strawberry.lazy('dcim.graphql.types')]]:
        return self.powerpanel_set.all()

    @strawberry_django.field
    def devices(self) -> List[Annotated["DeviceType", strawberry.lazy('dcim.graphql.types')]]:
        return self.devices.all()

    @strawberry_django.field
    def locations(self) -> List[Annotated["LocationType", strawberry.lazy('dcim.graphql.types')]]:
        return self.locations.all()

    @strawberry_django.field
    def asns(self) -> List[Annotated["ASNType", strawberry.lazy('ipam.graphql.types')]]:
        return self.asns.all()

    @strawberry_django.field
    def circuit_terminations(self) -> List[Annotated["CircuitTerminationType", strawberry.lazy('circuits.graphql.types')]]:
        return self.circuit_terminations.all()

    @strawberry_django.field
    def clusters(self) -> List[Annotated["ClusterType", strawberry.lazy('virtualization.graphql.types')]]:
        return self.clusters.all()

    @strawberry_django.field
    def vlans(self) -> List[Annotated["VLANType", strawberry.lazy('ipam.graphql.types')]]:
        return self.vlans.all()

    @strawberry_django.field
    def vlan_groups(self) -> List[Annotated["VLANGroupType", strawberry.lazy('ipam.graphql.types')]]:
        return self.vlan_groups.all()


@strawberry_django.type(
    models.SiteGroup,
    # fields='__all__',
    exclude=('parent',),  # bug - temp
    filters=SiteGroupFilter
)
class SiteGroupType(VLANGroupsMixin, ContactsMixin, OrganizationalObjectType):

    @strawberry_django.field
    def sites(self) -> List[Annotated["SiteType", strawberry.lazy('dcim.graphql.types')]]:
        return self.sites.all()

    @strawberry_django.field
    def vlan_groups(self) -> List[Annotated["VLANGroupType", strawberry.lazy('ipam.graphql.types')]]:
        return self.vlan_groups.all()

    @strawberry_django.field
    def parent(self) -> Annotated["SiteGroupType", strawberry.lazy('dcim.graphql.types')] | None:
        return self.parent

    @strawberry_django.field
    def children(self) -> List[Annotated["SiteGroupType", strawberry.lazy('dcim.graphql.types')]]:
        return self.children.all()


@strawberry_django.type(
    models.VirtualChassis,
    fields='__all__',
    filters=VirtualChassisFilter
)
class VirtualChassisType(NetBoxObjectType):
    member_count: BigInt

    @strawberry_django.field
    def members(self) -> List[Annotated["DeviceType", strawberry.lazy('dcim.graphql.types')]]:
        return self.members.all()


@strawberry_django.type(
    models.VirtualDeviceContext,
    fields='__all__',
    filters=VirtualDeviceContextFilter
)
class VirtualDeviceContextType(NetBoxObjectType):

    @strawberry_django.field
    def interfaces(self) -> List[Annotated["InterfaceType", strawberry.lazy('dcim.graphql.types')]]:
        return self.interfaces.all()
