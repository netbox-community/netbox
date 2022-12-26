from netbox.search import SearchIndex, register_search
from . import models


@register_search
class WirelessLANIndex(SearchIndex):
    model = models.WirelessLAN
    fields = (
        ('ssid', 100),
        ('description', 500),
        ('auth_psk', 2000),
        ('comments', 5000),
    )


@register_search
class WirelessLANGroupIndex(SearchIndex):
    model = models.WirelessLANGroup
    fields = (
        ('name', 100),
        ('slug', 110),
        ('description', 500),
    )


@register_search
class WirelessLinkIndex(SearchIndex):
    model = models.WirelessLink
    fields = (
        ('ssid', 100),
        ('description', 500),
        ('auth_psk', 2000),
        ('comments', 5000),
    )
