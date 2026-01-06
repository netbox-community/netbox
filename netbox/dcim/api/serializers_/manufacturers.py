from dcim.models import Manufacturer
from netbox.api.fields import RelatedObjectCountField
from netbox.api.serializers import OrganizationalModelSerializer

__all__ = (
    'ManufacturerSerializer',
)


class ManufacturerSerializer(OrganizationalModelSerializer):

    # Related object counts
    devicetype_count = RelatedObjectCountField('device_types')
    moduletype_count = RelatedObjectCountField('module_types')
    inventoryitem_count = RelatedObjectCountField('inventory_items')
    platform_count = RelatedObjectCountField('platforms')

    class Meta:
        model = Manufacturer
        fields = [
            'id', 'url', 'display_url', 'display', 'name', 'slug', 'description', 'owner', 'comments', 'tags',
            'custom_fields', 'created', 'last_updated', 'devicetype_count', 'moduletype_count', 'inventoryitem_count',
            'platform_count',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'slug', 'description')
