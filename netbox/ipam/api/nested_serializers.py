from rest_framework import serializers

from ipam.models import Aggregate, IPAddress, Prefix, RIR, Role, VLAN, VLANGroup, VRF
from utilities.api import WritableNestedSerializer

__all__ = [
    'NestedAggregateSerializer',
    'NestedIPAddressSerializer',
    'NestedPrefixSerializer',
    'NestedRIRSerializer',
    'NestedRoleSerializer',
    'NestedVLANGroupSerializer',
    'NestedVLANSerializer',
    'NestedVRFSerializer',
]


#
# VRFs
#

class NestedVRFSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:vrf-detail')
    prefix_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = VRF
        fields = ['id', 'url', 'name', 'rd', 'prefix_count']


#
# RIRs/aggregates
#

class NestedRIRSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:rir-detail')
    aggregate_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = RIR
        fields = ['id', 'url', 'name', 'slug', 'aggregate_count']


class NestedAggregateSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:aggregate-detail')

    class Meta:
        model = Aggregate
        fields = ['id', 'url', 'family', 'prefix']


#
# VLANs
#

class NestedRoleSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:role-detail')
    prefix_count = serializers.IntegerField(read_only=True)
    vlan_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Role
        fields = ['id', 'url', 'name', 'slug', 'prefix_count', 'vlan_count']


class NestedVLANGroupSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:vlangroup-detail')
    vlan_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = VLANGroup
        fields = ['id', 'url', 'name', 'slug', 'vlan_count']


class NestedVLANSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:vlan-detail')

    class Meta:
        model = VLAN
        fields = ['id', 'url', 'vid', 'name', 'display_name']


#
# Prefixes
#

class NestedPrefixSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:prefix-detail')

    class Meta:
        model = Prefix
        fields = ['id', 'url', 'family', 'prefix']


#
# IP addresses
#


class NestedIPAddressSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:ipaddress-detail')

    class Meta:
        model = IPAddress
        fields = ['id', 'url', 'family', 'address']
