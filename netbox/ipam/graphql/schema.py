import graphene

from ipam import models
from netbox.graphql.fields import ObjectField, ObjectListField
from utilities.graphql_optimizer import gql_query_optimizer
from .types import *


class IPAMQuery(graphene.ObjectType):
    asn = ObjectField(ASNType)
    asn_list = ObjectListField(ASNType)

    def resolve_asn_list(root, info, **kwargs):
        return gql_query_optimizer(models.ASN.objects.all(), info)

    asn_range = ObjectField(ASNRangeType)
    asn_range_list = ObjectListField(ASNRangeType)

    def resolve_asn_range_list(root, info, **kwargs):
        return gql_query_optimizer(models.ASNRange.objects.all(), info)

    aggregate = ObjectField(AggregateType)
    aggregate_list = ObjectListField(AggregateType)

    def resolve_aggregate_list(root, info, **kwargs):
        return gql_query_optimizer(models.Aggregate.objects.all(), info)

    ip_address = ObjectField(IPAddressType)
    ip_address_list = ObjectListField(IPAddressType)

    def resolve_ip_address_list(root, info, **kwargs):
        return gql_query_optimizer(models.IPAddress.objects.all(), info)

    ip_range = ObjectField(IPRangeType)
    ip_range_list = ObjectListField(IPRangeType)

    def resolve_ip_range_list(root, info, **kwargs):
        return gql_query_optimizer(models.IPRange.objects.all(), info)

    prefix = ObjectField(PrefixType)
    prefix_list = ObjectListField(PrefixType)

    def resolve_prefix_list(root, info, **kwargs):
        return gql_query_optimizer(models.Prefix.objects.all(), info)

    rir = ObjectField(RIRType)
    rir_list = ObjectListField(RIRType)

    def resolve_rir_list(root, info, **kwargs):
        return gql_query_optimizer(models.RIR.objects.all(), info)

    role = ObjectField(RoleType)
    role_list = ObjectListField(RoleType)

    def resolve_role_list(root, info, **kwargs):
        return gql_query_optimizer(models.Role.objects.all(), info)

    route_target = ObjectField(RouteTargetType)
    route_target_list = ObjectListField(RouteTargetType)

    def resolve_route_target_list(root, info, **kwargs):
        return gql_query_optimizer(models.RouteTarget.objects.all(), info)

    service = ObjectField(ServiceType)
    service_list = ObjectListField(ServiceType)

    def resolve_service_list(root, info, **kwargs):
        return gql_query_optimizer(models.Service.objects.all(), info)

    service_template = ObjectField(ServiceTemplateType)
    service_template_list = ObjectListField(ServiceTemplateType)

    def resolve_service_template_list(root, info, **kwargs):
        return gql_query_optimizer(models.ServiceTemplate.objects.all(), info)

    fhrp_group = ObjectField(FHRPGroupType)
    fhrp_group_list = ObjectListField(FHRPGroupType)

    def resolve_fhrp_group_list(root, info, **kwargs):
        return gql_query_optimizer(models.FHRPGroup.objects.all(), info)

    fhrp_group_assignment = ObjectField(FHRPGroupAssignmentType)
    fhrp_group_assignment_list = ObjectListField(FHRPGroupAssignmentType)

    def resolve_fhrp_group_assignment_list(root, info, **kwargs):
        return gql_query_optimizer(models.FHRPGroupAssignment.objects.all(), info)

    vlan = ObjectField(VLANType)
    vlan_list = ObjectListField(VLANType)

    def resolve_vlan_list(root, info, **kwargs):
        return gql_query_optimizer(models.VLAN.objects.all(), info)

    vlan_group = ObjectField(VLANGroupType)
    vlan_group_list = ObjectListField(VLANGroupType)

    def resolve_vlan_group_list(root, info, **kwargs):
        return gql_query_optimizer(models.VLANGroup.objects.all(), info)

    vrf = ObjectField(VRFType)
    vrf_list = ObjectListField(VRFType)

    def resolve_vrf_list(root, info, **kwargs):
        return gql_query_optimizer(models.VRF.objects.all(), info)
