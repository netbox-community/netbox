import django_tables2 as tables

from ipam.models import *
from netbox.tables import NetBoxTable, columns
from tenancy.tables import TenancyColumnsMixin

__all__ = (
    'RouteTargetTable',
    'VRFTable',
)

VRF_TARGETS = """
{% for rt in value.all %}
  <a href="{{ rt.get_absolute_url }}">{{ rt }}</a>{% if not forloop.last %}<br />{% endif %}
{% endfor %}
"""


#
# VRFs
#

class VRFTable(TenancyColumnsMixin, NetBoxTable):
    name = tables.Column(
        linkify=True
    )
    rd = tables.Column(
        verbose_name='RD'
    )
    enforce_unique = columns.BooleanColumn(
        verbose_name='Unique'
    )
    import_targets = columns.TemplateColumn(
        template_code=VRF_TARGETS,
        orderable=False
    )
    export_targets = columns.TemplateColumn(
        template_code=VRF_TARGETS,
        orderable=False
    )
    comments = columns.MarkdownColumn()
    tags = columns.TagColumn(
        url_name='ipam:vrf_list'
    )

    class Meta(NetBoxTable.Meta):
        model = VRF
        fields = (
            'pk', 'id', 'name', 'rd', 'tenant', 'tenant_group', 'enforce_unique', 'import_targets', 'export_targets',
            'description', 'comments', 'tags', 'created', 'last_updated',
        )
        default_columns = ('pk', 'name', 'rd', 'tenant', 'description')


#
# Route targets
#

class RouteTargetTable(TenancyColumnsMixin, NetBoxTable):
    name = tables.Column(
        linkify=True
    )
    comments = columns.MarkdownColumn()
    tags = columns.TagColumn(
        url_name='ipam:routetarget_list'
    )

    class Meta(NetBoxTable.Meta):
        model = RouteTarget
        fields = (
            'pk', 'id', 'name', 'tenant', 'tenant_group', 'description', 'comments', 'tags', 'created', 'last_updated',
        )
        default_columns = ('pk', 'name', 'tenant', 'description')
