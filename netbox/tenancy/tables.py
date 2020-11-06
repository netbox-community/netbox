import django_tables2 as tables

from utilities.tables import BaseTable, ButtonsColumn, LinkedCountColumn, TagColumn, ToggleColumn
from .models import Tenant, TenantGroup

MPTT_LINK = """
{% if record.get_children %}
    <span style="padding-left: {{ record.get_ancestors|length }}0px "><i class="mdi mdi-chevron-right"></i>
{% else %}
    <span style="padding-left: {{ record.get_ancestors|length }}9px">
{% endif %}
    <a href="{{ record.get_absolute_url }}">{{ record.name }}</a>
</span>
"""

COL_TENANT = """
{% if record.tenant %}
    <a href="{% url 'tenancy:tenant' slug=record.tenant.slug %}" title="{{ record.tenant.description }}">{{ record.tenant }}</a>
{% else %}
    &mdash;
{% endif %}
"""


#
# Tenant groups
#

class TenantGroupTable(BaseTable):
    pk = ToggleColumn()
    name = tables.TemplateColumn(
        template_code=MPTT_LINK,
        orderable=False
    )
    tenant_count = LinkedCountColumn(
        viewname='tenancy:tenant_list',
        url_params={'group': 'slug'},
        verbose_name='Tenants'
    )
    actions = ButtonsColumn(TenantGroup, pk_field='slug')

    class Meta(BaseTable.Meta):
        model = TenantGroup
        fields = ('pk', 'name', 'tenant_count', 'description', 'slug', 'actions')
        default_columns = ('pk', 'name', 'tenant_count', 'description', 'actions')


#
# Tenants
#

class TenantTable(BaseTable):
    pk = ToggleColumn()
    name = tables.LinkColumn()
    tags = TagColumn(
        url_name='tenancy:tenant_list'
    )

    class Meta(BaseTable.Meta):
        model = Tenant
        fields = ('pk', 'name', 'slug', 'group', 'description', 'tags')
        default_columns = ('pk', 'name', 'group', 'description')
