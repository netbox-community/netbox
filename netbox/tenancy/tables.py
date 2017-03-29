import django_tables2 as tables
from django_tables2.utils import Accessor

from utilities.tables import BaseTable, SearchTable, ToggleColumn

from .models import Tenant, TenantGroup


TENANTGROUP_ACTIONS = """
{% if perms.tenancy.change_tenantgroup %}
    <a href="{% url 'tenancy:tenantgroup_edit' slug=record.slug %}" class="btn btn-xs btn-warning"><i class="glyphicon glyphicon-pencil" aria-hidden="true"></i></a>
{% endif %}
"""


#
# Tenant groups
#

class TenantGroupTable(BaseTable):
    pk = ToggleColumn()
    name = tables.LinkColumn(verbose_name='Name')
    tenant_count = tables.Column(verbose_name='Tenants')
    slug = tables.Column(verbose_name='Slug')
    actions = tables.TemplateColumn(template_code=TENANTGROUP_ACTIONS, attrs={'td': {'class': 'text-right'}},
                                    verbose_name='')

    class Meta(BaseTable.Meta):
        model = TenantGroup
        fields = ('pk', 'name', 'tenant_count', 'slug', 'actions')


#
# Tenants
#

class TenantTable(BaseTable):
    pk = ToggleColumn()
    name = tables.LinkColumn()

    class Meta(BaseTable.Meta):
        model = Tenant
        fields = ('pk', 'name', 'group', 'description')


class TenantSearchTable(SearchTable):

    class Meta(SearchTable.Meta):
        model = Tenant
        fields = ('name', 'group', 'description')
