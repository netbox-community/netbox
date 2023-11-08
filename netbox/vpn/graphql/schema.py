import graphene

from netbox.graphql.fields import ObjectField, ObjectListField
from utilities.graphql_optimizer import gql_query_optimizer
from vpn import models
from .types import *


class VPNQuery(graphene.ObjectType):
    ipsec_profile = ObjectField(IPSecProfileType)
    ipsec_profile_list = ObjectListField(IPSecProfileType)

    def resolve_ipsec_profile_list(root, info, **kwargs):
        return gql_query_optimizer(models.IPSecProfile.objects.all(), info)

    tunnel = ObjectField(TunnelType)
    tunnel_list = ObjectListField(TunnelType)

    def resolve_tunnel_list(root, info, **kwargs):
        return gql_query_optimizer(models.Tunnel.objects.all(), info)

    tunnel_termination = ObjectField(TunnelTerminationType)
    tunnel_termination_list = ObjectListField(TunnelTerminationType)

    def resolve_tunnel_termination_list(root, info, **kwargs):
        return gql_query_optimizer(models.TunnelTermination.objects.all(), info)
