import django_tables2 as tables
from django_tables2.utils import Accessor

from netbox.tables import NetBoxTable, columns
from tenancy.tables import TenantColumn
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

class ProviderTable(NetBoxTable):
    name = tables.Column(
        linkify=True
    )
    circuit_count = tables.Column(
        accessor=Accessor('count_circuits'),
        verbose_name='Circuits'
    )
    comments = columns.MarkdownColumn()
    tags = columns.TagColumn(
        url_name='circuits:provider_list'
    )

    class Meta(NetBoxTable.Meta):
        model = Provider
        fields = (
            'pk', 'id', 'name', 'asn', 'account', 'portal_url', 'noc_contact', 'admin_contact', 'circuit_count',
            'comments', 'tags', 'created', 'last_updated',
        )
        default_columns = ('pk', 'name', 'asn', 'account', 'circuit_count')


#
# Provider networks
#

class ProviderNetworkTable(NetBoxTable):
    name = tables.Column(
        linkify=True
    )
    provider = tables.Column(
        linkify=True
    )
    comments = columns.MarkdownColumn()
    tags = columns.TagColumn(
        url_name='circuits:providernetwork_list'
    )

    class Meta(NetBoxTable.Meta):
        model = ProviderNetwork
        fields = (
            'pk', 'id', 'name', 'provider', 'service_id', 'description', 'comments', 'created', 'last_updated', 'tags',
        )
        default_columns = ('pk', 'name', 'provider', 'service_id', 'description')


#
# Circuit types
#

class CircuitTypeTable(NetBoxTable):
    name = tables.Column(
        linkify=True
    )
    tags = columns.TagColumn(
        url_name='circuits:circuittype_list'
    )
    circuit_count = tables.Column(
        verbose_name='Circuits'
    )

    class Meta(NetBoxTable.Meta):
        model = CircuitType
        fields = (
            'pk', 'id', 'name', 'circuit_count', 'description', 'slug', 'tags', 'created', 'last_updated', 'actions',
        )
        default_columns = ('pk', 'name', 'circuit_count', 'description', 'slug')


#
# Circuits
#

class CircuitTable(NetBoxTable):
    cid = tables.Column(
        linkify=True,
        verbose_name='Circuit ID'
    )
    provider = tables.Column(
        linkify=True
    )
    status = columns.ChoiceFieldColumn()
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
    comments = columns.MarkdownColumn()
    tags = columns.TagColumn(
        url_name='circuits:circuit_list'
    )

    class Meta(NetBoxTable.Meta):
        model = Circuit
        fields = (
            'pk', 'id', 'cid', 'provider', 'type', 'status', 'tenant', 'termination_a', 'termination_z', 'install_date',
            'commit_rate', 'description', 'comments', 'tags', 'created', 'last_updated',
        )
        default_columns = (
            'pk', 'cid', 'provider', 'type', 'status', 'tenant', 'termination_a', 'termination_z', 'description',
        )
