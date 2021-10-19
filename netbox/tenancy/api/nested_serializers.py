from rest_framework import serializers

from netbox.api import WritableNestedSerializer
from tenancy.models import *

__all__ = [
    'NestedContactSerializer',
    'NestedContactGroupSerializer',
    'NestedContactRoleSerializer',
    'NestedTenantGroupSerializer',
    'NestedTenantSerializer',
]


#
# Tenants
#

class NestedTenantGroupSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='tenancy-api:tenantgroup-detail')
    tenant_count = serializers.IntegerField(read_only=True)
    _depth = serializers.IntegerField(source='level', read_only=True)

    class Meta:
        model = TenantGroup
        fields = ['id', 'url', 'display', 'name', 'slug', 'tenant_count', '_depth']


class NestedTenantSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='tenancy-api:tenant-detail')

    class Meta:
        model = Tenant
        fields = ['id', 'url', 'display', 'name', 'slug']


#
# Contacts
#

class NestedContactGroupSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='tenancy-api:contactgroup-detail')
    contact_count = serializers.IntegerField(read_only=True)
    _depth = serializers.IntegerField(source='level', read_only=True)

    class Meta:
        model = ContactGroup
        fields = ['id', 'url', 'display', 'name', 'slug', 'contact_count', '_depth']


class NestedContactRoleSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='tenancy-api:contactrole-detail')

    class Meta:
        model = ContactRole
        fields = ['id', 'url', 'display', 'name', 'slug']


class NestedContactSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='tenancy-api:contact-detail')

    class Meta:
        model = Contact
        fields = ['id', 'url', 'display', 'name']
