from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers

from circuits.models import *
from netbox.api.fields import RelatedObjectCountField
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
    display_url = serializers.HyperlinkedIdentityField(view_name='circuits:providernetwork')

    class Meta:
        model = ProviderNetwork
        fields = ['id', 'url', 'display_url', 'display', 'name']


#
# Providers
#

@extend_schema_serializer(
    exclude_fields=('circuit_count',),
)
class NestedProviderSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='circuits-api:provider-detail')
    display_url = serializers.HyperlinkedIdentityField(view_name='circuits:provider')
    circuit_count = RelatedObjectCountField('circuits')

    class Meta:
        model = Provider
        fields = ['id', 'url', 'display_url', 'display', 'name', 'slug', 'circuit_count']


#
# Provider Accounts
#

class NestedProviderAccountSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='circuits-api:provideraccount-detail')
    display_url = serializers.HyperlinkedIdentityField(view_name='circuits:provideraccount')

    class Meta:
        model = ProviderAccount
        fields = ['id', 'url', 'display_url', 'display', 'name', 'account']


#
# Circuits
#

@extend_schema_serializer(
    exclude_fields=('circuit_count',),
)
class NestedCircuitTypeSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='circuits-api:circuittype-detail')
    display_url = serializers.HyperlinkedIdentityField(view_name='circuits:circuittype')
    circuit_count = RelatedObjectCountField('circuits')

    class Meta:
        model = CircuitType
        fields = ['id', 'url', 'display_url', 'display', 'name', 'slug', 'circuit_count']


class NestedCircuitSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='circuits-api:circuit-detail')
    display_url = serializers.HyperlinkedIdentityField(view_name='circuits:circuit')

    class Meta:
        model = Circuit
        fields = ['id', 'url', 'display_url', 'display', 'cid']


class NestedCircuitTerminationSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='circuits-api:circuittermination-detail')
    display_url = serializers.HyperlinkedIdentityField(view_name='circuits:circuittermination')
    circuit = NestedCircuitSerializer()

    class Meta:
        model = CircuitTermination
        fields = ['id', 'url', 'display_url', 'display', 'circuit', 'term_side', 'cable', '_occupied']
