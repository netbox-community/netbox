from core.models import ObjectType
from extras.models import Bookmark
from netbox.api.fields import ContentTypeField
from netbox.api.gfk_fields import GFKSerializerField
from netbox.api.serializers import ValidatedModelSerializer
from users.api.serializers_.users import UserSerializer

__all__ = (
    'BookmarkSerializer',
)


class BookmarkSerializer(ValidatedModelSerializer):
    object_type = ContentTypeField(
        queryset=ObjectType.objects.with_feature('bookmarks'),
    )
    object = GFKSerializerField(read_only=True)
    user = UserSerializer(nested=True)

    class Meta:
        model = Bookmark
        fields = [
            'id', 'url', 'display', 'object_type', 'object_id', 'object', 'user', 'created',
        ]
        brief_fields = ('id', 'url', 'display', 'object_id', 'object_type')
