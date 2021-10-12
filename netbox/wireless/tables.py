import django_tables2 as tables

from .models import WirelessLAN
from utilities.tables import BaseTable, TagColumn, ToggleColumn

__all__ = (
    'WirelessLANTable',
)


class WirelessLANTable(BaseTable):
    pk = ToggleColumn()
    ssid = tables.Column(
        linkify=True
    )
    tags = TagColumn(
        url_name='wireless:wirelesslan_list'
    )

    class Meta(BaseTable.Meta):
        model = WirelessLAN
        fields = ('pk', 'ssid', 'description', 'vlan')
        default_columns = ('pk', 'ssid', 'description', 'vlan')
