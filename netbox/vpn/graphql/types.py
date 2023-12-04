import graphene

from extras.graphql.mixins import ContactsMixin, CustomFieldsMixin, TagsMixin
from netbox.graphql.types import ObjectType, OrganizationalObjectType, NetBoxObjectType
from vpn import filtersets, models

__all__ = (
    'IKEPolicyType',
    'IKEProposalType',
    'IPSecPolicyType',
    'IPSecProfileType',
    'IPSecProposalType',
    'L2VPNType',
    'L2VPNTerminationType',
    'TunnelGroupType',
    'TunnelTerminationType',
    'TunnelType',
)


class TunnelGroupType(OrganizationalObjectType):

    class Meta:
        model = models.TunnelGroup
        fields = '__all__'
        filterset_class = filtersets.TunnelGroupFilterSet


class TunnelTerminationType(CustomFieldsMixin, TagsMixin, ObjectType):

    class Meta:
        model = models.TunnelTermination
        fields = '__all__'
        filterset_class = filtersets.TunnelTerminationFilterSet


class TunnelType(NetBoxObjectType):

    class Meta:
        model = models.Tunnel
        fields = '__all__'
        filterset_class = filtersets.TunnelFilterSet


class IKEProposalType(OrganizationalObjectType):

    class Meta:
        model = models.IKEProposal
        fields = '__all__'
        filterset_class = filtersets.IKEProposalFilterSet


class IKEPolicyType(OrganizationalObjectType):

    class Meta:
        model = models.IKEPolicy
        fields = '__all__'
        filterset_class = filtersets.IKEPolicyFilterSet


class IPSecProposalType(OrganizationalObjectType):

    class Meta:
        model = models.IPSecProposal
        fields = '__all__'
        filterset_class = filtersets.IPSecProposalFilterSet


class IPSecPolicyType(OrganizationalObjectType):

    class Meta:
        model = models.IPSecPolicy
        fields = '__all__'
        filterset_class = filtersets.IPSecPolicyFilterSet


class IPSecProfileType(OrganizationalObjectType):

    class Meta:
        model = models.IPSecProfile
        fields = '__all__'
        filterset_class = filtersets.IPSecProfileFilterSet


class L2VPNType(ContactsMixin, NetBoxObjectType):
    class Meta:
        model = models.L2VPN
        fields = '__all__'
        filtersets_class = filtersets.L2VPNFilterSet


class L2VPNTerminationType(NetBoxObjectType):
    assigned_object = graphene.Field('vpn.graphql.gfk_mixins.L2VPNAssignmentType')

    class Meta:
        model = models.L2VPNTermination
        exclude = ('assigned_object_type', 'assigned_object_id')
        filtersets_class = filtersets.L2VPNTerminationFilterSet
