import django_tables2 as tables
from django.utils.translation import gettext_lazy as _

from ipam.models import *
from netbox.tables import PrimaryModelTable, columns
from tenancy.tables import ContactsColumnMixin

__all__ = (
    'ServiceTable',
    'ServiceTemplateTable',
)


class ServiceTemplateTable(PrimaryModelTable):
    name = tables.Column(
        verbose_name=_('Name'),
        linkify=True
    )
    ports = tables.Column(
        verbose_name=_('Port Mappings'),
        accessor=tables.A('port_list'),
        orderable=False,
    )
    tags = columns.TagColumn(
        url_name='ipam:servicetemplate_list'
    )

    class Meta(PrimaryModelTable.Meta):
        model = ServiceTemplate
        fields = (
            'pk', 'id', 'name', 'ports', 'description', 'comments', 'tags', 'created', 'last_updated',
        )
        default_columns = ('pk', 'name', 'ports', 'description')


class ServiceTable(ContactsColumnMixin, PrimaryModelTable):
    name = tables.Column(
        verbose_name=_('Name'),
        linkify=True
    )
    parent = tables.Column(
        verbose_name=_('Parent'),
        linkify=True,
        order_by=('device', 'virtual_machine')
    )
    ports = tables.Column(
        verbose_name=_('Port Mappings'),
        accessor=tables.A('port_list'),
        orderable=False,
    )
    tags = columns.TagColumn(
        url_name='ipam:service_list'
    )

    class Meta(PrimaryModelTable.Meta):
        model = Service
        fields = (
            'pk', 'id', 'name', 'parent', 'ports', 'ipaddresses', 'description', 'contacts', 'comments',
            'tags', 'created', 'last_updated',
        )
        default_columns = ('pk', 'name', 'parent', 'ports', 'description')
