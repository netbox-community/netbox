import django_tables2 as tables

from utilities.tables import (
    BaseTable, ContentTypeColumn, MarkdownColumn, TagColumn, ToggleColumn,
)
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
    member_count = tables.Column(
        verbose_name='Members'
    )
    tags = TagColumn(
        url_name='ipam:fhrpgroup_list'
    )

    class Meta(BaseTable.Meta):
        model = FHRPGroup
        fields = (
            'pk', 'group_id', 'protocol', 'auth_type', 'auth_key', 'description', 'ip_addresses', 'member_count',
            'tags',
        )
        default_columns = ('pk', 'group_id', 'protocol', 'auth_type', 'description', 'ip_addresses', 'member_count')


class FHRPGroupAssignmentTable(BaseTable):
    pk = ToggleColumn()
    content_type = ContentTypeColumn(
        verbose_name='Object Type'
    )
    object = tables.Column(
        linkify=True,
        orderable=False
    )
    group = tables.Column(
        linkify=True
    )

    class Meta(BaseTable.Meta):
        model = FHRPGroupAssignment
        fields = ('pk', 'content_type', 'object', 'group', 'priority')
        default_columns = ('pk', 'content_type', 'object', 'group', 'priority')
