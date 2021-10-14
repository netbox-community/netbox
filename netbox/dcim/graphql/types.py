from dcim import filtersets, models
from extras.graphql.mixins import (
    ChangelogMixin, ConfigContextMixin, CustomFieldsMixin, ImageAttachmentsMixin, TagsMixin,
)
from ipam.graphql.mixins import IPAddressesMixin, VLANGroupsMixin
from netbox.graphql.types import BaseObjectType, OrganizationalObjectType, PrimaryObjectType

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
    'LocationType',
    'ManufacturerType',
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

class CableType(PrimaryObjectType):

    class Meta:
        model = models.Cable
        fields = '__all__'
        filterset_class = filtersets.CableFilterSet

    def resolve_type(self, info):
        return self.type or None

    def resolve_length_unit(self, info):
        return self.length_unit or None


class ConsolePortType(ComponentObjectType):

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


class ConsoleServerPortType(ComponentObjectType):

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


class DeviceType(ConfigContextMixin, ImageAttachmentsMixin, PrimaryObjectType):

    class Meta:
        model = models.Device
        fields = '__all__'
        filterset_class = filtersets.DeviceFilterSet

    def resolve_face(self, info):
        return self.face or None


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


class DeviceRoleType(OrganizationalObjectType):

    class Meta:
        model = models.DeviceRole
        fields = '__all__'
        filterset_class = filtersets.DeviceRoleFilterSet


class DeviceTypeType(PrimaryObjectType):

    class Meta:
        model = models.DeviceType
        fields = '__all__'
        filterset_class = filtersets.DeviceTypeFilterSet

    def resolve_subdevice_role(self, info):
        return self.subdevice_role or None

    def resolve_airflow(self, info):
        return self.airflow or None


class FrontPortType(ComponentObjectType):

    class Meta:
        model = models.FrontPort
        fields = '__all__'
        filterset_class = filtersets.FrontPortFilterSet


class FrontPortTemplateType(ComponentTemplateObjectType):

    class Meta:
        model = models.FrontPortTemplate
        fields = '__all__'
        filterset_class = filtersets.FrontPortTemplateFilterSet


class InterfaceType(IPAddressesMixin, ComponentObjectType):

    class Meta:
        model = models.Interface
        exclude = ('_path',)
        filterset_class = filtersets.InterfaceFilterSet

    def resolve_mode(self, info):
        return self.mode or None


class InterfaceTemplateType(ComponentTemplateObjectType):

    class Meta:
        model = models.InterfaceTemplate
        fields = '__all__'
        filterset_class = filtersets.InterfaceTemplateFilterSet


class InventoryItemType(ComponentObjectType):

    class Meta:
        model = models.InventoryItem
        fields = '__all__'
        filterset_class = filtersets.InventoryItemFilterSet


class LocationType(VLANGroupsMixin, ImageAttachmentsMixin, OrganizationalObjectType):

    class Meta:
        model = models.Location
        fields = '__all__'
        filterset_class = filtersets.LocationFilterSet


class ManufacturerType(OrganizationalObjectType):

    class Meta:
        model = models.Manufacturer
        fields = '__all__'
        filterset_class = filtersets.ManufacturerFilterSet


class PlatformType(OrganizationalObjectType):

    class Meta:
        model = models.Platform
        fields = '__all__'
        filterset_class = filtersets.PlatformFilterSet


class PowerFeedType(PrimaryObjectType):

    class Meta:
        model = models.PowerFeed
        exclude = ('_path',)
        filterset_class = filtersets.PowerFeedFilterSet


class PowerOutletType(ComponentObjectType):

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


class PowerPanelType(PrimaryObjectType):

    class Meta:
        model = models.PowerPanel
        fields = '__all__'
        filterset_class = filtersets.PowerPanelFilterSet


class PowerPortType(ComponentObjectType):

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


class RackType(VLANGroupsMixin, ImageAttachmentsMixin, PrimaryObjectType):

    class Meta:
        model = models.Rack
        fields = '__all__'
        filterset_class = filtersets.RackFilterSet

    def resolve_type(self, info):
        return self.type or None

    def resolve_outer_unit(self, info):
        return self.outer_unit or None


class RackReservationType(PrimaryObjectType):

    class Meta:
        model = models.RackReservation
        fields = '__all__'
        filterset_class = filtersets.RackReservationFilterSet


class RackRoleType(OrganizationalObjectType):

    class Meta:
        model = models.RackRole
        fields = '__all__'
        filterset_class = filtersets.RackRoleFilterSet


class RearPortType(ComponentObjectType):

    class Meta:
        model = models.RearPort
        fields = '__all__'
        filterset_class = filtersets.RearPortFilterSet


class RearPortTemplateType(ComponentTemplateObjectType):

    class Meta:
        model = models.RearPortTemplate
        fields = '__all__'
        filterset_class = filtersets.RearPortTemplateFilterSet


class RegionType(VLANGroupsMixin, OrganizationalObjectType):

    class Meta:
        model = models.Region
        fields = '__all__'
        filterset_class = filtersets.RegionFilterSet


class SiteType(VLANGroupsMixin, ImageAttachmentsMixin, PrimaryObjectType):

    class Meta:
        model = models.Site
        fields = '__all__'
        filterset_class = filtersets.SiteFilterSet


class SiteGroupType(VLANGroupsMixin, OrganizationalObjectType):

    class Meta:
        model = models.SiteGroup
        fields = '__all__'
        filterset_class = filtersets.SiteGroupFilterSet


class VirtualChassisType(PrimaryObjectType):

    class Meta:
        model = models.VirtualChassis
        fields = '__all__'
        filterset_class = filtersets.VirtualChassisFilterSet
