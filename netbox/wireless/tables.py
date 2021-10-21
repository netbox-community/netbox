import django_tables2 as tables

from dcim.models import Interface
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
    tags = TagColumn(
        url_name='wireless:wirelesslangroup_list'
    )
    actions = ButtonsColumn(WirelessLANGroup)

    class Meta(BaseTable.Meta):
        model = WirelessLANGroup
        fields = ('pk', 'name', 'wirelesslan_count', 'description', 'slug', 'tags', 'actions')
        default_columns = ('pk', 'name', 'wirelesslan_count', 'description', 'actions')


class WirelessLANTable(BaseTable):
    pk = ToggleColumn()
    ssid = tables.Column(
        linkify=True
    )
    group = tables.Column(
        linkify=True
    )
    interface_count = tables.Column(
        verbose_name='Interfaces'
    )
    tags = TagColumn(
        url_name='wireless:wirelesslan_list'
    )

    class Meta(BaseTable.Meta):
        model = WirelessLAN
        fields = (
            'pk', 'ssid', 'group', 'description', 'vlan', 'interface_count', 'auth_type', 'auth_cipher', 'auth_psk',
            'tags',
        )
        default_columns = ('pk', 'ssid', 'group', 'description', 'vlan', 'auth_type', 'interface_count')


class WirelessLANInterfacesTable(BaseTable):
    pk = ToggleColumn()
    device = tables.Column(
        linkify=True
    )
    name = tables.Column(
        linkify=True
    )

    class Meta(BaseTable.Meta):
        model = Interface
        fields = ('pk', 'device', 'name', 'rf_role', 'rf_channel')
        default_columns = ('pk', 'device', 'name', 'rf_role', 'rf_channel')


class WirelessLinkTable(BaseTable):
    pk = ToggleColumn()
    id = tables.Column(
        linkify=True,
        verbose_name='ID'
    )
    status = ChoiceFieldColumn()
    device_a = tables.Column(
        accessor=tables.A('interface_a__device'),
        linkify=True
    )
    interface_a = tables.Column(
        linkify=True
    )
    device_b = tables.Column(
        accessor=tables.A('interface_b__device'),
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
        fields = (
            'pk', 'id', 'status', 'device_a', 'interface_a', 'device_b', 'interface_b', 'ssid', 'description',
            'auth_type', 'auth_cipher', 'auth_psk', 'tags',
        )
        default_columns = (
            'pk', 'id', 'status', 'device_a', 'interface_a', 'device_b', 'interface_b', 'ssid', 'auth_type',
            'description',
        )
