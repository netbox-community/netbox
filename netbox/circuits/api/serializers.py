from rest_framework import serializers

from circuits.choices import CircuitStatusChoices
from circuits.models import *
from dcim.api.nested_serializers import NestedSiteSerializer
from dcim.api.serializers import CabledObjectSerializer
from ipam.api.nested_serializers import NestedASNSerializer
from ipam.models import ASN
from netbox.api.fields import ChoiceField, RelatedObjectCountField, SerializedPKRelatedField
from netbox.api.serializers import NetBoxModelSerializer, WritableNestedSerializer
from tenancy.api.nested_serializers import NestedTenantSerializer
from .nested_serializers import *


#
# Providers
#

class ProviderSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='circuits-api:provider-detail')
    accounts = SerializedPKRelatedField(
        queryset=ProviderAccount.objects.all(),
        serializer=NestedProviderAccountSerializer,
        required=False,
        many=True
    )
    asns = SerializedPKRelatedField(
        queryset=ASN.objects.all(),
        serializer=NestedASNSerializer,
        required=False,
        many=True
    )

    # Related object counts
    circuit_count = RelatedObjectCountField('circuits')

    class Meta:
        model = Provider
        fields = [
            'id', 'url', 'display', 'name', 'slug', 'accounts', 'description', 'comments', 'asns', 'tags',
            'custom_fields', 'created', 'last_updated', 'circuit_count',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'slug', 'description', 'circuit_count')


#
# Provider Accounts
#

class ProviderAccountSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='circuits-api:provideraccount-detail')
    provider = NestedProviderSerializer()

    class Meta:
        model = ProviderAccount
        fields = [
            'id', 'url', 'display', 'provider', 'name', 'account', 'description', 'comments', 'tags', 'custom_fields',
            'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'account', 'description')


#
# Provider networks
#

class ProviderNetworkSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='circuits-api:providernetwork-detail')
    provider = NestedProviderSerializer()

    class Meta:
        model = ProviderNetwork
        fields = [
            'id', 'url', 'display', 'provider', 'name', 'service_id', 'description', 'comments', 'tags',
            'custom_fields', 'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'description')


#
# Circuits
#

class CircuitTypeSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='circuits-api:circuittype-detail')

    # Related object counts
    circuit_count = RelatedObjectCountField('circuits')

    class Meta:
        model = CircuitType
        fields = [
            'id', 'url', 'display', 'name', 'slug', 'color', 'description', 'tags', 'custom_fields', 'created',
            'last_updated', 'circuit_count',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'slug', 'description', 'circuit_count')


class CircuitCircuitTerminationSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='circuits-api:circuittermination-detail')
    site = NestedSiteSerializer(allow_null=True)
    provider_network = NestedProviderNetworkSerializer(allow_null=True)

    class Meta:
        model = CircuitTermination
        fields = [
            'id', 'url', 'display', 'site', 'provider_network', 'port_speed', 'upstream_speed', 'xconnect_id',
            'description',
        ]


class CircuitSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='circuits-api:circuit-detail')
    provider = NestedProviderSerializer()
    provider_account = NestedProviderAccountSerializer(required=False, allow_null=True)
    status = ChoiceField(choices=CircuitStatusChoices, required=False)
    type = NestedCircuitTypeSerializer()
    tenant = NestedTenantSerializer(required=False, allow_null=True)
    termination_a = CircuitCircuitTerminationSerializer(read_only=True, allow_null=True)
    termination_z = CircuitCircuitTerminationSerializer(read_only=True, allow_null=True)

    class Meta:
        model = Circuit
        fields = [
            'id', 'url', 'display', 'cid', 'provider', 'provider_account', 'type', 'status', 'tenant', 'install_date',
            'termination_date', 'commit_rate', 'description', 'termination_a', 'termination_z', 'comments', 'tags',
            'custom_fields', 'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'cid', 'description')


class CircuitTerminationSerializer(NetBoxModelSerializer, CabledObjectSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='circuits-api:circuittermination-detail')
    circuit = NestedCircuitSerializer()
    site = NestedSiteSerializer(required=False, allow_null=True)
    provider_network = NestedProviderNetworkSerializer(required=False, allow_null=True)

    class Meta:
        model = CircuitTermination
        fields = [
            'id', 'url', 'display', 'circuit', 'term_side', 'site', 'provider_network', 'port_speed', 'upstream_speed',
            'xconnect_id', 'pp_info', 'description', 'mark_connected', 'cable', 'cable_end', 'link_peers',
            'link_peers_type', 'tags', 'custom_fields', 'created', 'last_updated', '_occupied',
        ]
        brief_fields = ('id', 'url', 'display', 'circuit', 'term_side', 'description', 'cable', '_occupied')
