from typing import TYPE_CHECKING, Annotated

import strawberry
import strawberry_django

from extras.graphql.mixins import ContactsMixin, CustomFieldsMixin, TagsMixin
from netbox.graphql.types import NetBoxObjectType, ObjectType, OrganizationalObjectType, PrimaryObjectType
from vpn import models

from .filters import *

if TYPE_CHECKING:
    from dcim.graphql.types import InterfaceType
    from ipam.graphql.types import IPAddressType, RouteTargetType, VLANType
    from netbox.graphql.types import ContentTypeType
    from tenancy.graphql.types import TenantType
    from virtualization.graphql.types import VMInterfaceType

__all__ = (
    'IKEPolicyType',
    'IKEProposalType',
    'IPSecPolicyType',
    'IPSecProfileType',
    'IPSecProposalType',
    'L2VPNTerminationType',
    'L2VPNType',
    'TunnelGroupType',
    'TunnelTerminationType',
    'TunnelType',
)


@strawberry_django.type(
    models.TunnelGroup,
    fields='__all__',
    filters=TunnelGroupFilter,
    pagination=True
)
class TunnelGroupType(ContactsMixin, OrganizationalObjectType):

    tunnels: list[Annotated["TunnelType", strawberry.lazy('vpn.graphql.types')]]


@strawberry_django.type(
    models.TunnelTermination,
    fields='__all__',
    filters=TunnelTerminationFilter,
    pagination=True
)
class TunnelTerminationType(CustomFieldsMixin, TagsMixin, ObjectType):
    tunnel: Annotated["TunnelType", strawberry.lazy('vpn.graphql.types')]
    termination_type: Annotated["ContentTypeType", strawberry.lazy('netbox.graphql.types')] | None
    outside_ip: Annotated["IPAddressType", strawberry.lazy('ipam.graphql.types')] | None


@strawberry_django.type(
    models.Tunnel,
    fields='__all__',
    filters=TunnelFilter,
    pagination=True
)
class TunnelType(ContactsMixin, PrimaryObjectType):
    group: Annotated["TunnelGroupType", strawberry.lazy('vpn.graphql.types')] | None
    ipsec_profile: Annotated["IPSecProfileType", strawberry.lazy('vpn.graphql.types')] | None
    tenant: Annotated["TenantType", strawberry.lazy('tenancy.graphql.types')] | None

    terminations: list[Annotated["TunnelTerminationType", strawberry.lazy('vpn.graphql.types')]]


@strawberry_django.type(
    models.IKEProposal,
    fields='__all__',
    filters=IKEProposalFilter,
    pagination=True
)
class IKEProposalType(PrimaryObjectType):
    ike_policies: list[Annotated["IKEPolicyType", strawberry.lazy('vpn.graphql.types')]]


@strawberry_django.type(
    models.IKEPolicy,
    fields='__all__',
    filters=IKEPolicyFilter,
    pagination=True
)
class IKEPolicyType(PrimaryObjectType):
    proposals: list[Annotated["IKEProposalType", strawberry.lazy('vpn.graphql.types')]]
    ipsec_profiles: list[Annotated["IPSecProfileType", strawberry.lazy('vpn.graphql.types')]]


@strawberry_django.type(
    models.IPSecProposal,
    fields='__all__',
    filters=IPSecProposalFilter,
    pagination=True
)
class IPSecProposalType(PrimaryObjectType):
    ipsec_policies: list[Annotated["IPSecPolicyType", strawberry.lazy('vpn.graphql.types')]]


@strawberry_django.type(
    models.IPSecPolicy,
    fields='__all__',
    filters=IPSecPolicyFilter,
    pagination=True
)
class IPSecPolicyType(PrimaryObjectType):
    proposals: list[Annotated["IPSecProposalType", strawberry.lazy('vpn.graphql.types')]]
    ipsec_profiles: list[Annotated["IPSecProfileType", strawberry.lazy('vpn.graphql.types')]]


@strawberry_django.type(
    models.IPSecProfile,
    fields='__all__',
    filters=IPSecProfileFilter,
    pagination=True
)
class IPSecProfileType(PrimaryObjectType):
    ike_policy: Annotated["IKEPolicyType", strawberry.lazy('vpn.graphql.types')]
    ipsec_policy: Annotated["IPSecPolicyType", strawberry.lazy('vpn.graphql.types')]

    tunnels: list[Annotated["TunnelType", strawberry.lazy('vpn.graphql.types')]]


@strawberry_django.type(
    models.L2VPN,
    fields='__all__',
    filters=L2VPNFilter,
    pagination=True
)
class L2VPNType(ContactsMixin, PrimaryObjectType):
    tenant: Annotated["TenantType", strawberry.lazy('tenancy.graphql.types')] | None

    export_targets: list[Annotated["RouteTargetType", strawberry.lazy('ipam.graphql.types')]]
    terminations: list[Annotated["L2VPNTerminationType", strawberry.lazy('vpn.graphql.types')]]
    import_targets: list[Annotated["RouteTargetType", strawberry.lazy('ipam.graphql.types')]]


@strawberry_django.type(
    models.L2VPNTermination,
    exclude=['assigned_object_type', 'assigned_object_id'],
    filters=L2VPNTerminationFilter,
    pagination=True
)
class L2VPNTerminationType(NetBoxObjectType):
    l2vpn: Annotated["L2VPNType", strawberry.lazy('vpn.graphql.types')]

    @strawberry_django.field
    def assigned_object(self) -> Annotated[
        Annotated['InterfaceType', strawberry.lazy('dcim.graphql.types')]
        | Annotated['VLANType', strawberry.lazy('ipam.graphql.types')]
        | Annotated['VMInterfaceType', strawberry.lazy('virtualization.graphql.types')],
        strawberry.union('L2VPNAssignmentType'),
    ]:
        return self.assigned_object
