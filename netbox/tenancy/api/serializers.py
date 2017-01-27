from rest_framework import serializers

from extras.api.serializers import CustomFieldSerializer
from tenancy.models import Tenant, TenantGroup


#
# Tenant groups
#

class TenantGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = TenantGroup
        fields = ['id', 'name', 'slug']


class NestedTenantGroupSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = TenantGroup
        fields = ['id', 'url', 'name', 'slug']


#
# Tenants
#

class TenantSerializer(CustomFieldSerializer, serializers.ModelSerializer):
    group = NestedTenantGroupSerializer()

    class Meta:
        model = Tenant
        fields = ['id', 'name', 'slug', 'group', 'description', 'comments', 'custom_fields']


class NestedTenantSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Tenant
        fields = ['id', 'url', 'name', 'slug']
