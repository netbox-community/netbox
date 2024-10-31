from typing import List

import strawberry
import strawberry_django

from .types import *


@strawberry.type(name="Query")
class IPAMQuery:
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
