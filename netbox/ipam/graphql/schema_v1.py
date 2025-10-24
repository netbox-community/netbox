from typing import List

import strawberry
import strawberry_django

from .types_v1 import *


@strawberry.type(name="Query")
class IPAMQueryV1:
    asn: ASNTypeV1 = strawberry_django.field()
    asn_list: List[ASNTypeV1] = strawberry_django.field()

    asn_range: ASNRangeTypeV1 = strawberry_django.field()
    asn_range_list: List[ASNRangeTypeV1] = strawberry_django.field()

    aggregate: AggregateTypeV1 = strawberry_django.field()
    aggregate_list: List[AggregateTypeV1] = strawberry_django.field()

    ip_address: IPAddressTypeV1 = strawberry_django.field()
    ip_address_list: List[IPAddressTypeV1] = strawberry_django.field()

    ip_range: IPRangeTypeV1 = strawberry_django.field()
    ip_range_list: List[IPRangeTypeV1] = strawberry_django.field()

    prefix: PrefixTypeV1 = strawberry_django.field()
    prefix_list: List[PrefixTypeV1] = strawberry_django.field()

    rir: RIRTypeV1 = strawberry_django.field()
    rir_list: List[RIRTypeV1] = strawberry_django.field()

    role: RoleTypeV1 = strawberry_django.field()
    role_list: List[RoleTypeV1] = strawberry_django.field()

    route_target: RouteTargetTypeV1 = strawberry_django.field()
    route_target_list: List[RouteTargetTypeV1] = strawberry_django.field()

    service: ServiceTypeV1 = strawberry_django.field()
    service_list: List[ServiceTypeV1] = strawberry_django.field()

    service_template: ServiceTemplateTypeV1 = strawberry_django.field()
    service_template_list: List[ServiceTemplateTypeV1] = strawberry_django.field()

    fhrp_group: FHRPGroupTypeV1 = strawberry_django.field()
    fhrp_group_list: List[FHRPGroupTypeV1] = strawberry_django.field()

    fhrp_group_assignment: FHRPGroupAssignmentTypeV1 = strawberry_django.field()
    fhrp_group_assignment_list: List[FHRPGroupAssignmentTypeV1] = strawberry_django.field()

    vlan: VLANTypeV1 = strawberry_django.field()
    vlan_list: List[VLANTypeV1] = strawberry_django.field()

    vlan_group: VLANGroupTypeV1 = strawberry_django.field()
    vlan_group_list: List[VLANGroupTypeV1] = strawberry_django.field()

    vlan_translation_policy: VLANTranslationPolicyTypeV1 = strawberry_django.field()
    vlan_translation_policy_list: List[VLANTranslationPolicyTypeV1] = strawberry_django.field()

    vlan_translation_rule: VLANTranslationRuleTypeV1 = strawberry_django.field()
    vlan_translation_rule_list: List[VLANTranslationRuleTypeV1] = strawberry_django.field()

    vrf: VRFTypeV1 = strawberry_django.field()
    vrf_list: List[VRFTypeV1] = strawberry_django.field()
