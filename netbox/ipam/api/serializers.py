from rest_framework import serializers

from dcim.api.serializers import DeviceNestedSerializer, NestedInterfaceSerializer, SiteNestedSerializer
from extras.api.serializers import CustomFieldSerializer
from ipam.models import Aggregate, IPAddress, Prefix, RIR, Role, Service, VLAN, VLANGroup, VRF
from tenancy.api.serializers import TenantNestedSerializer


#
# VRFs
#

class VRFSerializer(CustomFieldSerializer, serializers.ModelSerializer):
    tenant = TenantNestedSerializer()

    class Meta:
        model = VRF
        fields = ['id', 'name', 'rd', 'tenant', 'enforce_unique', 'description', 'custom_fields']


class VRFNestedSerializer(VRFSerializer):

    class Meta(VRFSerializer.Meta):
        fields = ['id', 'name', 'rd']


class VRFTenantSerializer(VRFSerializer):
    """
    Include tenant serializer. Useful for determining tenant inheritance for Prefixes and IPAddresses.
    """

    class Meta(VRFSerializer.Meta):
        fields = ['id', 'name', 'rd', 'tenant']


#
# Roles
#

class RoleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Role
        fields = ['id', 'name', 'slug', 'weight']


class RoleNestedSerializer(RoleSerializer):

    class Meta(RoleSerializer.Meta):
        fields = ['id', 'name', 'slug']


#
# RIRs
#

class RIRSerializer(serializers.ModelSerializer):

    class Meta:
        model = RIR
        fields = ['id', 'name', 'slug', 'is_private']


class RIRNestedSerializer(RIRSerializer):

    class Meta(RIRSerializer.Meta):
        fields = ['id', 'name', 'slug']


#
# Aggregates
#

class AggregateSerializer(CustomFieldSerializer, serializers.ModelSerializer):
    rir = RIRNestedSerializer()

    class Meta:
        model = Aggregate
        fields = ['id', 'family', 'prefix', 'rir', 'date_added', 'description', 'custom_fields']


class AggregateNestedSerializer(AggregateSerializer):

    class Meta(AggregateSerializer.Meta):
        fields = ['id', 'family', 'prefix']


#
# VLAN groups
#

class VLANGroupSerializer(serializers.ModelSerializer):
    site = SiteNestedSerializer()

    class Meta:
        model = VLANGroup
        fields = ['id', 'name', 'slug', 'site']


class VLANGroupNestedSerializer(VLANGroupSerializer):

    class Meta(VLANGroupSerializer.Meta):
        fields = ['id', 'name', 'slug']


#
# VLANs
#

class VLANSerializer(CustomFieldSerializer, serializers.ModelSerializer):
    site = SiteNestedSerializer()
    group = VLANGroupNestedSerializer()
    tenant = TenantNestedSerializer()
    role = RoleNestedSerializer()

    class Meta:
        model = VLAN
        fields = ['id', 'site', 'group', 'vid', 'name', 'tenant', 'status', 'role', 'description', 'display_name',
                  'custom_fields']


class VLANNestedSerializer(VLANSerializer):

    class Meta(VLANSerializer.Meta):
        fields = ['id', 'vid', 'name', 'display_name']


#
# Prefixes
#

class PrefixSerializer(CustomFieldSerializer, serializers.ModelSerializer):
    site = SiteNestedSerializer()
    vrf = VRFTenantSerializer()
    tenant = TenantNestedSerializer()
    vlan = VLANNestedSerializer()
    role = RoleNestedSerializer()

    class Meta:
        model = Prefix
        fields = ['id', 'family', 'prefix', 'site', 'vrf', 'tenant', 'vlan', 'status', 'role', 'is_pool', 'description',
                  'custom_fields']


class PrefixNestedSerializer(PrefixSerializer):

    class Meta(PrefixSerializer.Meta):
        fields = ['id', 'family', 'prefix']


#
# IP addresses
#

class IPAddressSerializer(CustomFieldSerializer, serializers.ModelSerializer):
    vrf = VRFTenantSerializer()
    tenant = TenantNestedSerializer()
    interface = NestedInterfaceSerializer()

    class Meta:
        model = IPAddress
        fields = ['id', 'family', 'address', 'vrf', 'tenant', 'status', 'interface', 'description', 'nat_inside',
                  'nat_outside', 'custom_fields']


class IPAddressNestedSerializer(IPAddressSerializer):

    class Meta(IPAddressSerializer.Meta):
        fields = ['id', 'family', 'address']

IPAddressSerializer._declared_fields['nat_inside'] = IPAddressNestedSerializer()
IPAddressSerializer._declared_fields['nat_outside'] = IPAddressNestedSerializer()


#
# Services
#

class ServiceSerializer(serializers.ModelSerializer):
    device = DeviceNestedSerializer()
    ipaddresses = IPAddressNestedSerializer(many=True)

    class Meta:
        model = Service
        fields = ['id', 'device', 'name', 'port', 'protocol', 'ipaddresses', 'description']


class ServiceNestedSerializer(ServiceSerializer):

    class Meta(ServiceSerializer.Meta):
        fields = ['id', 'name', 'port', 'protocol']
