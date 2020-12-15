from rest_framework import serializers

from extras.api.customfields import CustomFieldModelSerializer
from extras.api.serializers import TaggedObjectSerializer
from netbox.api import ValidatedModelSerializer
from tenancy.models import Tenant, TenantGroup
from .nested_serializers import *


#
# Tenants
#

class TenantGroupSerializer(ValidatedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='tenancy-api:tenantgroup-detail')
    parent = NestedTenantGroupSerializer(required=False, allow_null=True)
    tenant_count = serializers.IntegerField(read_only=True, default=0)
    _depth = serializers.IntegerField(source='level', read_only=True)

    class Meta:
        model = TenantGroup
        fields = ['id', 'url', 'name', 'slug', 'parent', 'description', 'tenant_count', '_depth']


class TenantSerializer(TaggedObjectSerializer, CustomFieldModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='tenancy-api:tenant-detail')
    group = NestedTenantGroupSerializer(required=False)
    circuit_count = serializers.IntegerField(read_only=True, default=0)
    device_count = serializers.IntegerField(read_only=True, default=0)
    ipaddress_count = serializers.IntegerField(read_only=True, default=0)
    prefix_count = serializers.IntegerField(read_only=True, default=0)
    rack_count = serializers.IntegerField(read_only=True, default=0)
    site_count = serializers.IntegerField(read_only=True, default=0)
    virtualmachine_count = serializers.IntegerField(read_only=True, default=0)
    vlan_count = serializers.IntegerField(read_only=True, default=0)
    vrf_count = serializers.IntegerField(read_only=True, default=0)
    cluster_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Tenant
        fields = [
            'id', 'url', 'name', 'slug', 'group', 'description', 'comments', 'tags', 'custom_fields', 'created',
            'last_updated', 'circuit_count', 'device_count', 'ipaddress_count', 'prefix_count', 'rack_count',
            'site_count', 'virtualmachine_count', 'vlan_count', 'vrf_count', 'cluster_count',
        ]
