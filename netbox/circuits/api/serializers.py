from rest_framework import serializers

from circuits.models import Provider, Circuit, CircuitTermination, CircuitType
from dcim.api.serializers import NestedSiteSerializer, DeviceInterfaceSerializer
from extras.api.serializers import CustomFieldSerializer
from tenancy.api.serializers import NestedTenantSerializer


#
# Providers
#

class ProviderSerializer(CustomFieldSerializer, serializers.ModelSerializer):

    class Meta:
        model = Provider
        fields = [
            'id', 'name', 'slug', 'asn', 'account', 'portal_url', 'noc_contact', 'admin_contact', 'comments',
            'custom_fields',
        ]


class NestedProviderSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='circuits-api:provider-detail')

    class Meta:
        model = Provider
        fields = ['id', 'url', 'name', 'slug']


#
# Circuit types
#

class CircuitTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = CircuitType
        fields = ['id', 'name', 'slug']


class NestedCircuitTypeSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='circuits-api:circuittype-detail')

    class Meta:
        model = CircuitType
        fields = ['id', 'url', 'name', 'slug']


#
# Circuit Terminations
#

class CircuitTerminationSerializer(serializers.ModelSerializer):
    site = NestedSiteSerializer()
    interface = DeviceInterfaceSerializer()

    class Meta:
        model = CircuitTermination
        fields = ['id', 'term_side', 'site', 'interface', 'port_speed', 'upstream_speed', 'xconnect_id', 'pp_info']


#
# Circuits
#

class CircuitSerializer(CustomFieldSerializer, serializers.ModelSerializer):
    provider = NestedProviderSerializer()
    type = NestedCircuitTypeSerializer()
    tenant = NestedTenantSerializer()

    class Meta:
        model = Circuit
        fields = [
            'id', 'cid', 'provider', 'type', 'tenant', 'install_date', 'commit_rate', 'description', 'comments',
            'custom_fields',
        ]


class NestedCircuitSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='circuits-api:circuit-detail')

    class Meta:
        model = Circuit
        fields = ['id', 'url', 'cid']


# TODO: Delete this
class CircuitDetailSerializer(CircuitSerializer):
    terminations = CircuitTerminationSerializer(many=True)

    class Meta(CircuitSerializer.Meta):
        fields = [
            'id', 'cid', 'provider', 'type', 'tenant', 'install_date', 'commit_rate', 'description', 'comments',
            'terminations', 'custom_fields',
        ]
