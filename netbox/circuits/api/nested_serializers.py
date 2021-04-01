from rest_framework import serializers

from circuits.models import *
from netbox.api import WritableNestedSerializer

__all__ = [
    'NestedCircuitSerializer',
    'NestedCircuitTerminationSerializer',
    'NestedCircuitTypeSerializer',
    'NestedProviderNetworkSerializer',
    'NestedProviderSerializer',
]


#
# Provider networks
#

class NestedProviderNetworkSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='circuits-api:providernetwork-detail')

    class Meta:
        model = Provider
        fields = ['id', 'url', 'display', 'name']


#
# Providers
#

class NestedProviderSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='circuits-api:provider-detail')
    circuit_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Provider
        fields = ['id', 'url', 'display', 'name', 'slug', 'circuit_count']


#
# Circuits
#

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
