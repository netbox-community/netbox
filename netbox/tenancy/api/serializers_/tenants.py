from rest_framework import serializers

from netbox.api.fields import RelatedObjectCountField
from netbox.api.serializers import NestedGroupModelSerializer, NetBoxModelSerializer
from tenancy.models import Tenant, TenantGroup
from .nested import NestedTenantGroupSerializer

__all__ = (
    'TenantGroupSerializer',
    'TenantSerializer',
)


class TenantGroupSerializer(NestedGroupModelSerializer):
    parent = NestedTenantGroupSerializer(required=False, allow_null=True)
    tenant_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = TenantGroup
        fields = [
            'id', 'url', 'display_url', 'display', 'name', 'slug', 'parent', 'description', 'tags', 'custom_fields',
            'created', 'last_updated', 'tenant_count', '_depth',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'slug', 'description', 'tenant_count', '_depth')


class TenantSerializer(NetBoxModelSerializer):
    group = TenantGroupSerializer(nested=True, required=False, allow_null=True, default=None)

    # Related object counts
    circuit_count = RelatedObjectCountField('circuits')
    device_count = RelatedObjectCountField('devices')
    rack_count = RelatedObjectCountField('racks')
    site_count = RelatedObjectCountField('sites')
    ipaddress_count = RelatedObjectCountField('ip_addresses')
    prefix_count = RelatedObjectCountField('prefixes')
    vlan_count = RelatedObjectCountField('vlans')
    vrf_count = RelatedObjectCountField('vrfs')
    virtualmachine_count = RelatedObjectCountField('virtual_machines')
    cluster_count = RelatedObjectCountField('clusters')

    class Meta:
        model = Tenant
        fields = [
            'id', 'url', 'display_url', 'display', 'name', 'slug', 'group', 'description', 'comments', 'tags',
            'custom_fields', 'created', 'last_updated', 'circuit_count', 'device_count', 'ipaddress_count',
            'prefix_count', 'rack_count', 'site_count', 'virtualmachine_count', 'vlan_count', 'vrf_count',
            'cluster_count',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'slug', 'description')
