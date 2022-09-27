import dcim.filtersets
import dcim.tables
from dcim.models import (
    Cable,
    Device,
    DeviceType,
    Interface,
    Location,
    Module,
    ModuleType,
    PowerFeed,
    Rack,
    RackReservation,
    Site,
    VirtualChassis,
)
from django.db import models
from search.models import SearchMixin
from utilities.utils import count_related


class SiteIndex(SearchMixin):
    model = Site
    queryset = Site.objects.prefetch_related('region', 'tenant', 'tenant__group')
    filterset = dcim.filtersets.SiteFilterSet
    table = dcim.tables.SiteTable
    url = 'dcim:site_list'
    choice_header = 'DCIM'


class RackIndex(SearchMixin):
    model = Rack
    queryset = Rack.objects.prefetch_related('site', 'location', 'tenant', 'tenant__group', 'role').annotate(
        device_count=count_related(Device, 'rack')
    )
    filterset = dcim.filtersets.RackFilterSet
    table = dcim.tables.RackTable
    url = 'dcim:rack_list'
    choice_header = 'DCIM'


class RackReservationIndex(SearchMixin):
    model = RackReservation
    queryset = RackReservation.objects.prefetch_related('rack', 'user')
    filterset = dcim.filtersets.RackReservationFilterSet
    table = dcim.tables.RackReservationTable
    url = 'dcim:rackreservation_list'
    choice_header = 'DCIM'


class LocationIndex(SearchMixin):
    model = Site
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
    choice_header = 'DCIM'


class DeviceTypeIndex(SearchMixin):
    model = DeviceType
    queryset = DeviceType.objects.prefetch_related('manufacturer').annotate(
        instance_count=count_related(Device, 'device_type')
    )
    filterset = dcim.filtersets.DeviceTypeFilterSet
    table = dcim.tables.DeviceTypeTable
    url = 'dcim:devicetype_list'
    choice_header = 'DCIM'


class DeviceIndex(SearchMixin):
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
    choice_header = 'DCIM'


class ModuleTypeIndex(SearchMixin):
    model = ModuleType
    queryset = ModuleType.objects.prefetch_related('manufacturer').annotate(
        instance_count=count_related(Module, 'module_type')
    )
    filterset = dcim.filtersets.ModuleTypeFilterSet
    table = dcim.tables.ModuleTypeTable
    url = 'dcim:moduletype_list'
    choice_header = 'DCIM'


class ModuleIndex(SearchMixin):
    model = Module
    queryset = Module.objects.prefetch_related(
        'module_type__manufacturer',
        'device',
        'module_bay',
    )
    filterset = dcim.filtersets.ModuleFilterSet
    table = dcim.tables.ModuleTable
    url = 'dcim:module_list'
    choice_header = 'DCIM'


class VirtualChassisIndex(SearchMixin):
    model = VirtualChassis
    queryset = VirtualChassis.objects.prefetch_related('master').annotate(
        member_count=count_related(Device, 'virtual_chassis')
    )
    filterset = dcim.filtersets.VirtualChassisFilterSet
    table = dcim.tables.VirtualChassisTable
    url = 'dcim:virtualchassis_list'
    choice_header = 'DCIM'


class CableIndex(SearchMixin):
    model = Cable
    queryset = Cable.objects.all()
    filterset = dcim.filtersets.CableFilterSet
    table = dcim.tables.CableTable
    url = 'dcim:cable_list'
    choice_header = 'DCIM'


class PowerFeedIndex(SearchMixin):
    model = PowerFeed
    queryset = PowerFeed.objects.all()
    filterset = dcim.filtersets.PowerFeedFilterSet
    table = dcim.tables.PowerFeedTable
    url = 'dcim:powerfeed_list'
    choice_header = 'DCIM'


DCIM_SEARCH_TYPES = {
    'site': SiteIndex,
    'rack': RackIndex,
    'rackreservation': RackReservationIndex,
    'location': LocationIndex,
    'devicetype': DeviceTypeIndex,
    'device': DeviceIndex,
    'moduletype': ModuleTypeIndex,
    'module': ModuleIndex,
    'virtualchassis': VirtualChassisIndex,
    'cable': CableIndex,
    'powerfeed': PowerFeedIndex,
}
