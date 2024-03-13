import strawberry
import strawberry_django
from vpn import filtersets, models

from netbox.graphql.filter_mixins import autotype_decorator, BaseFilterMixin

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
@autotype_decorator(filtersets.TunnelGroupFilterSet)
class TunnelGroupFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.TunnelTermination, lookups=True)
@autotype_decorator(filtersets.TunnelTerminationFilterSet)
class TunnelTerminationFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.Tunnel, lookups=True)
@autotype_decorator(filtersets.TunnelFilterSet)
class TunnelFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.IKEProposal, lookups=True)
@autotype_decorator(filtersets.IKEProposalFilterSet)
class IKEProposalFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.IKEPolicy, lookups=True)
@autotype_decorator(filtersets.IKEPolicyFilterSet)
class IKEPolicyFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.IPSecProposal, lookups=True)
@autotype_decorator(filtersets.IPSecProposalFilterSet)
class IPSecProposalFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.IPSecPolicy, lookups=True)
@autotype_decorator(filtersets.IPSecPolicyFilterSet)
class IPSecPolicyFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.IPSecProfile, lookups=True)
@autotype_decorator(filtersets.IPSecProfileFilterSet)
class IPSecProfileFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.L2VPN, lookups=True)
@autotype_decorator(filtersets.L2VPNFilterSet)
class L2VPNFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.L2VPNTermination, lookups=True)
@autotype_decorator(filtersets.L2VPNTerminationFilterSet)
class L2VPNTerminationFilter(BaseFilterMixin):
    pass
