from rest_framework import serializers

from dcim.api.serializers import NestedDeviceSerializer, DeviceInterfaceSerializer, NestedSiteSerializer
from extras.api.serializers import CustomFieldSerializer
from ipam.models import Aggregate, IPAddress, Prefix, RIR, Role, Service, VLAN, VLANGroup, VRF
from tenancy.api.serializers import NestedTenantSerializer
from utilities.api import WritableSerializerMixin


#
# VRFs
#

class VRFSerializer(CustomFieldSerializer, serializers.ModelSerializer):
    tenant = NestedTenantSerializer()

    class Meta:
        model = VRF
        fields = ['id', 'name', 'rd', 'tenant', 'enforce_unique', 'description', 'custom_fields']


class NestedVRFSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = VRF
        fields = ['id', 'url', 'name', 'rd']


#
# Roles
#

class RoleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Role
        fields = ['id', 'name', 'slug', 'weight']


class NestedRoleSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Role
        fields = ['id', 'url', 'name', 'slug']


#
# RIRs
#

class RIRSerializer(serializers.ModelSerializer):

    class Meta:
        model = RIR
        fields = ['id', 'name', 'slug', 'is_private']


class NestedRIRSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = RIR
        fields = ['id', 'url', 'name', 'slug']


#
# Aggregates
#

class AggregateSerializer(CustomFieldSerializer, serializers.ModelSerializer):
    rir = NestedRIRSerializer()

    class Meta:
        model = Aggregate
        fields = ['id', 'family', 'prefix', 'rir', 'date_added', 'description', 'custom_fields']


class NestedAggregateSerializer(serializers.HyperlinkedModelSerializer):

    class Meta(AggregateSerializer.Meta):
        model = Aggregate
        fields = ['id', 'url', 'family', 'prefix']


#
# VLAN groups
#

class VLANGroupSerializer(WritableSerializerMixin, serializers.ModelSerializer):
    site = NestedSiteSerializer()

    class Meta:
        model = VLANGroup
        fields = ['id', 'name', 'slug', 'site']


class NestedVLANGroupSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = VLANGroup
        fields = ['id', 'url', 'name', 'slug']


#
# VLANs
#

class VLANSerializer(CustomFieldSerializer, serializers.ModelSerializer):
    site = NestedSiteSerializer()
    group = NestedVLANGroupSerializer()
    tenant = NestedTenantSerializer()
    role = NestedRoleSerializer()

    class Meta:
        model = VLAN
        fields = [
            'id', 'site', 'group', 'vid', 'name', 'tenant', 'status', 'role', 'description', 'display_name',
            'custom_fields',
        ]


class NestedVLANSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = VLAN
        fields = ['id', 'url', 'vid', 'name', 'display_name']


#
# Prefixes
#

class PrefixSerializer(CustomFieldSerializer, serializers.ModelSerializer):
    site = NestedSiteSerializer()
    vrf = NestedVRFSerializer()
    tenant = NestedTenantSerializer()
    vlan = NestedVLANSerializer()
    role = NestedRoleSerializer()

    class Meta:
        model = Prefix
        fields = [
            'id', 'family', 'prefix', 'site', 'vrf', 'tenant', 'vlan', 'status', 'role', 'is_pool', 'description',
            'custom_fields',
        ]


class NestedPrefixSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Prefix
        fields = ['id', 'url', 'family', 'prefix']


#
# IP addresses
#

class IPAddressSerializer(CustomFieldSerializer, serializers.ModelSerializer):
    vrf = NestedVRFSerializer()
    tenant = NestedTenantSerializer()
    interface = DeviceInterfaceSerializer()

    class Meta:
        model = IPAddress
        fields = [
            'id', 'family', 'address', 'vrf', 'tenant', 'status', 'interface', 'description', 'nat_inside',
            'nat_outside', 'custom_fields',
        ]


class NestedIPAddressSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = IPAddress
        fields = ['id', 'url', 'family', 'address']

IPAddressSerializer._declared_fields['nat_inside'] = NestedIPAddressSerializer()
IPAddressSerializer._declared_fields['nat_outside'] = NestedIPAddressSerializer()


#
# Services
#

class ServiceSerializer(serializers.ModelSerializer):
    device = NestedDeviceSerializer()
    ipaddresses = NestedIPAddressSerializer(many=True)

    class Meta:
        model = Service
        fields = ['id', 'device', 'name', 'port', 'protocol', 'ipaddresses', 'description']


class ChildServiceSerializer(serializers.HyperlinkedModelSerializer):
    ipaddresses = NestedIPAddressSerializer(many=True)

    class Meta:
        model = Service
        fields = ['id', 'url', 'name', 'port', 'protocol', 'ipaddresses', 'description']
