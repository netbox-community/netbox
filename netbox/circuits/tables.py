import django_tables2 as tables
from django_tables2.utils import Accessor

from tenancy.tables import TenantColumn
from utilities.tables import BaseTable, ButtonsColumn, ChoiceFieldColumn, TagColumn, ToggleColumn
from .models import *


#
# Providers
#

class ProviderTable(BaseTable):
    pk = ToggleColumn()
    name = tables.Column(
        linkify=True
    )
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
# Provider networks
#

class ProviderNetworkTable(BaseTable):
    pk = ToggleColumn()
    name = tables.Column(
        linkify=True
    )
    provider = tables.Column(
        linkify=True
    )
    tags = TagColumn(
        url_name='circuits:providernetwork_list'
    )

    class Meta(BaseTable.Meta):
        model = ProviderNetwork
        fields = ('pk', 'name', 'provider', 'description', 'tags')
        default_columns = ('pk', 'name', 'provider', 'description')


#
# Circuit types
#

class CircuitTypeTable(BaseTable):
    pk = ToggleColumn()
    name = tables.Column(
        linkify=True
    )
    circuit_count = tables.Column(
        verbose_name='Circuits'
    )
    actions = ButtonsColumn(CircuitType)

    class Meta(BaseTable.Meta):
        model = CircuitType
        fields = ('pk', 'name', 'circuit_count', 'description', 'slug', 'actions')
        default_columns = ('pk', 'name', 'circuit_count', 'description', 'slug', 'actions')


#
# Circuits
#

class CircuitTable(BaseTable):
    pk = ToggleColumn()
    cid = tables.Column(
        linkify=True,
        verbose_name='ID'
    )
    provider = tables.Column(
        linkify=True
    )
    status = ChoiceFieldColumn()
    tenant = TenantColumn()
    termination_a = tables.Column(
        linkify=True,
        verbose_name='Side A'
    )
    termination_z = tables.Column(
        linkify=True,
        verbose_name='Side Z'
    )
    tags = TagColumn(
        url_name='circuits:circuit_list'
    )

    class Meta(BaseTable.Meta):
        model = Circuit
        fields = (
            'pk', 'cid', 'provider', 'type', 'status', 'tenant', 'termination_a', 'termination_z', 'install_date',
            'commit_rate', 'description', 'tags',
        )
        default_columns = (
            'pk', 'cid', 'provider', 'type', 'status', 'tenant', 'termination_a', 'termination_z', 'description',
        )
