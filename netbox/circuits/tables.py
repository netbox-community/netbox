import django_tables2 as tables
from django_tables2.utils import Accessor

from tenancy.tables import COL_TENANT
from utilities.tables import BaseTable, ButtonsColumn, ChoiceFieldColumn, TagColumn, ToggleColumn
from .models import Circuit, CircuitType, Provider


#
# Providers
#

class ProviderTable(BaseTable):
    pk = ToggleColumn()
    name = tables.LinkColumn()
    circuit_count = tables.Column(
        accessor=Accessor('count_circuits'),
        verbose_name='Circuits'
    )
    tags = TagColumn(
        url_name='circuits:provider_list'
    )

    class Meta(BaseTable.Meta):
        model = Provider
        fields = (
            'pk', 'name', 'asn', 'account', 'portal_url', 'noc_contact', 'admin_contact', 'circuit_count', 'tags',
        )
        default_columns = ('pk', 'name', 'asn', 'account', 'circuit_count')


#
# Circuit types
#

class CircuitTypeTable(BaseTable):
    pk = ToggleColumn()
    name = tables.LinkColumn()
    circuit_count = tables.Column(
        verbose_name='Circuits'
    )
    actions = ButtonsColumn(CircuitType, pk_field='slug')

    class Meta(BaseTable.Meta):
        model = CircuitType
        fields = ('pk', 'name', 'circuit_count', 'description', 'slug', 'actions')
        default_columns = ('pk', 'name', 'circuit_count', 'description', 'slug', 'actions')


#
# Circuits
#

class CircuitTable(BaseTable):
    pk = ToggleColumn()
    cid = tables.LinkColumn(
        verbose_name='ID'
    )
    provider = tables.LinkColumn(
        viewname='circuits:provider',
        args=[Accessor('provider__slug')]
    )
    status = ChoiceFieldColumn()
    tenant = tables.TemplateColumn(
        template_code=COL_TENANT
    )
    a_side = tables.Column(
        verbose_name='A Side'
    )
    z_side = tables.Column(
        verbose_name='Z Side'
    )
    tags = TagColumn(
        url_name='circuits:circuit_list'
    )

    class Meta(BaseTable.Meta):
        model = Circuit
        fields = (
            'pk', 'cid', 'provider', 'type', 'status', 'tenant', 'a_side', 'z_side', 'install_date', 'commit_rate',
            'description', 'tags',
        )
        default_columns = ('pk', 'cid', 'provider', 'type', 'status', 'tenant', 'a_side', 'z_side', 'description')
