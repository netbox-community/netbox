from typing import Annotated, List

import strawberry
import strawberry_django

from circuits import models
from dcim.graphql.mixins import CabledObjectMixin
from extras.graphql.mixins import ContactsMixin, CustomFieldsMixin, TagsMixin
from netbox.graphql.types import BaseObjectType, NetBoxObjectType, ObjectType, OrganizationalObjectType
from tenancy.graphql.types import TenantType
from .filters import *

__all__ = (
    'CircuitTerminationType',
    'CircuitType',
    'CircuitGroupAssignmentType',
    'CircuitGroupType',
    'CircuitTypeType',
    'ProviderType',
    'ProviderAccountType',
    'ProviderNetworkType',
)


@strawberry_django.type(
    models.Provider,
    fields='__all__',
    filters=ProviderFilter
)
class ProviderType(NetBoxObjectType, ContactsMixin):

    networks: List[Annotated["ProviderNetworkType", strawberry.lazy('circuits.graphql.types')]]
    circuits: List[Annotated["CircuitType", strawberry.lazy('circuits.graphql.types')]]
    asns: List[Annotated["ASNType", strawberry.lazy('ipam.graphql.types')]]
    accounts: List[Annotated["ProviderAccountType", strawberry.lazy('circuits.graphql.types')]]


@strawberry_django.type(
    models.ProviderAccount,
    fields='__all__',
    filters=ProviderAccountFilter
)
class ProviderAccountType(NetBoxObjectType):
    provider: Annotated["ProviderType", strawberry.lazy('circuits.graphql.types')]

    circuits: List[Annotated["CircuitType", strawberry.lazy('circuits.graphql.types')]]


@strawberry_django.type(
    models.ProviderNetwork,
    fields='__all__',
    filters=ProviderNetworkFilter
)
class ProviderNetworkType(NetBoxObjectType):
    provider: Annotated["ProviderType", strawberry.lazy('circuits.graphql.types')]

    circuit_terminations: List[Annotated["CircuitTerminationType", strawberry.lazy('circuits.graphql.types')]]


@strawberry_django.type(
    models.CircuitTermination,
    fields='__all__',
    filters=CircuitTerminationFilter
)
class CircuitTerminationType(CustomFieldsMixin, TagsMixin, CabledObjectMixin, ObjectType):
    circuit: Annotated["CircuitType", strawberry.lazy('circuits.graphql.types')]
    provider_network: Annotated["ProviderNetworkType", strawberry.lazy('circuits.graphql.types')] | None
    site: Annotated["SiteType", strawberry.lazy('dcim.graphql.types')] | None


@strawberry_django.type(
    models.CircuitType,
    fields='__all__',
    filters=CircuitTypeFilter
)
class CircuitTypeType(OrganizationalObjectType):
    color: str

    circuits: List[Annotated["CircuitType", strawberry.lazy('circuits.graphql.types')]]


@strawberry_django.type(
    models.Circuit,
    fields='__all__',
    filters=CircuitFilter
)
class CircuitType(NetBoxObjectType, ContactsMixin):
    provider: ProviderType
    provider_account: ProviderAccountType | None
    termination_a: CircuitTerminationType | None
    termination_z: CircuitTerminationType | None
    type: CircuitTypeType
    tenant: TenantType | None

    terminations: List[CircuitTerminationType]


@strawberry_django.type(
    models.CircuitGroup,
    fields='__all__',
    filters=CircuitGroupFilter
)
class CircuitGroupType(OrganizationalObjectType):
    tenant: TenantType | None


@strawberry_django.type(
    models.CircuitGroupAssignment,
    fields='__all__',
    filters=CircuitGroupAssignmentFilter
)
class CircuitGroupAssignmentType(TagsMixin, BaseObjectType):
    group: Annotated["CircuitGroupType", strawberry.lazy('circuits.graphql.types')]
    circuit: Annotated["CircuitType", strawberry.lazy('circuits.graphql.types')]
