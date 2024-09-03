from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers

from netbox.api.serializers import WritableNestedSerializer
from tenancy import models

__all__ = (
    'NestedContactGroupSerializer',
    'NestedTenantGroupSerializer',
)


@extend_schema_serializer(
    exclude_fields=('contact_count',),
)
class NestedContactGroupSerializer(WritableNestedSerializer):
    contact_count = serializers.IntegerField(read_only=True)
    _depth = serializers.IntegerField(source='level', read_only=True)

    class Meta:
        model = models.ContactGroup
        fields = ['id', 'url', 'display_url', 'display', 'name', 'slug', 'contact_count', '_depth']


@extend_schema_serializer(
    exclude_fields=('tenant_count',),
)
class NestedTenantGroupSerializer(WritableNestedSerializer):
    tenant_count = serializers.IntegerField(read_only=True)
    _depth = serializers.IntegerField(source='level', read_only=True)

    class Meta:
        model = models.TenantGroup
        fields = ['id', 'url', 'display_url', 'display', 'name', 'slug', 'tenant_count', '_depth']
