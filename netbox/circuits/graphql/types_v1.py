from typing import Annotated, List, TYPE_CHECKING, Union

import strawberry
import strawberry_django

from circuits import models
from dcim.graphql.mixins_v1 import CabledObjectMixinV1
from extras.graphql.mixins_v1 import ContactsMixinV1, CustomFieldsMixinV1, TagsMixinV1
from netbox.graphql.types_v1 import (
    BaseObjectTypeV1, ObjectTypeV1, OrganizationalObjectTypeV1, PrimaryObjectTypeV1
)
from tenancy.graphql.types_v1 import TenantTypeV1
from .filters_v1 import *

if TYPE_CHECKING:
    from dcim.graphql.types_v1 import InterfaceTypeV1, LocationTypeV1, RegionTypeV1, SiteGroupTypeV1, SiteTypeV1
    from ipam.graphql.types_v1 import ASNTypeV1

__all__ = (
    'CircuitGroupAssignmentTypeV1',
    'CircuitGroupTypeV1',
    'CircuitTerminationTypeV1',
    'CircuitTypeV1',
    'CircuitTypeTypeV1',
    'ProviderTypeV1',
    'ProviderAccountTypeV1',
    'ProviderNetworkTypeV1',
    'VirtualCircuitTerminationTypeV1',
    'VirtualCircuitTypeV1',
    'VirtualCircuitTypeTypeV1',
)


@strawberry_django.type(
    models.Provider,
    fields='__all__',
    filters=ProviderFilterV1,
    pagination=True
)
class ProviderTypeV1(ContactsMixinV1, PrimaryObjectTypeV1):

    networks: List[Annotated["ProviderNetworkTypeV1", strawberry.lazy('circuits.graphql.types_v1')]]
    circuits: List[Annotated["CircuitTypeV1", strawberry.lazy('circuits.graphql.types_v1')]]
    asns: List[Annotated["ASNTypeV1", strawberry.lazy('ipam.graphql.types_v1')]]
    accounts: List[Annotated["ProviderAccountTypeV1", strawberry.lazy('circuits.graphql.types_v1')]]


@strawberry_django.type(
    models.ProviderAccount,
    fields='__all__',
    filters=ProviderAccountFilterV1,
    pagination=True
)
class ProviderAccountTypeV1(ContactsMixinV1, PrimaryObjectTypeV1):
    provider: Annotated["ProviderTypeV1", strawberry.lazy('circuits.graphql.types_v1')]

    circuits: List[Annotated["CircuitTypeV1", strawberry.lazy('circuits.graphql.types_v1')]]


@strawberry_django.type(
    models.ProviderNetwork,
    fields='__all__',
    filters=ProviderNetworkFilterV1,
    pagination=True
)
class ProviderNetworkTypeV1(PrimaryObjectTypeV1):
    provider: Annotated["ProviderTypeV1", strawberry.lazy('circuits.graphql.types_v1')]

    circuit_terminations: List[Annotated["CircuitTerminationTypeV1", strawberry.lazy('circuits.graphql.types_v1')]]


@strawberry_django.type(
    models.CircuitTermination,
    exclude=['termination_type', 'termination_id', '_location', '_region', '_site', '_site_group', '_provider_network'],
    filters=CircuitTerminationFilterV1,
    pagination=True
)
class CircuitTerminationTypeV1(CustomFieldsMixinV1, TagsMixinV1, CabledObjectMixinV1, ObjectTypeV1):
    circuit: Annotated["CircuitTypeV1", strawberry.lazy('circuits.graphql.types_v1')]

    @strawberry_django.field
    def termination(self) -> Annotated[Union[
        Annotated["LocationTypeV1", strawberry.lazy('dcim.graphql.types_v1')],
        Annotated["RegionTypeV1", strawberry.lazy('dcim.graphql.types_v1')],
        Annotated["SiteGroupTypeV1", strawberry.lazy('dcim.graphql.types_v1')],
        Annotated["SiteTypeV1", strawberry.lazy('dcim.graphql.types_v1')],
        Annotated["ProviderNetworkTypeV1", strawberry.lazy('circuits.graphql.types_v1')],
    ], strawberry.union("CircuitTerminationTerminationTypeV1")] | None:
        return self.termination


@strawberry_django.type(
    models.CircuitType,
    fields='__all__',
    filters=CircuitTypeFilterV1,
    pagination=True
)
class CircuitTypeTypeV1(OrganizationalObjectTypeV1):
    color: str

    circuits: List[Annotated["CircuitTypeV1", strawberry.lazy('circuits.graphql.types_v1')]]


@strawberry_django.type(
    models.Circuit,
    fields='__all__',
    filters=CircuitFilterV1,
    pagination=True
)
class CircuitTypeV1(PrimaryObjectTypeV1, ContactsMixinV1):
    provider: ProviderTypeV1
    provider_account: ProviderAccountTypeV1 | None
    termination_a: CircuitTerminationTypeV1 | None
    termination_z: CircuitTerminationTypeV1 | None
    type: CircuitTypeTypeV1
    tenant: TenantTypeV1 | None

    terminations: List[CircuitTerminationTypeV1]


@strawberry_django.type(
    models.CircuitGroup,
    fields='__all__',
    filters=CircuitGroupFilterV1,
    pagination=True
)
class CircuitGroupTypeV1(OrganizationalObjectTypeV1):
    tenant: TenantTypeV1 | None


@strawberry_django.type(
    models.CircuitGroupAssignment,
    exclude=['member_type', 'member_id'],
    filters=CircuitGroupAssignmentFilterV1,
    pagination=True
)
class CircuitGroupAssignmentTypeV1(TagsMixinV1, BaseObjectTypeV1):
    group: Annotated["CircuitGroupTypeV1", strawberry.lazy('circuits.graphql.types_v1')]

    @strawberry_django.field
    def member(self) -> Annotated[Union[
        Annotated["CircuitTypeV1", strawberry.lazy('circuits.graphql.types_v1')],
        Annotated["VirtualCircuitTypeV1", strawberry.lazy('circuits.graphql.types_v1')],
    ], strawberry.union("CircuitGroupAssignmentMemberTypeV1")] | None:
        return self.member


@strawberry_django.type(
    models.VirtualCircuitType,
    fields='__all__',
    filters=VirtualCircuitTypeFilterV1,
    pagination=True
)
class VirtualCircuitTypeTypeV1(OrganizationalObjectTypeV1):
    color: str

    virtual_circuits: List[Annotated["VirtualCircuitTypeV1", strawberry.lazy('circuits.graphql.types_v1')]]


@strawberry_django.type(
    models.VirtualCircuitTermination,
    fields='__all__',
    filters=VirtualCircuitTerminationFilterV1,
    pagination=True
)
class VirtualCircuitTerminationTypeV1(CustomFieldsMixinV1, TagsMixinV1, ObjectTypeV1):
    virtual_circuit: Annotated[
        "VirtualCircuitTypeV1",
        strawberry.lazy('circuits.graphql.types_v1')
    ] = strawberry_django.field(select_related=["virtual_circuit"])
    interface: Annotated[
        "InterfaceTypeV1",
        strawberry.lazy('dcim.graphql.types_v1')
    ] = strawberry_django.field(select_related=["interface"])


@strawberry_django.type(
    models.VirtualCircuit,
    fields='__all__',
    filters=VirtualCircuitFilterV1,
    pagination=True
)
class VirtualCircuitTypeV1(PrimaryObjectTypeV1):
    provider_network: ProviderNetworkTypeV1 = strawberry_django.field(select_related=["provider_network"])
    provider_account: ProviderAccountTypeV1 | None
    type: Annotated["VirtualCircuitTypeTypeV1", strawberry.lazy('circuits.graphql.types_v1')] = strawberry_django.field(
        select_related=["type"]
    )
    tenant: TenantTypeV1 | None

    terminations: List[VirtualCircuitTerminationTypeV1]
