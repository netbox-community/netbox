from __future__ import unicode_literals

from rest_framework import serializers
from taggit_serializer.serializers import TaggitSerializer, TagListSerializerField

from extras.api.customfields import CustomFieldModelSerializer
from tenancy.models import Tenant, TenantGroup
from utilities.api import ValidatedModelSerializer, WritableNestedSerializer


#
# Tenant groups
#

class TenantGroupSerializer(ValidatedModelSerializer):

    class Meta:
        model = TenantGroup
        fields = ['id', 'name', 'slug']


class NestedTenantGroupSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='tenancy-api:tenantgroup-detail')

    class Meta:
        model = TenantGroup
        fields = ['id', 'url', 'name', 'slug']


#
# Tenants
#

class TenantSerializer(TaggitSerializer, CustomFieldModelSerializer):
    group = NestedTenantGroupSerializer(required=False)
    tags = TagListSerializerField(required=False)

    class Meta:
        model = Tenant
        fields = [
            'id', 'name', 'slug', 'group', 'description', 'comments', 'tags', 'custom_fields', 'created',
            'last_updated',
        ]


class NestedTenantSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='tenancy-api:tenant-detail')

    class Meta:
        model = Tenant
        fields = ['id', 'url', 'name', 'slug']
