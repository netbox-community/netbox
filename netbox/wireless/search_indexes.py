import dcim.filtersets
import dcim.tables
from django.db import models
from search.models import SearchMixin
from wireless.models import WirelessLAN, WirelessLink


class WirelessLANIndex(SearchMixin):
    def __init__(self):
        self.model = WirelessLAN
        self.queryset = WirelessLAN.objects.prefetch_related('group', 'vlan').annotate(
            interface_count=count_related(Interface, 'wireless_lans')
        )
        self.filterset = wireless.filtersets.WirelessLANFilterSet
        self.table = wireless.tables.WirelessLANTable
        self.url = 'wireless:wirelesslan_list'


class WirelessLinkIndex(SearchMixin):
    def __init__(self):
        self.model = WirelessLink
        self.queryset = WirelessLink.objects.prefetch_related('interface_a__device', 'interface_b__device')
        self.filterset = wireless.filtersets.WirelessLinkFilterSet
        self.table = wireless.tables.WirelessLinkTable
        self.url = 'wireless:wirelesslink_list'


WIRELESS_SEARCH_TYPES = {
    'wirelesslan': WirelessLANIndex(),
    'wirelesslink': WirelessLinkIndex(),
}
