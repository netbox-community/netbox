import graphene

from circuits import models
from netbox.graphql.fields import ObjectField, ObjectListField
from .types import *
from utilities.graphql_optimizer import gql_query_optimizer


class CircuitsQuery(graphene.ObjectType):
    circuit = ObjectField(CircuitType)
    circuit_list = ObjectListField(CircuitType)

    def resolve_circuit_list(root, info, **kwargs):
        return gql_query_optimizer(models.Circuit.objects.all(), info)

    circuit_termination = ObjectField(CircuitTerminationType)
    circuit_termination_list = ObjectListField(CircuitTerminationType)

    def resolve_circuit_termination_list(root, info, **kwargs):
        return gql_query_optimizer(models.CircuitTermination.objects.all(), info)

    circuit_type = ObjectField(CircuitTypeType)
    circuit_type_list = ObjectListField(CircuitTypeType)

    def resolve_circuit_type_list(root, info, **kwargs):
        return gql_query_optimizer(models.CircuitType.objects.all(), info)

    provider = ObjectField(ProviderType)
    provider_list = ObjectListField(ProviderType)

    def resolve_provider_list(root, info, **kwargs):
        return gql_query_optimizer(models.Provider.objects.all(), info)

    provider_account = ObjectField(ProviderAccountType)
    provider_account_list = ObjectListField(ProviderAccountType)

    provider_network = ObjectField(ProviderNetworkType)
    provider_network_list = ObjectListField(ProviderNetworkType)

    def resolve_provider_network_list(root, info, **kwargs):
        return gql_query_optimizer(models.ProviderNetwork.objects.all(), info)
