import graphene

from netbox.graphql.fields import ObjectField, ObjectListField
from .types import *


class CircuitsQuery(graphene.ObjectType):
    circuit = ObjectField(CircuitType)
    circuit_list = ObjectListField(CircuitType)

    circuit_termination = ObjectField(CircuitTerminationType)
    circuit_termination_list = ObjectListField(CircuitTerminationType)

    circuit_type = ObjectField(CircuitTypeType)
    circuit_type_list = ObjectListField(CircuitTypeType)

    provider = ObjectField(ProviderType)
    provider_list = ObjectListField(ProviderType)

    provider_network = ObjectField(ProviderNetworkType)
    provider_network_list = ObjectListField(ProviderNetworkType)
