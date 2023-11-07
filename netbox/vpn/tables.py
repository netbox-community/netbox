import django_tables2 as tables
from django.utils.translation import gettext_lazy as _
from django_tables2.utils import Accessor

from tenancy.tables import TenancyColumnsMixin
from netbox.tables import NetBoxTable, columns
from vpn.models import *

__all__ = (
    'IPSecProfileTable',
    'TunnelTable',
    'TunnelTerminationTable',
)


class TunnelTable(TenancyColumnsMixin, NetBoxTable):
    name = tables.Column(
        verbose_name=_('Name'),
        linkify=True
    )
    status = columns.ChoiceFieldColumn(
        verbose_name=_('Status')
    )
    encapsulation = columns.ChoiceFieldColumn(
        verbose_name=_('Encapsulation')
    )
    ipsec_profile = tables.Column(
        verbose_name=_('IPSec profile'),
        linkify=True
    )
    terminations_count = columns.LinkedCountColumn(
        accessor=Accessor('count_terminations'),
        viewname='vpn:tunneltermination_list',
        url_params={'tunnel_id': 'pk'},
        verbose_name=_('Terminations')
    )
    comments = columns.MarkdownColumn(
        verbose_name=_('Comments'),
    )
    tags = columns.TagColumn(
        url_name='vpn:tunnel_list'
    )

    class Meta(NetBoxTable.Meta):
        model = Tunnel
        fields = (
            'pk', 'id', 'name', 'status', 'encapsulation', 'ipsec_profile', 'tenant', 'tenant_group', 'preshared_key',
            'tunnel_id', 'termination_count', 'description', 'comments', 'tags', 'created', 'last_updated',
        )
        default_columns = ('pk', 'name', 'status', 'encapsulation', 'tenant', 'termination_count')


class TunnelTerminationTable(TenancyColumnsMixin, NetBoxTable):
    tunnel = tables.Column(
        verbose_name=_('Tunnel'),
        linkify=True
    )
    role = columns.ChoiceFieldColumn(
        verbose_name=_('Role')
    )
    interface = tables.Column(
        verbose_name=_('Interface'),
        linkify=True
    )
    outside_ip = tables.Column(
        verbose_name=_('Outside IP'),
        linkify=True
    )
    tags = columns.TagColumn(
        url_name='vpn:tunneltermination_list'
    )

    class Meta(NetBoxTable.Meta):
        model = TunnelTermination
        fields = (
            'pk', 'id', 'tunnel', 'role', 'interface', 'outside_ip', 'tags', 'created', 'last_updated',
        )
        default_columns = ('pk', 'tunnel', 'role', 'interface', 'outside_ip')


class IPSecProfileTable(TenancyColumnsMixin, NetBoxTable):
    name = tables.Column(
        verbose_name=_('Name'),
        linkify=True
    )
    protocol = columns.ChoiceFieldColumn(
        verbose_name=_('Protocol')
    )
    ike_version = columns.ChoiceFieldColumn(
        verbose_name=_('IKE Version')
    )
    phase1_encryption = columns.ChoiceFieldColumn(
        verbose_name=_('Phase 1 Encryption')
    )
    phase1_authentication = columns.ChoiceFieldColumn(
        verbose_name=_('Phase 1 Authentication')
    )
    phase1_group = columns.ChoiceFieldColumn(
        verbose_name=_('Phase 1 Group')
    )
    phase2_encryption = columns.ChoiceFieldColumn(
        verbose_name=_('Phase 2 Encryption')
    )
    phase2_authentication = columns.ChoiceFieldColumn(
        verbose_name=_('Phase 2 Authentication')
    )
    phase2_group = columns.ChoiceFieldColumn(
        verbose_name=_('Phase 2 Group')
    )
    comments = columns.MarkdownColumn(
        verbose_name=_('Comments'),
    )
    tags = columns.TagColumn(
        url_name='vpn:tunnel_list'
    )

    class Meta(NetBoxTable.Meta):
        model = IPSecProfile
        fields = (
            'pk', 'id', 'name', 'protocol', 'ike_version', 'phase1_encryption', 'phase1_authentication', 'phase1_group',
            'phase1_sa_lifetime', 'phase2_encryption', 'phase2_authentication', 'phase2_group', 'phase1_sa_lifetime',
            'description', 'comments', 'tags', 'created', 'last_updated',
        )
        default_columns = ('pk', 'name', 'protocol', 'ike_version', 'description')
