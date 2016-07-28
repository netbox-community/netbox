import django_tables2 as tables
from django_tables2.utils import Accessor

from utilities.tables import BaseTable, ToggleColumn

from .models import Circuit, CircuitType, Provider


CIRCUITTYPE_ACTIONS = """
{% if perms.circuit.change_circuittype %}
    <a href="{% url 'circuits:circuittype_edit' slug=record.slug %}" class="btn btn-xs btn-warning"><i class="glyphicon glyphicon-pencil" aria-hidden="true"></i></a>
{% endif %}
"""


#
# Providers
#

class ProviderTable(BaseTable):
    pk = ToggleColumn()
    name = tables.LinkColumn('circuits:provider', args=[Accessor('slug')], verbose_name='Name')
    asn = tables.Column(verbose_name='ASN')
    circuit_count = tables.Column(accessor=Accessor('count_circuits'), verbose_name='Circuits')

    class Meta(BaseTable.Meta):
        model = Provider
        fields = ('pk', 'name', 'asn', 'circuit_count')


#
# Circuit types
#

class CircuitTypeTable(BaseTable):
    pk = ToggleColumn()
    name = tables.LinkColumn(verbose_name='Name')
    circuit_count = tables.Column(verbose_name='Circuits')
    slug = tables.Column(verbose_name='Slug')
    actions = tables.TemplateColumn(template_code=CIRCUITTYPE_ACTIONS, attrs={'td': {'class': 'text-right'}},
                                    verbose_name='')

    class Meta(BaseTable.Meta):
        model = CircuitType
        fields = ('pk', 'name', 'circuit_count', 'slug', 'actions')


#
# Circuits
#

class CircuitTable(BaseTable):
    pk = ToggleColumn()
    cid = tables.LinkColumn('circuits:circuit', args=[Accessor('pk')], verbose_name='ID')
    type = tables.Column(verbose_name='Type')
    provider = tables.LinkColumn('circuits:provider', args=[Accessor('provider.slug')], verbose_name='Provider')
    tenant = tables.LinkColumn('tenancy:tenant', args=[Accessor('tenant.slug')], verbose_name='Tenant')
    site = tables.LinkColumn('dcim:site', args=[Accessor('site.slug')], verbose_name='Site')
    port_speed_human = tables.Column(verbose_name='Port Speed')
    commit_rate_human = tables.Column(verbose_name='Commit Rate')

    class Meta(BaseTable.Meta):
        model = Circuit
        fields = ('pk', 'cid', 'type', 'provider', 'tenant', 'site', 'port_speed_human', 'commit_rate_human')
