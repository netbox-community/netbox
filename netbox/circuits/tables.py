import django_tables2 as tables
from django_tables2.utils import Accessor

from tenancy.tables import TenantColumn
from utilities.tables import BaseTable, ButtonsColumn, ChoiceFieldColumn, MarkdownColumn, TagColumn, ToggleColumn
from .models import *


__all__ = (
    'CircuitTable',
    'CircuitTypeTable',
    'ProviderTable',
    'ProviderNetworkTable',
)


CIRCUITTERMINATION_LINK = """
{% if value.site %}
  <a href="{{ value.site.get_absolute_url }}">{{ value.site }}</a>
{% elif value.provider_network %}
  <a href="{{ value.provider_network.get_absolute_url }}">{{ value.provider_network }}</a>
{% endif %}
"""

#
# Table columns
#


class CommitRateColumn(tables.TemplateColumn):
    """
    Humanize the commit rate in the column view
    """

    template_code = """
        {% load helpers %}
        {{ record.commit_rate|humanize_speed }}
        """

    def __init__(self, *args, **kwargs):
        super().__init__(template_code=self.template_code, *args, **kwargs)

    def value(self, value):
        return str(value) if value else None

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
    comments = MarkdownColumn()
    tags = TagColumn(
        url_name='circuits:provider_list'
    )

    class Meta(BaseTable.Meta):
        model = Provider
        fields = (
            'pk', 'id', 'name', 'asn', 'account', 'portal_url', 'noc_contact', 'admin_contact', 'circuit_count',
            'comments', 'tags', 'created', 'last_updated',
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
    comments = MarkdownColumn()
    tags = TagColumn(
        url_name='circuits:providernetwork_list'
    )

    class Meta(BaseTable.Meta):
        model = ProviderNetwork
        fields = ('pk', 'id', 'name', 'provider', 'description', 'comments', 'tags', 'created', 'last_updated',)
        default_columns = ('pk', 'name', 'provider', 'description')


#
# Circuit types
#

class CircuitTypeTable(BaseTable):
    pk = ToggleColumn()
    name = tables.Column(
        linkify=True
    )
    tags = TagColumn(
        url_name='circuits:circuittype_list'
    )
    circuit_count = tables.Column(
        verbose_name='Circuits'
    )
    actions = ButtonsColumn(CircuitType)

    class Meta(BaseTable.Meta):
        model = CircuitType
        fields = ('pk', 'id', 'name', 'circuit_count', 'description', 'slug', 'tags', 'actions', 'created', 'last_updated',)
        default_columns = ('pk', 'name', 'circuit_count', 'description', 'slug', 'actions')


#
# Circuits
#

class CircuitTable(BaseTable):
    pk = ToggleColumn()
    cid = tables.Column(
        linkify=True,
        verbose_name='Circuit ID'
    )
    provider = tables.Column(
        linkify=True
    )
    status = ChoiceFieldColumn()
    tenant = TenantColumn()
    termination_a = tables.TemplateColumn(
        template_code=CIRCUITTERMINATION_LINK,
        verbose_name='Side A'
    )
    termination_z = tables.TemplateColumn(
        template_code=CIRCUITTERMINATION_LINK,
        verbose_name='Side Z'
    )
    commit_rate = CommitRateColumn()
    comments = MarkdownColumn()
    tags = TagColumn(
        url_name='circuits:circuit_list'
    )

    class Meta(BaseTable.Meta):
        model = Circuit
        fields = (
            'pk', 'id', 'cid', 'provider', 'type', 'status', 'tenant', 'termination_a', 'termination_z', 'install_date',
            'commit_rate', 'description', 'comments', 'tags', 'created', 'last_updated',
        )
        default_columns = (
            'pk', 'cid', 'provider', 'type', 'status', 'tenant', 'termination_a', 'termination_z', 'description',
        )
