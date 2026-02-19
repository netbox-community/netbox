import strawberry
import strawberry_django

from .types import *


@strawberry.type(name="Query")
class CircuitsQuery:
    circuit: CircuitType = strawberry_django.field()
    circuit_list: list[CircuitType] = strawberry_django.field()

    circuit_termination: CircuitTerminationType = strawberry_django.field()
    circuit_termination_list: list[CircuitTerminationType] = strawberry_django.field()

    circuit_type: CircuitTypeType = strawberry_django.field()
    circuit_type_list: list[CircuitTypeType] = strawberry_django.field()

    circuit_group: CircuitGroupType = strawberry_django.field()
    circuit_group_list: list[CircuitGroupType] = strawberry_django.field()

    circuit_group_assignment: CircuitGroupAssignmentType = strawberry_django.field()
    circuit_group_assignment_list: list[CircuitGroupAssignmentType] = strawberry_django.field()

    provider: ProviderType = strawberry_django.field()
    provider_list: list[ProviderType] = strawberry_django.field()

    provider_account: ProviderAccountType = strawberry_django.field()
    provider_account_list: list[ProviderAccountType] = strawberry_django.field()

    provider_network: ProviderNetworkType = strawberry_django.field()
    provider_network_list: list[ProviderNetworkType] = strawberry_django.field()

    virtual_circuit: VirtualCircuitType = strawberry_django.field()
    virtual_circuit_list: list[VirtualCircuitType] = strawberry_django.field()

    virtual_circuit_termination: VirtualCircuitTerminationType = strawberry_django.field()
    virtual_circuit_termination_list: list[VirtualCircuitTerminationType] = strawberry_django.field()

    virtual_circuit_type: VirtualCircuitTypeType = strawberry_django.field()
    virtual_circuit_type_list: list[VirtualCircuitTypeType] = strawberry_django.field()
