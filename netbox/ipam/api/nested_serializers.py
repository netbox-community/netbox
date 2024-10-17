import warnings

from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers

from ipam import models
from netbox.api.fields import RelatedObjectCountField
from netbox.api.serializers import WritableNestedSerializer
from .field_serializers import IPAddressField
from .serializers_.nested import NestedIPAddressSerializer

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

# TODO: Remove in v4.2
warnings.warn(
    "Dedicated nested serializers will be removed in NetBox v4.2. Use Serializer(nested=True) instead.",
    DeprecationWarning
)


#
# ASN ranges
#

class NestedASNRangeSerializer(WritableNestedSerializer):

    class Meta:
        model = models.ASNRange
        fields = ['id', 'url', 'display_url', 'display', 'name']


#
# ASNs
#

class NestedASNSerializer(WritableNestedSerializer):

    class Meta:
        model = models.ASN
        fields = ['id', 'url', 'display_url', 'display', 'asn']


#
# VRFs
#

@extend_schema_serializer(
    exclude_fields=('prefix_count',),
)
class NestedVRFSerializer(WritableNestedSerializer):
    prefix_count = RelatedObjectCountField('prefixes')

    class Meta:
        model = models.VRF
        fields = ['id', 'url', 'display_url', 'display', 'name', 'rd', 'prefix_count']


#
# Route targets
#

class NestedRouteTargetSerializer(WritableNestedSerializer):

    class Meta:
        model = models.RouteTarget
        fields = ['id', 'url', 'display_url', 'display', 'name']


#
# RIRs/aggregates
#

@extend_schema_serializer(
    exclude_fields=('aggregate_count',),
)
class NestedRIRSerializer(WritableNestedSerializer):
    aggregate_count = RelatedObjectCountField('aggregates')

    class Meta:
        model = models.RIR
        fields = ['id', 'url', 'display_url', 'display', 'name', 'slug', 'aggregate_count']


class NestedAggregateSerializer(WritableNestedSerializer):
    family = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.Aggregate
        fields = ['id', 'url', 'display_url', 'display', 'family', 'prefix']


#
# FHRP groups
#

class NestedFHRPGroupSerializer(WritableNestedSerializer):

    class Meta:
        model = models.FHRPGroup
        fields = ['id', 'url', 'display_url', 'display', 'protocol', 'group_id']


class NestedFHRPGroupAssignmentSerializer(WritableNestedSerializer):
    group = NestedFHRPGroupSerializer()

    class Meta:
        model = models.FHRPGroupAssignment
        fields = ['id', 'url', 'display_url', 'display', 'group', 'interface_type', 'interface_id', 'priority']


#
# VLANs
#

@extend_schema_serializer(
    exclude_fields=('prefix_count', 'vlan_count'),
)
class NestedRoleSerializer(WritableNestedSerializer):
    prefix_count = RelatedObjectCountField('prefixes')
    vlan_count = RelatedObjectCountField('vlans')

    class Meta:
        model = models.Role
        fields = ['id', 'url', 'display_url', 'display', 'name', 'slug', 'prefix_count', 'vlan_count']


@extend_schema_serializer(
    exclude_fields=('vlan_count',),
)
class NestedVLANGroupSerializer(WritableNestedSerializer):
    vlan_count = RelatedObjectCountField('vlans')

    class Meta:
        model = models.VLANGroup
        fields = ['id', 'url', 'display_url', 'display', 'name', 'slug', 'vlan_count']


class NestedVLANSerializer(WritableNestedSerializer):

    class Meta:
        model = models.VLAN
        fields = ['id', 'url', 'display_url', 'display', 'vid', 'name']


#
# Prefixes
#

class NestedPrefixSerializer(WritableNestedSerializer):
    family = serializers.IntegerField(read_only=True)
    _depth = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.Prefix
        fields = ['id', 'url', 'display_url', 'display', 'family', 'prefix', '_depth']


#
# IP ranges
#

class NestedIPRangeSerializer(WritableNestedSerializer):
    family = serializers.IntegerField(read_only=True)
    start_address = IPAddressField()
    end_address = IPAddressField()

    class Meta:
        model = models.IPRange
        fields = ['id', 'url', 'display_url', 'display', 'family', 'start_address', 'end_address']


#
# Services
#

class NestedServiceTemplateSerializer(WritableNestedSerializer):

    class Meta:
        model = models.ServiceTemplate
        fields = ['id', 'url', 'display_url', 'display', 'name', 'protocol', 'ports']


class NestedServiceSerializer(WritableNestedSerializer):

    class Meta:
        model = models.Service
        fields = ['id', 'url', 'display_url', 'display', 'name', 'protocol', 'ports']
