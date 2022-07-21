import django_tables2 as tables

from dcim.models import Interface
from netbox.tables import NetBoxTable, columns
from wireless.models import *

__all__ = (
    'WirelessLANGroupTable',
    'WirelessLANInterfacesTable',
    'WirelessLANTable',
)


class WirelessLANGroupTable(NetBoxTable):
    name = columns.MPTTColumn(
        linkify=True
    )
    wirelesslan_count = columns.LinkedCountColumn(
        viewname='wireless:wirelesslan_list',
        url_params={'group_id': 'pk'},
        verbose_name='Wireless LANs'
    )
    tags = columns.TagColumn(
        url_name='wireless:wirelesslangroup_list'
    )

    class Meta(NetBoxTable.Meta):
        model = WirelessLANGroup
        fields = (
            'pk', 'name', 'wirelesslan_count', 'description', 'slug', 'tags', 'created', 'last_updated', 'actions',
        )
        default_columns = ('pk', 'name', 'wirelesslan_count', 'description')


class WirelessLANTable(NetBoxTable):
    ssid = tables.Column(
        linkify=True
    )
    group = tables.Column(
        linkify=True
    )
    interface_count = tables.Column(
        verbose_name='Interfaces'
    )
    tags = columns.TagColumn(
        url_name='wireless:wirelesslan_list'
    )

    class Meta(NetBoxTable.Meta):
        model = WirelessLAN
        fields = (
            'pk', 'ssid', 'group', 'description', 'vlan', 'interface_count', 'auth_type', 'auth_cipher', 'auth_psk',
            'tags', 'created', 'last_updated',
        )
        default_columns = ('pk', 'ssid', 'group', 'description', 'vlan', 'auth_type', 'interface_count')


class WirelessLANInterfacesTable(NetBoxTable):
    device = tables.Column(
        linkify=True
    )
    name = tables.Column(
        linkify=True
    )

    class Meta(NetBoxTable.Meta):
        model = Interface
        fields = ('pk', 'device', 'name', 'rf_role', 'rf_channel')
        default_columns = ('pk', 'device', 'name', 'rf_role', 'rf_channel')
