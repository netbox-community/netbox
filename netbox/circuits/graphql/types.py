from typing import Annotated, List

import strawberry
import strawberry_django

from circuits import models
from dcim.graphql.mixins import CabledObjectMixin
from extras.graphql.mixins import ContactsMixin, CustomFieldsMixin, TagsMixin
from netbox.graphql.types import NetBoxObjectType, ObjectType, OrganizationalObjectType
from tenancy.graphql.types import TenantType
from .filters import *

__all__ = (
    'CircuitTerminationType',
    'CircuitType',
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

    @strawberry_django.field
    def networks(self) -> List[Annotated["ProviderNetworkType", strawberry.lazy('circuits.graphql.types')]]:
        return self.networks.all()

    @strawberry_django.field
    def circuits(self) -> List[Annotated["CircuitType", strawberry.lazy('circuits.graphql.types')]]:
        return self.circuits.all()

    @strawberry_django.field
    def asns(self) -> List[Annotated["ASNType", strawberry.lazy('ipam.graphql.types')]]:
        return self.asns.all()

    @strawberry_django.field
    def accounts(self) -> List[Annotated["ProviderAccountType", strawberry.lazy('circuits.graphql.types')]]:
        return self.accounts.all()


@strawberry_django.type(
    models.ProviderAccount,
    fields='__all__',
    filters=ProviderAccountFilter
)
class ProviderAccountType(NetBoxObjectType):
    provider: Annotated["ProviderType", strawberry.lazy('circuits.graphql.types')]

    @strawberry_django.field
    def circuits(self) -> List[Annotated["CircuitType", strawberry.lazy('circuits.graphql.types')]]:
        return self.circuits.all()


@strawberry_django.type(
    models.ProviderNetwork,
    fields='__all__',
    filters=ProviderNetworkFilter
)
class ProviderNetworkType(NetBoxObjectType):
    provider: Annotated["ProviderType", strawberry.lazy('circuits.graphql.types')]

    @strawberry_django.field
    def circuit_terminations(self) -> List[Annotated["CircuitTerminationType", strawberry.lazy('circuits.graphql.types')]]:
        return self.circuit_terminations.all()


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

    @strawberry_django.field
    def circuits(self) -> List[Annotated["CircuitType", strawberry.lazy('circuits.graphql.types')]]:
        return self.circuits.all()


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

    @strawberry_django.field
    def terminations(self) -> List[CircuitTerminationType]:
        return self.terminations.all()
