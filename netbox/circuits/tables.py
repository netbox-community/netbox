from __future__ import unicode_literals

import django_tables2 as tables
from django.utils.safestring import mark_safe
from django_tables2.utils import Accessor

from utilities.tables import BaseTable, ToggleColumn
from .models import Circuit, CircuitType, Provider

CIRCUITTYPE_ACTIONS = """
{% if perms.circuit.change_circuittype %}
    <a href="{% url 'circuits:circuittype_edit' slug=record.slug %}" class="btn btn-xs btn-warning"><i class="glyphicon glyphicon-pencil" aria-hidden="true"></i></a>
{% endif %}
"""


class CircuitTerminationColumn(tables.Column):

    def render(self, value):
        if value.interface:
            return mark_safe('<a href="{}" title="{}">{}</a>'.format(
                value.interface.device.get_absolute_url(),
                value.site,
                value.interface.device
            ))
        return mark_safe('<a href="{}">{}</a>'.format(
            value.site.get_absolute_url(),
            value.site
        ))


#
# Providers
#

class ProviderTable(BaseTable):
    pk = ToggleColumn()
    name = tables.LinkColumn()

    class Meta(BaseTable.Meta):
        model = Provider
        fields = ('pk', 'name', 'asn', 'account',)


class ProviderDetailTable(ProviderTable):
    circuit_count = tables.Column(accessor=Accessor('count_circuits'), verbose_name='Circuits')

    class Meta(ProviderTable.Meta):
        model = Provider
        fields = ('pk', 'name', 'asn', 'account', 'circuit_count')


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
    termination_a = CircuitTerminationColumn(orderable=False, verbose_name='A Side')
    termination_z = CircuitTerminationColumn(orderable=False, verbose_name='Z Side')

    class Meta(BaseTable.Meta):
        model = Circuit
        fields = ('pk', 'cid', 'type', 'provider', 'tenant', 'termination_a', 'termination_z', 'description')
