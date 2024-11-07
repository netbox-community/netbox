import django_tables2 as tables
from django.utils.translation import gettext_lazy as _

from circuits.models import *
from netbox.tables import NetBoxTable, columns
from tenancy.tables import ContactsColumnMixin, TenancyColumnsMixin

__all__ = (
    'VirtualCircuitTable',
    'VirtualCircuitTerminationTable',
)


class VirtualCircuitTable(TenancyColumnsMixin, ContactsColumnMixin, NetBoxTable):
    cid = tables.Column(
        linkify=True,
        verbose_name=_('Circuit ID')
    )
    provider = tables.Column(
        accessor=tables.A('provider_network__provider'),
        verbose_name=_('Provider'),
        linkify=True
    )
    provider_network = tables.Column(
        linkify=True,
        verbose_name=_('Provider network')
    )
    provider_account = tables.Column(
        linkify=True,
        verbose_name=_('Account')
    )
    status = columns.ChoiceFieldColumn()
    termination_count = columns.LinkedCountColumn(
        viewname='circuits:virtualcircuittermination_list',
        url_params={'virtual_circuit_id': 'pk'},
        verbose_name=_('Terminations')
    )
    comments = columns.MarkdownColumn(
        verbose_name=_('Comments')
    )
    tags = columns.TagColumn(
        url_name='circuits:virtualcircuit_list'
    )

    class Meta(NetBoxTable.Meta):
        model = VirtualCircuit
        fields = (
            'pk', 'id', 'cid', 'provider', 'provider_account', 'provider_network', 'status', 'tenant', 'tenant_group',
            'description', 'comments', 'tags', 'created', 'last_updated',
        )
        default_columns = (
            'pk', 'cid', 'provider', 'provider_account', 'provider_network', 'status', 'tenant', 'termination_count',
            'description',
        )


class VirtualCircuitTerminationTable(NetBoxTable):
    virtual_circuit = tables.Column(
        verbose_name=_('Virtual circuit'),
        linkify=True
    )
    provider = tables.Column(
        accessor=tables.A('virtual_circuit__provider_network__provider'),
        verbose_name=_('Provider'),
        linkify=True
    )
    provider_network = tables.Column(
        accessor=tables.A('virtual_circuit__provider_network'),
        linkify=True,
        verbose_name=_('Provider network')
    )
    provider_account = tables.Column(
        linkify=True,
        verbose_name=_('Account')
    )
    role = columns.ChoiceFieldColumn()
    device = tables.Column(
        accessor=tables.A('interface__device'),
        linkify=True,
        verbose_name=_('Device')
    )
    interface = tables.Column(
        verbose_name=_('Interface'),
        linkify=True
    )

    class Meta(NetBoxTable.Meta):
        model = VirtualCircuitTermination
        fields = (
            'pk', 'id', 'virtual_circuit', 'provider', 'provider_network', 'provider_account', 'role', 'interfaces',
            'description', 'created', 'last_updated', 'actions',
        )
        default_columns = (
            'pk', 'id', 'virtual_circuit', 'role', 'device', 'interface', 'description',
        )
