from rest_framework import serializers

from ipam import models
from utilities.api import WritableNestedSerializer

__all__ = [
    'NestedAggregateSerializer',
    'NestedIPAddressSerializer',
    'NestedPrefixSerializer',
    'NestedRIRSerializer',
    'NestedRoleSerializer',
    'NestedServiceSerializer',
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
        model = models.VRF
        fields = ['id', 'url', 'name', 'rd', 'prefix_count']


#
# RIRs/aggregates
#

class NestedRIRSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:rir-detail')
    aggregate_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.RIR
        fields = ['id', 'url', 'name', 'slug', 'aggregate_count']


class NestedAggregateSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:aggregate-detail')

    class Meta:
        model = models.Aggregate
        fields = ['id', 'url', 'family', 'prefix']


#
# VLANs
#

class NestedRoleSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:role-detail')
    prefix_count = serializers.IntegerField(read_only=True)
    vlan_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.Role
        fields = ['id', 'url', 'name', 'slug', 'prefix_count', 'vlan_count']


class NestedVLANGroupSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:vlangroup-detail')
    vlan_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.VLANGroup
        fields = ['id', 'url', 'name', 'slug', 'vlan_count']


class NestedVLANSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:vlan-detail')

    class Meta:
        model = models.VLAN
        fields = ['id', 'url', 'vid', 'name', 'display_name']


#
# Prefixes
#

class NestedPrefixSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:prefix-detail')

    class Meta:
        model = models.Prefix
        fields = ['id', 'url', 'family', 'prefix']


#
# IP addresses
#

class NestedIPAddressSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:ipaddress-detail')

    class Meta:
        model = models.IPAddress
        fields = ['id', 'url', 'family', 'address']


#
# Services
#

class NestedServiceSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:service-detail')

    class Meta:
        model = models.Service
        fields = ['id', 'url', 'name', 'protocol', 'port']
