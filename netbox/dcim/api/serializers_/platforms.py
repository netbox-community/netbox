from rest_framework import serializers

from dcim.models import Platform
from extras.api.serializers_.configtemplates import ConfigTemplateSerializer
from netbox.api.fields import RelatedObjectCountField
from netbox.api.serializers import NetBoxModelSerializer
from .manufacturers import ManufacturerSerializer

__all__ = (
    'PlatformSerializer',
)


class PlatformSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:platform-detail')
    manufacturer = ManufacturerSerializer(nested=True, required=False, allow_null=True)
    config_template = ConfigTemplateSerializer(nested=True, required=False, allow_null=True, default=None)

    # Related object counts
    device_count = RelatedObjectCountField('devices')
    virtualmachine_count = RelatedObjectCountField('virtual_machines')

    class Meta:
        model = Platform
        fields = [
            'id', 'url', 'display', 'name', 'slug', 'manufacturer', 'config_template', 'description', 'tags',
            'custom_fields', 'created', 'last_updated', 'device_count', 'virtualmachine_count',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'slug', 'description', 'device_count', 'virtualmachine_count')
