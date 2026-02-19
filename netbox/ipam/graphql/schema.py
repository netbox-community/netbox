import strawberry
import strawberry_django

from .types import *


@strawberry.type(name="Query")
class IPAMQuery:
    asn: ASNType = strawberry_django.field()
    asn_list: list[ASNType] = strawberry_django.field()

    asn_range: ASNRangeType = strawberry_django.field()
    asn_range_list: list[ASNRangeType] = strawberry_django.field()

    aggregate: AggregateType = strawberry_django.field()
    aggregate_list: list[AggregateType] = strawberry_django.field()

    ip_address: IPAddressType = strawberry_django.field()
    ip_address_list: list[IPAddressType] = strawberry_django.field()

    ip_range: IPRangeType = strawberry_django.field()
    ip_range_list: list[IPRangeType] = strawberry_django.field()

    prefix: PrefixType = strawberry_django.field()
    prefix_list: list[PrefixType] = strawberry_django.field()

    rir: RIRType = strawberry_django.field()
    rir_list: list[RIRType] = strawberry_django.field()

    role: RoleType = strawberry_django.field()
    role_list: list[RoleType] = strawberry_django.field()

    route_target: RouteTargetType = strawberry_django.field()
    route_target_list: list[RouteTargetType] = strawberry_django.field()

    service: ServiceType = strawberry_django.field()
    service_list: list[ServiceType] = strawberry_django.field()

    service_template: ServiceTemplateType = strawberry_django.field()
    service_template_list: list[ServiceTemplateType] = strawberry_django.field()

    fhrp_group: FHRPGroupType = strawberry_django.field()
    fhrp_group_list: list[FHRPGroupType] = strawberry_django.field()

    fhrp_group_assignment: FHRPGroupAssignmentType = strawberry_django.field()
    fhrp_group_assignment_list: list[FHRPGroupAssignmentType] = strawberry_django.field()

    vlan: VLANType = strawberry_django.field()
    vlan_list: list[VLANType] = strawberry_django.field()

    vlan_group: VLANGroupType = strawberry_django.field()
    vlan_group_list: list[VLANGroupType] = strawberry_django.field()

    vlan_translation_policy: VLANTranslationPolicyType = strawberry_django.field()
    vlan_translation_policy_list: list[VLANTranslationPolicyType] = strawberry_django.field()

    vlan_translation_rule: VLANTranslationRuleType = strawberry_django.field()
    vlan_translation_rule_list: list[VLANTranslationRuleType] = strawberry_django.field()

    vrf: VRFType = strawberry_django.field()
    vrf_list: list[VRFType] = strawberry_django.field()
