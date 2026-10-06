from functools import cached_property

from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from core.models import ObjectType
from extras.models import Tag, TaggedItem
from netbox.api.exceptions import SerializerNotFound
from netbox.api.fields import ContentTypeField, RelatedObjectCountField
from netbox.api.serializers import BaseModelSerializer, ChangeLogMessageSerializer, ValidatedModelSerializer
from users.api.serializers_.mixins import OwnerMixin
from utilities.api import get_serializer_for_model

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

    @cached_property
    def _object_serializers(self):
        return {}

    @extend_schema_field(serializers.JSONField())
    def get_object(self, obj):
        """
        Serialize a nested representation of the tagged object.
        """
        try:
            serializer_class = get_serializer_for_model(obj.content_object)
        except SerializerNotFound:
            return obj.object_repr
        if serializer_class not in self._object_serializers:
            self._object_serializers[serializer_class] = serializer_class(
                nested=True, context={'request': self.context['request']}
            )
        return self._object_serializers[serializer_class].to_representation(obj.content_object)
