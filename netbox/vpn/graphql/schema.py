from typing import List

import strawberry
import strawberry_django

from vpn import models
from .types import *


@strawberry.type
class VPNQuery:
    @strawberry.field
    def ike_policy(self, id: int) -> IKEPolicyType:
        return models.IKEPolicy.objects.get(pk=id)
    ike_policy_list: List[IKEPolicyType] = strawberry_django.field()

    @strawberry.field
    def ike_proposal(self, id: int) -> IKEProposalType:
        return models.IKEProposal.objects.get(pk=id)
    ike_proposal_list: List[IKEProposalType] = strawberry_django.field()

    @strawberry.field
    def ipsec_policy(self, id: int) -> IPSecPolicyType:
        return models.IPSecPolicy.objects.get(pk=id)
    ipsec_policy_list: List[IPSecPolicyType] = strawberry_django.field()

    @strawberry.field
    def ipsec_profile(self, id: int) -> IPSecProfileType:
        return models.IPSecProfile.objects.get(pk=id)
    ipsec_profile_list: List[IPSecProfileType] = strawberry_django.field()

    @strawberry.field
    def ipsec_proposal(self, id: int) -> IPSecProposalType:
        return models.IPSecProposal.objects.get(pk=id)
    ipsec_proposal_list: List[IPSecProposalType] = strawberry_django.field()

    @strawberry.field
    def l2vpn(self, id: int) -> L2VPNType:
        return models.L2VPN.objects.get(pk=id)
    l2vpn_list: List[L2VPNType] = strawberry_django.field()

    @strawberry.field
    def l2vpn_termination(self, id: int) -> L2VPNTerminationType:
        return models.L2VPNTermination.objects.get(pk=id)
    l2vpn_termination_list: List[L2VPNTerminationType] = strawberry_django.field()

    @strawberry.field
    def tunnel(self, id: int) -> TunnelType:
        return models.Tunnel.objects.get(pk=id)
    tunnel_list: List[TunnelType] = strawberry_django.field()

    @strawberry.field
    def tunnel_group(self, id: int) -> TunnelGroupType:
        return models.TunnelGroup.objects.get(pk=id)
    tunnel_group_list: List[TunnelGroupType] = strawberry_django.field()

    @strawberry.field
    def tunnel_termination(self, id: int) -> TunnelTerminationType:
        return models.TunnelTermination.objects.get(pk=id)
    tunnel_termination_list: List[TunnelTerminationType] = strawberry_django.field()
