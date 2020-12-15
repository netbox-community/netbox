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
    tenant_count = serializers.IntegerField(read_only=True)
    _depth = serializers.IntegerField(source='level', read_only=True)

    class Meta:
        model = TenantGroup
        fields = ['id', 'url', 'name', 'slug', 'parent', 'description', 'tenant_count', '_depth']


class TenantSerializer(TaggedObjectSerializer, CustomFieldModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='tenancy-api:tenant-detail')
    group = NestedTenantGroupSerializer(required=False)
    circuit_count = serializers.IntegerField(read_only=True)
    device_count = serializers.IntegerField(read_only=True)
    ipaddress_count = serializers.IntegerField(read_only=True)
    prefix_count = serializers.IntegerField(read_only=True)
    rack_count = serializers.IntegerField(read_only=True)
    site_count = serializers.IntegerField(read_only=True)
    virtualmachine_count = serializers.IntegerField(read_only=True)
    vlan_count = serializers.IntegerField(read_only=True)
    vrf_count = serializers.IntegerField(read_only=True)
    cluster_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Tenant
        fields = [
            'id', 'url', 'name', 'slug', 'group', 'description', 'comments', 'tags', 'custom_fields', 'created',
            'last_updated', 'circuit_count', 'device_count', 'ipaddress_count', 'prefix_count', 'rack_count',
            'site_count', 'virtualmachine_count', 'vlan_count', 'vrf_count', 'cluster_count',
        ]
