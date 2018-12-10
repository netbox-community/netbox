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

    class Meta:
        model = VRF
        fields = ['id', 'url', 'name', 'rd']


#
# RIRs/aggregates
#

class NestedRIRSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:rir-detail')

    class Meta:
        model = RIR
        fields = ['id', 'url', 'name', 'slug']


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

    class Meta:
        model = Role
        fields = ['id', 'url', 'name', 'slug']


class NestedVLANGroupSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:vlangroup-detail')

    class Meta:
        model = VLANGroup
        fields = ['id', 'url', 'name', 'slug']


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
