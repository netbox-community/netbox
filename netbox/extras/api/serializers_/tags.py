from rest_framework import serializers

from core.models import ContentType
from extras.models import Tag
from netbox.api.fields import ContentTypeField, RelatedObjectCountField
from netbox.api.serializers import ValidatedModelSerializer

__all__ = (
    'TagSerializer',
)


class TagSerializer(ValidatedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='extras-api:tag-detail')
    object_types = ContentTypeField(
        queryset=ContentType.objects.with_feature('tags'),
        many=True,
        required=False
    )

    # Related object counts
    tagged_items = RelatedObjectCountField('extras_taggeditem_items')

    class Meta:
        model = Tag
        fields = [
            'id', 'url', 'display', 'name', 'slug', 'color', 'description', 'object_types', 'tagged_items', 'created',
            'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'slug', 'color', 'description')
