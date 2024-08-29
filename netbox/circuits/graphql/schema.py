from typing import List

import strawberry
import strawberry_django

from .types import *


@strawberry.type(name="Query")
class CircuitsQuery:
    circuit: CircuitType = strawberry_django.field()
    circuit_list: List[CircuitType] = strawberry_django.field()

    circuit_termination: CircuitTerminationType = strawberry_django.field()
    circuit_termination_list: List[CircuitTerminationType] = strawberry_django.field()

    circuit_type: CircuitTypeType = strawberry_django.field()
    circuit_type_list: List[CircuitTypeType] = strawberry_django.field()

    provider: ProviderType = strawberry_django.field()
    provider_list: List[ProviderType] = strawberry_django.field()

    provider_account: ProviderAccountType = strawberry_django.field()
    provider_account_list: List[ProviderAccountType] = strawberry_django.field()

    provider_network: ProviderNetworkType = strawberry_django.field()
    provider_network_list: List[ProviderNetworkType] = strawberry_django.field()
