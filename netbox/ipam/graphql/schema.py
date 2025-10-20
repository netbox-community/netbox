from typing import List

import strawberry
import strawberry_django
from strawberry_django.pagination import OffsetPaginated

from .types import *


@strawberry.type(name="Query")
class IPAMQueryOld:
    asn: ASNType = strawberry_django.field()
    asn_list: List[ASNType] = strawberry_django.field()

    asn_range: ASNRangeType = strawberry_django.field()
    asn_range_list: List[ASNRangeType] = strawberry_django.field()

    aggregate: AggregateType = strawberry_django.field()
    aggregate_list: List[AggregateType] = strawberry_django.field()

    ip_address: IPAddressType = strawberry_django.field()
    ip_address_list: List[IPAddressType] = strawberry_django.field()

    ip_range: IPRangeType = strawberry_django.field()
    ip_range_list: List[IPRangeType] = strawberry_django.field()

    prefix: PrefixType = strawberry_django.field()
    prefix_list: List[PrefixType] = strawberry_django.field()

    rir: RIRType = strawberry_django.field()
    rir_list: List[RIRType] = strawberry_django.field()

    role: RoleType = strawberry_django.field()
    role_list: List[RoleType] = strawberry_django.field()

    route_target: RouteTargetType = strawberry_django.field()
    route_target_list: List[RouteTargetType] = strawberry_django.field()

    service: ServiceType = strawberry_django.field()
    service_list: List[ServiceType] = strawberry_django.field()

    service_template: ServiceTemplateType = strawberry_django.field()
    service_template_list: List[ServiceTemplateType] = strawberry_django.field()

    fhrp_group: FHRPGroupType = strawberry_django.field()
    fhrp_group_list: List[FHRPGroupType] = strawberry_django.field()

    fhrp_group_assignment: FHRPGroupAssignmentType = strawberry_django.field()
    fhrp_group_assignment_list: List[FHRPGroupAssignmentType] = strawberry_django.field()

    vlan: VLANType = strawberry_django.field()
    vlan_list: List[VLANType] = strawberry_django.field()

    vlan_group: VLANGroupType = strawberry_django.field()
    vlan_group_list: List[VLANGroupType] = strawberry_django.field()

    vlan_translation_policy: VLANTranslationPolicyType = strawberry_django.field()
    vlan_translation_policy_list: List[VLANTranslationPolicyType] = strawberry_django.field()

    vlan_translation_rule: VLANTranslationRuleType = strawberry_django.field()
    vlan_translation_rule_list: List[VLANTranslationRuleType] = strawberry_django.field()

    vrf: VRFType = strawberry_django.field()
    vrf_list: List[VRFType] = strawberry_django.field()


@strawberry.type(name="Query")
class IPAMQuery:
    asn: ASNType = strawberry_django.field()
    asn_list: OffsetPaginated[ASNType] = strawberry_django.offset_paginated()

    asn_range: ASNRangeType = strawberry_django.field()
    asn_range_list: OffsetPaginated[ASNRangeType] = strawberry_django.offset_paginated()

    aggregate: AggregateType = strawberry_django.field()
    aggregate_list: OffsetPaginated[AggregateType] = strawberry_django.offset_paginated()

    ip_address: IPAddressType = strawberry_django.field()
    ip_address_list: OffsetPaginated[IPAddressType] = strawberry_django.offset_paginated()

    ip_range: IPRangeType = strawberry_django.field()
    ip_range_list: OffsetPaginated[IPRangeType] = strawberry_django.offset_paginated()

    prefix: PrefixType = strawberry_django.field()
    prefix_list: OffsetPaginated[PrefixType] = strawberry_django.offset_paginated()

    rir: RIRType = strawberry_django.field()
    rir_list: OffsetPaginated[RIRType] = strawberry_django.offset_paginated()

    role: RoleType = strawberry_django.field()
    role_list: OffsetPaginated[RoleType] = strawberry_django.offset_paginated()

    route_target: RouteTargetType = strawberry_django.field()
    route_target_list: OffsetPaginated[RouteTargetType] = strawberry_django.offset_paginated()

    service: ServiceType = strawberry_django.field()
    service_list: OffsetPaginated[ServiceType] = strawberry_django.offset_paginated()

    service_template: ServiceTemplateType = strawberry_django.field()
    service_template_list: OffsetPaginated[ServiceTemplateType] = strawberry_django.offset_paginated()

    fhrp_group: FHRPGroupType = strawberry_django.field()
    fhrp_group_list: OffsetPaginated[FHRPGroupType] = strawberry_django.offset_paginated()

    fhrp_group_assignment: FHRPGroupAssignmentType = strawberry_django.field()
    fhrp_group_assignment_list: OffsetPaginated[FHRPGroupAssignmentType] = strawberry_django.offset_paginated()

    vlan: VLANType = strawberry_django.field()
    vlan_list: OffsetPaginated[VLANType] = strawberry_django.offset_paginated()

    vlan_group: VLANGroupType = strawberry_django.field()
    vlan_group_list: OffsetPaginated[VLANGroupType] = strawberry_django.offset_paginated()

    vlan_translation_policy: VLANTranslationPolicyType = strawberry_django.field()
    vlan_translation_policy_list: OffsetPaginated[VLANTranslationPolicyType] = strawberry_django.offset_paginated()

    vlan_translation_rule: VLANTranslationRuleType = strawberry_django.field()
    vlan_translation_rule_list: OffsetPaginated[VLANTranslationRuleType] = strawberry_django.offset_paginated()

    vrf: VRFType = strawberry_django.field()
    vrf_list: OffsetPaginated[VRFType] = strawberry_django.offset_paginated()
