import django_tables2 as tables

from utilities.tables import BaseTable, ButtonsColumn, LinkedCountColumn, MPTTColumn, TagColumn, ToggleColumn
from .models import Tenant, TenantGroup


#
# Table columns
#

class TenantColumn(tables.TemplateColumn):
    """
    Render a colored label (e.g. for DeviceRoles).
    """
    template_code = """
    {% if record.tenant %}
        <a href="{{ record.tenant.get_absolute_url }}" title="{{ record.tenant.description }}">{{ record.tenant }}</a>
    {% elif record.vrf.tenant %}
        <a href="{{ record.vrf.tenant.get_absolute_url }}" title="{{ record.vrf.tenant.description }}">{{ record.vrf.tenant }}</a>*
    {% else %}
        &mdash;
    {% endif %}
    """

    def __init__(self, *args, **kwargs):
        super().__init__(template_code=self.template_code, *args, **kwargs)

    def value(self, value):
        return str(value)


#
# Tenant groups
#

class TenantGroupTable(BaseTable):
    pk = ToggleColumn()
    name = MPTTColumn(
        linkify=True
    )
    tenant_count = LinkedCountColumn(
        viewname='tenancy:tenant_list',
        url_params={'group': 'slug'},
        verbose_name='Tenants'
    )
    actions = ButtonsColumn(TenantGroup)

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
