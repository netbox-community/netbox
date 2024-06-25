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
    circuit_count = RelatedObjectCountField('circuits')

    class Meta:
        model = Provider
        fields = ['id', 'url', 'display_url', 'display', 'name', 'slug', 'circuit_count']


#
# Provider Accounts
#

class NestedProviderAccountSerializer(WritableNestedSerializer):

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
    circuit_count = RelatedObjectCountField('circuits')

    class Meta:
        model = CircuitType
        fields = ['id', 'url', 'display_url', 'display', 'name', 'slug', 'circuit_count']


class NestedCircuitSerializer(WritableNestedSerializer):

    class Meta:
        model = Circuit
        fields = ['id', 'url', 'display_url', 'display', 'cid']


class NestedCircuitTerminationSerializer(WritableNestedSerializer):
    circuit = NestedCircuitSerializer()

    class Meta:
        model = CircuitTermination
        fields = ['id', 'url', 'display_url', 'display', 'circuit', 'term_side', 'cable', '_occupied']
