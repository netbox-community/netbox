from dcim import filtersets, models
from netbox.search import SearchIndex, register_search
from utilities.utils import count_related


@register_search()
class CableIndex(SearchIndex):
    model = models.Cable
    fields = (
        ('label', 100),
    )
    queryset = models.Cable.objects.all()
    filterset = filtersets.CableFilterSet


@register_search()
class DeviceIndex(SearchIndex):
    model = models.Device
    fields = (
        ('asset_tag', 50),
        ('serial', 60),
        ('name', 100),
        ('comments', 1000),
    )
    queryset = models.Device.objects.prefetch_related(
        'device_type__manufacturer',
        'device_role',
        'tenant',
        'tenant__group',
        'site',
        'rack',
        'primary_ip4',
        'primary_ip6',
    )
    filterset = filtersets.DeviceFilterSet


@register_search()
class DeviceRoleIndex(SearchIndex):
    model = models.DeviceRole
    fields = (
        ('name', 100),
        ('slug', 100),
        ('description', 500),
    )


@register_search()
class DeviceTypeIndex(SearchIndex):
    model = models.DeviceType
    fields = (
        ('model', 100),
        ('part_number', 200),
        ('comments', 1000),
    )
    queryset = models.DeviceType.objects.prefetch_related('manufacturer').annotate(
        instance_count=count_related(models.Device, 'device_type')
    )
    filterset = filtersets.DeviceTypeFilterSet


@register_search()
class LocationIndex(SearchIndex):
    model = models.Location
    fields = (
        ('name', 100),
        ('slug', 100),
        ('description', 500),
    )
    queryset = models.Location.objects.add_related_count(
        models.Location.objects.add_related_count(
            models.Location.objects.all(), models.Device, 'location', 'device_count', cumulative=True
        ),
        models.Rack,
        'location',
        'rack_count',
        cumulative=True,
    ).prefetch_related('site')
    filterset = filtersets.LocationFilterSet


@register_search()
class ModuleIndex(SearchIndex):
    model = models.Module
    fields = (
        ('asset_tag', 50),
        ('serial', 60),
        ('comments', 1000),
    )
    queryset = models.Module.objects.prefetch_related(
        'module_type__manufacturer',
        'device',
        'module_bay',
    )
    filterset = filtersets.ModuleFilterSet


@register_search()
class ModuleTypeIndex(SearchIndex):
    model = models.ModuleType
    fields = (
        ('model', 100),
        ('part_number', 200),
        ('comments', 1000),
    )
    queryset = models.ModuleType.objects.prefetch_related('manufacturer').annotate(
        instance_count=count_related(models.Module, 'module_type')
    )
    filterset = filtersets.ModuleTypeFilterSet


@register_search()
class PowerFeedIndex(SearchIndex):
    model = models.PowerFeed
    fields = (
        ('name', 100),
        ('comments', 1000),
    )
    queryset = models.PowerFeed.objects.all()
    filterset = filtersets.PowerFeedFilterSet


@register_search()
class RackIndex(SearchIndex):
    model = models.Rack
    fields = (
        ('asset_tag', 50),
        ('serial', 60),
        ('name', 100),
        ('facility_id', 100),
        ('comments', 1000),
    )
    queryset = models.Rack.objects.prefetch_related('site', 'location', 'tenant', 'tenant__group', 'role').annotate(
        device_count=count_related(models.Device, 'rack')
    )
    filterset = filtersets.RackFilterSet


@register_search()
class RackReservationIndex(SearchIndex):
    model = models.RackReservation
    fields = (
        ('description', 500),
    )
    queryset = models.RackReservation.objects.prefetch_related('rack', 'user')
    filterset = filtersets.RackReservationFilterSet


@register_search()
class RegionIndex(SearchIndex):
    model = models.Region
    fields = (
        ('name', 100),
        ('slug', 100),
        ('description', 500)
    )


@register_search()
class SiteIndex(SearchIndex):
    model = models.Site
    fields = (
        ('name', 100),
        ('facility', 100),
        ('description', 500),
        ('physical_address', 1000),
        ('shipping_address', 1000),
    )
    queryset = models.Site.objects.prefetch_related('region', 'tenant', 'tenant__group')
    filterset = filtersets.SiteFilterSet


@register_search()
class SiteGroupIndex(SearchIndex):
    model = models.SiteGroup
    fields = (
        ('name', 100),
        ('slug', 100),
        ('description', 500)
    )


@register_search()
class VirtualChassisIndex(SearchIndex):
    model = models.VirtualChassis
    fields = (
        ('name', 100),
        ('domain', 300)
    )
    queryset = models.VirtualChassis.objects.prefetch_related('master').annotate(
        member_count=count_related(models.Device, 'virtual_chassis')
    )
    filterset = filtersets.VirtualChassisFilterSet
