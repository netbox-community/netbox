import strawberry
import strawberry_django

from .types import *


@strawberry.type(name="Query")
class VPNQuery:
    ike_policy: IKEPolicyType = strawberry_django.field()
    ike_policy_list: list[IKEPolicyType] = strawberry_django.field()

    ike_proposal: IKEProposalType = strawberry_django.field()
    ike_proposal_list: list[IKEProposalType] = strawberry_django.field()

    ipsec_policy: IPSecPolicyType = strawberry_django.field()
    ipsec_policy_list: list[IPSecPolicyType] = strawberry_django.field()

    ipsec_profile: IPSecProfileType = strawberry_django.field()
    ipsec_profile_list: list[IPSecProfileType] = strawberry_django.field()

    ipsec_proposal: IPSecProposalType = strawberry_django.field()
    ipsec_proposal_list: list[IPSecProposalType] = strawberry_django.field()

    l2vpn: L2VPNType = strawberry_django.field()
    l2vpn_list: list[L2VPNType] = strawberry_django.field()

    l2vpn_termination: L2VPNTerminationType = strawberry_django.field()
    l2vpn_termination_list: list[L2VPNTerminationType] = strawberry_django.field()

    tunnel: TunnelType = strawberry_django.field()
    tunnel_list: list[TunnelType] = strawberry_django.field()

    tunnel_group: TunnelGroupType = strawberry_django.field()
    tunnel_group_list: list[TunnelGroupType] = strawberry_django.field()

    tunnel_termination: TunnelTerminationType = strawberry_django.field()
    tunnel_termination_list: list[TunnelTerminationType] = strawberry_django.field()
