from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers

from ipam import models
from netbox.api.serializers import WritableNestedSerializer
from .field_serializers import IPAddressField

__all__ = [
    'NestedAggregateSerializer',
    'NestedASNSerializer',
    'NestedASNRangeSerializer',
    'NestedFHRPGroupSerializer',
    'NestedFHRPGroupAssignmentSerializer',
    'NestedIPAddressSerializer',
    'NestedIPRangeSerializer',
    'NestedPrefixSerializer',
    'NestedRIRSerializer',
    'NestedRoleSerializer',
    'NestedRouteTargetSerializer',
    'NestedServiceSerializer',
    'NestedServiceTemplateSerializer',
    'NestedVLANGroupSerializer',
    'NestedVLANSerializer',
    'NestedVRFSerializer',
]


#
# ASN ranges
#

class NestedASNRangeSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:asnrange-detail')

    class Meta:
        model = models.ASNRange
        fields = ['id', 'url', 'display', 'name']


#
# ASNs
#

class NestedASNSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:asn-detail')

    class Meta:
        model = models.ASN
        fields = ['id', 'url', 'display', 'asn']


#
# VRFs
#

@extend_schema_serializer(
    exclude_fields=('prefix_count',),
)
class NestedVRFSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:vrf-detail')
    prefix_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.VRF
        fields = ['id', 'url', 'display', 'name', 'rd', 'prefix_count']


#
# Route targets
#

class NestedRouteTargetSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:routetarget-detail')

    class Meta:
        model = models.RouteTarget
        fields = ['id', 'url', 'display', 'name']


#
# RIRs/aggregates
#

@extend_schema_serializer(
    exclude_fields=('aggregate_count',),
)
class NestedRIRSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:rir-detail')
    aggregate_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.RIR
        fields = ['id', 'url', 'display', 'name', 'slug', 'aggregate_count']


class NestedAggregateSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:aggregate-detail')
    family = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.Aggregate
        fields = ['id', 'url', 'display', 'family', 'prefix']


#
# FHRP groups
#

class NestedFHRPGroupSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:fhrpgroup-detail')

    class Meta:
        model = models.FHRPGroup
        fields = ['id', 'url', 'display', 'protocol', 'group_id']


class NestedFHRPGroupAssignmentSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:fhrpgroupassignment-detail')
    group = NestedFHRPGroupSerializer()

    class Meta:
        model = models.FHRPGroupAssignment
        fields = ['id', 'url', 'display', 'group', 'interface_type', 'interface_id', 'priority']


#
# VLANs
#

@extend_schema_serializer(
    exclude_fields=('prefix_count', 'vlan_count'),
)
class NestedRoleSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:role-detail')
    prefix_count = serializers.IntegerField(read_only=True)
    vlan_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.Role
        fields = ['id', 'url', 'display', 'name', 'slug', 'prefix_count', 'vlan_count']


@extend_schema_serializer(
    exclude_fields=('vlan_count',),
)
class NestedVLANGroupSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:vlangroup-detail')
    vlan_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.VLANGroup
        fields = ['id', 'url', 'display', 'name', 'slug', 'vlan_count']


class NestedVLANSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:vlan-detail')

    class Meta:
        model = models.VLAN
        fields = ['id', 'url', 'display', 'vid', 'name']


#
# Prefixes
#

class NestedPrefixSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:prefix-detail')
    family = serializers.IntegerField(read_only=True)
    _depth = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.Prefix
        fields = ['id', 'url', 'display', 'family', 'prefix', '_depth']


#
# IP ranges
#

class NestedIPRangeSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:iprange-detail')
    family = serializers.IntegerField(read_only=True)
    start_address = IPAddressField()
    end_address = IPAddressField()

    class Meta:
        model = models.IPRange
        fields = ['id', 'url', 'display', 'family', 'start_address', 'end_address']


#
# IP addresses
#

class NestedIPAddressSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:ipaddress-detail')
    family = serializers.IntegerField(read_only=True)
    address = IPAddressField()

    class Meta:
        model = models.IPAddress
        fields = ['id', 'url', 'display', 'family', 'address']


#
# Services
#

class NestedServiceTemplateSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:servicetemplate-detail')

    class Meta:
        model = models.ServiceTemplate
        fields = ['id', 'url', 'display', 'name', 'protocol', 'ports']


class NestedServiceSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:service-detail')

    class Meta:
        model = models.Service
        fields = ['id', 'url', 'display', 'name', 'protocol', 'ports']
