import strawberry
import strawberry_django
from strawberry import auto
from vpn import models, filtersets
from netbox.graphql import filters


__all__ = (
    'TunnelGroupFilter',
    'TunnelTerminationFilter',
    'TunnelFilter',
    'IKEProposalFilter',
    'IKEPolicyFilter',
    'IPSecProposalFilter',
    'IPSecPolicyFilter',
    'IPSecProfileFilter',
    'L2VPNFilter',
    'L2VPNTerminationFilter',
)


@strawberry_django.filter(models.TunnelGroup, lookups=True)
class TunnelGroupFilter(filtersets.TunnelGroupFilterSet):
    id: auto


@strawberry_django.filter(models.TunnelTermination, lookups=True)
class TunnelTerminationFilter(filtersets.TunnelTerminationFilterSet):
    id: auto


@strawberry_django.filter(models.Tunnel, lookups=True)
class TunnelFilter(filtersets.TunnelFilterSet):
    id: auto


@strawberry_django.filter(models.IKEProposal, lookups=True)
class IKEProposalFilter(filtersets.IKEProposalFilterSet):
    id: auto


@strawberry_django.filter(models.IKEPolicy, lookups=True)
class IKEPolicyFilter(filtersets.IKEPolicyFilterSet):
    id: auto


@strawberry_django.filter(models.IPSecProposal, lookups=True)
class IPSecProposalFilter(filtersets.IPSecProposalFilterSet):
    id: auto


@strawberry_django.filter(models.IPSecPolicy, lookups=True)
class IPSecPolicyFilter(filtersets.IPSecPolicyFilterSet):
    id: auto


@strawberry_django.filter(models.IPSecProfile, lookups=True)
class IPSecProfileFilter(filtersets.IPSecProfileFilterSet):
    id: auto


@strawberry_django.filter(models.L2VPN, lookups=True)
class L2VPNFilter(filtersets.L2VPNFilterSet):
    id: auto


@strawberry_django.filter(models.L2VPNTermination, lookups=True)
class L2VPNTerminationFilter(filtersets.L2VPNTerminationFilterSet):
    id: auto
