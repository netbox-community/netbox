from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from core.models import ObjectType
from extras.models import Bookmark
from netbox.api.fields import ContentTypeField
from netbox.api.serializers import ValidatedModelSerializer
from users.api.serializers_.users import UserSerializer
from utilities.api import get_serializer_for_model

__all__ = (
    'BookmarkSerializer',
)


class BookmarkSerializer(ValidatedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='extras-api:bookmark-detail')
    object_type = ContentTypeField(
        queryset=ObjectType.objects.with_feature('bookmarks'),
    )
    object = serializers.SerializerMethodField(read_only=True)
    user = UserSerializer(nested=True)

    class Meta:
        model = Bookmark
        fields = [
            'id', 'url', 'display', 'object_type', 'object_id', 'object', 'user', 'created',
        ]
        brief_fields = ('id', 'url', 'display', 'object_id', 'object_type')

    @extend_schema_field(serializers.JSONField(allow_null=True))
    def get_object(self, instance):
        serializer = get_serializer_for_model(instance.object)
        context = {'request': self.context['request']}
        return serializer(instance.object, nested=True, context=context).data
