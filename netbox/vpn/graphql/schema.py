import graphene

from netbox.graphql.fields import ObjectField, ObjectListField
from utilities.graphql_optimizer import gql_query_optimizer
from vpn import models
from .types import *


class VPNQuery(graphene.ObjectType):

    ike_policy = ObjectField(IKEPolicyType)
    ike_policy_list = ObjectListField(IKEPolicyType)

    def resolve_ike_policy_list(root, info, **kwargs):
        return gql_query_optimizer(models.IKEPolicy.objects.all(), info)

    ike_proposal = ObjectField(IKEProposalType)
    ike_proposal_list = ObjectListField(IKEProposalType)

    def resolve_ike_proposal_list(root, info, **kwargs):
        return gql_query_optimizer(models.IKEProposal.objects.all(), info)

    ipsec_policy = ObjectField(IPSecPolicyType)
    ipsec_policy_list = ObjectListField(IPSecPolicyType)

    def resolve_ipsec_policy_list(root, info, **kwargs):
        return gql_query_optimizer(models.IPSecPolicy.objects.all(), info)

    ipsec_profile = ObjectField(IPSecProfileType)
    ipsec_profile_list = ObjectListField(IPSecProfileType)

    def resolve_ipsec_profile_list(root, info, **kwargs):
        return gql_query_optimizer(models.IPSecProfile.objects.all(), info)

    ipsec_proposal = ObjectField(IPSecProposalType)
    ipsec_proposal_list = ObjectListField(IPSecProposalType)

    def resolve_ipsec_proposal_list(root, info, **kwargs):
        return gql_query_optimizer(models.IPSecProposal.objects.all(), info)

    l2vpn = ObjectField(L2VPNType)
    l2vpn_list = ObjectListField(L2VPNType)

    def resolve_l2vpn_list(root, info, **kwargs):
        return gql_query_optimizer(models.L2VPN.objects.all(), info)

    l2vpn_termination = ObjectField(L2VPNTerminationType)
    l2vpn_termination_list = ObjectListField(L2VPNTerminationType)

    def resolve_l2vpn_termination_list(root, info, **kwargs):
        return gql_query_optimizer(models.L2VPNTermination.objects.all(), info)

    tunnel = ObjectField(TunnelType)
    tunnel_list = ObjectListField(TunnelType)

    def resolve_tunnel_list(root, info, **kwargs):
        return gql_query_optimizer(models.Tunnel.objects.all(), info)

    tunnel_group = ObjectField(TunnelGroupType)
    tunnel_group_list = ObjectListField(TunnelGroupType)

    def resolve_tunnel_group_list(root, info, **kwargs):
        return gql_query_optimizer(models.TunnelGroup.objects.all(), info)

    tunnel_termination = ObjectField(TunnelTerminationType)
    tunnel_termination_list = ObjectListField(TunnelTerminationType)

    def resolve_tunnel_termination_list(root, info, **kwargs):
        return gql_query_optimizer(models.TunnelTermination.objects.all(), info)
