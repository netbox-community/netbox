import wireless.filtersets
import wireless.tables
from dcim.models import Interface
from netbox.search import SearchIndex, register_search
from utilities.utils import count_related
from wireless.models import WirelessLAN, WirelessLink


@register_search()
class WirelessLANIndex(SearchIndex):
    model = WirelessLAN
    queryset = WirelessLAN.objects.prefetch_related('group', 'vlan').annotate(
        interface_count=count_related(Interface, 'wireless_lans')
    )
    filterset = wireless.filtersets.WirelessLANFilterSet
    table = wireless.tables.WirelessLANTable
    url = 'wireless:wirelesslan_list'


@register_search()
class WirelessLinkIndex(SearchIndex):
    model = WirelessLink
    queryset = WirelessLink.objects.prefetch_related('interface_a__device', 'interface_b__device')
    filterset = wireless.filtersets.WirelessLinkFilterSet
    table = wireless.tables.WirelessLinkTable
    url = 'wireless:wirelesslink_list'
