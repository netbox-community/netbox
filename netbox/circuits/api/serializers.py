from rest_framework import serializers
from taggit_serializer.serializers import TaggitSerializer, TagListSerializerField

from circuits.constants import CIRCUIT_STATUS_CHOICES
from circuits.models import Provider, Circuit, CircuitTermination, CircuitType
from dcim.api.nested_serializers import NestedCableSerializer, NestedSiteSerializer
from dcim.api.serializers import ConnectedEndpointSerializer
from extras.api.customfields import CustomFieldModelSerializer
from tenancy.api.nested_serializers import NestedTenantSerializer
from utilities.api import ChoiceField, ValidatedModelSerializer
from .nested_serializers import *


#
# Providers
#

class ProviderSerializer(TaggitSerializer, CustomFieldModelSerializer):
    tags = TagListSerializerField(required=False)
    circuit_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Provider
        fields = [
            'id', 'name', 'slug', 'asn', 'account', 'portal_url', 'noc_contact', 'admin_contact', 'comments', 'tags',
            'custom_fields', 'created', 'last_updated', 'circuit_count',
        ]


#
# Circuits
#

class CircuitTypeSerializer(ValidatedModelSerializer):
    circuit_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = CircuitType
        fields = ['id', 'name', 'slug', 'circuit_count']


class CircuitSerializer(TaggitSerializer, CustomFieldModelSerializer):
    provider = NestedProviderSerializer()
    status = ChoiceField(choices=CIRCUIT_STATUS_CHOICES, required=False)
    type = NestedCircuitTypeSerializer()
    tenant = NestedTenantSerializer(required=False, allow_null=True)
    tags = TagListSerializerField(required=False)

    class Meta:
        model = Circuit
        fields = [
            'id', 'cid', 'provider', 'type', 'status', 'tenant', 'install_date', 'commit_rate', 'description',
            'comments', 'tags', 'custom_fields', 'created', 'last_updated',
        ]


class CircuitTerminationSerializer(ConnectedEndpointSerializer):
    circuit = NestedCircuitSerializer()
    site = NestedSiteSerializer()
    cable = NestedCableSerializer(read_only=True)

    class Meta:
        model = CircuitTermination
        fields = [
            'id', 'circuit', 'term_side', 'site', 'port_speed', 'upstream_speed', 'xconnect_id', 'pp_info',
            'description', 'connected_endpoint_type', 'connected_endpoint', 'connection_status', 'cable',
        ]
