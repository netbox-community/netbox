from rest_framework import serializers

from circuits.choices import CircuitStatusChoices
from circuits.models import *
from dcim.api.nested_serializers import NestedCableSerializer, NestedSiteSerializer
from dcim.api.serializers import LinkTerminationSerializer
from netbox.api import ChoiceField
from netbox.api.serializers import PrimaryModelSerializer, ValidatedModelSerializer, WritableNestedSerializer
from tenancy.api.nested_serializers import NestedTenantSerializer
from .nested_serializers import *


#
# Providers
#

class ProviderSerializer(PrimaryModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='circuits-api:provider-detail')
    circuit_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Provider
        fields = [
            'id', 'url', 'display', 'name', 'slug', 'asn', 'account', 'portal_url', 'noc_contact', 'admin_contact',
            'comments', 'tags', 'custom_fields', 'created', 'last_updated', 'circuit_count',
        ]


#
# Provider networks
#

class ProviderNetworkSerializer(PrimaryModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='circuits-api:providernetwork-detail')
    provider = NestedProviderSerializer()

    class Meta:
        model = ProviderNetwork
        fields = [
            'id', 'url', 'display', 'provider', 'name', 'description', 'comments', 'tags', 'custom_fields', 'created',
            'last_updated',
        ]


#
# Circuits
#

class CircuitTypeSerializer(PrimaryModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='circuits-api:circuittype-detail')
    circuit_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = CircuitType
        fields = [
            'id', 'url', 'display', 'name', 'slug', 'description', 'tags', 'custom_fields', 'created', 'last_updated',
            'circuit_count',
        ]


class CircuitCircuitTerminationSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='circuits-api:circuittermination-detail')
    site = NestedSiteSerializer()
    provider_network = NestedProviderNetworkSerializer()

    class Meta:
        model = CircuitTermination
        fields = [
            'id', 'url', 'display', 'site', 'provider_network', 'port_speed', 'upstream_speed', 'xconnect_id',
        ]


class CircuitSerializer(PrimaryModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='circuits-api:circuit-detail')
    provider = NestedProviderSerializer()
    status = ChoiceField(choices=CircuitStatusChoices, required=False)
    type = NestedCircuitTypeSerializer()
    tenant = NestedTenantSerializer(required=False, allow_null=True)
    termination_a = CircuitCircuitTerminationSerializer(read_only=True)
    termination_z = CircuitCircuitTerminationSerializer(read_only=True)

    class Meta:
        model = Circuit
        fields = [
            'id', 'url', 'display', 'cid', 'provider', 'type', 'status', 'tenant', 'install_date', 'commit_rate',
            'description', 'termination_a', 'termination_z', 'comments', 'tags', 'custom_fields', 'created',
            'last_updated',
        ]


class CircuitTerminationSerializer(ValidatedModelSerializer, LinkTerminationSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='circuits-api:circuittermination-detail')
    circuit = NestedCircuitSerializer()
    site = NestedSiteSerializer(required=False, allow_null=True)
    provider_network = NestedProviderNetworkSerializer(required=False, allow_null=True)
    cable = NestedCableSerializer(read_only=True)

    class Meta:
        model = CircuitTermination
        fields = [
            'id', 'url', 'display', 'circuit', 'term_side', 'site', 'provider_network', 'port_speed', 'upstream_speed',
            'xconnect_id', 'pp_info', 'description', 'mark_connected', 'cable', 'link_peer', 'link_peer_type',
            '_occupied',
        ]
