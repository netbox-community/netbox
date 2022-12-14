import django_tables2 as tables

from dcim.models import Interface
from netbox.tables import NetBoxTable, columns
from tenancy.tables import TenancyColumnsMixin
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
    comments = columns.MarkdownColumn()
    tags = columns.TagColumn(
        url_name='wireless:wirelesslangroup_list'
    )

    class Meta(NetBoxTable.Meta):
        model = WirelessLANGroup
        fields = (
            'pk', 'name', 'wirelesslan_count', 'slug', 'description', 'comments', 'tags', 'created', 'last_updated',
            'actions',
        )
        default_columns = ('pk', 'name', 'wirelesslan_count', 'description')


class WirelessLANTable(TenancyColumnsMixin, NetBoxTable):
    ssid = tables.Column(
        linkify=True
    )
    group = tables.Column(
        linkify=True
    )
    status = columns.ChoiceFieldColumn()
    interface_count = tables.Column(
        verbose_name='Interfaces'
    )
    comments = columns.MarkdownColumn()
    tags = columns.TagColumn(
        url_name='wireless:wirelesslan_list'
    )

    class Meta(NetBoxTable.Meta):
        model = WirelessLAN
        fields = (
            'pk', 'ssid', 'group', 'status', 'tenant', 'tenant_group', 'vlan', 'interface_count', 'auth_type',
            'auth_cipher', 'auth_psk', 'description', 'comments', 'tags', 'created', 'last_updated',
        )
        default_columns = ('pk', 'ssid', 'group', 'status', 'description', 'vlan', 'auth_type', 'interface_count')


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
