import django_tables2 as tables

from ipam.models import *
from netbox.tables import NetBoxTable, columns

__all__ = (
    'FHRPGroupTable',
    'FHRPGroupAssignmentTable',
)


IPADDRESSES = """
{% for ip in record.ip_addresses.all %}
  <a href="{{ ip.get_absolute_url }}">{{ ip }}</a><br />
{% endfor %}
"""


class FHRPGroupTable(NetBoxTable):
    group_id = tables.Column(
        linkify=True
    )
    comments = columns.MarkdownColumn()
    ip_addresses = tables.TemplateColumn(
        template_code=IPADDRESSES,
        orderable=False,
        verbose_name='IP Addresses'
    )
    interface_count = tables.Column(
        verbose_name='Interfaces'
    )
    tags = columns.TagColumn(
        url_name='ipam:fhrpgroup_list'
    )

    class Meta(NetBoxTable.Meta):
        model = FHRPGroup
        fields = (
            'pk', 'group_id', 'protocol', 'auth_type', 'auth_key', 'description', 'ip_addresses', 'interface_count',
            'tags', 'created', 'last_updated',
        )
        default_columns = ('pk', 'group_id', 'protocol', 'auth_type', 'description', 'ip_addresses', 'interface_count')


class FHRPGroupAssignmentTable(NetBoxTable):
    interface_parent = tables.Column(
        accessor=tables.A('interface.parent_object'),
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
    actions = columns.ActionsColumn(
        sequence=('edit', 'delete')
    )

    class Meta(NetBoxTable.Meta):
        model = FHRPGroupAssignment
        fields = ('pk', 'group', 'interface_parent', 'interface', 'priority')
        exclude = ('id',)
