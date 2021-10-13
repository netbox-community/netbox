import django_tables2 as tables

from .models import *
from utilities.tables import BaseTable, ChoiceFieldColumn, TagColumn, ToggleColumn

__all__ = (
    'WirelessLANTable',
    'WirelessLinkTable',
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


class WirelessLinkTable(BaseTable):
    pk = ToggleColumn()
    id = tables.Column(
        linkify=True,
        verbose_name='ID'
    )
    status = ChoiceFieldColumn()
    interface_a = tables.Column(
        linkify=True
    )
    interface_b = tables.Column(
        linkify=True
    )
    tags = TagColumn(
        url_name='wireless:wirelesslink_list'
    )

    class Meta(BaseTable.Meta):
        model = WirelessLink
        fields = ('pk', 'id', 'status', 'interface_a', 'interface_b', 'ssid', 'description')
        default_columns = ('pk', 'id', 'status', 'interface_a', 'interface_b', 'ssid', 'description')
