from rest_framework import serializers

from dcim.api.serializers_.sites import SiteSerializer
from netbox.api.fields import ChoiceField, RelatedObjectCountField
from netbox.api.serializers import NetBoxModelSerializer
from tenancy.api.serializers_.tenants import TenantSerializer
from virtualization.choices import *
from virtualization.models import Cluster, ClusterGroup, ClusterType

__all__ = (
    'ClusterGroupSerializer',
    'ClusterSerializer',
    'ClusterTypeSerializer',
)


class ClusterTypeSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='virtualization-api:clustertype-detail')

    # Related object counts
    cluster_count = RelatedObjectCountField('clusters')

    class Meta:
        model = ClusterType
        fields = [
            'id', 'url', 'display', 'name', 'slug', 'description', 'tags', 'custom_fields', 'created', 'last_updated',
            'cluster_count',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'slug', 'description', 'cluster_count')


class ClusterGroupSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='virtualization-api:clustergroup-detail')

    # Related object counts
    cluster_count = RelatedObjectCountField('clusters')

    class Meta:
        model = ClusterGroup
        fields = [
            'id', 'url', 'display', 'name', 'slug', 'description', 'tags', 'custom_fields', 'created', 'last_updated',
            'cluster_count',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'slug', 'description', 'cluster_count')


class ClusterSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='virtualization-api:cluster-detail')
    type = ClusterTypeSerializer(nested=True)
    group = ClusterGroupSerializer(nested=True, required=False, allow_null=True, default=None)
    status = ChoiceField(choices=ClusterStatusChoices, required=False)
    tenant = TenantSerializer(nested=True, required=False, allow_null=True)
    site = SiteSerializer(nested=True, required=False, allow_null=True, default=None)

    # Related object counts
    device_count = RelatedObjectCountField('devices')
    virtualmachine_count = RelatedObjectCountField('virtual_machines')

    class Meta:
        model = Cluster
        fields = [
            'id', 'url', 'display', 'name', 'type', 'group', 'status', 'tenant', 'site', 'description', 'comments',
            'tags', 'custom_fields', 'created', 'last_updated', 'device_count', 'virtualmachine_count',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'description', 'virtualmachine_count')
