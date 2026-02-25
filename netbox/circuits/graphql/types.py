from typing import TYPE_CHECKING, Annotated

import strawberry
import strawberry_django

from circuits import models
from dcim.graphql.mixins import CabledObjectMixin
from extras.graphql.mixins import ContactsMixin, CustomFieldsMixin, TagsMixin
from netbox.graphql.types import BaseObjectType, ObjectType, OrganizationalObjectType, PrimaryObjectType
from tenancy.graphql.types import TenantType

from .filters import *

if TYPE_CHECKING:
    from dcim.graphql.types import InterfaceType, LocationType, RegionType, SiteGroupType, SiteType
    from ipam.graphql.types import ASNType

__all__ = (
    'CircuitGroupAssignmentType',
    'CircuitGroupType',
    'CircuitTerminationType',
    'CircuitType',
    'CircuitTypeType',
    'ProviderAccountType',
    'ProviderNetworkType',
    'ProviderType',
    'VirtualCircuitTerminationType',
    'VirtualCircuitType',
    'VirtualCircuitTypeType',
)


@strawberry_django.type(
    models.Provider,
    fields='__all__',
    filters=ProviderFilter,
    pagination=True
)
class ProviderType(ContactsMixin, PrimaryObjectType):
    networks: list[Annotated["ProviderNetworkType", strawberry.lazy('circuits.graphql.types')]]
    circuits: list[Annotated["CircuitType", strawberry.lazy('circuits.graphql.types')]]
    asns: list[Annotated["ASNType", strawberry.lazy('ipam.graphql.types')]]
    accounts: list[Annotated["ProviderAccountType", strawberry.lazy('circuits.graphql.types')]]


@strawberry_django.type(
    models.ProviderAccount,
    fields='__all__',
    filters=ProviderAccountFilter,
    pagination=True
)
class ProviderAccountType(ContactsMixin, PrimaryObjectType):
    provider: Annotated["ProviderType", strawberry.lazy('circuits.graphql.types')]
    circuits: list[Annotated["CircuitType", strawberry.lazy('circuits.graphql.types')]]


@strawberry_django.type(
    models.ProviderNetwork,
    fields='__all__',
    filters=ProviderNetworkFilter,
    pagination=True
)
class ProviderNetworkType(PrimaryObjectType):
    provider: Annotated["ProviderType", strawberry.lazy('circuits.graphql.types')]
    circuit_terminations: list[Annotated["CircuitTerminationType", strawberry.lazy('circuits.graphql.types')]]


@strawberry_django.type(
    models.CircuitTermination,
    exclude=['termination_type', 'termination_id', '_location', '_region', '_site', '_site_group', '_provider_network'],
    filters=CircuitTerminationFilter,
    pagination=True
)
class CircuitTerminationType(CustomFieldsMixin, TagsMixin, CabledObjectMixin, ObjectType):
    circuit: Annotated['CircuitType', strawberry.lazy('circuits.graphql.types')]

    @strawberry_django.field
    def termination(self) -> Annotated[
        Annotated['LocationType', strawberry.lazy('dcim.graphql.types')]
        | Annotated['RegionType', strawberry.lazy('dcim.graphql.types')]
        | Annotated['SiteGroupType', strawberry.lazy('dcim.graphql.types')]
        | Annotated['SiteType', strawberry.lazy('dcim.graphql.types')]
        | Annotated['ProviderNetworkType', strawberry.lazy('circuits.graphql.types')],
        strawberry.union('CircuitTerminationTerminationType'),
    ] | None:
        return self.termination


@strawberry_django.type(
    models.CircuitType,
    fields='__all__',
    filters=CircuitTypeFilter,
    pagination=True
)
class CircuitTypeType(OrganizationalObjectType):
    color: str

    circuits: list[Annotated["CircuitType", strawberry.lazy('circuits.graphql.types')]]


@strawberry_django.type(
    models.Circuit,
    fields='__all__',
    filters=CircuitFilter,
    pagination=True
)
class CircuitType(PrimaryObjectType, ContactsMixin):
    provider: ProviderType
    provider_account: ProviderAccountType | None
    termination_a: CircuitTerminationType | None
    termination_z: CircuitTerminationType | None
    type: CircuitTypeType
    tenant: TenantType | None
    terminations: list[CircuitTerminationType]


@strawberry_django.type(
    models.CircuitGroup,
    fields='__all__',
    filters=CircuitGroupFilter,
    pagination=True
)
class CircuitGroupType(OrganizationalObjectType):
    tenant: TenantType | None


@strawberry_django.type(
    models.CircuitGroupAssignment,
    exclude=['member_type', 'member_id'],
    filters=CircuitGroupAssignmentFilter,
    pagination=True
)
class CircuitGroupAssignmentType(TagsMixin, BaseObjectType):
    group: Annotated['CircuitGroupType', strawberry.lazy('circuits.graphql.types')]

    @strawberry_django.field
    def member(self) -> Annotated[
        Annotated['CircuitType', strawberry.lazy('circuits.graphql.types')]
        | Annotated['VirtualCircuitType', strawberry.lazy('circuits.graphql.types')],
        strawberry.union('CircuitGroupAssignmentMemberType'),
    ] | None:
        return self.member


@strawberry_django.type(
    models.VirtualCircuitType,
    fields='__all__',
    filters=VirtualCircuitTypeFilter,
    pagination=True
)
class VirtualCircuitTypeType(OrganizationalObjectType):
    color: str

    virtual_circuits: list[Annotated["VirtualCircuitType", strawberry.lazy('circuits.graphql.types')]]


@strawberry_django.type(
    models.VirtualCircuitTermination,
    fields='__all__',
    filters=VirtualCircuitTerminationFilter,
    pagination=True
)
class VirtualCircuitTerminationType(CustomFieldsMixin, TagsMixin, ObjectType):
    virtual_circuit: Annotated[
        "VirtualCircuitType",
        strawberry.lazy('circuits.graphql.types')
    ] = strawberry_django.field(select_related=["virtual_circuit"])
    interface: Annotated[
        "InterfaceType",
        strawberry.lazy('dcim.graphql.types')
    ] = strawberry_django.field(select_related=["interface"])


@strawberry_django.type(
    models.VirtualCircuit,
    fields='__all__',
    filters=VirtualCircuitFilter,
    pagination=True
)
class VirtualCircuitType(ContactsMixin, PrimaryObjectType):
    provider_network: ProviderNetworkType = strawberry_django.field(select_related=["provider_network"])
    provider_account: ProviderAccountType | None
    type: Annotated["VirtualCircuitTypeType", strawberry.lazy('circuits.graphql.types')] = strawberry_django.field(
        select_related=["type"]
    )
    tenant: TenantType | None
    terminations: list[VirtualCircuitTerminationType]
