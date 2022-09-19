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

    def __init__(self):
        self.model = Site
        self.queryset = Site.objects.prefetch_related('region', 'tenant', 'tenant__group')
        self.filterset = dcim.filtersets.SiteFilterSet
        self.table = dcim.tables.SiteTable
        self.url = 'dcim:site_list'


class RackIndex(SearchMixin):

    def __init__(self):
        self.model = Rack
        self.queryset = Rack.objects.prefetch_related('site', 'location', 'tenant', 'tenant__group', 'role').annotate(
            device_count=count_related(Device, 'rack')
        )
        self.filterset = dcim.filtersets.RackFilterSet
        self.table = dcim.tables.RackTable
        self.url = 'dcim:rack_list'


class RackReservationIndex(SearchMixin):

    def __init__(self):
        self.model = RackReservation
        self.queryset = RackReservation.objects.prefetch_related('rack', 'user')
        self.filterset = dcim.filtersets.RackReservationFilterSet
        self.table = dcim.tables.RackReservationTable
        self.url = 'dcim:rackreservation_list'


class LocationIndex(SearchMixin):

    def __init__(self):
        self.model = Site
        self.queryset = Location.objects.add_related_count(
            Location.objects.add_related_count(Location.objects.all(), Device, 'location', 'device_count', cumulative=True),
            Rack,
            'location',
            'rack_count',
            cumulative=True,
        ).prefetch_related('site')
        self.filterset = dcim.filtersets.LocationFilterSet
        self.table = dcim.tables.LocationTable
        self.url = 'dcim:location_list'


class DeviceTypeIndex(SearchMixin):

    def __init__(self):
        self.model = DeviceType
        self.queryset = DeviceType.objects.prefetch_related('manufacturer').annotate(
            instance_count=count_related(Device, 'device_type')
        )
        self.filterset = dcim.filtersets.DeviceTypeFilterSet
        self.table = dcim.tables.DeviceTypeTable
        self.url = 'dcim:devicetype_list'


class DeviceIndex(SearchMixin):

    def __init__(self):
        self.model = DeviceIndex
        self.queryset = Device.objects.prefetch_related(
            'device_type__manufacturer',
            'device_role',
            'tenant',
            'tenant__group',
            'site',
            'rack',
            'primary_ip4',
            'primary_ip6',
        )
        self.filterset = dcim.filtersets.DeviceFilterSet
        self.table = dcim.tables.DeviceTable
        self.url = 'dcim:device_list'


class ModuleTypeIndex(SearchMixin):

    def __init__(self):
        self.model = ModuleType
        self.queryset = ModuleType.objects.prefetch_related('manufacturer').annotate(
            instance_count=count_related(Module, 'module_type')
        )
        self.filterset = dcim.filtersets.ModuleTypeFilterSet
        self.table = dcim.tables.ModuleTypeTable
        self.url = 'dcim:moduletype_list'


class ModuleIndex(SearchMixin):

    def __init__(self):
        self.model = Module
        self.queryset = Module.objects.prefetch_related(
            'module_type__manufacturer',
            'device',
            'module_bay',
        )
        self.filterset = dcim.filtersets.ModuleFilterSet
        self.table = dcim.tables.ModuleTable
        self.url = 'dcim:module_list'


class VirtualChassisIndex(SearchMixin):

    def __init__(self):
        self.model = VirtualChassis
        self.queryset = VirtualChassis.objects.prefetch_related('master').annotate(
            member_count=count_related(Device, 'virtual_chassis')
        )
        self.filterset = dcim.filtersets.VirtualChassisFilterSet
        self.table = dcim.tables.VirtualChassisTable
        self.url = 'dcim:virtualchassis_list'


class CableIndex(SearchMixin):

    def __init__(self):
        self.model = Cable
        self.queryset = Cable.objects.all()
        self.filterset = dcim.filtersets.CableFilterSet
        self.table = dcim.tables.CableTable
        self.url = 'dcim:cable_list'


class PowerFeedIndex(SearchMixin):

    def __init__(self):
        self.model = PowerFeed
        self.queryset = PowerFeed.objects.all()
        self.filterset = dcim.filtersets.PowerFeedFilterSet
        self.table = dcim.tables.PowerFeedTable
        self.url = 'dcim:powerfeed_list'


DCIM_SEARCH_TYPES = {
    'site': SiteIndex(),
    'rack': RackIndex(),
    'rackreservation': RackReservationIndex(),
    'location': LocationIndex(),
    'devicetype': DeviceTypeIndex(),
    'device': DeviceIndex(),
    'moduletype': ModuleTypeIndex(),
    'module': ModuleIndex(),
    'virtualchassis': VirtualChassisIndex(),
    'cable': CableIndex(),
    'powerfeed': PowerFeedIndex(),
}
