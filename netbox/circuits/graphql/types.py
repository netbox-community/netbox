import graphene

from circuits import filtersets, models
from dcim.graphql.mixins import CabledObjectMixin
from extras.graphql.mixins import CustomFieldsMixin, TagsMixin, ContactsMixin
from netbox.graphql.types import ObjectType, OrganizationalObjectType, NetBoxObjectType

__all__ = (
    'CircuitTerminationType',
    'CircuitType',
    'CircuitTypeType',
    'ProviderType',
    'ProviderNetworkType',
)


class CircuitTerminationType(CustomFieldsMixin, TagsMixin, CabledObjectMixin, ObjectType):

    class Meta:
        model = models.CircuitTermination
        fields = '__all__'
        filterset_class = filtersets.CircuitTerminationFilterSet


class CircuitType(NetBoxObjectType, ContactsMixin):
    class Meta:
        model = models.Circuit
        fields = '__all__'
        filterset_class = filtersets.CircuitFilterSet


class CircuitTypeType(OrganizationalObjectType):

    class Meta:
        model = models.CircuitType
        fields = '__all__'
        filterset_class = filtersets.CircuitTypeFilterSet


class ProviderType(NetBoxObjectType, ContactsMixin):

    class Meta:
        model = models.Provider
        fields = '__all__'
        filterset_class = filtersets.ProviderFilterSet


class ProviderNetworkType(NetBoxObjectType):

    class Meta:
        model = models.ProviderNetwork
        fields = '__all__'
        filterset_class = filtersets.ProviderNetworkFilterSet
