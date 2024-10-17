from typing import List

import strawberry
import strawberry_django

from .types import *


@strawberry.type(name="Query")
class VPNQuery:
    ike_policy: IKEPolicyType = strawberry_django.field()
    ike_policy_list: List[IKEPolicyType] = strawberry_django.field()

    ike_proposal: IKEProposalType = strawberry_django.field()
    ike_proposal_list: List[IKEProposalType] = strawberry_django.field()

    ipsec_policy: IPSecPolicyType = strawberry_django.field()
    ipsec_policy_list: List[IPSecPolicyType] = strawberry_django.field()

    ipsec_profile: IPSecProfileType = strawberry_django.field()
    ipsec_profile_list: List[IPSecProfileType] = strawberry_django.field()

    ipsec_proposal: IPSecProposalType = strawberry_django.field()
    ipsec_proposal_list: List[IPSecProposalType] = strawberry_django.field()

    l2vpn: L2VPNType = strawberry_django.field()
    l2vpn_list: List[L2VPNType] = strawberry_django.field()

    l2vpn_termination: L2VPNTerminationType = strawberry_django.field()
    l2vpn_termination_list: List[L2VPNTerminationType] = strawberry_django.field()

    tunnel: TunnelType = strawberry_django.field()
    tunnel_list: List[TunnelType] = strawberry_django.field()

    tunnel_group: TunnelGroupType = strawberry_django.field()
    tunnel_group_list: List[TunnelGroupType] = strawberry_django.field()

    tunnel_termination: TunnelTerminationType = strawberry_django.field()
    tunnel_termination_list: List[TunnelTerminationType] = strawberry_django.field()
