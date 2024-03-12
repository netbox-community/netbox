import strawberry
import strawberry_django
from strawberry import auto
from wireless import filtersets, models

__all__ = (
    'WirelessLANGroupFilter',
    'WirelessLANFilter',
    'WirelessLinkFilter',
)


@strawberry_django.filter(models.WirelessLANGroup, lookups=True)
class WirelessLANGroupFilter(filtersets.WirelessLANGroupFilterSet):
    id: auto


@strawberry_django.filter(models.WirelessLAN, lookups=True)
class WirelessLANFilter(filtersets.WirelessLANFilterSet):
    id: auto


@strawberry_django.filter(models.WirelessLink, lookups=True)
class WirelessLinkFilter(filtersets.WirelessLinkFilterSet):
    id: auto
