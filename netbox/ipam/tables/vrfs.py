import django_tables2 as tables

from tenancy.tables import TenantColumn
from utilities.tables import BaseTable, BooleanColumn, TagColumn, TemplateColumn, ToggleColumn
from ipam.models import *

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

class VRFTable(BaseTable):
    pk = ToggleColumn()
    name = tables.Column(
        linkify=True
    )
    rd = tables.Column(
        verbose_name='RD'
    )
    tenant = TenantColumn()
    enforce_unique = BooleanColumn(
        verbose_name='Unique'
    )
    import_targets = TemplateColumn(
        template_code=VRF_TARGETS,
        orderable=False
    )
    export_targets = TemplateColumn(
        template_code=VRF_TARGETS,
        orderable=False
    )
    tags = TagColumn(
        url_name='ipam:vrf_list'
    )

    class Meta(BaseTable.Meta):
        model = VRF
        fields = (
            'pk', 'id', 'name', 'rd', 'tenant', 'enforce_unique', 'description', 'import_targets', 'export_targets', 'tags',
        )
        default_columns = ('pk', 'name', 'rd', 'tenant', 'description')


#
# Route targets
#

class RouteTargetTable(BaseTable):
    pk = ToggleColumn()
    name = tables.Column(
        linkify=True
    )
    tenant = TenantColumn()
    tags = TagColumn(
        url_name='ipam:vrf_list'
    )

    class Meta(BaseTable.Meta):
        model = RouteTarget
        fields = ('pk', 'id', 'name', 'tenant', 'description', 'tags')
        default_columns = ('pk', 'name', 'tenant', 'description')
