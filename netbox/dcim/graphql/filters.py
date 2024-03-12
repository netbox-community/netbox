import strawberry
import strawberry_django
from dcim import filtersets, models
from strawberry import auto

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
    'RearPortFilter',
    'RearPortTemplateFilter',
    'RegionFilter',
    'SiteFilter',
    'SiteGroupFilter',
    'VirtualChassisFilter',
    'VirtualDeviceContextFilter',
)


@strawberry_django.filter(models.Cable, lookups=True)
class CableFilter(filtersets.CableFilterSet):
    id: auto


@strawberry_django.filter(models.CableTermination, lookups=True)
class CableTerminationFilter(filtersets.CableTerminationFilterSet):
    id: auto


@strawberry_django.filter(models.ConsolePort, lookups=True)
class ConsolePortFilter(filtersets.ConsolePortFilterSet):
    id: auto


@strawberry_django.filter(models.ConsolePortTemplate, lookups=True)
class ConsolePortTemplateFilter(filtersets.ConsolePortTemplateFilterSet):
    id: auto


@strawberry_django.filter(models.ConsoleServerPort, lookups=True)
class ConsoleServerPortFilter(filtersets.ConsoleServerPortFilterSet):
    id: auto


@strawberry_django.filter(models.ConsoleServerPortTemplate, lookups=True)
class ConsoleServerPortTemplateFilter(filtersets.ConsoleServerPortTemplateFilterSet):
    id: auto


@strawberry_django.filter(models.Device, lookups=True)
class DeviceFilter(filtersets.DeviceFilterSet):
    id: auto


@strawberry_django.filter(models.DeviceBay, lookups=True)
class DeviceBayFilter(filtersets.DeviceBayFilterSet):
    id: auto


@strawberry_django.filter(models.DeviceBayTemplate, lookups=True)
class DeviceBayTemplateFilter(filtersets.DeviceBayTemplateFilterSet):
    id: auto


@strawberry_django.filter(models.InventoryItemTemplate, lookups=True)
class InventoryItemTemplateFilter(filtersets.InventoryItemTemplateFilterSet):
    id: auto


@strawberry_django.filter(models.DeviceRole, lookups=True)
class DeviceRoleFilter(filtersets.DeviceRoleFilterSet):
    id: auto


@strawberry_django.filter(models.DeviceType, lookups=True)
class DeviceTypeFilter(filtersets.DeviceTypeFilterSet):
    id: auto


@strawberry_django.filter(models.FrontPort, lookups=True)
class FrontPortFilter(filtersets.FrontPortFilterSet):
    id: auto


@strawberry_django.filter(models.FrontPortTemplate, lookups=True)
class FrontPortTemplateFilter(filtersets.FrontPortTemplateFilterSet):
    id: auto


@strawberry_django.filter(models.Interface, lookups=True)
class InterfaceFilter(filtersets.InterfaceFilterSet):
    id: auto


@strawberry_django.filter(models.InterfaceTemplate, lookups=True)
class InterfaceTemplateFilter(filtersets.InterfaceTemplateFilterSet):
    id: auto


@strawberry_django.filter(models.InventoryItem, lookups=True)
class InventoryItemFilter(filtersets.InventoryItemFilterSet):
    id: auto


@strawberry_django.filter(models.InventoryItemRole, lookups=True)
class InventoryItemRoleFilter(filtersets.InventoryItemRoleFilterSet):
    id: auto


@strawberry_django.filter(models.Location, lookups=True)
class LocationFilter(filtersets.LocationFilterSet):
    id: auto


@strawberry_django.filter(models.Manufacturer, lookups=True)
class ManufacturerFilter(filtersets.ManufacturerFilterSet):
    id: auto


@strawberry_django.filter(models.Module, lookups=True)
class ModuleFilter(filtersets.ModuleFilterSet):
    id: auto


@strawberry_django.filter(models.ModuleBay, lookups=True)
class ModuleBayFilter(filtersets.ModuleBayFilterSet):
    id: auto


@strawberry_django.filter(models.ModuleBayTemplate, lookups=True)
class ModuleBayTemplateFilter(filtersets.ModuleBayTemplateFilterSet):
    id: auto


@strawberry_django.filter(models.ModuleType, lookups=True)
class ModuleTypeFilter(filtersets.ModuleTypeFilterSet):
    id: auto


@strawberry_django.filter(models.Platform, lookups=True)
class PlatformFilter(filtersets.PlatformFilterSet):
    id: auto


@strawberry_django.filter(models.PowerFeed, lookups=True)
class PowerFeedFilter(filtersets.PowerFeedFilterSet):
    id: auto


@strawberry_django.filter(models.PowerOutlet, lookups=True)
class PowerOutletFilter(filtersets.PowerOutletFilterSet):
    id: auto


@strawberry_django.filter(models.PowerOutletTemplate, lookups=True)
class PowerOutletTemplateFilter(filtersets.PowerOutletTemplateFilterSet):
    id: auto


@strawberry_django.filter(models.PowerPanel, lookups=True)
class PowerPanelFilter(filtersets.PowerPanelFilterSet):
    id: auto


@strawberry_django.filter(models.PowerPort, lookups=True)
class PowerPortFilter(filtersets.PowerPortFilterSet):
    id: auto


@strawberry_django.filter(models.PowerPortTemplate, lookups=True)
class PowerPortTemplateFilter(filtersets.PowerPortTemplateFilterSet):
    id: auto


@strawberry_django.filter(models.Rack, lookups=True)
class RackFilter(filtersets.RackFilterSet):
    id: auto


@strawberry_django.filter(models.RackReservation, lookups=True)
class RackReservationFilter(filtersets.RackReservationFilterSet):
    id: auto


@strawberry_django.filter(models.RackRole, lookups=True)
class RackRoleFilter(filtersets.RackRoleFilterSet):
    id: auto


@strawberry_django.filter(models.RearPort, lookups=True)
class RearPortFilter(filtersets.RearPortFilterSet):
    id: auto


@strawberry_django.filter(models.RearPortTemplate, lookups=True)
class RearPortTemplateFilter(filtersets.RearPortTemplateFilterSet):
    id: auto


@strawberry_django.filter(models.Region, lookups=True)
class RegionFilter(filtersets.RegionFilterSet):
    id: auto


@strawberry_django.filter(models.Site, lookups=True)
class SiteFilter(filtersets.SiteFilterSet):
    id: auto


@strawberry_django.filter(models.SiteGroup, lookups=True)
class SiteGroupFilter(filtersets.SiteGroupFilterSet):
    id: auto


@strawberry_django.filter(models.VirtualChassis, lookups=True)
class VirtualChassisFilter(filtersets.VirtualChassisFilterSet):
    id: auto


@strawberry_django.filter(models.VirtualDeviceContext, lookups=True)
class VirtualDeviceContextFilter(filtersets.VirtualDeviceContextFilterSet):
    id: auto
