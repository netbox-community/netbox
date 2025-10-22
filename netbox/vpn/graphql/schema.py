from typing import List

import strawberry
import strawberry_django
from strawberry_django.pagination import OffsetPaginated

from .types import *


@strawberry.type(name="Query")
class VPNQueryV1:
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


@strawberry.type(name="Query")
class VPNQuery:
    ike_policy: IKEPolicyType = strawberry_django.field()
    ike_policy_list: OffsetPaginated[IKEPolicyType] = strawberry_django.offset_paginated()

    ike_proposal: IKEProposalType = strawberry_django.field()
    ike_proposal_list: OffsetPaginated[IKEProposalType] = strawberry_django.offset_paginated()

    ipsec_policy: IPSecPolicyType = strawberry_django.field()
    ipsec_policy_list: OffsetPaginated[IPSecPolicyType] = strawberry_django.offset_paginated()

    ipsec_profile: IPSecProfileType = strawberry_django.field()
    ipsec_profile_list: OffsetPaginated[IPSecProfileType] = strawberry_django.offset_paginated()

    ipsec_proposal: IPSecProposalType = strawberry_django.field()
    ipsec_proposal_list: OffsetPaginated[IPSecProposalType] = strawberry_django.offset_paginated()

    l2vpn: L2VPNType = strawberry_django.field()
    l2vpn_list: OffsetPaginated[L2VPNType] = strawberry_django.offset_paginated()

    l2vpn_termination: L2VPNTerminationType = strawberry_django.field()
    l2vpn_termination_list: OffsetPaginated[L2VPNTerminationType] = strawberry_django.offset_paginated()

    tunnel: TunnelType = strawberry_django.field()
    tunnel_list: OffsetPaginated[TunnelType] = strawberry_django.offset_paginated()

    tunnel_group: TunnelGroupType = strawberry_django.field()
    tunnel_group_list: OffsetPaginated[TunnelGroupType] = strawberry_django.offset_paginated()

    tunnel_termination: TunnelTerminationType = strawberry_django.field()
    tunnel_termination_list: OffsetPaginated[TunnelTerminationType] = strawberry_django.offset_paginated()
