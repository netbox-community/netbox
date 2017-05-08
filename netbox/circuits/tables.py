import django_tables2 as tables
from django_tables2.utils import Accessor

from utilities.tables import BaseTable, SearchTable, ToggleColumn

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
    name = tables.LinkColumn()
    circuit_count = tables.Column(accessor=Accessor('count_circuits'), verbose_name='Circuits')

    class Meta(BaseTable.Meta):
        model = Provider
        fields = ('pk', 'name', 'asn', 'account', 'circuit_count')


class ProviderSearchTable(SearchTable):
    name = tables.LinkColumn()

    class Meta(SearchTable.Meta):
        model = Provider
        fields = ('name', 'asn', 'account')


#
# Circuit types
#

class CircuitTypeTable(BaseTable):
    pk = ToggleColumn()
    name = tables.LinkColumn()
    circuit_count = tables.Column(verbose_name='Circuits')
    actions = tables.TemplateColumn(
        template_code=CIRCUITTYPE_ACTIONS, attrs={'td': {'class': 'text-right'}}, verbose_name=''
    )

    class Meta(BaseTable.Meta):
        model = CircuitType
        fields = ('pk', 'name', 'circuit_count', 'slug', 'actions')


#
# Circuits
#

class CircuitTable(BaseTable):
    pk = ToggleColumn()
    cid = tables.LinkColumn(verbose_name='ID')
    provider = tables.LinkColumn('circuits:provider', args=[Accessor('provider.slug')])
    tenant = tables.LinkColumn('tenancy:tenant', args=[Accessor('tenant.slug')])
    a_side = tables.LinkColumn(
        'dcim:site', accessor=Accessor('termination_a.site'), orderable=False,
        args=[Accessor('termination_a.site.slug')]
    )
    z_side = tables.LinkColumn(
        'dcim:site', accessor=Accessor('termination_z.site'), orderable=False,
        args=[Accessor('termination_z.site.slug')]
    )

    class Meta(BaseTable.Meta):
        model = Circuit
        fields = ('pk', 'cid', 'type', 'provider', 'tenant', 'a_side', 'z_side', 'description')


class CircuitSearchTable(SearchTable):
    cid = tables.LinkColumn(verbose_name='ID')
    provider = tables.LinkColumn('circuits:provider', args=[Accessor('provider.slug')])
    tenant = tables.LinkColumn('tenancy:tenant', args=[Accessor('tenant.slug')])

    class Meta(SearchTable.Meta):
        model = Circuit
        fields = ('cid', 'type', 'provider', 'tenant', 'description')
