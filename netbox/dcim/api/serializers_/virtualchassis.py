from rest_framework import serializers

from dcim.models import VirtualChassis
from netbox.api.serializers import PrimaryModelSerializer

from .nested import NestedDeviceSerializer

__all__ = (
    'VirtualChassisSerializer',
)


class VirtualChassisSerializer(PrimaryModelSerializer):
    master = NestedDeviceSerializer(required=False, allow_null=True, default=None)
    members = NestedDeviceSerializer(many=True, read_only=True)

    # Counter fields
    member_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = VirtualChassis
        fields = [
            'id', 'url', 'display_url', 'display', 'name', 'domain', 'master', 'description', 'owner', 'comments',
            'tags', 'custom_fields', 'created', 'last_updated', 'member_count', 'members',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'master', 'description', 'member_count')
