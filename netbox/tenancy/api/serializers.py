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


class TenantGroupNestedSerializer(TenantGroupSerializer):

    class Meta(TenantGroupSerializer.Meta):
        pass


#
# Tenants
#

class TenantSerializer(CustomFieldSerializer, serializers.ModelSerializer):
    group = TenantGroupNestedSerializer()

    class Meta:
        model = Tenant
        fields = ['id', 'name', 'slug', 'group', 'comments', 'custom_fields']


class TenantNestedSerializer(TenantSerializer):

    class Meta(TenantSerializer.Meta):
        fields = ['id', 'name', 'slug']
