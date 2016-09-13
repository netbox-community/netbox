from rest_framework import serializers

from circuits.models import Provider, CircuitType, Circuit
from dcim.api.serializers import SiteNestedSerializer, InterfaceNestedSerializer
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
# Circuits
#

class CircuitSerializer(CustomFieldSerializer, serializers.ModelSerializer):
    provider = ProviderNestedSerializer()
    type = CircuitTypeNestedSerializer()
    tenant = TenantNestedSerializer()
    site = SiteNestedSerializer()
    interface = InterfaceNestedSerializer()

    class Meta:
        model = Circuit
        fields = ['id', 'cid', 'provider', 'type', 'tenant', 'site', 'interface', 'install_date', 'port_speed',
                  'upstream_speed', 'commit_rate', 'xconnect_id', 'comments', 'custom_fields']


class CircuitNestedSerializer(CircuitSerializer):

    class Meta(CircuitSerializer.Meta):
        fields = ['id', 'cid']
