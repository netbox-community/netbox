import django_tables2 as tables
from django.utils.translation import gettext_lazy as _

from ipam.models import *
from netbox.tables import PrimaryModelTable, columns
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

class VRFTable(TenancyColumnsMixin, PrimaryModelTable):
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
    tags = columns.TagColumn(
        url_name='ipam:vrf_list'
    )

    class Meta(PrimaryModelTable.Meta):
        model = VRF
        fields = (
            'pk', 'id', 'name', 'rd', 'tenant', 'tenant_group', 'enforce_unique', 'import_targets', 'export_targets',
            'description', 'comments', 'tags', 'created', 'last_updated',
        )
        default_columns = ('pk', 'name', 'rd', 'tenant', 'description')


#
# Route targets
#

class RouteTargetTable(TenancyColumnsMixin, PrimaryModelTable):
    name = tables.Column(
        verbose_name=_('Name'),
        linkify=True
    )
    tags = columns.TagColumn(
        url_name='ipam:routetarget_list'
    )

    class Meta(PrimaryModelTable.Meta):
        model = RouteTarget
        fields = (
            'pk', 'id', 'name', 'tenant', 'tenant_group', 'description', 'comments', 'tags', 'created', 'last_updated',
        )
        default_columns = ('pk', 'name', 'tenant', 'description')
