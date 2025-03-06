from core.models import ObjectType
from extras.models import Tag
from netbox.api.fields import ContentTypeField, RelatedObjectCountField
from netbox.api.serializers import ValidatedModelSerializer

__all__ = (
    'TagSerializer',
)


class TagSerializer(ValidatedModelSerializer):
    object_types = ContentTypeField(
        queryset=ObjectType.objects.with_feature('tags'),
        many=True,
        required=False
    )

    # Related object counts
    tagged_items = RelatedObjectCountField('extras_taggeditem_items')

    class Meta:
        model = Tag
        fields = [
            'id', 'url', 'display_url', 'display', 'name', 'slug', 'color', 'description', 'object_types',
            'tagged_items', 'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'slug', 'color', 'description')
