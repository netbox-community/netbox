import django_tables2 as tables

from ipam.models import L2VPN, L2VPNTermination
from netbox.tables import NetBoxTable, columns
from tenancy.tables import TenancyColumnsMixin

__all__ = (
    'L2VPNTable',
    'L2VPNTerminationTable',
)

L2VPN_TARGETS = """
{% for rt in value.all %}
  <a href="{{ rt.get_absolute_url }}">{{ rt }}</a>{% if not forloop.last %}<br />{% endif %}
{% endfor %}
"""


class L2VPNTable(TenancyColumnsMixin, NetBoxTable):
    pk = columns.ToggleColumn()
    name = tables.Column(
        linkify=True
    )
    import_targets = columns.TemplateColumn(
        template_code=L2VPN_TARGETS,
        orderable=False
    )
    export_targets = columns.TemplateColumn(
        template_code=L2VPN_TARGETS,
        orderable=False
    )
    comments = columns.MarkdownColumn()
    tags = columns.TagColumn(
        url_name='ipam:l2vpn_list'
    )

    class Meta(NetBoxTable.Meta):
        model = L2VPN
        fields = (
            'pk', 'name', 'slug', 'identifier', 'type', 'import_targets', 'export_targets', 'tenant', 'tenant_group',
            'description', 'comments', 'tags', 'created', 'last_updated',
        )
        default_columns = ('pk', 'name', 'identifier', 'type', 'description')


class L2VPNTerminationTable(NetBoxTable):
    pk = columns.ToggleColumn()
    l2vpn = tables.Column(
        verbose_name='L2VPN',
        linkify=True
    )
    assigned_object_type = columns.ContentTypeColumn(
        verbose_name='Object Type'
    )
    assigned_object = tables.Column(
        linkify=True,
        orderable=False,
        verbose_name='Object'
    )
    assigned_object_parent = tables.Column(
        linkify=True,
        orderable=False,
        verbose_name='Object Parent'
    )
    assigned_object_site = tables.Column(
        linkify=True,
        orderable=False,
        verbose_name='Object Site'
    )

    class Meta(NetBoxTable.Meta):
        model = L2VPNTermination
        fields = (
            'pk', 'l2vpn', 'assigned_object_type', 'assigned_object', 'assigned_object_parent', 'assigned_object_site',
            'actions',
        )
        default_columns = (
            'pk', 'l2vpn', 'assigned_object_type', 'assigned_object_parent', 'assigned_object', 'actions',
        )
