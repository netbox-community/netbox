import django_tables2 as tables
from circuits.models import *
from django_tables2.utils import Accessor
from tenancy.tables import ContactsColumnMixin

from netbox.tables import NetBoxTable, columns

__all__ = (
    'ProviderTable',
    'ProviderAccountTable',
    'ProviderNetworkTable',
)


class ProviderTable(ContactsColumnMixin, NetBoxTable):
    name = tables.Column(
        linkify=True
    )
    accounts = columns.ManyToManyColumn(
        linkify_item=True,
        verbose_name='Accounts'
    )
    account_count = columns.LinkedCountColumn(
        accessor=tables.A('accounts__count'),
        viewname='circuits:provideraccount_list',
        url_params={'account_id': 'pk'},
        verbose_name='Account Count'
    )
    asns = columns.ManyToManyColumn(
        linkify_item=True,
        verbose_name='ASNs'
    )
    asn_count = columns.LinkedCountColumn(
        accessor=tables.A('asns__count'),
        viewname='ipam:asn_list',
        url_params={'provider_id': 'pk'},
        verbose_name='ASN Count'
    )
    circuit_count = columns.LinkedCountColumn(
        accessor=Accessor('count_circuits'),
        viewname='circuits:circuit_list',
        url_params={'provider_id': 'pk'},
        verbose_name='Circuits'
    )
    comments = columns.MarkdownColumn()
    tags = columns.TagColumn(
        url_name='circuits:provider_list'
    )

    class Meta(NetBoxTable.Meta):
        model = Provider
        fields = (
            'pk', 'id', 'name', 'accounts', 'account_count', 'asns', 'asn_count', 'circuit_count', 'description',
            'comments', 'contacts', 'tags', 'created', 'last_updated',
        )
        default_columns = ('pk', 'name', 'account_count', 'circuit_count')


class ProviderAccountTable(ContactsColumnMixin, NetBoxTable):
    account = tables.Column(
        linkify=True
    )
    name = tables.Column()
    provider = tables.Column(
        linkify=True
    )
    circuit_count = columns.LinkedCountColumn(
        accessor=Accessor('count_circuits'),
        viewname='circuits:circuit_list',
        url_params={'provider_account_id': 'pk'},
        verbose_name='Circuits'
    )
    comments = columns.MarkdownColumn()
    tags = columns.TagColumn(
        url_name='circuits:provideraccount_list'
    )

    class Meta(NetBoxTable.Meta):
        model = ProviderAccount
        fields = (
            'pk', 'id', 'account', 'name', 'provider', 'circuit_count', 'comments', 'contacts', 'tags', 'created',
            'last_updated',
        )
        default_columns = ('pk', 'account', 'name', 'provider', 'circuit_count')


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
