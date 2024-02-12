import strawberry
import strawberry_django

from dcim import models
from extras.graphql.mixins import (
    ChangelogMixin, ConfigContextMixin, ContactsMixin, CustomFieldsMixin, ImageAttachmentsMixin, TagsMixin,
)
from ipam.graphql.mixins import IPAddressesMixin, VLANGroupsMixin
from netbox.graphql.types import BaseObjectType, OrganizationalObjectType, NetBoxObjectType
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


class ComponentObjectType(
    ChangelogMixin,
    CustomFieldsMixin,
    TagsMixin,
    BaseObjectType
):
    """
    Base type for device/VM components
    """
    class Meta:
        abstract = True


class ComponentTemplateObjectType(
    ChangelogMixin,
    BaseObjectType
):
    """
    Base type for device/VM components
    """
    class Meta:
        abstract = True


#
# Model types
#

@strawberry_django.type(
    models.Cable,
    # fields='__all__',
    exclude=('color', ),  # bug - temp
    filters=CableFilter
)
class CableType(NetBoxObjectType):
    # a_terminations = graphene.List('dcim.graphql.gfk_mixins.CableTerminationTerminationType')
    # b_terminations = graphene.List('dcim.graphql.gfk_mixins.CableTerminationTerminationType')

    def resolve_type(self, info):
        return self.type or None

    def resolve_length_unit(self, info):
        return self.length_unit or None

    def resolve_a_terminations(self, info):
        return self.a_terminations

    def resolve_b_terminations(self, info):
        return self.b_terminations


@strawberry_django.type(
    models.CableTermination,
    exclude=('termination_type', 'termination_id'),
    filters=CableTerminationFilter
)
class CableTerminationType(NetBoxObjectType):
    # termination = graphene.Field('dcim.graphql.gfk_mixins.CableTerminationTerminationType')
    pass


@strawberry_django.type(
    models.ConsolePort,
    # exclude=('_path',),
    exclude=('_path', '_name',),  # bug - temp
    filters=ConsolePortFilter
)
class ConsolePortType(ComponentObjectType, CabledObjectMixin, PathEndpointMixin):

    def resolve_type(self, info):
        return self.type or None


@strawberry_django.type(
    models.ConsolePortTemplate,
    # fields='__all__',
    exclude=('_name',),  # bug - temp
    filters=ConsolePortTemplateFilter
)
class ConsolePortTemplateType(ComponentTemplateObjectType):

    def resolve_type(self, info):
        return self.type or None


@strawberry_django.type(
    models.ConsoleServerPort,
    # exclude=('_path',),
    exclude=('_path', '_name',),  # bug - temp
    filters=ConsoleServerPortFilter
)
class ConsoleServerPortType(ComponentObjectType, CabledObjectMixin, PathEndpointMixin):

    def resolve_type(self, info):
        return self.type or None


@strawberry_django.type(
    models.ConsoleServerPortTemplate,
    # fields='__all__',
    exclude=('_name',),  # bug - temp
    filters=ConsoleServerPortTemplateFilter
)
class ConsoleServerPortTemplateType(ComponentTemplateObjectType):

    def resolve_type(self, info):
        return self.type or None


@strawberry_django.type(
    models.Device,
    # fields='__all__',
    exclude=(
        '_name', 'console_port_count', 'console_server_port_count', 'power_port_count', 'power_outlet_count',
        'interface_count', 'front_port_count', 'rear_port_count', 'device_bay_count', 'module_bay_count',
        'inventory_item_count'
    ),  # bug - temp
    filters=DeviceFilter
)
class DeviceType(ConfigContextMixin, ImageAttachmentsMixin, ContactsMixin, NetBoxObjectType):

    def resolve_face(self, info):
        return self.face or None

    def resolve_airflow(self, info):
        return self.airflow or None


@strawberry_django.type(
    models.DeviceBay,
    # fields='__all__',
    exclude=('_name',),  # bug - temp
    filters=DeviceBayFilter
)
class DeviceBayType(ComponentObjectType):
    pass


@strawberry_django.type(
    models.DeviceBayTemplate,
    # fields='__all__',
    exclude=('_name',),  # bug - temp
    filters=DeviceBayTemplateFilter
)
class DeviceBayTemplateType(ComponentTemplateObjectType):
    pass


@strawberry_django.type(
    models.InventoryItemTemplate,
    exclude=('component_type', 'component_id', '_name', 'parent'),
    filters=InventoryItemTemplateFilter
)
class InventoryItemTemplateType(ComponentTemplateObjectType):
    # component = graphene.Field('dcim.graphql.gfk_mixins.InventoryItemTemplateComponentType')
    pass


@strawberry_django.type(
    models.DeviceRole,
    # fields='__all__',
    exclude=('color',),  # bug - temp
    filters=DeviceRoleFilter
)
class DeviceRoleType(OrganizationalObjectType):
    pass


@strawberry_django.type(
    models.DeviceType,
    # fields='__all__',
    exclude=(
        'console_port_template_count', 'console_server_port_template_count', 'power_port_template_count',
        'power_outlet_template_count', 'interface_template_count', 'front_port_template_count',
        'rear_port_template_count', 'device_bay_template_count', 'module_bay_template_count',
        'inventory_item_template_count',
    ),  # bug - temp
    filters=DeviceTypeFilter
)
class DeviceTypeType(NetBoxObjectType):

    def resolve_subdevice_role(self, info):
        return self.subdevice_role or None

    def resolve_airflow(self, info):
        return self.airflow or None

    def resolve_weight_unit(self, info):
        return self.weight_unit or None


@strawberry_django.type(
    models.FrontPort,
    # fields='__all__',
    exclude=('_name', 'color'),  # bug - temp
    filters=FrontPortFilter
)
class FrontPortType(ComponentObjectType, CabledObjectMixin):
    pass


@strawberry_django.type(
    models.FrontPortTemplate,
    # fields='__all__',
    exclude=('_name', 'color'),  # bug - temp
    filters=FrontPortTemplateFilter
)
class FrontPortTemplateType(ComponentTemplateObjectType):
    pass


@strawberry_django.type(
    models.Interface,
    # fields='__all__',
    exclude=('mac_address', '_name', 'wwn'),  # bug - temp
    filters=InterfaceFilter
)
class InterfaceType(IPAddressesMixin, ComponentObjectType, CabledObjectMixin, PathEndpointMixin):

    def resolve_poe_mode(self, info):
        return self.poe_mode or None

    def resolve_poe_type(self, info):
        return self.poe_type or None

    def resolve_mode(self, info):
        return self.mode or None

    def resolve_rf_role(self, info):
        return self.rf_role or None

    def resolve_rf_channel(self, info):
        return self.rf_channel or None


@strawberry_django.type(
    models.InterfaceTemplate,
    # fields='__all__',
    exclude=('_name',),  # bug - temp
    filters=InterfaceTemplateFilter
)
class InterfaceTemplateType(ComponentTemplateObjectType):

    def resolve_poe_mode(self, info):
        return self.poe_mode or None

    def resolve_poe_type(self, info):
        return self.poe_type or None

    def resolve_rf_role(self, info):
        return self.rf_role or None


@strawberry_django.type(
    models.InventoryItem,
    exclude=('component_type', 'component_id', '_name', 'parent'),
    filters=InventoryItemFilter
)
class InventoryItemType(ComponentObjectType):
    # component = graphene.Field('dcim.graphql.gfk_mixins.InventoryItemComponentType')
    pass


@strawberry_django.type(
    models.InventoryItemRole,
    # fields='__all__',
    exclude=('color', '_name'),  # bug - temp
    filters=InventoryItemRoleFilter
)
class InventoryItemRoleType(OrganizationalObjectType):
    pass


@strawberry_django.type(
    models.Location,
    # fields='__all__',
    exclude=('parent',),  # bug - temp
    filters=LocationFilter
)
class LocationType(VLANGroupsMixin, ImageAttachmentsMixin, ContactsMixin, OrganizationalObjectType):
    pass


@strawberry_django.type(
    models.Manufacturer,
    fields='__all__',
    filters=ManufacturerFilter
)
class ManufacturerType(OrganizationalObjectType, ContactsMixin):
    pass


@strawberry_django.type(
    models.Module,
    fields='__all__',
    filters=ModuleFilter
)
class ModuleType(ComponentObjectType):
    pass


@strawberry_django.type(
    models.ModuleBay,
    # fields='__all__',
    exclude=('_name',),  # bug - temp
    filters=ModuleBayFilter
)
class ModuleBayType(ComponentObjectType):
    pass


@strawberry_django.type(
    models.ModuleBayTemplate,
    # fields='__all__',
    exclude=('_name',),  # bug - temp
    filters=ModuleBayTemplateFilter
)
class ModuleBayTemplateType(ComponentTemplateObjectType):
    pass


@strawberry_django.type(
    models.ModuleType,
    fields='__all__',
    filters=ModuleTypeFilter
)
class ModuleTypeType(NetBoxObjectType):

    def resolve_weight_unit(self, info):
        return self.weight_unit or None


@strawberry_django.type(
    models.Platform,
    fields='__all__',
    filters=PlatformFilter
)
class PlatformType(OrganizationalObjectType):
    pass


@strawberry_django.type(
    models.PowerFeed,
    exclude=('_path',),
    filters=PowerFeedFilter
)
class PowerFeedType(NetBoxObjectType, CabledObjectMixin, PathEndpointMixin):
    pass


@strawberry_django.type(
    models.PowerOutlet,
    # fields='__all__',
    exclude=('_name',),  # bug - temp
    filters=PowerOutletFilter
)
class PowerOutletType(ComponentObjectType, CabledObjectMixin, PathEndpointMixin):

    def resolve_feed_leg(self, info):
        return self.feed_leg or None

    def resolve_type(self, info):
        return self.type or None


@strawberry_django.type(
    models.PowerOutletTemplate,
    # fields='__all__',
    exclude=('_name',),  # bug - temp
    filters=PowerOutletTemplateFilter
)
class PowerOutletTemplateType(ComponentTemplateObjectType):

    def resolve_feed_leg(self, info):
        return self.feed_leg or None

    def resolve_type(self, info):
        return self.type or None


@strawberry_django.type(
    models.PowerPanel,
    fields='__all__',
    filters=PowerPanelFilter
)
class PowerPanelType(NetBoxObjectType, ContactsMixin):
    pass


@strawberry_django.type(
    models.PowerPort,
    exclude=('_path', '_name'),
    filters=PowerPortFilter
)
class PowerPortType(ComponentObjectType, CabledObjectMixin, PathEndpointMixin):

    def resolve_type(self, info):
        return self.type or None


@strawberry_django.type(
    models.PowerPortTemplate,
    # fields='__all__',
    exclude=('_name',),  # bug - temp
    filters=PowerPortTemplateFilter
)
class PowerPortTemplateType(ComponentTemplateObjectType):

    def resolve_type(self, info):
        return self.type or None


@strawberry_django.type(
    models.Rack,
    # fields='__all__',
    exclude=('_name',),  # bug - temp
    filters=RackFilter
)
class RackType(VLANGroupsMixin, ImageAttachmentsMixin, ContactsMixin, NetBoxObjectType):

    def resolve_type(self, info):
        return self.type or None

    def resolve_outer_unit(self, info):
        return self.outer_unit or None

    def resolve_weight_unit(self, info):
        return self.weight_unit or None


@strawberry_django.type(
    models.RackReservation,
    # fields='__all__',
    exclude=('units',),  # bug - temp
    filters=RackReservationFilter
)
class RackReservationType(NetBoxObjectType):
    pass


@strawberry_django.type(
    models.RackRole,
    # fields='__all__',
    exclude=('color',),  # bug - temp
    filters=RackRoleFilter
)
class RackRoleType(OrganizationalObjectType):
    pass


@strawberry_django.type(
    models.RearPort,
    # fields='__all__',
    exclude=('_name', 'color'),  # bug - temp
    filters=RearPortFilter
)
class RearPortType(ComponentObjectType, CabledObjectMixin):
    pass


@strawberry_django.type(
    models.RearPortTemplate,
    # fields='__all__',
    exclude=('_name', 'color'),  # bug - temp
    filters=RearPortTemplateFilter
)
class RearPortTemplateType(ComponentTemplateObjectType):
    pass


@strawberry_django.type(
    models.Region,
    # fields='__all__',
    exclude=('parent',),  # bug - temp
    filters=RegionFilter
)
class RegionType(VLANGroupsMixin, ContactsMixin, OrganizationalObjectType):
    pass


@strawberry_django.type(
    models.Site,
    # fields='__all__',
    exclude=('_name', 'time_zone'),  # bug - temp
    filters=SiteFilter
)
class SiteType(VLANGroupsMixin, ImageAttachmentsMixin, ContactsMixin, NetBoxObjectType):
    # asn = graphene.Field(BigInt)
    pass


@strawberry_django.type(
    models.SiteGroup,
    # fields='__all__',
    exclude=('parent',),  # bug - temp
    filters=SiteGroupFilter
)
class SiteGroupType(VLANGroupsMixin, ContactsMixin, OrganizationalObjectType):
    pass


@strawberry_django.type(
    models.VirtualChassis,
    # fields='__all__',
    exclude=('member_count',),  # bug - temp
    filters=VirtualChassisFilter
)
class VirtualChassisType(NetBoxObjectType):
    pass


@strawberry_django.type(
    models.VirtualDeviceContext,
    fields='__all__',
    filters=VirtualDeviceContextFilter
)
class VirtualDeviceContextType(NetBoxObjectType):
    pass
