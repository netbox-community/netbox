from core.models import ObjectType
from extras.models import Tag, TaggedItem
from netbox.api.fields import ContentTypeField, RelatedObjectCountField
from netbox.api.gfk_fields import GFKSerializerField
from netbox.api.serializers import BaseModelSerializer, ChangeLogMessageSerializer, ValidatedModelSerializer
from users.api.serializers_.mixins import OwnerMixin

__all__ = (
    'TagSerializer',
    'TaggedItemSerializer',
)


class TagSerializer(OwnerMixin, ChangeLogMessageSerializer, ValidatedModelSerializer):
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
            'id', 'url', 'display_url', 'display', 'name', 'slug', 'color', 'description', 'weight',
            'object_types', 'tagged_items', 'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'slug', 'color', 'description')


class TaggedItemSerializer(BaseModelSerializer):
    object_type = ContentTypeField(
        source='content_type',
        read_only=True
    )
    # A plugin model can support tags without a REST API serializer
    object = GFKSerializerField(
        source='content_object',
        read_only=True,
        allow_missing_serializer=True
    )
    tag = TagSerializer(
        nested=True,
        read_only=True
    )

    class Meta:
        model = TaggedItem
        fields = [
            'id', 'url', 'display', 'object_type', 'object_id', 'object', 'tag',
        ]
        brief_fields = ('id', 'url', 'display', 'object_type', 'object_id', 'object', 'tag')
