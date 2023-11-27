from extras.graphql.mixins import CustomFieldsMixin, TagsMixin
from netbox.graphql.types import ObjectType, OrganizationalObjectType, NetBoxObjectType
from vpn import filtersets, models

__all__ = (
    'IKEPolicyType',
    'IKEProposalType',
    'IPSecPolicyType',
    'IPSecProfileType',
    'IPSecProposalType',
    'TunnelTerminationType',
    'TunnelType',
)


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
