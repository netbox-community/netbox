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

    circuit_group: CircuitGroupType = strawberry_django.field()
    circuit_group_list: List[CircuitGroupType] = strawberry_django.field()

    circuit_group_assignment: CircuitGroupAssignmentType = strawberry_django.field()
    circuit_group_assignment_list: List[CircuitGroupAssignmentType] = strawberry_django.field()

    provider: ProviderType = strawberry_django.field()
    provider_list: List[ProviderType] = strawberry_django.field()

    provider_account: ProviderAccountType = strawberry_django.field()
    provider_account_list: List[ProviderAccountType] = strawberry_django.field()

    provider_network: ProviderNetworkType = strawberry_django.field()
    provider_network_list: List[ProviderNetworkType] = strawberry_django.field()

    virtual_circuit: VirtualCircuitType = strawberry_django.field()
    virtual_circuit_list: List[VirtualCircuitType] = strawberry_django.field()

    virtual_circuit_termination: VirtualCircuitTerminationType = strawberry_django.field()
    virtual_circuit_termination_list: List[VirtualCircuitTerminationType] = strawberry_django.field()

    virtual_circuit_type: VirtualCircuitTypeType = strawberry_django.field()
    virtual_circuit_type_list: List[VirtualCircuitTypeType] = strawberry_django.field()
