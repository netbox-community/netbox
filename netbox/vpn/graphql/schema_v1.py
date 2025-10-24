from typing import List

import strawberry
import strawberry_django

from .types_v1 import *


@strawberry.type(name="Query")
class VPNQueryV1:
    ike_policy: IKEPolicyTypeV1 = strawberry_django.field()
    ike_policy_list: List[IKEPolicyTypeV1] = strawberry_django.field()

    ike_proposal: IKEProposalTypeV1 = strawberry_django.field()
    ike_proposal_list: List[IKEProposalTypeV1] = strawberry_django.field()

    ipsec_policy: IPSecPolicyTypeV1 = strawberry_django.field()
    ipsec_policy_list: List[IPSecPolicyTypeV1] = strawberry_django.field()

    ipsec_profile: IPSecProfileTypeV1 = strawberry_django.field()
    ipsec_profile_list: List[IPSecProfileTypeV1] = strawberry_django.field()

    ipsec_proposal: IPSecProposalTypeV1 = strawberry_django.field()
    ipsec_proposal_list: List[IPSecProposalTypeV1] = strawberry_django.field()

    l2vpn: L2VPNTypeV1 = strawberry_django.field()
    l2vpn_list: List[L2VPNTypeV1] = strawberry_django.field()

    l2vpn_termination: L2VPNTerminationTypeV1 = strawberry_django.field()
    l2vpn_termination_list: List[L2VPNTerminationTypeV1] = strawberry_django.field()

    tunnel: TunnelTypeV1 = strawberry_django.field()
    tunnel_list: List[TunnelTypeV1] = strawberry_django.field()

    tunnel_group: TunnelGroupTypeV1 = strawberry_django.field()
    tunnel_group_list: List[TunnelGroupTypeV1] = strawberry_django.field()

    tunnel_termination: TunnelTerminationTypeV1 = strawberry_django.field()
    tunnel_termination_list: List[TunnelTerminationTypeV1] = strawberry_django.field()
