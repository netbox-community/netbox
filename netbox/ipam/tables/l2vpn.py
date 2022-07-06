import django_tables2 as tables

from ipam.models import *
from ipam.models.l2vpn import L2VPN, L2VPNTermination
from netbox.tables import NetBoxTable, columns

__all__ = (
    'L2VPNTable',
    'L2VPNTerminationTable',
)

L2VPN_TARGETS = """
{% for rt in value.all %}
  <a href="{{ rt.get_absolute_url }}">{{ rt }}</a>{% if not forloop.last %}<br />{% endif %}
{% endfor %}
"""


class L2VPNTable(NetBoxTable):
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

    class Meta(NetBoxTable.Meta):
        model = L2VPN
        fields = ('pk', 'name', 'slug', 'type', 'description', 'import_targets', 'export_targets', 'tenant', 'actions')
        default_columns = ('pk', 'name', 'type', 'description', 'actions')


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
        verbose_name='Assigned Object',
        linkify=True,
        orderable=False
    )

    class Meta(NetBoxTable.Meta):
        model = L2VPNTermination
        fields = ('pk', 'l2vpn', 'assigned_object_type', 'assigned_object', 'actions')
        default_columns = ('pk', 'l2vpn', 'assigned_object_type', 'assigned_object', 'actions')
