from django.contrib.contenttypes.models import ContentType
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from ipam.models import FHRPGroup, FHRPGroupAssignment
from netbox.api.fields import ContentTypeField
from netbox.api.serializers import NetBoxModelSerializer
from netbox.constants import NESTED_SERIALIZER_PREFIX
from utilities.api import get_serializer_for_model
from .ip import IPAddressSerializer

__all__ = (
    'FHRPGroupAssignmentSerializer',
    'FHRPGroupSerializer',
)


class FHRPGroupSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:fhrpgroup-detail')
    ip_addresses = IPAddressSerializer(nested=True, many=True, read_only=True)

    class Meta:
        model = FHRPGroup
        fields = [
            'id', 'name', 'url', 'display', 'protocol', 'group_id', 'auth_type', 'auth_key', 'description', 'comments',
            'tags', 'custom_fields', 'created', 'last_updated', 'ip_addresses',
        ]
        brief_fields = ('id', 'url', 'display', 'protocol', 'group_id', 'description')


class FHRPGroupAssignmentSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:fhrpgroupassignment-detail')
    group = FHRPGroupSerializer(nested=True)
    interface_type = ContentTypeField(
        queryset=ContentType.objects.all()
    )
    interface = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = FHRPGroupAssignment
        fields = [
            'id', 'url', 'display', 'group', 'interface_type', 'interface_id', 'interface', 'priority', 'created',
            'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'group', 'interface_type', 'interface_id', 'priority')

    @extend_schema_field(serializers.JSONField(allow_null=True))
    def get_interface(self, obj):
        if obj.interface is None:
            return None
        serializer = get_serializer_for_model(obj.interface, prefix=NESTED_SERIALIZER_PREFIX)
        context = {'request': self.context['request']}
        return serializer(obj.interface, context=context).data
