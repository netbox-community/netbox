from rest_framework import serializers

from tenancy.models import Tenant, TenantGroup
from utilities.api import WritableNestedSerializer

__all__ = [
    'NestedTenantGroupSerializer',
    'NestedTenantSerializer',
]


#
# Tenants
#

class NestedTenantGroupSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='tenancy-api:tenantgroup-detail')

    class Meta:
        model = TenantGroup
        fields = ['id', 'url', 'name', 'slug']


class NestedTenantSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='tenancy-api:tenant-detail')

    class Meta:
        model = Tenant
        fields = ['id', 'url', 'name', 'slug']
