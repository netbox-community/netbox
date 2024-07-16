import strawberry_django

from dcim import filtersets, models
from netbox.graphql.filter_mixins import autotype_decorator, BaseFilterMixin

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
@autotype_decorator(filtersets.CableFilterSet)
class CableFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.CableTermination, lookups=True)
@autotype_decorator(filtersets.CableTerminationFilterSet)
class CableTerminationFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.ConsolePort, lookups=True)
@autotype_decorator(filtersets.ConsolePortFilterSet)
class ConsolePortFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.ConsolePortTemplate, lookups=True)
@autotype_decorator(filtersets.ConsolePortTemplateFilterSet)
class ConsolePortTemplateFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.ConsoleServerPort, lookups=True)
@autotype_decorator(filtersets.ConsoleServerPortFilterSet)
class ConsoleServerPortFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.ConsoleServerPortTemplate, lookups=True)
@autotype_decorator(filtersets.ConsoleServerPortTemplateFilterSet)
class ConsoleServerPortTemplateFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.Device, lookups=True)
@autotype_decorator(filtersets.DeviceFilterSet)
class DeviceFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.DeviceBay, lookups=True)
@autotype_decorator(filtersets.DeviceBayFilterSet)
class DeviceBayFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.DeviceBayTemplate, lookups=True)
@autotype_decorator(filtersets.DeviceBayTemplateFilterSet)
class DeviceBayTemplateFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.InventoryItemTemplate, lookups=True)
@autotype_decorator(filtersets.InventoryItemTemplateFilterSet)
class InventoryItemTemplateFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.DeviceRole, lookups=True)
@autotype_decorator(filtersets.DeviceRoleFilterSet)
class DeviceRoleFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.DeviceType, lookups=True)
@autotype_decorator(filtersets.DeviceTypeFilterSet)
class DeviceTypeFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.FrontPort, lookups=True)
@autotype_decorator(filtersets.FrontPortFilterSet)
class FrontPortFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.FrontPortTemplate, lookups=True)
@autotype_decorator(filtersets.FrontPortTemplateFilterSet)
class FrontPortTemplateFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.Interface, lookups=True)
@autotype_decorator(filtersets.InterfaceFilterSet)
class InterfaceFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.InterfaceTemplate, lookups=True)
@autotype_decorator(filtersets.InterfaceTemplateFilterSet)
class InterfaceTemplateFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.InventoryItem, lookups=True)
@autotype_decorator(filtersets.InventoryItemFilterSet)
class InventoryItemFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.InventoryItemRole, lookups=True)
@autotype_decorator(filtersets.InventoryItemRoleFilterSet)
class InventoryItemRoleFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.Location, lookups=True)
@autotype_decorator(filtersets.LocationFilterSet)
class LocationFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.Manufacturer, lookups=True)
@autotype_decorator(filtersets.ManufacturerFilterSet)
class ManufacturerFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.Module, lookups=True)
@autotype_decorator(filtersets.ModuleFilterSet)
class ModuleFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.ModuleBay, lookups=True)
@autotype_decorator(filtersets.ModuleBayFilterSet)
class ModuleBayFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.ModuleBayTemplate, lookups=True)
@autotype_decorator(filtersets.ModuleBayTemplateFilterSet)
class ModuleBayTemplateFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.ModuleType, lookups=True)
@autotype_decorator(filtersets.ModuleTypeFilterSet)
class ModuleTypeFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.Platform, lookups=True)
@autotype_decorator(filtersets.PlatformFilterSet)
class PlatformFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.PowerFeed, lookups=True)
@autotype_decorator(filtersets.PowerFeedFilterSet)
class PowerFeedFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.PowerOutlet, lookups=True)
@autotype_decorator(filtersets.PowerOutletFilterSet)
class PowerOutletFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.PowerOutletTemplate, lookups=True)
@autotype_decorator(filtersets.PowerOutletTemplateFilterSet)
class PowerOutletTemplateFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.PowerPanel, lookups=True)
@autotype_decorator(filtersets.PowerPanelFilterSet)
class PowerPanelFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.PowerPort, lookups=True)
@autotype_decorator(filtersets.PowerPortFilterSet)
class PowerPortFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.PowerPortTemplate, lookups=True)
@autotype_decorator(filtersets.PowerPortTemplateFilterSet)
class PowerPortTemplateFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.RackType, lookups=True)
@autotype_decorator(filtersets.RackTypeFilterSet)
class RackTypeFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.Rack, lookups=True)
@autotype_decorator(filtersets.RackFilterSet)
class RackFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.RackReservation, lookups=True)
@autotype_decorator(filtersets.RackReservationFilterSet)
class RackReservationFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.RackRole, lookups=True)
@autotype_decorator(filtersets.RackRoleFilterSet)
class RackRoleFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.RearPort, lookups=True)
@autotype_decorator(filtersets.RearPortFilterSet)
class RearPortFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.RearPortTemplate, lookups=True)
@autotype_decorator(filtersets.RearPortTemplateFilterSet)
class RearPortTemplateFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.Region, lookups=True)
@autotype_decorator(filtersets.RegionFilterSet)
class RegionFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.Site, lookups=True)
@autotype_decorator(filtersets.SiteFilterSet)
class SiteFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.SiteGroup, lookups=True)
@autotype_decorator(filtersets.SiteGroupFilterSet)
class SiteGroupFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.VirtualChassis, lookups=True)
@autotype_decorator(filtersets.VirtualChassisFilterSet)
class VirtualChassisFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.VirtualDeviceContext, lookups=True)
@autotype_decorator(filtersets.VirtualDeviceContextFilterSet)
class VirtualDeviceContextFilter(BaseFilterMixin):
    pass
