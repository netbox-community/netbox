from typing import List

import strawberry
import strawberry_django

from ipam import models
from .types import *


@strawberry.type
class IPAMQuery:
    @strawberry.field
    def asn(self, id: int) -> ASNType:
        return models.ASN.objects.get(pk=id)
    asn_list: List[ASNType] = strawberry_django.field()

    @strawberry.field
    def asn_range(self, id: int) -> ASNRangeType:
        return models.ASNRange.objects.get(pk=id)
    asn_range_list: List[ASNRangeType] = strawberry_django.field()

    @strawberry.field
    def aggregate(self, id: int) -> AggregateType:
        return models.Aggregate.objects.get(pk=id)
    aggregate_list: List[AggregateType] = strawberry_django.field()

    @strawberry.field
    def ip_address(self, id: int) -> IPAddressType:
        return models.IPAddress.objects.get(pk=id)
    ip_address_list: List[IPAddressType] = strawberry_django.field()

    @strawberry.field
    def ip_range(self, id: int) -> IPRangeType:
        return models.IPRange.objects.get(pk=id)
    ip_range_list: List[IPRangeType] = strawberry_django.field()

    @strawberry.field
    def prefix(self, id: int) -> PrefixType:
        return models.Prefix.objects.get(pk=id)
    prefix_list: List[PrefixType] = strawberry_django.field()

    @strawberry.field
    def rir(self, id: int) -> RIRType:
        return models.RIR.objects.get(pk=id)
    rir_list: List[RIRType] = strawberry_django.field()

    @strawberry.field
    def role(self, id: int) -> RoleType:
        return models.Role.objects.get(pk=id)
    role_list: List[RoleType] = strawberry_django.field()

    @strawberry.field
    def route_target(self, id: int) -> RouteTargetType:
        return models.RouteTarget.objects.get(pk=id)
    route_target_list: List[RouteTargetType] = strawberry_django.field()

    @strawberry.field
    def service(self, id: int) -> ServiceType:
        return models.Service.objects.get(pk=id)
    service_list: List[ServiceType] = strawberry_django.field()

    @strawberry.field
    def service_template(self, id: int) -> ServiceTemplateType:
        return models.ServiceTemplate.objects.get(pk=id)
    service_template_list: List[ServiceTemplateType] = strawberry_django.field()

    @strawberry.field
    def fhrp_group(self, id: int) -> FHRPGroupType:
        return models.FHRPGroup.objects.get(pk=id)
    fhrp_group_list: List[FHRPGroupType] = strawberry_django.field()

    @strawberry.field
    def fhrp_group_assignment(self, id: int) -> FHRPGroupAssignmentType:
        return models.FHRPGroupAssignment.objects.get(pk=id)
    fhrp_group_assignment_list: List[FHRPGroupAssignmentType] = strawberry_django.field()

    @strawberry.field
    def vlan(self, id: int) -> VLANType:
        return models.VLAN.objects.get(pk=id)
    vlan_list: List[VLANType] = strawberry_django.field()

    @strawberry.field
    def vlan_group(self, id: int) -> VLANGroupType:
        return models.VLANGroup.objects.get(pk=id)
    vlan_group_list: List[VLANGroupType] = strawberry_django.field()

    @strawberry.field
    def vrf(self, id: int) -> VRFType:
        return models.VRF.objects.get(pk=id)
    vrf_list: List[VRFType] = strawberry_django.field()
