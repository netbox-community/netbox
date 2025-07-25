from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from core.models import ObjectType
from extras.models import Tag, TaggedItem
from netbox.api.exceptions import SerializerNotFound
from netbox.api.fields import ContentTypeField, RelatedObjectCountField
from netbox.api.serializers import BaseModelSerializer, ChangeLogMessageSerializer, ValidatedModelSerializer
from utilities.api import get_serializer_for_model

__all__ = (
    'TagSerializer',
    'TaggedItemSerializer',
)


class TagSerializer(ChangeLogMessageSerializer, ValidatedModelSerializer):
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
    object = serializers.SerializerMethodField(
        read_only=True
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

    @extend_schema_field(serializers.JSONField())
    def get_object(self, obj):
        """
        Serialize a nested representation of the tagged object.
        """
        try:
            serializer = get_serializer_for_model(obj.content_object)
        except SerializerNotFound:
            return obj.object_repr
        data = serializer(obj.content_object, nested=True, context={'request': self.context['request']}).data

        return data
