from rest_framework import serializers

from dcim.models import Platform
from extras.api.serializers_.configtemplates import ConfigTemplateSerializer
from netbox.api.serializers import NestedGroupModelSerializer
from .manufacturers import ManufacturerSerializer
from .nested import NestedPlatformSerializer

__all__ = (
    'PlatformSerializer',
)


class PlatformSerializer(NestedGroupModelSerializer):
    parent = NestedPlatformSerializer(required=False, allow_null=True, default=None)
    manufacturer = ManufacturerSerializer(nested=True, required=False, allow_null=True)
    config_template = ConfigTemplateSerializer(nested=True, required=False, allow_null=True, default=None)

    # Related object counts
    device_count = serializers.IntegerField(read_only=True, default=0)
    virtualmachine_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Platform
        fields = [
            'id', 'url', 'display_url', 'display', 'parent', 'name', 'slug', 'manufacturer', 'config_template',
            'description', 'comments', 'tags', 'custom_fields', 'created', 'last_updated', 'device_count',
            'virtualmachine_count', '_depth',
        ]
        brief_fields = (
            'id', 'url', 'display', 'name', 'slug', 'description', 'device_count', 'virtualmachine_count', '_depth',
        )
