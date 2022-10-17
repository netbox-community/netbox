from dcim.models import Interface
from netbox.search import SearchIndex, register_search
from utilities.utils import count_related
from . import filtersets, models


@register_search()
class WirelessLANIndex(SearchIndex):
    model = models.WirelessLAN
    fields = (
        ('ssid', 100),
        ('description', 500),
        ('auth_psk', 2000),
    )
    queryset = models.WirelessLAN.objects.prefetch_related('group', 'vlan').annotate(
        interface_count=count_related(Interface, 'wireless_lans')
    )
    filterset = filtersets.WirelessLANFilterSet


@register_search()
class WirelessLANGroupIndex(SearchIndex):
    model = models.WirelessLANGroup
    fields = (
        ('name', 100),
        ('slug', 110),
        ('description', 500),
    )


@register_search()
class WirelessLinkIndex(SearchIndex):
    model = models.WirelessLink
    fields = (
        ('ssid', 100),
        ('description', 500),
        ('auth_psk', 2000),
    )
    queryset = models.WirelessLink.objects.prefetch_related('interface_a__device', 'interface_b__device')
    filterset = filtersets.WirelessLinkFilterSet
