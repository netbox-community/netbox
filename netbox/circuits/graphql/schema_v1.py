from typing import List

import strawberry
import strawberry_django

from .types_v1 import *


@strawberry.type(name="Query")
class CircuitsQueryV1:
    circuit: CircuitTypeV1 = strawberry_django.field()
    circuit_list: List[CircuitTypeV1] = strawberry_django.field()

    circuit_termination: CircuitTerminationTypeV1 = strawberry_django.field()
    circuit_termination_list: List[CircuitTerminationTypeV1] = strawberry_django.field()

    circuit_type: CircuitTypeTypeV1 = strawberry_django.field()
    circuit_type_list: List[CircuitTypeTypeV1] = strawberry_django.field()

    circuit_group: CircuitGroupTypeV1 = strawberry_django.field()
    circuit_group_list: List[CircuitGroupTypeV1] = strawberry_django.field()

    circuit_group_assignment: CircuitGroupAssignmentTypeV1 = strawberry_django.field()
    circuit_group_assignment_list: List[CircuitGroupAssignmentTypeV1] = strawberry_django.field()

    provider: ProviderTypeV1 = strawberry_django.field()
    provider_list: List[ProviderTypeV1] = strawberry_django.field()

    provider_account: ProviderAccountTypeV1 = strawberry_django.field()
    provider_account_list: List[ProviderAccountTypeV1] = strawberry_django.field()

    provider_network: ProviderNetworkTypeV1 = strawberry_django.field()
    provider_network_list: List[ProviderNetworkTypeV1] = strawberry_django.field()

    virtual_circuit: VirtualCircuitTypeV1 = strawberry_django.field()
    virtual_circuit_list: List[VirtualCircuitTypeV1] = strawberry_django.field()

    virtual_circuit_termination: VirtualCircuitTerminationTypeV1 = strawberry_django.field()
    virtual_circuit_termination_list: List[VirtualCircuitTerminationTypeV1] = strawberry_django.field()

    virtual_circuit_type: VirtualCircuitTypeTypeV1 = strawberry_django.field()
    virtual_circuit_type_list: List[VirtualCircuitTypeTypeV1] = strawberry_django.field()
