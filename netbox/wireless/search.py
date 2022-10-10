import wireless.filtersets
import wireless.tables
from dcim.models import Interface
from netbox.search.models import SearchMixin
from netbox.search import register_search
from utilities.utils import count_related
from wireless.models import WirelessLAN, WirelessLink


@register_search(WirelessLAN)
class WirelessLANIndex(SearchMixin):
    queryset = WirelessLAN.objects.prefetch_related('group', 'vlan').annotate(
        interface_count=count_related(Interface, 'wireless_lans')
    )
    filterset = wireless.filtersets.WirelessLANFilterSet
    table = wireless.tables.WirelessLANTable
    url = 'wireless:wirelesslan_list'
    choice_header = 'Wireless'


@register_search(WirelessLink)
class WirelessLinkIndex(SearchMixin):
    queryset = WirelessLink.objects.prefetch_related('interface_a__device', 'interface_b__device')
    filterset = wireless.filtersets.WirelessLinkFilterSet
    table = wireless.tables.WirelessLinkTable
    url = 'wireless:wirelesslink_list'
    choice_header = 'Wireless'
