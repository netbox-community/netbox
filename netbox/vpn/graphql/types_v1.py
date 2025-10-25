from typing import Annotated, List, TYPE_CHECKING, Union

import strawberry
import strawberry_django

from extras.graphql.mixins_v1 import ContactsMixinV1, CustomFieldsMixinV1, TagsMixinV1
from netbox.graphql.types_v1 import ObjectTypeV1, OrganizationalObjectTypeV1, NetBoxObjectTypeV1, PrimaryObjectTypeV1
from vpn import models
from .filters_v1 import *

if TYPE_CHECKING:
    from dcim.graphql.types_v1 import InterfaceTypeV1
    from ipam.graphql.types_v1 import IPAddressTypeV1, RouteTargetTypeV1, VLANTypeV1
    from netbox.graphql.types_v1 import ContentTypeTypeV1
    from tenancy.graphql.types_v1 import TenantTypeV1
    from virtualization.graphql.types_v1 import VMInterfaceTypeV1

__all__ = (
    'IKEPolicyTypeV1',
    'IKEProposalTypeV1',
    'IPSecPolicyTypeV1',
    'IPSecProfileTypeV1',
    'IPSecProposalTypeV1',
    'L2VPNTypeV1',
    'L2VPNTerminationTypeV1',
    'TunnelGroupTypeV1',
    'TunnelTerminationTypeV1',
    'TunnelTypeV1',
)


@strawberry_django.type(
    models.TunnelGroup,
    fields='__all__',
    filters=TunnelGroupFilterV1,
    pagination=True
)
class TunnelGroupTypeV1(ContactsMixinV1, OrganizationalObjectTypeV1):

    tunnels: List[Annotated["TunnelTypeV1", strawberry.lazy('vpn.graphql.types_v1')]]


@strawberry_django.type(
    models.TunnelTermination,
    fields='__all__',
    filters=TunnelTerminationFilterV1,
    pagination=True
)
class TunnelTerminationTypeV1(CustomFieldsMixinV1, TagsMixinV1, ObjectTypeV1):
    tunnel: Annotated["TunnelTypeV1", strawberry.lazy('vpn.graphql.types_v1')]
    termination_type: Annotated["ContentTypeTypeV1", strawberry.lazy('netbox.graphql.types_v1')] | None
    outside_ip: Annotated["IPAddressTypeV1", strawberry.lazy('ipam.graphql.types_v1')] | None


@strawberry_django.type(
    models.Tunnel,
    fields='__all__',
    filters=TunnelFilterV1,
    pagination=True
)
class TunnelTypeV1(ContactsMixinV1, PrimaryObjectTypeV1):
    group: Annotated["TunnelGroupTypeV1", strawberry.lazy('vpn.graphql.types_v1')] | None
    ipsec_profile: Annotated["IPSecProfileTypeV1", strawberry.lazy('vpn.graphql.types_v1')] | None
    tenant: Annotated["TenantTypeV1", strawberry.lazy('tenancy.graphql.types_v1')] | None

    terminations: List[Annotated["TunnelTerminationTypeV1", strawberry.lazy('vpn.graphql.types_v1')]]


@strawberry_django.type(
    models.IKEProposal,
    fields='__all__',
    filters=IKEProposalFilterV1,
    pagination=True
)
class IKEProposalTypeV1(PrimaryObjectTypeV1):
    ike_policies: List[Annotated["IKEPolicyTypeV1", strawberry.lazy('vpn.graphql.types_v1')]]


@strawberry_django.type(
    models.IKEPolicy,
    fields='__all__',
    filters=IKEPolicyFilterV1,
    pagination=True
)
class IKEPolicyTypeV1(OrganizationalObjectTypeV1):

    proposals: List[Annotated["IKEProposalTypeV1", strawberry.lazy('vpn.graphql.types_v1')]]
    ipsec_profiles: List[Annotated["IPSecProfileTypeV1", strawberry.lazy('vpn.graphql.types_v1')]]


@strawberry_django.type(
    models.IPSecProposal,
    fields='__all__',
    filters=IPSecProposalFilterV1,
    pagination=True
)
class IPSecProposalTypeV1(PrimaryObjectTypeV1):

    ipsec_policies: List[Annotated["IPSecPolicyTypeV1", strawberry.lazy('vpn.graphql.types_v1')]]


@strawberry_django.type(
    models.IPSecPolicy,
    fields='__all__',
    filters=IPSecPolicyFilterV1,
    pagination=True
)
class IPSecPolicyTypeV1(OrganizationalObjectTypeV1):

    proposals: List[Annotated["IPSecProposalTypeV1", strawberry.lazy('vpn.graphql.types_v1')]]
    ipsec_profiles: List[Annotated["IPSecProfileTypeV1", strawberry.lazy('vpn.graphql.types_v1')]]


@strawberry_django.type(
    models.IPSecProfile,
    fields='__all__',
    filters=IPSecProfileFilterV1,
    pagination=True
)
class IPSecProfileTypeV1(OrganizationalObjectTypeV1):
    ike_policy: Annotated["IKEPolicyTypeV1", strawberry.lazy('vpn.graphql.types_v1')]
    ipsec_policy: Annotated["IPSecPolicyTypeV1", strawberry.lazy('vpn.graphql.types_v1')]

    tunnels: List[Annotated["TunnelTypeV1", strawberry.lazy('vpn.graphql.types_v1')]]


@strawberry_django.type(
    models.L2VPN,
    fields='__all__',
    filters=L2VPNFilterV1,
    pagination=True
)
class L2VPNTypeV1(ContactsMixinV1, PrimaryObjectTypeV1):
    tenant: Annotated["TenantTypeV1", strawberry.lazy('tenancy.graphql.types_v1')] | None

    export_targets: List[Annotated["RouteTargetTypeV1", strawberry.lazy('ipam.graphql.types_v1')]]
    terminations: List[Annotated["L2VPNTerminationTypeV1", strawberry.lazy('vpn.graphql.types_v1')]]
    import_targets: List[Annotated["RouteTargetTypeV1", strawberry.lazy('ipam.graphql.types_v1')]]


@strawberry_django.type(
    models.L2VPNTermination,
    exclude=['assigned_object_type', 'assigned_object_id'],
    filters=L2VPNTerminationFilterV1,
    pagination=True
)
class L2VPNTerminationTypeV1(NetBoxObjectTypeV1):
    l2vpn: Annotated["L2VPNTypeV1", strawberry.lazy('vpn.graphql.types_v1')]

    @strawberry_django.field
    def assigned_object(self) -> Annotated[Union[
        Annotated["InterfaceTypeV1", strawberry.lazy('dcim.graphql.types_v1')],
        Annotated["VLANTypeV1", strawberry.lazy('ipam.graphql.types_v1')],
        Annotated["VMInterfaceTypeV1", strawberry.lazy('virtualization.graphql.types_v1')],
    ], strawberry.union("L2VPNAssignmentTypeV1")]:
        return self.assigned_object
