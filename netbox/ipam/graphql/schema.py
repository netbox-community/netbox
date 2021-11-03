import graphene

from netbox.graphql.fields import ObjectField, ObjectListField
from .types import *


class IPAMQuery(graphene.ObjectType):
    asn = ObjectField(ASNType)
    asn_list = ObjectListField(ASNType)

    aggregate = ObjectField(AggregateType)
    aggregate_list = ObjectListField(AggregateType)

    ip_address = ObjectField(IPAddressType)
    ip_address_list = ObjectListField(IPAddressType)

    ip_range = ObjectField(IPRangeType)
    ip_range_list = ObjectListField(IPRangeType)

    prefix = ObjectField(PrefixType)
    prefix_list = ObjectListField(PrefixType)

    rir = ObjectField(RIRType)
    rir_list = ObjectListField(RIRType)

    role = ObjectField(RoleType)
    role_list = ObjectListField(RoleType)

    route_target = ObjectField(RouteTargetType)
    route_target_list = ObjectListField(RouteTargetType)

    service = ObjectField(ServiceType)
    service_list = ObjectListField(ServiceType)

    fhrp_group = ObjectField(FHRPGroupType)
    fhrp_group_list = ObjectListField(FHRPGroupType)

    fhrp_group_assignment = ObjectField(FHRPGroupAssignmentType)
    fhrp_group_assignment_list = ObjectListField(FHRPGroupAssignmentType)

    vlan = ObjectField(VLANType)
    vlan_list = ObjectListField(VLANType)

    vlan_group = ObjectField(VLANGroupType)
    vlan_group_list = ObjectListField(VLANGroupType)

    vrf = ObjectField(VRFType)
    vrf_list = ObjectListField(VRFType)
