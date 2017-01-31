from rest_framework import serializers

from dcim.api.serializers import NestedDeviceSerializer, DeviceInterfaceSerializer, NestedSiteSerializer
from extras.api.serializers import CustomFieldValueSerializer
from ipam.models import Aggregate, IPAddress, Prefix, RIR, Role, Service, VLAN, VLANGroup, VRF
from tenancy.api.serializers import NestedTenantSerializer


#
# VRFs
#

class VRFSerializer(serializers.ModelSerializer):
    tenant = NestedTenantSerializer()
    custom_field_values = CustomFieldValueSerializer(many=True)

    class Meta:
        model = VRF
        fields = ['id', 'name', 'rd', 'tenant', 'enforce_unique', 'description', 'custom_field_values']


class NestedVRFSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:vrf-detail')

    class Meta:
        model = VRF
        fields = ['id', 'url', 'name', 'rd']


class WritableVRFSerializer(serializers.ModelSerializer):

    class Meta:
        model = VRF
        fields = ['id', 'name', 'rd', 'tenant', 'enforce_unique', 'description']


#
# Roles
#

class RoleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Role
        fields = ['id', 'name', 'slug', 'weight']


class NestedRoleSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:role-detail')

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


class NestedRIRSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:rir-detail')

    class Meta:
        model = RIR
        fields = ['id', 'url', 'name', 'slug']


#
# Aggregates
#

class AggregateSerializer(serializers.ModelSerializer):
    rir = NestedRIRSerializer()
    custom_field_values = CustomFieldValueSerializer(many=True)

    class Meta:
        model = Aggregate
        fields = ['id', 'family', 'prefix', 'rir', 'date_added', 'description', 'custom_field_values']


class NestedAggregateSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:aggregate-detail')

    class Meta(AggregateSerializer.Meta):
        model = Aggregate
        fields = ['id', 'url', 'family', 'prefix']


class WritableAggregateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Aggregate
        fields = ['id', 'family', 'prefix', 'rir', 'date_added', 'description']


#
# VLAN groups
#

class VLANGroupSerializer(serializers.ModelSerializer):
    site = NestedSiteSerializer()

    class Meta:
        model = VLANGroup
        fields = ['id', 'name', 'slug', 'site']


class NestedVLANGroupSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:vlangroup-detail')

    class Meta:
        model = VLANGroup
        fields = ['id', 'url', 'name', 'slug']


class WritableVLANGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = VLANGroup
        fields = ['id', 'name', 'slug', 'site']


#
# VLANs
#

class VLANSerializer(serializers.ModelSerializer):
    site = NestedSiteSerializer()
    group = NestedVLANGroupSerializer()
    tenant = NestedTenantSerializer()
    role = NestedRoleSerializer()
    custom_field_values = CustomFieldValueSerializer(many=True)

    class Meta:
        model = VLAN
        fields = [
            'id', 'site', 'group', 'vid', 'name', 'tenant', 'status', 'role', 'description', 'display_name',
            'custom_field_values',
        ]


class NestedVLANSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:vlan-detail')

    class Meta:
        model = VLAN
        fields = ['id', 'url', 'vid', 'name', 'display_name']


class WritableVLANSerializer(serializers.ModelSerializer):

    class Meta:
        model = VLAN
        fields = [
            'id', 'site', 'group', 'vid', 'name', 'tenant', 'status', 'role', 'description',
        ]


#
# Prefixes
#

class PrefixSerializer(serializers.ModelSerializer):
    site = NestedSiteSerializer()
    vrf = NestedVRFSerializer()
    tenant = NestedTenantSerializer()
    vlan = NestedVLANSerializer()
    role = NestedRoleSerializer()
    custom_field_values = CustomFieldValueSerializer(many=True)

    class Meta:
        model = Prefix
        fields = [
            'id', 'family', 'prefix', 'site', 'vrf', 'tenant', 'vlan', 'status', 'role', 'is_pool', 'description',
            'custom_field_values',
        ]


class NestedPrefixSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:prefix-detail')

    class Meta:
        model = Prefix
        fields = ['id', 'url', 'family', 'prefix']


class WritablePrefixSerializer(serializers.ModelSerializer):

    class Meta:
        model = Prefix
        fields = [
            'id', 'family', 'prefix', 'site', 'vrf', 'tenant', 'vlan', 'status', 'role', 'is_pool', 'description',
        ]


#
# IP addresses
#

class IPAddressSerializer(serializers.ModelSerializer):
    vrf = NestedVRFSerializer()
    tenant = NestedTenantSerializer()
    interface = DeviceInterfaceSerializer()
    custom_field_values = CustomFieldValueSerializer(many=True)

    class Meta:
        model = IPAddress
        fields = [
            'id', 'family', 'address', 'vrf', 'tenant', 'status', 'interface', 'description', 'nat_inside',
            'nat_outside', 'custom_field_values',
        ]


class NestedIPAddressSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:ipaddress-detail')

    class Meta:
        model = IPAddress
        fields = ['id', 'url', 'family', 'address']

IPAddressSerializer._declared_fields['nat_inside'] = NestedIPAddressSerializer()
IPAddressSerializer._declared_fields['nat_outside'] = NestedIPAddressSerializer()


class WritableIPAddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = IPAddress
        fields = ['id', 'family', 'address', 'vrf', 'tenant', 'status', 'interface', 'description', 'nat_inside']


#
# Services
#

class ServiceSerializer(serializers.ModelSerializer):
    device = NestedDeviceSerializer()
    ipaddresses = NestedIPAddressSerializer(many=True)

    class Meta:
        model = Service
        fields = ['id', 'device', 'name', 'port', 'protocol', 'ipaddresses', 'description']


class DeviceServiceSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:service-detail')
    ipaddresses = NestedIPAddressSerializer(many=True)

    class Meta:
        model = Service
        fields = ['id', 'url', 'name', 'port', 'protocol', 'ipaddresses', 'description']
