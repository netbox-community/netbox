from circuits import filtersets, models
from netbox.graphql.types import BaseObjectType, ObjectType, PrimaryObjectType

__all__ = (
    'CircuitTerminationType',
    'CircuitType',
    'CircuitTypeType',
    'ProviderType',
    'ProviderNetworkType',
)


class CircuitTerminationType(BaseObjectType):

    class Meta:
        model = models.CircuitTermination
        fields = '__all__'
        filterset_class = filtersets.CircuitTerminationFilterSet


class CircuitType(PrimaryObjectType):

    class Meta:
        model = models.Circuit
        fields = '__all__'
        filterset_class = filtersets.CircuitFilterSet


class CircuitTypeType(ObjectType):

    class Meta:
        model = models.CircuitType
        fields = '__all__'
        filterset_class = filtersets.CircuitTypeFilterSet


class ProviderType(PrimaryObjectType):

    class Meta:
        model = models.Provider
        fields = '__all__'
        filterset_class = filtersets.ProviderFilterSet


class ProviderNetworkType(PrimaryObjectType):

    class Meta:
        model = models.ProviderNetwork
        fields = '__all__'
        filterset_class = filtersets.ProviderNetworkFilterSet
