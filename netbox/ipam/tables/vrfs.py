import django_tables2 as tables

from ipam.models import *
from netbox.tables import NetBoxTable, columns
from tenancy.tables import TenantColumn

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

class VRFTable(NetBoxTable):
    name = tables.Column(
        linkify=True
    )
    rd = tables.Column(
        verbose_name='RD'
    )
    tenant = TenantColumn()
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
    tags = columns.TagColumn(
        url_name='ipam:vrf_list'
    )

    class Meta(NetBoxTable.Meta):
        model = VRF
        fields = (
            'pk', 'id', 'name', 'rd', 'tenant', 'enforce_unique', 'description', 'import_targets', 'export_targets',
            'tags', 'created', 'last_updated',
        )
        default_columns = ('pk', 'name', 'rd', 'tenant', 'description')


#
# Route targets
#

class RouteTargetTable(NetBoxTable):
    name = tables.Column(
        linkify=True
    )
    tenant = TenantColumn()
    tags = columns.TagColumn(
        url_name='ipam:vrf_list'
    )

    class Meta(NetBoxTable.Meta):
        model = RouteTarget
        fields = ('pk', 'id', 'name', 'tenant', 'description', 'tags', 'created', 'last_updated',)
        default_columns = ('pk', 'name', 'tenant', 'description')
