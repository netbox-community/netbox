from typing import Annotated, List, Union

import strawberry
import strawberry_django

from extras.graphql.mixins import ContactsMixin, CustomFieldsMixin, TagsMixin
from netbox.graphql.types import ObjectType, OrganizationalObjectType, NetBoxObjectType
from vpn import models
from .filters import *

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


@strawberry_django.type(
    models.TunnelGroup,
    fields='__all__',
    filters=TunnelGroupFilter
)
class TunnelGroupType(OrganizationalObjectType):
    pass


@strawberry_django.type(
    models.TunnelTermination,
    fields='__all__',
    filters=TunnelTerminationFilter
)
class TunnelTerminationType(CustomFieldsMixin, TagsMixin, ObjectType):
    pass


@strawberry_django.type(
    models.Tunnel,
    fields='__all__',
    filters=TunnelFilter
)
class TunnelType(NetBoxObjectType):
    pass


@strawberry_django.type(
    models.IKEProposal,
    fields='__all__',
    filters=IKEProposalFilter
)
class IKEProposalType(OrganizationalObjectType):

    @strawberry_django.field
    def ike_policies(self) -> List[Annotated["IKEPolicyType", strawberry.lazy('vpn.graphql.types')]]:
        return self.ike_policies.all()


@strawberry_django.type(
    models.IKEPolicy,
    fields='__all__',
    filters=IKEPolicyFilter
)
class IKEPolicyType(OrganizationalObjectType):

    @strawberry_django.field
    def proposals(self) -> List[Annotated["IKEProposalType", strawberry.lazy('vpn.graphql.types')]]:
        return self.proposals.all()

    @strawberry_django.field
    def ipsec_profiles(self) -> List[Annotated["IPSecProposalType", strawberry.lazy('vpn.graphql.types')]]:
        return self.ipsec_profiles.all()


@strawberry_django.type(
    models.IPSecProposal,
    fields='__all__',
    filters=IPSecProposalFilter
)
class IPSecProposalType(OrganizationalObjectType):

    @strawberry_django.field
    def ipsec_policies(self) -> List[Annotated["IPSecPolicyType", strawberry.lazy('vpn.graphql.types')]]:
        return self.ipsec_policies.all()


@strawberry_django.type(
    models.IPSecPolicy,
    fields='__all__',
    filters=IPSecPolicyFilter
)
class IPSecPolicyType(OrganizationalObjectType):

    @strawberry_django.field
    def proposals(self) -> List[Annotated["IKEProposalType", strawberry.lazy('vpn.graphql.types')]]:
        return self.proposals.all()

    @strawberry_django.field
    def ipsec_profiles(self) -> List[Annotated["IPSecProposalType", strawberry.lazy('vpn.graphql.types')]]:
        return self.ipsec_profiles.all()


@strawberry_django.type(
    models.IPSecProfile,
    fields='__all__',
    filters=IPSecProfileFilter
)
class IPSecProfileType(OrganizationalObjectType):

    @strawberry_django.field
    def tunnels(self) -> List[Annotated["TunnelType", strawberry.lazy('vpn.graphql.types')]]:
        return self.tunnels.all()


@strawberry_django.type(
    models.L2VPN,
    fields='__all__',
    filters=L2VPNFilter
)
class L2VPNType(ContactsMixin, NetBoxObjectType):

    @strawberry_django.field
    def export_targets(self) -> List[Annotated["RouteTargetType", strawberry.lazy('ipam.graphql.types')]]:
        return self.export_targets.all()

    @strawberry_django.field
    def terminations(self) -> List[Annotated["L2VPNTerminationType", strawberry.lazy('vpn.graphql.types')]]:
        return self.terminations.all()

    @strawberry_django.field
    def import_targets(self) -> List[Annotated["RouteTargetType", strawberry.lazy('ipam.graphql.types')]]:
        return self.import_targets.all()


@strawberry_django.type(
    models.L2VPNTermination,
    exclude=('assigned_object_type', 'assigned_object_id'),
    filters=L2VPNTerminationFilter
)
class L2VPNTerminationType(NetBoxObjectType):

    @strawberry_django.field
    def assigned_object(self) -> Annotated[Union[
        Annotated["InterfaceType", strawberry.lazy('dcim.graphql.types')],
        Annotated["VLANType", strawberry.lazy('ipam.graphql.types')],
        Annotated["VMInterfaceType", strawberry.lazy('virtualization.graphql.types')],
    ], strawberry.union("L2VPNAssignmentType")]:
        return self.assigned_object
