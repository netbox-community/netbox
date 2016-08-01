from rest_framework import serializers

from dcim.api.serializers import SiteNestedSerializer, InterfaceNestedSerializer
from ipam.models import VRF, Role, RIR, Aggregate, Prefix, IPAddress, VLAN, VLANGroup
from tenancy.api.serializers import TenantNestedSerializer


#
# VRFs
#

class VRFSerializer(serializers.ModelSerializer):
    tenant = TenantNestedSerializer()

    class Meta:
        model = VRF
        fields = ['id', 'name', 'rd', 'tenant', 'enforce_unique', 'description']


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
        fields = ['id', 'name', 'slug']


class RIRNestedSerializer(RIRSerializer):

    class Meta(RIRSerializer.Meta):
        pass


#
# Aggregates
#

class AggregateSerializer(serializers.ModelSerializer):
    rir = RIRNestedSerializer()

    class Meta:
        model = Aggregate
        fields = ['id', 'family', 'prefix', 'rir', 'date_added', 'description']


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

class VLANSerializer(serializers.ModelSerializer):
    site = SiteNestedSerializer()
    group = VLANGroupNestedSerializer()
    tenant = TenantNestedSerializer()
    role = RoleNestedSerializer()

    class Meta:
        model = VLAN
        fields = ['id', 'site', 'group', 'vid', 'name', 'tenant', 'status', 'role', 'description', 'display_name']


class VLANNestedSerializer(VLANSerializer):

    class Meta(VLANSerializer.Meta):
        fields = ['id', 'vid', 'name', 'display_name']


#
# Prefixes
#

class PrefixSerializer(serializers.ModelSerializer):
    site = SiteNestedSerializer()
    vrf = VRFTenantSerializer()
    tenant = TenantNestedSerializer()
    vlan = VLANNestedSerializer()
    role = RoleNestedSerializer()

    class Meta:
        model = Prefix
        fields = ['id', 'family', 'prefix', 'site', 'vrf', 'tenant', 'vlan', 'status', 'role', 'description']


class PrefixNestedSerializer(PrefixSerializer):

    class Meta(PrefixSerializer.Meta):
        fields = ['id', 'family', 'prefix']


#
# IP addresses
#

class IPAddressSerializer(serializers.ModelSerializer):
    vrf = VRFTenantSerializer()
    tenant = TenantNestedSerializer()
    interface = InterfaceNestedSerializer()

    class Meta:
        model = IPAddress
        fields = ['id', 'family', 'address', 'vrf', 'tenant', 'interface', 'description', 'nat_inside', 'nat_outside']


class IPAddressNestedSerializer(IPAddressSerializer):

    class Meta(IPAddressSerializer.Meta):
        fields = ['id', 'family', 'address']

IPAddressSerializer._declared_fields['nat_inside'] = IPAddressNestedSerializer()
IPAddressSerializer._declared_fields['nat_outside'] = IPAddressNestedSerializer()
