import django_tables2 as tables

from utilities.tables import BaseTable, ButtonsColumn, MarkdownColumn, TagColumn, ToggleColumn
from ipam.models import *

__all__ = (
    'FHRPGroupTable',
    'FHRPGroupAssignmentTable',
)


IPADDRESSES = """
{% for ip in record.ip_addresses.all %}
  <a href="{{ ip.get_absolute_url }}">{{ ip }}</a><br />
{% endfor %}
"""


class FHRPGroupTable(BaseTable):
    pk = ToggleColumn()
    group_id = tables.Column(
        linkify=True
    )
    comments = MarkdownColumn()
    ip_addresses = tables.TemplateColumn(
        template_code=IPADDRESSES,
        orderable=False,
        verbose_name='IP Addresses'
    )
    interface_count = tables.Column(
        verbose_name='Interfaces'
    )
    tags = TagColumn(
        url_name='ipam:fhrpgroup_list'
    )

    class Meta(BaseTable.Meta):
        model = FHRPGroup
        fields = (
            'pk', 'group_id', 'protocol', 'auth_type', 'auth_key', 'description', 'ip_addresses', 'interface_count',
            'tags',
        )
        default_columns = ('pk', 'group_id', 'protocol', 'auth_type', 'description', 'ip_addresses', 'interface_count')


class FHRPGroupAssignmentTable(BaseTable):
    pk = ToggleColumn()
    object_parent = tables.Column(
        accessor=tables.A('object.parent_object'),
        linkify=True,
        orderable=False,
        verbose_name='Parent'
    )
    interface = tables.Column(
        linkify=True,
        orderable=False
    )
    group = tables.Column(
        linkify=True
    )
    actions = ButtonsColumn(
        model=FHRPGroupAssignment,
        buttons=('edit', 'delete', 'foo')
    )

    class Meta(BaseTable.Meta):
        model = FHRPGroupAssignment
        fields = ('pk', 'group', 'object_parent', 'interface', 'priority')
