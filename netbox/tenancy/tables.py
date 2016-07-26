import django_tables2 as tables
from django_tables2.utils import Accessor

from utilities.tables import BaseTable, ToggleColumn

from .models import Tenant, TenantGroup


TENANTGROUP_EDIT_LINK = """
{% if perms.tenancy.change_tenantgroup %}
    <a href="{% url 'tenancy:tenantgroup_edit' slug=record.slug %}">Edit</a>
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
    edit = tables.TemplateColumn(template_code=TENANTGROUP_EDIT_LINK, verbose_name='')

    class Meta(BaseTable.Meta):
        model = TenantGroup
        fields = ('pk', 'name', 'tenant_count', 'slug', 'edit')


#
# Tenants
#

class TenantTable(BaseTable):
    pk = ToggleColumn()
    name = tables.LinkColumn('tenancy:tenant', args=[Accessor('slug')], verbose_name='Name')
    group = tables.Column(verbose_name='Group')

    class Meta(BaseTable.Meta):
        model = Tenant
        fields = ('pk', 'name', 'group')
