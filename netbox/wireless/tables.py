import django_tables2 as tables

from utilities.tables import (
    BaseTable, ButtonsColumn, ChoiceFieldColumn, LinkedCountColumn, MPTTColumn, TagColumn, ToggleColumn,
)
from .models import *

__all__ = (
    'WirelessLANTable',
    'WirelessLANGroupTable',
    'WirelessLinkTable',
)


class WirelessLANGroupTable(BaseTable):
    pk = ToggleColumn()
    name = MPTTColumn(
        linkify=True
    )
    wirelesslan_count = LinkedCountColumn(
        viewname='wireless:wirelesslan_list',
        url_params={'group_id': 'pk'},
        verbose_name='Wireless LANs'
    )
    actions = ButtonsColumn(WirelessLANGroup)

    class Meta(BaseTable.Meta):
        model = WirelessLANGroup
        fields = ('pk', 'name', 'wirelesslan_count', 'description', 'slug', 'actions')
        default_columns = ('pk', 'name', 'wirelesslan_count', 'description', 'actions')


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
