import django_tables2 as tables

from netbox.tables import NetBoxTable, columns
from tenancy.tables import TenancyColumnsMixin
from wireless.models import *

__all__ = (
    'WirelessLinkTable',
)


class WirelessLinkTable(TenancyColumnsMixin, NetBoxTable):
    id = tables.Column(
        linkify=True,
        verbose_name='ID'
    )
    status = columns.ChoiceFieldColumn()
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
    tags = columns.TagColumn(
        url_name='wireless:wirelesslink_list'
    )

    class Meta(NetBoxTable.Meta):
        model = WirelessLink
        fields = (
            'pk', 'id', 'status', 'device_a', 'interface_a', 'device_b', 'interface_b', 'ssid', 'tenant',
            'tenant_group', 'description', 'auth_type', 'auth_cipher', 'auth_psk', 'tags', 'created', 'last_updated',
        )
        default_columns = (
            'pk', 'id', 'status', 'device_a', 'interface_a', 'device_b', 'interface_b', 'ssid', 'auth_type',
            'description',
        )
