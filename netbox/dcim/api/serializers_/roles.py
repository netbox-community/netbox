from rest_framework import serializers

from dcim.models import DeviceRole, InventoryItemRole
from extras.api.serializers_.configtemplates import ConfigTemplateSerializer
from netbox.api.fields import RelatedObjectCountField
from netbox.api.serializers import NetBoxModelSerializer

__all__ = (
    'DeviceRoleSerializer',
    'InventoryItemRoleSerializer',
)


class DeviceRoleSerializer(NetBoxModelSerializer):
    config_template = ConfigTemplateSerializer(nested=True, required=False, allow_null=True, default=None)

    # Related object counts
    device_count = RelatedObjectCountField('devices')
    virtualmachine_count = RelatedObjectCountField('virtual_machines')

    class Meta:
        model = DeviceRole
        fields = [
            'id', 'url', 'display_url', 'display', 'name', 'slug', 'color', 'vm_role', 'config_template',
            'description', 'tags', 'custom_fields', 'created', 'last_updated', 'device_count', 'virtualmachine_count',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'slug', 'description', 'device_count', 'virtualmachine_count')


class InventoryItemRoleSerializer(NetBoxModelSerializer):

    # Related object counts
    inventoryitem_count = RelatedObjectCountField('inventory_items')

    class Meta:
        model = InventoryItemRole
        fields = [
            'id', 'url', 'display_url', 'display', 'name', 'slug', 'color', 'description', 'tags', 'custom_fields',
            'created', 'last_updated', 'inventoryitem_count',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'slug', 'description', 'inventoryitem_count')
