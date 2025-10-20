from typing import List

import strawberry
import strawberry_django
from strawberry_django.pagination import OffsetPaginated

from .types import *


@strawberry.type(name="Query")
class CircuitsQueryOld:
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


@strawberry.type(name="Query")
class CircuitsQuery:
    circuit: CircuitType = strawberry_django.field()
    circuit_list: OffsetPaginated[CircuitType] = strawberry_django.offset_paginated()

    circuit_termination: CircuitTerminationType = strawberry_django.field()
    circuit_termination_list: OffsetPaginated[CircuitTerminationType] = strawberry_django.offset_paginated()

    circuit_type: CircuitTypeType = strawberry_django.field()
    circuit_type_list: OffsetPaginated[CircuitTypeType] = strawberry_django.offset_paginated()

    circuit_group: CircuitGroupType = strawberry_django.field()
    circuit_group_list: OffsetPaginated[CircuitGroupType] = strawberry_django.offset_paginated()

    circuit_group_assignment: CircuitGroupAssignmentType = strawberry_django.field()
    circuit_group_assignment_list: OffsetPaginated[CircuitGroupAssignmentType] = strawberry_django.offset_paginated()

    provider: ProviderType = strawberry_django.field()
    provider_list: OffsetPaginated[ProviderType] = strawberry_django.offset_paginated()

    provider_account: ProviderAccountType = strawberry_django.field()
    provider_account_list: OffsetPaginated[ProviderAccountType] = strawberry_django.offset_paginated()

    provider_network: ProviderNetworkType = strawberry_django.field()
    provider_network_list: OffsetPaginated[ProviderNetworkType] = strawberry_django.offset_paginated()

    virtual_circuit: VirtualCircuitType = strawberry_django.field()
    virtual_circuit_list: OffsetPaginated[VirtualCircuitType] = strawberry_django.offset_paginated()

    virtual_circuit_termination: VirtualCircuitTerminationType = strawberry_django.field()
    virtual_circuit_termination_list: OffsetPaginated[VirtualCircuitTerminationType] = (
        strawberry_django.offset_paginated()
    )

    virtual_circuit_type: VirtualCircuitTypeType = strawberry_django.field()
    virtual_circuit_type_list: OffsetPaginated[VirtualCircuitTypeType] = strawberry_django.offset_paginated()
