from drf_spectacular.utils import extend_schema_field, extend_schema_serializer
from drf_spectacular.types import OpenApiTypes
from rest_framework import serializers

from circuits.models import *
from netbox.api.serializers import WritableNestedSerializer

__all__ = [
    'NestedCircuitSerializer',
    'NestedCircuitTerminationSerializer',
    'NestedCircuitTypeSerializer',
    'NestedProviderNetworkSerializer',
    'NestedProviderSerializer',
    'NestedProviderAccountSerializer',
]


#
# Provider networks
#

class NestedProviderNetworkSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='circuits-api:providernetwork-detail')

    class Meta:
        model = ProviderNetwork
        fields = ['id', 'url', 'display', 'name']


#
# Providers
#

@extend_schema_serializer(
    exclude_fields=('circuit_count',),
)
class NestedProviderSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='circuits-api:provider-detail')
    circuit_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Provider
        fields = ['id', 'url', 'display', 'name', 'slug', 'circuit_count']


#
# Provider Accounts
#

class NestedProviderAccountSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='circuits-api:provideraccount-detail')

    class Meta:
        model = ProviderAccount
        fields = ['id', 'url', 'display', 'name', 'account']


#
# Circuits
#

@extend_schema_serializer(
    exclude_fields=('circuit_count',),
)
class NestedCircuitTypeSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='circuits-api:circuittype-detail')
    circuit_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = CircuitType
        fields = ['id', 'url', 'display', 'name', 'slug', 'circuit_count']


class NestedCircuitSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='circuits-api:circuit-detail')

    class Meta:
        model = Circuit
        fields = ['id', 'url', 'display', 'cid']


class NestedCircuitTerminationSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='circuits-api:circuittermination-detail')
    circuit = NestedCircuitSerializer()

    class Meta:
        model = CircuitTermination
        fields = ['id', 'url', 'display', 'circuit', 'term_side', 'cable', '_occupied']
