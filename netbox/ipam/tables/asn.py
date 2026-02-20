import django_tables2 as tables
from django.utils.translation import gettext_lazy as _

from ipam.models import *
from netbox.tables import OrganizationalModelTable, PrimaryModelTable, columns
from tenancy.tables import ContactsColumnMixin, TenancyColumnsMixin

__all__ = (
    'ASNRangeTable',
    'ASNTable',
)


class ASNRangeTable(TenancyColumnsMixin, OrganizationalModelTable):
    name = tables.Column(
        verbose_name=_('Name'),
        linkify=True
    )
    rir = tables.Column(
        verbose_name=_('RIR'),
        linkify=True
    )
    start_asdot = tables.Column(
        accessor=tables.A('start_asdot'),
        order_by=tables.A('start'),
        verbose_name=_('Start (ASDOT)')
    )
    end_asdot = tables.Column(
        accessor=tables.A('end_asdot'),
        order_by=tables.A('end'),
        verbose_name=_('End (ASDOT)')
    )
    tags = columns.TagColumn(
        url_name='ipam:asnrange_list'
    )
    asn_count = tables.Column(
        verbose_name=_('ASNs')
    )

    class Meta(OrganizationalModelTable.Meta):
        model = ASNRange
        fields = (
            'pk', 'name', 'slug', 'rir', 'start', 'start_asdot', 'end', 'end_asdot', 'asn_count', 'tenant',
            'tenant_group', 'description', 'comments', 'tags', 'created', 'last_updated', 'actions',
        )
        default_columns = ('pk', 'name', 'rir', 'start', 'end', 'tenant', 'asn_count', 'description')


class ASNTable(TenancyColumnsMixin, ContactsColumnMixin, PrimaryModelTable):
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
    tags = columns.TagColumn(
        url_name='ipam:asn_list'
    )

    class Meta(PrimaryModelTable.Meta):
        model = ASN
        fields = (
            'pk', 'asn', 'asn_asdot', 'rir', 'site_count', 'provider_count', 'tenant', 'tenant_group', 'description',
            'contacts', 'comments', 'sites', 'tags', 'created', 'last_updated', 'actions',
        )
        default_columns = (
            'pk', 'asn', 'rir', 'site_count', 'provider_count', 'sites', 'description', 'tenant',
        )
