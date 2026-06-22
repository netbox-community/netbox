from django.urls import reverse

from dcim.models import (
    ConsolePort,
    ConsoleServerPort,
    DeviceBay,
    FrontPort,
    InventoryItem,
    Location,
    ModuleBay,
    PowerFeed,
    PowerOutlet,
    PowerPanel,
    PowerPort,
    RearPort,
    Site,
)
from netbox.ui.breadcrumbs import Breadcrumb, BreadcrumbTrail, register_breadcrumbs


@register_breadcrumbs
class SiteBreadcrumbs(BreadcrumbTrail):
    model = Site
    items = (
        Breadcrumb(
            lambda o: o.region.get_ancestors(include_self=True) if o.region else [],
            url=lambda region: f"{reverse('dcim:site_list')}?region_id={region.pk}",
        ),
        Breadcrumb(
            lambda o: o.group.get_ancestors(include_self=True) if o.group else [],
            url=lambda group: f"{reverse('dcim:site_list')}?group_id={group.pk}",
        ),
    )


@register_breadcrumbs
class LocationBreadcrumbs(BreadcrumbTrail):
    model = Location
    items = (
        Breadcrumb(lambda o: o.get_ancestors()),
    )


@register_breadcrumbs
class ConsolePortBreadcrumbs(BreadcrumbTrail):
    model = ConsolePort
    items = (
        Breadcrumb('device', url=lambda o: reverse('dcim:device_consoleports', kwargs={'pk': o.pk})),
    )


@register_breadcrumbs
class ConsoleServerPortBreadcrumbs(BreadcrumbTrail):
    model = ConsoleServerPort
    items = (
        Breadcrumb('device', url=lambda o: reverse('dcim:device_consoleserverports', kwargs={'pk': o.pk})),
    )


@register_breadcrumbs
class PowerPortBreadcrumbs(BreadcrumbTrail):
    model = PowerPort
    items = (
        Breadcrumb('device', url=lambda o: reverse('dcim:device_powerports', kwargs={'pk': o.pk})),
    )


@register_breadcrumbs
class PowerOutletBreadcrumbs(BreadcrumbTrail):
    model = PowerOutlet
    items = (
        Breadcrumb('device', url=lambda o: reverse('dcim:device_poweroutlets', kwargs={'pk': o.pk})),
    )


@register_breadcrumbs
class FrontPortBreadcrumbs(BreadcrumbTrail):
    model = FrontPort
    items = (
        Breadcrumb('device', url=lambda o: reverse('dcim:device_frontports', kwargs={'pk': o.pk})),
    )


@register_breadcrumbs
class RearPortBreadcrumbs(BreadcrumbTrail):
    model = RearPort
    items = (
        Breadcrumb('device', url=lambda o: reverse('dcim:device_rearports', kwargs={'pk': o.pk})),
    )


@register_breadcrumbs
class ModuleBayBreadcrumbs(BreadcrumbTrail):
    model = ModuleBay
    items = (
        Breadcrumb('device', url=lambda o: reverse('dcim:device_modulebays', kwargs={'pk': o.pk})),
    )


@register_breadcrumbs
class DeviceBayBreadcrumbs(BreadcrumbTrail):
    model = DeviceBay
    items = (
        Breadcrumb('device', url=lambda o: reverse('dcim:device_devicebays', kwargs={'pk': o.pk})),
    )


@register_breadcrumbs
class InventoryItemBreadcrumbs(BreadcrumbTrail):
    model = InventoryItem
    items = (
        Breadcrumb('device', url=lambda o: reverse('dcim:device_inventory', kwargs={'pk': o.pk})),
    )


@register_breadcrumbs
class PowerPanelBreadcrumbs(BreadcrumbTrail):
    model = PowerPanel
    items = (
        Breadcrumb('site', url=lambda o: f"{reverse('dcim:powerpanel_list')}?site_id={o.pk}"),
        Breadcrumb('location'),
    )


@register_breadcrumbs
class PowerFeedBreadcrumbs(BreadcrumbTrail):
    model = PowerFeed
    items = (
        Breadcrumb('power_panel.site', url=lambda o: f"{reverse('dcim:powerfeed_list')}?site_id={o.pk}"),
        Breadcrumb('power_panel', url=lambda o: f"{reverse('dcim:powerfeed_list')}?power_panel_id={o.pk}"),
        Breadcrumb('rack', url=lambda o: f"{reverse('dcim:powerfeed_list')}?rack_id={o.pk}"),
    )
