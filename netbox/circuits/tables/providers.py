import django_tables2 as tables
from django_tables2.utils import Accessor

from circuits.models import *
from netbox.tables import NetBoxTable, columns

__all__ = (
    'ProviderTable',
    'ProviderNetworkTable',
)


class ProviderTable(NetBoxTable):
    name = tables.Column(
        linkify=True
    )
    circuit_count = tables.Column(
        accessor=Accessor('count_circuits'),
        verbose_name='Circuits'
    )
    comments = columns.MarkdownColumn()
    tags = columns.TagColumn(
        url_name='circuits:provider_list'
    )

    class Meta(NetBoxTable.Meta):
        model = Provider
        fields = (
            'pk', 'id', 'name', 'asn', 'account', 'portal_url', 'noc_contact', 'admin_contact', 'circuit_count',
            'comments', 'tags', 'created', 'last_updated',
        )
        default_columns = ('pk', 'name', 'asn', 'account', 'circuit_count')


class ProviderNetworkTable(NetBoxTable):
    name = tables.Column(
        linkify=True
    )
    provider = tables.Column(
        linkify=True
    )
    comments = columns.MarkdownColumn()
    tags = columns.TagColumn(
        url_name='circuits:providernetwork_list'
    )

    class Meta(NetBoxTable.Meta):
        model = ProviderNetwork
        fields = (
            'pk', 'id', 'name', 'provider', 'service_id', 'description', 'comments', 'created', 'last_updated', 'tags',
        )
        default_columns = ('pk', 'name', 'provider', 'service_id', 'description')
