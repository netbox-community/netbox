from rest_framework import serializers

from extras.api.serializers import CustomFieldModelSerializer
from tenancy.models import Tenant, TenantGroup


#
# Tenant groups
#

class TenantGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = TenantGroup
        fields = ['id', 'name', 'slug']


class NestedTenantGroupSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='tenancy-api:tenantgroup-detail')

    class Meta:
        model = TenantGroup
        fields = ['id', 'url', 'name', 'slug']


#
# Tenants
#

class TenantSerializer(CustomFieldModelSerializer):
    group = NestedTenantGroupSerializer()

    class Meta:
        model = Tenant
        fields = ['id', 'name', 'slug', 'group', 'description', 'comments', 'custom_fields']


class NestedTenantSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='tenancy-api:tenant-detail')

    class Meta:
        model = Tenant
        fields = ['id', 'url', 'name', 'slug']


class WritableTenantSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tenant
        fields = ['id', 'name', 'slug', 'group', 'description', 'comments']
