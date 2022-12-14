import django_tables2 as tables

from ipam.models import *
from netbox.tables import NetBoxTable, columns

__all__ = (
    'ServiceTable',
    'ServiceTemplateTable',
)


class ServiceTemplateTable(NetBoxTable):
    name = tables.Column(
        linkify=True
    )
    ports = tables.Column(
        accessor=tables.A('port_list'),
        order_by=tables.A('ports'),
    )
    comments = columns.MarkdownColumn()
    tags = columns.TagColumn(
        url_name='ipam:servicetemplate_list'
    )

    class Meta(NetBoxTable.Meta):
        model = ServiceTemplate
        fields = (
            'pk', 'id', 'name', 'protocol', 'ports', 'description', 'comments', 'tags', 'created', 'last_updated',
        )
        default_columns = ('pk', 'name', 'protocol', 'ports', 'description')


class ServiceTable(NetBoxTable):
    name = tables.Column(
        linkify=True
    )
    parent = tables.Column(
        linkify=True,
        order_by=('device', 'virtual_machine')
    )
    ports = tables.Column(
        accessor=tables.A('port_list'),
        order_by=tables.A('ports'),
    )
    comments = columns.MarkdownColumn()
    tags = columns.TagColumn(
        url_name='ipam:service_list'
    )

    class Meta(NetBoxTable.Meta):
        model = Service
        fields = (
            'pk', 'id', 'name', 'parent', 'protocol', 'ports', 'ipaddresses', 'description', 'comments', 'tags',
            'created', 'last_updated',
        )
        default_columns = ('pk', 'name', 'parent', 'protocol', 'ports', 'description')
