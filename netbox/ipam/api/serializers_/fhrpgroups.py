from django.contrib.contenttypes.models import ContentType
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from ipam.models import FHRPGroup, FHRPGroupAssignment
from netbox.api.fields import ContentTypeField
from netbox.api.serializers import NetBoxModelSerializer
from utilities.api import get_serializer_for_model
from .ip import IPAddressSerializer

__all__ = (
    'FHRPGroupAssignmentSerializer',
    'FHRPGroupSerializer',
)


class FHRPGroupSerializer(NetBoxModelSerializer):
    ip_addresses = IPAddressSerializer(nested=True, many=True, read_only=True)

    class Meta:
        model = FHRPGroup
        fields = [
            'id', 'name', 'url', 'display_url', 'display', 'protocol', 'group_id', 'auth_type', 'auth_key',
            'description', 'comments', 'tags', 'custom_fields', 'created', 'last_updated', 'ip_addresses',
        ]
        brief_fields = ('id', 'url', 'display', 'protocol', 'group_id', 'description')


class FHRPGroupAssignmentSerializer(NetBoxModelSerializer):
    group = FHRPGroupSerializer(nested=True)
    interface_type = ContentTypeField(
        queryset=ContentType.objects.all()
    )
    interface = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = FHRPGroupAssignment
        fields = [
            'id', 'url', 'display', 'group', 'interface_type', 'interface_id', 'interface',
            'priority', 'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'group', 'interface_type', 'interface_id', 'priority')

    @extend_schema_field(serializers.JSONField(allow_null=True))
    def get_interface(self, obj):
        if obj.interface is None:
            return None
        serializer = get_serializer_for_model(obj.interface)
        context = {'request': self.context['request']}
        return serializer(obj.interface, nested=True, context=context).data
