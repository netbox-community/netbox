import django_tables2 as tables

from utilities.tables import BaseTable, TagColumn, ToggleColumn
from ipam.models import *

__all__ = (
    'ServiceTable',
)


#
# Services
#

class ServiceTable(BaseTable):
    pk = ToggleColumn()
    name = tables.Column(
        linkify=True
    )
    parent = tables.Column(
        linkify=True,
        order_by=('device', 'virtual_machine')
    )
    ports = tables.TemplateColumn(
        template_code='{{ record.port_list }}',
        verbose_name='Ports'
    )
    tags = TagColumn(
        url_name='ipam:service_list'
    )

    class Meta(BaseTable.Meta):
        model = Service
        fields = ('pk', 'id', 'name', 'parent', 'protocol', 'ports', 'ipaddresses', 'description', 'tags')
        default_columns = ('pk', 'name', 'parent', 'protocol', 'ports', 'description')
