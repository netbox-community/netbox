import django_tables2 as tables
from circuits.models import *
from tenancy.tables import ContactsColumnMixin, TenancyColumnsMixin

from netbox.tables import NetBoxTable, columns

from .columns import CommitRateColumn

__all__ = (
    'CircuitTable',
    'CircuitTypeTable',
)


CIRCUITTERMINATION_LINK = """
{% if value.site %}
  <a href="{{ value.site.get_absolute_url }}">{{ value.site }}</a>
{% elif value.provider_network %}
  <a href="{{ value.provider_network.get_absolute_url }}">{{ value.provider_network }}</a>
{% endif %}
"""


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


class CircuitTable(TenancyColumnsMixin, ContactsColumnMixin, NetBoxTable):
    cid = tables.Column(
        linkify=True,
        verbose_name='Circuit ID'
    )
    provider = tables.Column(
        linkify=True
    )
    status = columns.ChoiceFieldColumn()
    termination_a = tables.TemplateColumn(
        template_code=CIRCUITTERMINATION_LINK,
        verbose_name='Side A'
    )
    termination_z = tables.TemplateColumn(
        template_code=CIRCUITTERMINATION_LINK,
        verbose_name='Side Z'
    )
    commit_rate = CommitRateColumn(
        verbose_name='Commit Rate'
    )
    comments = columns.MarkdownColumn()
    tags = columns.TagColumn(
        url_name='circuits:circuit_list'
    )

    class Meta(NetBoxTable.Meta):
        model = Circuit
        fields = (
            'pk', 'id', 'cid', 'provider', 'type', 'status', 'tenant', 'tenant_group', 'termination_a', 'termination_z',
            'install_date', 'termination_date', 'commit_rate', 'description', 'comments', 'contacts', 'tags', 'created',
            'last_updated',
        )
        default_columns = (
            'pk', 'cid', 'provider', 'type', 'status', 'tenant', 'termination_a', 'termination_z', 'description',
        )
