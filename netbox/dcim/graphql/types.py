import graphene

from dcim import filtersets, models
from extras.graphql.mixins import (
    ChangelogMixin, ConfigContextMixin, ContactsMixin, CustomFieldsMixin, ImageAttachmentsMixin, TagsMixin,
)
from ipam.graphql.mixins import IPAddressesMixin, VLANGroupsMixin
from netbox.graphql.scalars import BigInt
from netbox.graphql.types import BaseObjectType, OrganizationalObjectType, NetBoxObjectType
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

class CableType(NetBoxObjectType):
    a_terminations = graphene.List('dcim.graphql.gfk_mixins.CableTerminationTerminationType')
    b_terminations = graphene.List('dcim.graphql.gfk_mixins.CableTerminationTerminationType')

    class Meta:
        model = models.Cable
        fields = '__all__'
        filterset_class = filtersets.CableFilterSet

    def resolve_type(self, info):
        return self.type or None

    def resolve_length_unit(self, info):
        return self.length_unit or None

    def resolve_a_terminations(self, info):
        return self.a_terminations

    def resolve_b_terminations(self, info):
        return self.b_terminations


class CableTerminationType(NetBoxObjectType):
    termination = graphene.Field('dcim.graphql.gfk_mixins.CableTerminationTerminationType')

    class Meta:
        model = models.CableTermination
        exclude = ('termination_type', 'termination_id')
        filterset_class = filtersets.CableTerminationFilterSet


class ConsolePortType(ComponentObjectType, CabledObjectMixin, PathEndpointMixin):

    class Meta:
        model = models.ConsolePort
        exclude = ('_path',)
        filterset_class = filtersets.ConsolePortFilterSet

    def resolve_type(self, info):
        return self.type or None


class ConsolePortTemplateType(ComponentTemplateObjectType):

    class Meta:
        model = models.ConsolePortTemplate
        fields = '__all__'
        filterset_class = filtersets.ConsolePortTemplateFilterSet

    def resolve_type(self, info):
        return self.type or None


class ConsoleServerPortType(ComponentObjectType, CabledObjectMixin, PathEndpointMixin):

    class Meta:
        model = models.ConsoleServerPort
        exclude = ('_path',)
        filterset_class = filtersets.ConsoleServerPortFilterSet

    def resolve_type(self, info):
        return self.type or None


class ConsoleServerPortTemplateType(ComponentTemplateObjectType):

    class Meta:
        model = models.ConsoleServerPortTemplate
        fields = '__all__'
        filterset_class = filtersets.ConsoleServerPortTemplateFilterSet

    def resolve_type(self, info):
        return self.type or None


class DeviceType(ConfigContextMixin, ImageAttachmentsMixin, ContactsMixin, NetBoxObjectType):

    class Meta:
        model = models.Device
        fields = '__all__'
        filterset_class = filtersets.DeviceFilterSet

    def resolve_face(self, info):
        return self.face or None

    def resolve_airflow(self, info):
        return self.airflow or None


class DeviceBayType(ComponentObjectType):

    class Meta:
        model = models.DeviceBay
        fields = '__all__'
        filterset_class = filtersets.DeviceBayFilterSet


class DeviceBayTemplateType(ComponentTemplateObjectType):

    class Meta:
        model = models.DeviceBayTemplate
        fields = '__all__'
        filterset_class = filtersets.DeviceBayTemplateFilterSet


class InventoryItemTemplateType(ComponentTemplateObjectType):
    component = graphene.Field('dcim.graphql.gfk_mixins.InventoryItemTemplateComponentType')

    class Meta:
        model = models.InventoryItemTemplate
        exclude = ('component_type', 'component_id')
        filterset_class = filtersets.InventoryItemTemplateFilterSet


class DeviceRoleType(OrganizationalObjectType):

    class Meta:
        model = models.DeviceRole
        fields = '__all__'
        filterset_class = filtersets.DeviceRoleFilterSet


class DeviceTypeType(NetBoxObjectType):

    class Meta:
        model = models.DeviceType
        fields = '__all__'
        filterset_class = filtersets.DeviceTypeFilterSet

    def resolve_subdevice_role(self, info):
        return self.subdevice_role or None

    def resolve_airflow(self, info):
        return self.airflow or None

    def resolve_weight_unit(self, info):
        return self.weight_unit or None


class FrontPortType(ComponentObjectType, CabledObjectMixin):

    class Meta:
        model = models.FrontPort
        fields = '__all__'
        filterset_class = filtersets.FrontPortFilterSet


class FrontPortTemplateType(ComponentTemplateObjectType):

    class Meta:
        model = models.FrontPortTemplate
        fields = '__all__'
        filterset_class = filtersets.FrontPortTemplateFilterSet


class InterfaceType(IPAddressesMixin, ComponentObjectType, CabledObjectMixin, PathEndpointMixin):

    class Meta:
        model = models.Interface
        exclude = ('_path',)
        filterset_class = filtersets.InterfaceFilterSet

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


class InterfaceTemplateType(ComponentTemplateObjectType):

    class Meta:
        model = models.InterfaceTemplate
        fields = '__all__'
        filterset_class = filtersets.InterfaceTemplateFilterSet

    def resolve_poe_mode(self, info):
        return self.poe_mode or None

    def resolve_poe_type(self, info):
        return self.poe_type or None


class InventoryItemType(ComponentObjectType):
    component = graphene.Field('dcim.graphql.gfk_mixins.InventoryItemComponentType')

    class Meta:
        model = models.InventoryItem
        exclude = ('component_type', 'component_id')
        filterset_class = filtersets.InventoryItemFilterSet


class InventoryItemRoleType(OrganizationalObjectType):

    class Meta:
        model = models.InventoryItemRole
        fields = '__all__'
        filterset_class = filtersets.InventoryItemRoleFilterSet


class LocationType(VLANGroupsMixin, ImageAttachmentsMixin, ContactsMixin, OrganizationalObjectType):

    class Meta:
        model = models.Location
        fields = '__all__'
        filterset_class = filtersets.LocationFilterSet


class ManufacturerType(OrganizationalObjectType, ContactsMixin):

    class Meta:
        model = models.Manufacturer
        fields = '__all__'
        filterset_class = filtersets.ManufacturerFilterSet


class ModuleType(ComponentObjectType):

    class Meta:
        model = models.Module
        fields = '__all__'
        filterset_class = filtersets.ModuleFilterSet


class ModuleBayType(ComponentObjectType):

    class Meta:
        model = models.ModuleBay
        fields = '__all__'
        filterset_class = filtersets.ModuleBayFilterSet


class ModuleBayTemplateType(ComponentTemplateObjectType):

    class Meta:
        model = models.ModuleBayTemplate
        fields = '__all__'
        filterset_class = filtersets.ModuleBayTemplateFilterSet


class ModuleTypeType(NetBoxObjectType):

    class Meta:
        model = models.ModuleType
        fields = '__all__'
        filterset_class = filtersets.ModuleTypeFilterSet

    def resolve_weight_unit(self, info):
        return self.weight_unit or None


class PlatformType(OrganizationalObjectType):

    class Meta:
        model = models.Platform
        fields = '__all__'
        filterset_class = filtersets.PlatformFilterSet


class PowerFeedType(NetBoxObjectType, CabledObjectMixin, PathEndpointMixin):

    class Meta:
        model = models.PowerFeed
        exclude = ('_path',)
        filterset_class = filtersets.PowerFeedFilterSet


class PowerOutletType(ComponentObjectType, CabledObjectMixin, PathEndpointMixin):

    class Meta:
        model = models.PowerOutlet
        exclude = ('_path',)
        filterset_class = filtersets.PowerOutletFilterSet

    def resolve_feed_leg(self, info):
        return self.feed_leg or None

    def resolve_type(self, info):
        return self.type or None


class PowerOutletTemplateType(ComponentTemplateObjectType):

    class Meta:
        model = models.PowerOutletTemplate
        fields = '__all__'
        filterset_class = filtersets.PowerOutletTemplateFilterSet

    def resolve_feed_leg(self, info):
        return self.feed_leg or None

    def resolve_type(self, info):
        return self.type or None


class PowerPanelType(NetBoxObjectType, ContactsMixin):

    class Meta:
        model = models.PowerPanel
        fields = '__all__'
        filterset_class = filtersets.PowerPanelFilterSet


class PowerPortType(ComponentObjectType, CabledObjectMixin, PathEndpointMixin):

    class Meta:
        model = models.PowerPort
        exclude = ('_path',)
        filterset_class = filtersets.PowerPortFilterSet

    def resolve_type(self, info):
        return self.type or None


class PowerPortTemplateType(ComponentTemplateObjectType):

    class Meta:
        model = models.PowerPortTemplate
        fields = '__all__'
        filterset_class = filtersets.PowerPortTemplateFilterSet

    def resolve_type(self, info):
        return self.type or None


class RackType(VLANGroupsMixin, ImageAttachmentsMixin, ContactsMixin, NetBoxObjectType):

    class Meta:
        model = models.Rack
        fields = '__all__'
        filterset_class = filtersets.RackFilterSet

    def resolve_type(self, info):
        return self.type or None

    def resolve_outer_unit(self, info):
        return self.outer_unit or None

    def resolve_weight_unit(self, info):
        return self.weight_unit or None


class RackReservationType(NetBoxObjectType):

    class Meta:
        model = models.RackReservation
        fields = '__all__'
        filterset_class = filtersets.RackReservationFilterSet


class RackRoleType(OrganizationalObjectType):

    class Meta:
        model = models.RackRole
        fields = '__all__'
        filterset_class = filtersets.RackRoleFilterSet


class RearPortType(ComponentObjectType, CabledObjectMixin):

    class Meta:
        model = models.RearPort
        fields = '__all__'
        filterset_class = filtersets.RearPortFilterSet


class RearPortTemplateType(ComponentTemplateObjectType):

    class Meta:
        model = models.RearPortTemplate
        fields = '__all__'
        filterset_class = filtersets.RearPortTemplateFilterSet


class RegionType(VLANGroupsMixin, ContactsMixin, OrganizationalObjectType):

    class Meta:
        model = models.Region
        fields = '__all__'
        filterset_class = filtersets.RegionFilterSet


class SiteType(VLANGroupsMixin, ImageAttachmentsMixin, ContactsMixin, NetBoxObjectType):
    asn = graphene.Field(BigInt)

    class Meta:
        model = models.Site
        fields = '__all__'
        filterset_class = filtersets.SiteFilterSet


class SiteGroupType(VLANGroupsMixin, ContactsMixin, OrganizationalObjectType):

    class Meta:
        model = models.SiteGroup
        fields = '__all__'
        filterset_class = filtersets.SiteGroupFilterSet


class VirtualChassisType(NetBoxObjectType):

    class Meta:
        model = models.VirtualChassis
        fields = '__all__'
        filterset_class = filtersets.VirtualChassisFilterSet


class VirtualDeviceContextType(NetBoxObjectType):

    class Meta:
        model = models.VirtualDeviceContext
        fields = '__all__'
        filterset_class = filtersets.VirtualDeviceContextFilterSet
