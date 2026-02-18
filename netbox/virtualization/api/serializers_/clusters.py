from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from dcim.constants import LOCATION_SCOPE_TYPES
from netbox.api.fields import ChoiceField, ContentTypeField, RelatedObjectCountField
from netbox.api.gfk_fields import GFKSerializerField
from netbox.api.serializers import OrganizationalModelSerializer, PrimaryModelSerializer
from tenancy.api.serializers_.tenants import TenantSerializer
from virtualization.choices import *
from virtualization.models import Cluster, ClusterGroup, ClusterType

__all__ = (
    'ClusterGroupSerializer',
    'ClusterSerializer',
    'ClusterTypeSerializer',
)


class ClusterTypeSerializer(OrganizationalModelSerializer):

    # Related object counts
    cluster_count = RelatedObjectCountField('clusters')

    class Meta:
        model = ClusterType
        fields = [
            'id', 'url', 'display_url', 'display', 'name', 'slug', 'description', 'owner', 'comments', 'tags',
            'custom_fields', 'created', 'last_updated', 'cluster_count',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'slug', 'description', 'cluster_count')


class ClusterGroupSerializer(OrganizationalModelSerializer):

    # Related object counts
    cluster_count = RelatedObjectCountField('clusters')

    class Meta:
        model = ClusterGroup
        fields = [
            'id', 'url', 'display_url', 'display', 'name', 'slug', 'description', 'owner', 'comments', 'tags',
            'custom_fields', 'created', 'last_updated', 'cluster_count',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'slug', 'description', 'cluster_count')


class ClusterSerializer(PrimaryModelSerializer):
    type = ClusterTypeSerializer(nested=True)
    group = ClusterGroupSerializer(nested=True, required=False, allow_null=True, default=None)
    status = ChoiceField(choices=ClusterStatusChoices, required=False)
    tenant = TenantSerializer(nested=True, required=False, allow_null=True)
    scope_type = ContentTypeField(
        queryset=ContentType.objects.filter(
            model__in=LOCATION_SCOPE_TYPES
        ),
        allow_null=True,
        required=False,
        default=None
    )
    scope_id = serializers.IntegerField(allow_null=True, required=False, default=None)
    scope = GFKSerializerField(read_only=True)
    allocated_vcpus = serializers.DecimalField(
        read_only=True,
        max_digits=8,
        decimal_places=2,

    )
    allocated_memory = serializers.IntegerField(read_only=True)
    allocated_disk = serializers.IntegerField(read_only=True)

    # Related object counts
    device_count = RelatedObjectCountField('devices')
    virtualmachine_count = RelatedObjectCountField('virtual_machines')

    class Meta:
        model = Cluster
        fields = [
            'id', 'url', 'display_url', 'display', 'name', 'type', 'group', 'status', 'tenant', 'scope_type',
            'scope_id', 'scope', 'description', 'owner', 'comments', 'tags', 'custom_fields', 'created', 'last_updated',
            'device_count', 'virtualmachine_count', 'allocated_vcpus', 'allocated_memory', 'allocated_disk'
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'description', 'virtualmachine_count')
