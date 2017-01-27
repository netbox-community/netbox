from rest_framework import serializers

from circuits.models import Provider, Circuit, CircuitTermination, CircuitType
from dcim.api.serializers import SiteNestedSerializer, NestedInterfaceSerializer
from extras.api.serializers import CustomFieldSerializer
from tenancy.api.serializers import TenantNestedSerializer


#
# Providers
#

class ProviderSerializer(CustomFieldSerializer, serializers.ModelSerializer):

    class Meta:
        model = Provider
        fields = ['id', 'name', 'slug', 'asn', 'account', 'portal_url', 'noc_contact', 'admin_contact', 'comments',
                  'custom_fields']


class ProviderNestedSerializer(ProviderSerializer):

    class Meta(ProviderSerializer.Meta):
        fields = ['id', 'name', 'slug']


#
# Circuit types
#

class CircuitTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = CircuitType
        fields = ['id', 'name', 'slug']


class CircuitTypeNestedSerializer(CircuitTypeSerializer):

    class Meta(CircuitTypeSerializer.Meta):
        pass


#
# Circuit Terminations
#

class CircuitTerminationSerializer(serializers.ModelSerializer):
    site = SiteNestedSerializer()
    interface = NestedInterfaceSerializer()

    class Meta:
        model = CircuitTermination
        fields = ['id', 'term_side', 'site', 'interface', 'port_speed', 'upstream_speed', 'xconnect_id', 'pp_info']


#
# Circuits
#


class CircuitSerializer(CustomFieldSerializer, serializers.ModelSerializer):
    provider = ProviderNestedSerializer()
    type = CircuitTypeNestedSerializer()
    tenant = TenantNestedSerializer()

    class Meta:
        model = Circuit
        fields = ['id', 'cid', 'provider', 'type', 'tenant', 'install_date', 'commit_rate', 'description', 'comments',
                  'custom_fields']


class CircuitNestedSerializer(CircuitSerializer):

    class Meta(CircuitSerializer.Meta):
        fields = ['id', 'cid']


class CircuitDetailSerializer(CircuitSerializer):
    terminations = CircuitTerminationSerializer(many=True)

    class Meta(CircuitSerializer.Meta):
        fields = ['id', 'cid', 'provider', 'type', 'tenant', 'install_date', 'commit_rate', 'description', 'comments',
                  'terminations', 'custom_fields']
