from rest_framework import serializers

from dcim.models import Manufacturer
from netbox.api.fields import RelatedObjectCountField
from netbox.api.serializers import NetBoxModelSerializer

__all__ = (
    'ManufacturerSerializer',
)


class ManufacturerSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:manufacturer-detail')

    # Related object counts
    devicetype_count = RelatedObjectCountField('device_types')
    inventoryitem_count = RelatedObjectCountField('inventory_items')
    platform_count = RelatedObjectCountField('platforms')

    class Meta:
        model = Manufacturer
        fields = [
            'id', 'url', 'display', 'name', 'slug', 'description', 'tags', 'custom_fields', 'created', 'last_updated',
            'devicetype_count', 'inventoryitem_count', 'platform_count',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'slug', 'description', 'devicetype_count')
