import django_tables2 as tables

from ipam.models import *
from netbox.tables import BaseTable, columns

__all__ = (
    'ServiceTable',
    'ServiceTemplateTable',
)


class ServiceTemplateTable(BaseTable):
    pk = columns.ToggleColumn()
    name = tables.Column(
        linkify=True
    )
    ports = tables.Column(
        accessor=tables.A('port_list')
    )
    tags = columns.TagColumn(
        url_name='ipam:servicetemplate_list'
    )

    class Meta(BaseTable.Meta):
        model = ServiceTemplate
        fields = ('pk', 'id', 'name', 'protocol', 'ports', 'description', 'tags')
        default_columns = ('pk', 'name', 'protocol', 'ports', 'description')


class ServiceTable(BaseTable):
    pk = columns.ToggleColumn()
    name = tables.Column(
        linkify=True
    )
    parent = tables.Column(
        linkify=True,
        order_by=('device', 'virtual_machine')
    )
    ports = tables.Column(
        accessor=tables.A('port_list')
    )
    tags = columns.TagColumn(
        url_name='ipam:service_list'
    )

    class Meta(BaseTable.Meta):
        model = Service
        fields = (
            'pk', 'id', 'name', 'parent', 'protocol', 'ports', 'ipaddresses', 'description', 'tags', 'created',
            'last_updated',
        )
        default_columns = ('pk', 'name', 'parent', 'protocol', 'ports', 'description')
