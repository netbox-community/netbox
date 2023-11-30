import django_tables2 as tables
from django.utils.translation import gettext_lazy as _

from ipam.models import *
from netbox.tables import NetBoxTable, columns
from tenancy.tables import TenancyColumnsMixin

__all__ = (
    'ASNTable',
    'ASNRangeTable',
)


class ASNRangeTable(TenancyColumnsMixin, NetBoxTable):
    name = tables.Column(
        verbose_name=_('Name'),
        linkify=True
    )
    rir = tables.Column(
        verbose_name=_('RIR'),
        linkify=True
    )
    tags = columns.TagColumn(
        url_name='ipam:asnrange_list'
    )
    asn_count = tables.Column(
        verbose_name=_('ASNs')
    )

    class Meta(NetBoxTable.Meta):
        model = ASNRange
        fields = (
            'pk', 'name', 'slug', 'rir', 'start', 'end', 'asn_count', 'tenant', 'tenant_group', 'description', 'tags',
            'created', 'last_updated', 'actions',
        )
        default_columns = ('pk', 'name', 'rir', 'start', 'end', 'tenant', 'asn_count', 'description')


class ASNTable(TenancyColumnsMixin, NetBoxTable):
    asn = tables.Column(
        verbose_name=_('ASN'),
        linkify=True
    )
    rir = tables.Column(
        verbose_name=_('RIR'),
        linkify=True
    )
    asn_asdot = tables.Column(
        accessor=tables.A('asn_asdot'),
        linkify=True,
        order_by=tables.A('asn'),
        verbose_name=_('ASDOT')
    )
    site_count = columns.LinkedCountColumn(
        viewname='dcim:site_list',
        url_params={'asn_id': 'pk'},
        verbose_name=_('Site Count')
    )
    provider_count = columns.LinkedCountColumn(
        viewname='circuits:provider_list',
        url_params={'asn_id': 'pk'},
        verbose_name=_('Provider Count')
    )
    sites = columns.ManyToManyColumn(
        linkify_item=True,
        verbose_name=_('Sites')
    )
    comments = columns.MarkdownColumn(
        verbose_name=_('Comments'),
    )
    tags = columns.TagColumn(
        url_name='ipam:asn_list'
    )

    class Meta(NetBoxTable.Meta):
        model = ASN
        fields = (
            'pk', 'asn', 'asn_asdot', 'rir', 'site_count', 'provider_count', 'tenant', 'tenant_group', 'description',
            'comments', 'sites', 'tags', 'created', 'last_updated', 'actions',
        )
        default_columns = (
            'pk', 'asn', 'rir', 'site_count', 'provider_count', 'sites', 'description', 'tenant',
        )
