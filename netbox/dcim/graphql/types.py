from dcim import filtersets, models
from netbox.graphql.types import BaseObjectType, ObjectType, TaggedObjectType

__all__ = (
    'CableType',
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


class CableType(TaggedObjectType):

    class Meta:
        model = models.Cable
        fields = '__all__'
        filterset_class = filtersets.CableFilterSet


class ConsolePortType(TaggedObjectType):

    class Meta:
        model = models.ConsolePort
        fields = '__all__'
        filterset_class = filtersets.ConsolePortFilterSet


class ConsolePortTemplateType(BaseObjectType):

    class Meta:
        model = models.ConsolePortTemplate
        fields = '__all__'
        filterset_class = filtersets.ConsolePortTemplateFilterSet


class ConsoleServerPortType(TaggedObjectType):

    class Meta:
        model = models.ConsoleServerPort
        fields = '__all__'
        filterset_class = filtersets.ConsoleServerPortFilterSet


class ConsoleServerPortTemplateType(BaseObjectType):

    class Meta:
        model = models.ConsoleServerPortTemplate
        fields = '__all__'
        filterset_class = filtersets.ConsoleServerPortTemplateFilterSet


class DeviceType(TaggedObjectType):

    class Meta:
        model = models.Device
        fields = '__all__'
        filterset_class = filtersets.DeviceFilterSet


class DeviceBayType(TaggedObjectType):

    class Meta:
        model = models.DeviceBay
        fields = '__all__'
        filterset_class = filtersets.DeviceBayFilterSet


class DeviceBayTemplateType(BaseObjectType):

    class Meta:
        model = models.DeviceBayTemplate
        fields = '__all__'
        filterset_class = filtersets.DeviceBayTemplateFilterSet


class DeviceRoleType(ObjectType):

    class Meta:
        model = models.DeviceRole
        fields = '__all__'
        filterset_class = filtersets.DeviceRoleFilterSet


class DeviceTypeType(TaggedObjectType):

    class Meta:
        model = models.DeviceType
        fields = '__all__'
        filterset_class = filtersets.DeviceTypeFilterSet


class FrontPortType(TaggedObjectType):

    class Meta:
        model = models.FrontPort
        fields = '__all__'
        filterset_class = filtersets.FrontPortFilterSet


class FrontPortTemplateType(BaseObjectType):

    class Meta:
        model = models.FrontPortTemplate
        fields = '__all__'
        filterset_class = filtersets.FrontPortTemplateFilterSet


class InterfaceType(TaggedObjectType):

    class Meta:
        model = models.Interface
        fields = '__all__'
        filterset_class = filtersets.InterfaceFilterSet


class InterfaceTemplateType(BaseObjectType):

    class Meta:
        model = models.InterfaceTemplate
        fields = '__all__'
        filterset_class = filtersets.InterfaceTemplateFilterSet


class InventoryItemType(ObjectType):

    class Meta:
        model = models.InventoryItem
        fields = '__all__'
        filterset_class = filtersets.InventoryItemFilterSet


class LocationType(TaggedObjectType):

    class Meta:
        model = models.Location
        fields = '__all__'
        filterset_class = filtersets.LocationFilterSet


class ManufacturerType(ObjectType):

    class Meta:
        model = models.Manufacturer
        fields = '__all__'
        filterset_class = filtersets.ManufacturerFilterSet


class PlatformType(ObjectType):

    class Meta:
        model = models.Platform
        fields = '__all__'
        filterset_class = filtersets.PlatformFilterSet


class PowerFeedType(TaggedObjectType):

    class Meta:
        model = models.PowerFeed
        fields = '__all__'
        filterset_class = filtersets.PowerFeedFilterSet


class PowerOutletType(TaggedObjectType):

    class Meta:
        model = models.PowerOutlet
        fields = '__all__'
        filterset_class = filtersets.PowerOutletFilterSet


class PowerOutletTemplateType(BaseObjectType):

    class Meta:
        model = models.PowerOutletTemplate
        fields = '__all__'
        filterset_class = filtersets.PowerOutletTemplateFilterSet


class PowerPanelType(TaggedObjectType):

    class Meta:
        model = models.PowerPanel
        fields = '__all__'
        filterset_class = filtersets.PowerPanelFilterSet


class PowerPortType(TaggedObjectType):

    class Meta:
        model = models.PowerPort
        fields = '__all__'
        filterset_class = filtersets.PowerPortFilterSet


class PowerPortTemplateType(BaseObjectType):

    class Meta:
        model = models.PowerPortTemplate
        fields = '__all__'
        filterset_class = filtersets.PowerPortTemplateFilterSet


class RackType(TaggedObjectType):

    class Meta:
        model = models.Rack
        fields = '__all__'
        filterset_class = filtersets.RackFilterSet


class RackReservationType(TaggedObjectType):

    class Meta:
        model = models.RackReservation
        fields = '__all__'
        filterset_class = filtersets.RackReservationFilterSet


class RackRoleType(ObjectType):

    class Meta:
        model = models.RackRole
        fields = '__all__'
        filterset_class = filtersets.RackRoleFilterSet


class RearPortType(TaggedObjectType):

    class Meta:
        model = models.RearPort
        fields = '__all__'
        filterset_class = filtersets.RearPortFilterSet


class RearPortTemplateType(BaseObjectType):

    class Meta:
        model = models.RearPortTemplate
        fields = '__all__'
        filterset_class = filtersets.RearPortTemplateFilterSet


class RegionType(ObjectType):

    class Meta:
        model = models.Region
        fields = '__all__'
        filterset_class = filtersets.RegionFilterSet


class SiteType(TaggedObjectType):

    class Meta:
        model = models.Site
        fields = '__all__'
        filterset_class = filtersets.SiteFilterSet


class SiteGroupType(ObjectType):

    class Meta:
        model = models.SiteGroup
        fields = '__all__'
        filterset_class = filtersets.SiteGroupFilterSet


class VirtualChassisType(TaggedObjectType):

    class Meta:
        model = models.VirtualChassis
        fields = '__all__'
        filterset_class = filtersets.VirtualChassisFilterSet
