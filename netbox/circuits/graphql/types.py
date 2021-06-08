from circuits import filtersets, models
from netbox.graphql.types import *

__all__ = (
    'CircuitType',
    'CircuitTerminationType',
    'CircuitTypeType',
    'ProviderType',
    'ProviderNetworkType',
)


#
# Object types
#

class ProviderType(TaggedObjectType):

    class Meta:
        model = models.Provider
        fields = '__all__'
        filterset_class = filtersets.ProviderFilterSet


class ProviderNetworkType(TaggedObjectType):

    class Meta:
        model = models.ProviderNetwork
        fields = '__all__'
        filterset_class = filtersets.ProviderNetworkFilterSet


class CircuitType(TaggedObjectType):

    class Meta:
        model = models.Circuit
        fields = '__all__'
        filterset_class = filtersets.CircuitFilterSet


class CircuitTypeType(ObjectType):

    class Meta:
        model = models.CircuitType
        fields = '__all__'
        filterset_class = filtersets.CircuitTypeFilterSet


class CircuitTerminationType(BaseObjectType):

    class Meta:
        model = models.CircuitTermination
        fields = '__all__'
        filterset_class = filtersets.CircuitTerminationFilterSet
