import graphene

from netbox.graphql.fields import ObjectField, ObjectListField
from .types import *


class IPAMQuery(graphene.ObjectType):
    aggregate = ObjectField(AggregateType)
    aggregates = ObjectListField(AggregateType)

    ip_address = ObjectField(IPAddressType)
    ip_addresses = ObjectListField(IPAddressType)

    prefix = ObjectField(PrefixType)
    prefixes = ObjectListField(PrefixType)

    rir = ObjectField(RIRType)
    rirs = ObjectListField(RIRType)

    role = ObjectField(RoleType)
    roles = ObjectListField(RoleType)

    route_target = ObjectField(RouteTargetType)
    route_targets = ObjectListField(RouteTargetType)

    service = ObjectField(ServiceType)
    services = ObjectListField(ServiceType)

    vlan = ObjectField(VLANType)
    vlans = ObjectListField(VLANType)

    vlan_group = ObjectField(VLANGroupType)
    vlan_groups = ObjectListField(VLANGroupType)

    vrf = ObjectField(VRFType)
    vrfs = ObjectListField(VRFType)
