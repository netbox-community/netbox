from __future__ import unicode_literals

from rest_framework import serializers
from taggit_serializer.serializers import TaggitSerializer, TagListSerializerField

from circuits.constants import CIRCUIT_STATUS_CHOICES
from circuits.models import Circuit, CircuitTermination, CircuitType, Provider
from dcim.api.serializers import NestedInterfaceSerializer, NestedSiteSerializer
from extras.api.customfields import CustomFieldModelSerializer
from tenancy.api.serializers import NestedTenantSerializer
from utilities.api import ChoiceField, ValidatedModelSerializer, WritableNestedSerializer


#
# Providers
#

class ProviderSerializer(TaggitSerializer, CustomFieldModelSerializer):
    tags = TagListSerializerField(required=False)

    class Meta:
        model = Provider
        fields = [
            'id', 'name', 'slug', 'asn', 'account', 'portal_url', 'noc_contact', 'admin_contact', 'comments', 'tags',
            'custom_fields', 'created', 'last_updated',
        ]


class NestedProviderSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='circuits-api:provider-detail')

    class Meta:
        model = Provider
        fields = ['id', 'url', 'name', 'slug']


#
# Circuit types
#

class CircuitTypeSerializer(ValidatedModelSerializer):

    class Meta:
        model = CircuitType
        fields = ['id', 'name', 'slug']


class NestedCircuitTypeSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='circuits-api:circuittype-detail')

    class Meta:
        model = CircuitType
        fields = ['id', 'url', 'name', 'slug']


#
# Circuits
#

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


class NestedCircuitSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='circuits-api:circuit-detail')

    class Meta:
        model = Circuit
        fields = ['id', 'url', 'cid']


#
# Circuit Terminations
#

class CircuitTerminationSerializer(ValidatedModelSerializer):
    circuit = NestedCircuitSerializer()
    site = NestedSiteSerializer()
    interface = NestedInterfaceSerializer(required=False, allow_null=True)

    class Meta:
        model = CircuitTermination
        fields = [
            'id', 'circuit', 'term_side', 'site', 'interface', 'port_speed', 'upstream_speed', 'xconnect_id', 'pp_info',
        ]
