from rest_framework import serializers

from dcim.models import VirtualChassis
from netbox.api.serializers import NetBoxModelSerializer
from ..nested_serializers import *

__all__ = (
    'VirtualChassisSerializer',
)


class VirtualChassisSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:virtualchassis-detail')
    master = NestedDeviceSerializer(required=False, allow_null=True, default=None)

    # Counter fields
    member_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = VirtualChassis
        fields = [
            'id', 'url', 'display', 'name', 'domain', 'master', 'description', 'comments', 'tags', 'custom_fields',
            'created', 'last_updated', 'member_count',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'master', 'description', 'member_count')
