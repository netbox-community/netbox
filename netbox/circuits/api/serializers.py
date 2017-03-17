from rest_framework import serializers

from circuits.models import Provider, Circuit, CircuitTermination, CircuitType
from dcim.api.serializers import NestedSiteSerializer, InterfaceSerializer
from extras.api.customfields import CustomFieldModelSerializer
from tenancy.api.serializers import NestedTenantSerializer


#
# Providers
#

class ProviderSerializer(CustomFieldModelSerializer):

    class Meta:
        model = Provider
        fields = [
            'id', 'name', 'slug', 'asn', 'account', 'portal_url', 'noc_contact', 'admin_contact', 'comments',
            'custom_fields',
        ]


class NestedProviderSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='circuits-api:provider-detail')

    class Meta:
        model = Provider
        fields = ['id', 'url', 'name', 'slug']


class WritableProviderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Provider
        fields = ['name', 'slug', 'asn', 'account', 'portal_url', 'noc_contact', 'admin_contact', 'comments']


#
# Circuit types
#

class CircuitTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = CircuitType
        fields = ['id', 'name', 'slug']


class NestedCircuitTypeSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='circuits-api:circuittype-detail')

    class Meta:
        model = CircuitType
        fields = ['id', 'url', 'name', 'slug']


#
# Circuits
#

class CircuitSerializer(CustomFieldModelSerializer):
    provider = NestedProviderSerializer()
    type = NestedCircuitTypeSerializer()
    tenant = NestedTenantSerializer()

    class Meta:
        model = Circuit
        fields = [
            'id', 'cid', 'provider', 'type', 'tenant', 'install_date', 'commit_rate', 'description', 'comments',
            'custom_fields',
        ]


class NestedCircuitSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='circuits-api:circuit-detail')

    class Meta:
        model = Circuit
        fields = ['id', 'url', 'cid']


class WritableCircuitSerializer(serializers.ModelSerializer):

    class Meta:
        model = Circuit
        fields = ['cid', 'provider', 'type', 'tenant', 'install_date', 'commit_rate', 'description', 'comments']


#
# Circuit Terminations
#

class CircuitTerminationSerializer(serializers.ModelSerializer):
    circuit = NestedCircuitSerializer()
    site = NestedSiteSerializer()
    interface = InterfaceSerializer()

    class Meta:
        model = CircuitTermination
        fields = [
            'id', 'circuit', 'term_side', 'site', 'interface', 'port_speed', 'upstream_speed', 'xconnect_id', 'pp_info',
        ]


class WritableCircuitTerminationSerializer(serializers.ModelSerializer):

    class Meta:
        model = CircuitTermination
        fields = [
            'circuit', 'term_side', 'site', 'interface', 'port_speed', 'upstream_speed', 'xconnect_id', 'pp_info',
        ]
