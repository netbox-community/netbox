from django.contrib.contenttypes.models import ContentType

from ipam.models import FHRPGroup, FHRPGroupAssignment
from netbox.api.fields import ContentTypeField
from netbox.api.gfk_fields import GFKSerializerField
from netbox.api.serializers import NetBoxModelSerializer, PrimaryModelSerializer

from .ip import IPAddressSerializer

__all__ = (
    'FHRPGroupAssignmentSerializer',
    'FHRPGroupSerializer',
)


class FHRPGroupSerializer(PrimaryModelSerializer):
    ip_addresses = IPAddressSerializer(nested=True, many=True, read_only=True)

    class Meta:
        model = FHRPGroup
        fields = [
            'id', 'name', 'url', 'display_url', 'display', 'protocol', 'group_id', 'auth_type', 'auth_key',
            'description', 'owner', 'comments', 'tags', 'custom_fields', 'created', 'last_updated', 'ip_addresses',
        ]
        brief_fields = ('id', 'url', 'display', 'protocol', 'group_id', 'description')


class FHRPGroupAssignmentSerializer(NetBoxModelSerializer):
    group = FHRPGroupSerializer(nested=True)
    interface_type = ContentTypeField(
        queryset=ContentType.objects.all()
    )
    interface = GFKSerializerField(read_only=True)

    class Meta:
        model = FHRPGroupAssignment
        fields = [
            'id', 'url', 'display', 'group', 'interface_type', 'interface_id', 'interface',
            'priority', 'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'group', 'interface_type', 'interface_id', 'priority')
