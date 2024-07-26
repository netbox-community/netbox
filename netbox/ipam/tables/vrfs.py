from django.utils.translation import gettext_lazy as _
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
        verbose_name=_('Name'),
        linkify=True
    )
    rd = tables.Column(
        verbose_name=_('RD')
    )
    enforce_unique = columns.BooleanColumn(
        verbose_name=_('Unique'),
        false_mark=None
    )
    import_targets = columns.TemplateColumn(
        verbose_name=_('Import Targets'),
        template_code=VRF_TARGETS,
        orderable=False
    )
    export_targets = columns.TemplateColumn(
        verbose_name=_('Export Targets'),
        template_code=VRF_TARGETS,
        orderable=False
    )
    comments = columns.MarkdownColumn(
        verbose_name=_('Comments'),
    )
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
        verbose_name=_('Name'),
        linkify=True
    )
    comments = columns.MarkdownColumn(
        verbose_name=_('Comments'),
    )
    tags = columns.TagColumn(
        url_name='ipam:routetarget_list'
    )

    class Meta(NetBoxTable.Meta):
        model = RouteTarget
        fields = (
            'pk', 'id', 'name', 'tenant', 'tenant_group', 'description', 'comments', 'tags', 'created', 'last_updated',
        )
        default_columns = ('pk', 'name', 'tenant', 'description')
