from typing import List
import strawberry
import strawberry_django

from circuits import models
from .types import *


@strawberry.type
class CircuitsQuery:
    @strawberry.field
    def circuit(self, id: int) -> CircuitType:
        return models.Circuit.objects.get(id=id)
    circuit_list: List[CircuitType] = strawberry_django.field()

    @strawberry.field
    def circuit_termination(self, id: int) -> CircuitTerminationType:
        return models.CircuitTermination.objects.get(id=id)
    circuit_termination_list: List[CircuitTerminationType] = strawberry_django.field()

    @strawberry.field
    def circuit_type(self, id: int) -> CircuitTypeType:
        return models.CircuitType.objects.get(id=id)
    circuit_type_list: List[CircuitTypeType] = strawberry_django.field()

    @strawberry.field
    def provider(self, id: int) -> ProviderType:
        return models.Provider.objects.get(id=id)
    provider_list: List[ProviderType] = strawberry_django.field()

    @strawberry.field
    def provider_account(self, id: int) -> ProviderAccountType:
        return models.ProviderAccount.objects.get(id=id)
    provider_account_list: List[ProviderAccountType] = strawberry_django.field()

    @strawberry.field
    def provider_network(self, id: int) -> ProviderNetworkType:
        return models.ProviderNetwork.objects.get(id=id)
    provider_network_list: List[ProviderNetworkType] = strawberry_django.field()
