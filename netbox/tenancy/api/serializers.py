from rest_framework import serializers
from taggit_serializer.serializers import TaggitSerializer, TagListSerializerField

from extras.api.customfields import CustomFieldModelSerializer
from tenancy.models import Tenant, TenantGroup
from utilities.api import ValidatedModelSerializer
from .nested_serializers import *


#
# Tenants
#

class TenantGroupSerializer(ValidatedModelSerializer):
    parent = NestedTenantGroupSerializer(required=False, allow_null=True)
    tenant_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = TenantGroup
        fields = ['id', 'name', 'slug', 'parent', 'tenant_count']


class TenantSerializer(TaggitSerializer, CustomFieldModelSerializer):
    group = NestedTenantGroupSerializer(required=False)
    tags = TagListSerializerField(required=False)
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
            'id', 'name', 'slug', 'group', 'description', 'comments', 'tags', 'custom_fields', 'created',
            'last_updated', 'circuit_count', 'device_count', 'ipaddress_count', 'prefix_count', 'rack_count',
            'site_count', 'virtualmachine_count', 'vlan_count', 'vrf_count', 'cluster_count',
        ]
