from netbox.search import SearchIndex, register_search
from . import models


@register_search
class TunnelIndex(SearchIndex):
    model = models.Tunnel
    fields = (
        ('name', 100),
        ('tunnel_id', 300),
        ('description', 500),
        ('comments', 5000),
    )
    display_attrs = ('group', 'status', 'encapsulation', 'tenant', 'tunnel_id', 'description')


@register_search
class IKEProposalIndex(SearchIndex):
    model = models.IKEProposal
    fields = (
        ('name', 100),
        ('description', 500),
        ('comments', 5000),
    )
    display_attrs = ('description',)


@register_search
class IKEPolicyIndex(SearchIndex):
    model = models.IKEPolicy
    fields = (
        ('name', 100),
        ('description', 500),
        ('comments', 5000),
    )
    display_attrs = ('description',)


@register_search
class IPSecProposalIndex(SearchIndex):
    model = models.IPSecProposal
    fields = (
        ('name', 100),
        ('description', 500),
        ('comments', 5000),
    )
    display_attrs = ('description',)


@register_search
class IPSecPolicyIndex(SearchIndex):
    model = models.IPSecPolicy
    fields = (
        ('name', 100),
        ('description', 500),
        ('comments', 5000),
    )
    display_attrs = ('description',)


@register_search
class IPSecProfileIndex(SearchIndex):
    model = models.IPSecProfile
    fields = (
        ('name', 100),
        ('description', 500),
        ('comments', 5000),
    )
    display_attrs = ('description',)


@register_search
class L2VPNIndex(SearchIndex):
    model = models.L2VPN
    fields = (
        ('name', 100),
        ('slug', 110),
        ('identifier', 200),
        ('description', 500),
        ('comments', 5000),
    )
    display_attrs = ('type', 'identifier', 'tenant', 'description')
