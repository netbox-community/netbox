from django.utils.translation import gettext_lazy as _
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
        verbose_name=_('Name'),
        linkify=True
    )
    wirelesslan_count = columns.LinkedCountColumn(
        viewname='wireless:wirelesslan_list',
        url_params={'group_id': 'pk'},
        verbose_name=_('Wireless LANs')
    )
    comments = columns.MarkdownColumn(
        verbose_name=_('Comments'),
    )
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
        verbose_name=_('SSID'),
        linkify=True
    )
    group = tables.Column(
        verbose_name=_('Group'),
        linkify=True
    )
    status = columns.ChoiceFieldColumn(
        verbose_name=_('Status'),
    )
    scope_type = columns.ContentTypeColumn(
        verbose_name=_('Scope Type'),
    )
    scope = tables.Column(
        verbose_name=_('Scope'),
        linkify=True,
        orderable=False
    )
    interface_count = tables.Column(
        verbose_name=_('Interfaces')
    )
    comments = columns.MarkdownColumn(
        verbose_name=_('Comments'),
    )
    tags = columns.TagColumn(
        url_name='wireless:wirelesslan_list'
    )

    class Meta(NetBoxTable.Meta):
        model = WirelessLAN
        fields = (
            'pk', 'ssid', 'group', 'status', 'tenant', 'tenant_group', 'vlan', 'interface_count', 'auth_type',
            'auth_cipher', 'auth_psk', 'scope', 'scope_type', 'description', 'comments', 'tags', 'created',
            'last_updated',
        )
        default_columns = ('pk', 'ssid', 'group', 'status', 'description', 'vlan', 'auth_type', 'interface_count')


class WirelessLANInterfacesTable(NetBoxTable):
    device = tables.Column(
        verbose_name=_('Device'),
        linkify=True
    )
    name = tables.Column(
        verbose_name=_('Name'),
        linkify=True
    )

    class Meta(NetBoxTable.Meta):
        model = Interface
        fields = ('pk', 'device', 'name', 'rf_role', 'rf_channel')
        default_columns = ('pk', 'device', 'name', 'rf_role', 'rf_channel')
