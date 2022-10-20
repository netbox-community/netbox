import dcim.filtersets
import dcim.tables
from dcim.models import (
    Cable,
    Device,
    DeviceType,
    Location,
    Module,
    ModuleType,
    PowerFeed,
    Rack,
    RackReservation,
    Site,
    VirtualChassis,
)
from netbox.search import SearchIndex, register_search
from utilities.utils import count_related


@register_search()
class SiteIndex(SearchIndex):
    model = Site
    queryset = Site.objects.prefetch_related('region', 'tenant', 'tenant__group')
    filterset = dcim.filtersets.SiteFilterSet
    table = dcim.tables.SiteTable
    url = 'dcim:site_list'


@register_search()
class RackIndex(SearchIndex):
    model = Rack
    queryset = Rack.objects.prefetch_related('site', 'location', 'tenant', 'tenant__group', 'role').annotate(
        device_count=count_related(Device, 'rack')
    )
    filterset = dcim.filtersets.RackFilterSet
    table = dcim.tables.RackTable
    url = 'dcim:rack_list'


@register_search()
class RackReservationIndex(SearchIndex):
    model = RackReservation
    queryset = RackReservation.objects.prefetch_related('rack', 'user')
    filterset = dcim.filtersets.RackReservationFilterSet
    table = dcim.tables.RackReservationTable
    url = 'dcim:rackreservation_list'


@register_search()
class LocationIndex(SearchIndex):
    model = Location
    queryset = Location.objects.add_related_count(
        Location.objects.add_related_count(Location.objects.all(), Device, 'location', 'device_count', cumulative=True),
        Rack,
        'location',
        'rack_count',
        cumulative=True,
    ).prefetch_related('site')
    filterset = dcim.filtersets.LocationFilterSet
    table = dcim.tables.LocationTable
    url = 'dcim:location_list'


@register_search()
class DeviceTypeIndex(SearchIndex):
    model = DeviceType
    queryset = DeviceType.objects.prefetch_related('manufacturer').annotate(
        instance_count=count_related(Device, 'device_type')
    )
    filterset = dcim.filtersets.DeviceTypeFilterSet
    table = dcim.tables.DeviceTypeTable
    url = 'dcim:devicetype_list'


@register_search()
class DeviceIndex(SearchIndex):
    model = Device
    queryset = Device.objects.prefetch_related(
        'device_type__manufacturer',
        'device_role',
        'tenant',
        'tenant__group',
        'site',
        'rack',
        'primary_ip4',
        'primary_ip6',
    )
    filterset = dcim.filtersets.DeviceFilterSet
    table = dcim.tables.DeviceTable
    url = 'dcim:device_list'


@register_search()
class ModuleTypeIndex(SearchIndex):
    model = ModuleType
    queryset = ModuleType.objects.prefetch_related('manufacturer').annotate(
        instance_count=count_related(Module, 'module_type')
    )
    filterset = dcim.filtersets.ModuleTypeFilterSet
    table = dcim.tables.ModuleTypeTable
    url = 'dcim:moduletype_list'


@register_search()
class ModuleIndex(SearchIndex):
    model = Module
    queryset = Module.objects.prefetch_related(
        'module_type__manufacturer',
        'device',
        'module_bay',
    )
    filterset = dcim.filtersets.ModuleFilterSet
    table = dcim.tables.ModuleTable
    url = 'dcim:module_list'


@register_search()
class VirtualChassisIndex(SearchIndex):
    model = VirtualChassis
    queryset = VirtualChassis.objects.prefetch_related('master').annotate(
        member_count=count_related(Device, 'virtual_chassis')
    )
    filterset = dcim.filtersets.VirtualChassisFilterSet
    table = dcim.tables.VirtualChassisTable
    url = 'dcim:virtualchassis_list'


@register_search()
class CableIndex(SearchIndex):
    model = Cable
    queryset = Cable.objects.all()
    filterset = dcim.filtersets.CableFilterSet
    table = dcim.tables.CableTable
    url = 'dcim:cable_list'


@register_search()
class PowerFeedIndex(SearchIndex):
    model = PowerFeed
    queryset = PowerFeed.objects.all()
    filterset = dcim.filtersets.PowerFeedFilterSet
    table = dcim.tables.PowerFeedTable
    url = 'dcim:powerfeed_list'
