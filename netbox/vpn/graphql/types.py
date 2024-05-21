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

    tunnels: List[Annotated["TunnelType", strawberry.lazy('vpn.graphql.types')]]


@strawberry_django.type(
    models.TunnelTermination,
    fields='__all__',
    filters=TunnelTerminationFilter
)
class TunnelTerminationType(CustomFieldsMixin, TagsMixin, ObjectType):
    tunnel: Annotated["TunnelType", strawberry.lazy('vpn.graphql.types')]
    termination_type: Annotated["ContentTypeType", strawberry.lazy('netbox.graphql.types')] | None
    outside_ip: Annotated["IPAddressType", strawberry.lazy('ipam.graphql.types')] | None


@strawberry_django.type(
    models.Tunnel,
    fields='__all__',
    filters=TunnelFilter
)
class TunnelType(NetBoxObjectType):
    group: Annotated["TunnelGroupType", strawberry.lazy('vpn.graphql.types')] | None
    ipsec_profile: Annotated["IPSecProfileType", strawberry.lazy('vpn.graphql.types')] | None
    tenant: Annotated["TenantType", strawberry.lazy('tenancy.graphql.types')] | None

    terminations: List[Annotated["TunnelTerminationType", strawberry.lazy('vpn.graphql.types')]]


@strawberry_django.type(
    models.IKEProposal,
    fields='__all__',
    filters=IKEProposalFilter
)
class IKEProposalType(OrganizationalObjectType):

    ike_policies: List[Annotated["IKEPolicyType", strawberry.lazy('vpn.graphql.types')]]


@strawberry_django.type(
    models.IKEPolicy,
    fields='__all__',
    filters=IKEPolicyFilter
)
class IKEPolicyType(OrganizationalObjectType):

    proposals: List[Annotated["IKEProposalType", strawberry.lazy('vpn.graphql.types')]]
    ipsec_profiles: List[Annotated["IPSecProposalType", strawberry.lazy('vpn.graphql.types')]]


@strawberry_django.type(
    models.IPSecProposal,
    fields='__all__',
    filters=IPSecProposalFilter
)
class IPSecProposalType(OrganizationalObjectType):

    ipsec_policies: List[Annotated["IPSecPolicyType", strawberry.lazy('vpn.graphql.types')]]


@strawberry_django.type(
    models.IPSecPolicy,
    fields='__all__',
    filters=IPSecPolicyFilter
)
class IPSecPolicyType(OrganizationalObjectType):

    proposals: List[Annotated["IPSecProposalType", strawberry.lazy('vpn.graphql.types')]]
    ipsec_profiles: List[Annotated["IPSecProfileType", strawberry.lazy('vpn.graphql.types')]]


@strawberry_django.type(
    models.IPSecProfile,
    fields='__all__',
    filters=IPSecProfileFilter
)
class IPSecProfileType(OrganizationalObjectType):
    ike_policy: Annotated["IKEPolicyType", strawberry.lazy('vpn.graphql.types')]
    ipsec_policy: Annotated["IPSecPolicyType", strawberry.lazy('vpn.graphql.types')]

    tunnels: List[Annotated["TunnelType", strawberry.lazy('vpn.graphql.types')]]


@strawberry_django.type(
    models.L2VPN,
    fields='__all__',
    filters=L2VPNFilter
)
class L2VPNType(ContactsMixin, NetBoxObjectType):
    tenant: Annotated["TenantType", strawberry.lazy('tenancy.graphql.types')] | None

    export_targets: List[Annotated["RouteTargetType", strawberry.lazy('ipam.graphql.types')]]
    terminations: List[Annotated["L2VPNTerminationType", strawberry.lazy('vpn.graphql.types')]]
    import_targets: List[Annotated["RouteTargetType", strawberry.lazy('ipam.graphql.types')]]


@strawberry_django.type(
    models.L2VPNTermination,
    exclude=('assigned_object_type', 'assigned_object_id'),
    filters=L2VPNTerminationFilter
)
class L2VPNTerminationType(NetBoxObjectType):
    l2vpn: Annotated["L2VPNType", strawberry.lazy('vpn.graphql.types')]

    @strawberry_django.field
    def assigned_object(self) -> Annotated[Union[
        Annotated["InterfaceType", strawberry.lazy('dcim.graphql.types')],
        Annotated["VLANType", strawberry.lazy('ipam.graphql.types')],
        Annotated["VMInterfaceType", strawberry.lazy('virtualization.graphql.types')],
    ], strawberry.union("L2VPNAssignmentType")]:
        return self.assigned_object
