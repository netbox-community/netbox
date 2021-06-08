import graphene

from netbox.graphql.fields import ObjectField, ObjectListField
from .types import *


class CircuitsQuery(graphene.ObjectType):
    circuit = ObjectField(CircuitType)
    circuits = ObjectListField(CircuitType)

    circuit_termination = ObjectField(CircuitTerminationType)
    circuit_terminations = ObjectListField(CircuitTerminationType)

    circuit_type = ObjectField(CircuitTypeType)
    circuit_types = ObjectListField(CircuitTypeType)

    provider = ObjectField(ProviderType)
    providers = ObjectListField(ProviderType)

    provider_network = ObjectField(ProviderNetworkType)
    provider_networks = ObjectListField(ProviderNetworkType)
