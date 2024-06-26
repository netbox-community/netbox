from django.utils.translation import gettext_lazy as _
import django_tables2 as tables

from circuits.models import *
from tenancy.tables import ContactsColumnMixin, TenancyColumnsMixin

from netbox.tables import NetBoxTable, columns

from .columns import CommitRateColumn

__all__ = (
    'CircuitTable',
    'CircuitTerminationTable',
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
        linkify=True,
        verbose_name=_('Name'),
    )
    color = columns.ColorColumn()
    tags = columns.TagColumn(
        url_name='circuits:circuittype_list'
    )
    circuit_count = columns.LinkedCountColumn(
        viewname='circuits:circuit_list',
        url_params={'type_id': 'pk'},
        verbose_name=_('Circuits')
    )

    class Meta(NetBoxTable.Meta):
        model = CircuitType
        fields = (
            'pk', 'id', 'name', 'circuit_count', 'color', 'description', 'slug', 'tags', 'created', 'last_updated', 'actions',
        )
        default_columns = ('pk', 'name', 'circuit_count', 'description', 'slug')


class CircuitTable(TenancyColumnsMixin, ContactsColumnMixin, NetBoxTable):
    cid = tables.Column(
        linkify=True,
        verbose_name=_('Circuit ID')
    )
    provider = tables.Column(
        verbose_name=_('Provider'),
        linkify=True
    )
    provider_account = tables.Column(
        linkify=True,
        verbose_name=_('Account')
    )
    status = columns.ChoiceFieldColumn()
    termination_a = tables.TemplateColumn(
        template_code=CIRCUITTERMINATION_LINK,
        orderable=False,
        verbose_name=_('Side A')
    )
    termination_z = tables.TemplateColumn(
        template_code=CIRCUITTERMINATION_LINK,
        orderable=False,
        verbose_name=_('Side Z')
    )
    commit_rate = CommitRateColumn(
        verbose_name=_('Commit Rate')
    )
    comments = columns.MarkdownColumn(
        verbose_name=_('Comments'),
    )
    tags = columns.TagColumn(
        url_name='circuits:circuit_list'
    )

    class Meta(NetBoxTable.Meta):
        model = Circuit
        fields = (
            'pk', 'id', 'cid', 'provider', 'provider_account', 'type', 'status', 'tenant', 'tenant_group',
            'termination_a', 'termination_z', 'install_date', 'termination_date', 'commit_rate', 'description',
            'comments', 'contacts', 'tags', 'created', 'last_updated',
        )
        default_columns = (
            'pk', 'cid', 'provider', 'type', 'status', 'tenant', 'termination_a', 'termination_z', 'description',
        )


class CircuitTerminationTable(NetBoxTable):
    circuit = tables.Column(
        verbose_name=_('Circuit'),
        linkify=True
    )
    provider = tables.Column(
        verbose_name=_('Provider'),
        linkify=True,
        accessor='circuit.provider'
    )
    site = tables.Column(
        verbose_name=_('Site'),
        linkify=True
    )
    provider_network = tables.Column(
        verbose_name=_('Provider Network'),
        linkify=True
    )

    class Meta(NetBoxTable.Meta):
        model = CircuitTermination
        fields = (
            'pk', 'id', 'circuit', 'provider', 'term_side', 'site', 'provider_network', 'port_speed', 'upstream_speed',
            'xconnect_id', 'pp_info', 'description', 'created', 'last_updated', 'actions',
        )
        default_columns = ('pk', 'id', 'circuit', 'provider', 'term_side', 'description')
