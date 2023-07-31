from django.utils.translation import gettext_lazy as _
import django_tables2 as tables
from tenancy.models import *
from tenancy.tables import ContactsColumnMixin

from netbox.tables import NetBoxTable, columns

__all__ = (
    'TenantGroupTable',
    'TenantTable',
)


class TenantGroupTable(NetBoxTable):
    name = columns.MPTTColumn(
        verbose_name=_('Name'),
        linkify=True
    )
    tenant_count = columns.LinkedCountColumn(
        viewname='tenancy:tenant_list',
        url_params={'group_id': 'pk'},
        verbose_name=_('Tenants')
    )
    tags = columns.TagColumn(
        url_name='tenancy:tenantgroup_list'
    )

    class Meta(NetBoxTable.Meta):
        model = TenantGroup
        fields = (
            'pk', 'id', 'name', 'tenant_count', 'description', 'slug', 'tags', 'created', 'last_updated', 'actions',
        )
        default_columns = ('pk', 'name', 'tenant_count', 'description')


class TenantTable(ContactsColumnMixin, NetBoxTable):
    name = tables.Column(
        verbose_name=_('Name'),
        linkify=True
    )
    group = tables.Column(
        verbose_name=_('Group'),
        linkify=True
    )
    comments = columns.MarkdownColumn(
        verbose_name=_('Comments'),
    )
    tags = columns.TagColumn(
        url_name='tenancy:tenant_list'
    )

    class Meta(NetBoxTable.Meta):
        model = Tenant
        fields = (
            'pk', 'id', 'name', 'slug', 'group', 'description', 'comments', 'contacts', 'tags', 'created',
            'last_updated',
        )
        default_columns = ('pk', 'name', 'group', 'description')
