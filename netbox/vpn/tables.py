import django_tables2 as tables
from django.utils.translation import gettext_lazy as _
from django_tables2.utils import Accessor

from tenancy.tables import TenancyColumnsMixin
from netbox.tables import NetBoxTable, columns
from vpn.models import *

__all__ = (
    'IKEPolicyTable',
    'IKEProposalTable',
    'IPSecPolicyTable',
    'IPSecProposalTable',
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
            'pk', 'id', 'name', 'status', 'encapsulation', 'ipsec_profile', 'tenant', 'tenant_group', 'tunnel_id',
            'termination_count', 'description', 'comments', 'tags', 'created', 'last_updated',
        )
        default_columns = ('pk', 'name', 'status', 'encapsulation', 'tenant', 'terminations_count')


class TunnelTerminationTable(TenancyColumnsMixin, NetBoxTable):
    tunnel = tables.Column(
        verbose_name=_('Tunnel'),
        linkify=True
    )
    role = columns.ChoiceFieldColumn(
        verbose_name=_('Role')
    )
    interface_parent = tables.Column(
        accessor='interface__parent_object',
        linkify=True,
        orderable=False,
        verbose_name=_('Host')
    )
    interface = tables.Column(
        verbose_name=_('Interface'),
        linkify=True
    )
    ip_addresses = tables.ManyToManyColumn(
        accessor=tables.A('interface__ip_addresses'),
        orderable=False,
        linkify_item=True,
        verbose_name=_('IP Addresses')
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
            'pk', 'id', 'tunnel', 'role', 'interface_parent', 'interface', 'ip_addresses', 'outside_ip', 'tags',
            'created', 'last_updated',
        )
        default_columns = ('pk', 'id', 'tunnel', 'role', 'interface_parent', 'interface', 'ip_addresses', 'outside_ip')


class IKEProposalTable(NetBoxTable):
    name = tables.Column(
        verbose_name=_('Name'),
        linkify=True
    )
    authentication_method = tables.Column(
        verbose_name=_('Authentication Method')
    )
    encryption_algorithm = tables.Column(
        verbose_name=_('Encryption Algorithm')
    )
    authentication_algorithm = tables.Column(
        verbose_name=_('Authentication Algorithm')
    )
    group = tables.Column(
        verbose_name=_('Group')
    )
    sa_lifetime = tables.Column(
        verbose_name=_('SA Lifetime')
    )
    tags = columns.TagColumn(
        url_name='vpn:ikeproposal_list'
    )

    class Meta(NetBoxTable.Meta):
        model = IKEProposal
        fields = (
            'pk', 'id', 'name', 'authentication_method', 'encryption_algorithm', 'authentication_algorithm',
            'group', 'sa_lifetime', 'description', 'tags', 'created', 'last_updated',
        )
        default_columns = (
            'pk', 'name', 'authentication_method', 'encryption_algorithm', 'authentication_algorithm', 'group',
            'sa_lifetime', 'description',
        )


class IKEPolicyTable(NetBoxTable):
    name = tables.Column(
        verbose_name=_('Name'),
        linkify=True
    )
    version = tables.Column(
        verbose_name=_('Version')
    )
    mode = tables.Column(
        verbose_name=_('Mode')
    )
    proposals = tables.ManyToManyColumn(
        linkify_item=True,
        verbose_name=_('Proposals')
    )
    preshared_key = tables.Column(
        verbose_name=_('Pre-shared Key')
    )
    tags = columns.TagColumn(
        url_name='vpn:ikepolicy_list'
    )

    class Meta(NetBoxTable.Meta):
        model = IKEPolicy
        fields = (
            'pk', 'id', 'name', 'version', 'mode', 'proposals', 'preshared_key', 'description', 'tags', 'created',
            'last_updated',
        )
        default_columns = (
            'pk', 'name', 'version', 'mode', 'proposals', 'description',
        )


class IPSecProposalTable(NetBoxTable):
    name = tables.Column(
        verbose_name=_('Name'),
        linkify=True
    )
    encryption_algorithm = tables.Column(
        verbose_name=_('Encryption Algorithm')
    )
    authentication_algorithm = tables.Column(
        verbose_name=_('Authentication Algorithm')
    )
    sa_lifetime_seconds = tables.Column(
        verbose_name=_('SA Lifetime (Seconds)')
    )
    sa_lifetime_data = tables.Column(
        verbose_name=_('SA Lifetime (KB)')
    )
    tags = columns.TagColumn(
        url_name='vpn:ipsecproposal_list'
    )

    class Meta(NetBoxTable.Meta):
        model = IPSecProposal
        fields = (
            'pk', 'id', 'name', 'encryption_algorithm', 'authentication_algorithm', 'sa_lifetime_seconds',
            'sa_lifetime_data', 'description', 'tags', 'created', 'last_updated',
        )
        default_columns = (
            'pk', 'name', 'encryption_algorithm', 'authentication_algorithm', 'sa_lifetime_seconds',
            'sa_lifetime_data', 'description',
        )


class IPSecPolicyTable(NetBoxTable):
    name = tables.Column(
        verbose_name=_('Name'),
        linkify=True
    )
    proposals = tables.ManyToManyColumn(
        linkify_item=True,
        verbose_name=_('Proposals')
    )
    pfs_group = tables.Column(
        verbose_name=_('PFS Group')
    )
    tags = columns.TagColumn(
        url_name='vpn:ipsecpolicy_list'
    )

    class Meta(NetBoxTable.Meta):
        model = IPSecPolicy
        fields = (
            'pk', 'id', 'name', 'proposals', 'pfs_group', 'description', 'tags', 'created', 'last_updated',
        )
        default_columns = (
            'pk', 'name', 'proposals', 'pfs_group', 'description',
        )


class IPSecProfileTable(NetBoxTable):
    name = tables.Column(
        verbose_name=_('Name'),
        linkify=True
    )
    mode = tables.Column(
        verbose_name=_('Mode')
    )
    ike_policy = tables.Column(
        linkify=True,
        verbose_name=_('IKE Policy')
    )
    ipsec_policy = tables.Column(
        linkify=True,
        verbose_name=_('IPSec Policy')
    )
    comments = columns.MarkdownColumn(
        verbose_name=_('Comments'),
    )
    tags = columns.TagColumn(
        url_name='vpn:ipsecprofile_list'
    )

    class Meta(NetBoxTable.Meta):
        model = IPSecProfile
        fields = (
            'pk', 'id', 'name', 'mode', 'ike_policy', 'ipsec_policy', 'description', 'comments', 'tags', 'created',
            'last_updated',
        )
        default_columns = ('pk', 'name', 'mode', 'ike_policy', 'ipsec_policy', 'description')
