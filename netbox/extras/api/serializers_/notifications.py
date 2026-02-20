from core.models import ObjectType
from extras.models import Notification, NotificationGroup, Subscription
from netbox.api.fields import ContentTypeField, SerializedPKRelatedField
from netbox.api.gfk_fields import GFKSerializerField
from netbox.api.serializers import ChangeLogMessageSerializer, ValidatedModelSerializer
from users.api.serializers_.users import GroupSerializer, UserSerializer
from users.models import Group, User

__all__ = (
    'NotificationGroupSerializer',
    'NotificationSerializer',
    'SubscriptionSerializer',
)


class NotificationSerializer(ValidatedModelSerializer):
    object_type = ContentTypeField(
        queryset=ObjectType.objects.with_feature('notifications'),
    )
    object = GFKSerializerField(read_only=True)
    user = UserSerializer(nested=True)

    class Meta:
        model = Notification
        fields = [
            'id', 'url', 'display', 'object_type', 'object_id', 'object', 'user', 'created', 'read', 'event_type',
        ]
        brief_fields = ('id', 'url', 'display', 'object_type', 'object_id', 'user', 'read', 'event_type')


class NotificationGroupSerializer(ChangeLogMessageSerializer, ValidatedModelSerializer):
    groups = SerializedPKRelatedField(
        queryset=Group.objects.all(),
        serializer=GroupSerializer,
        nested=True,
        required=False,
        many=True
    )
    users = SerializedPKRelatedField(
        queryset=User.objects.all(),
        serializer=UserSerializer,
        nested=True,
        required=False,
        many=True
    )

    class Meta:
        model = NotificationGroup
        fields = [
            'id', 'url', 'display', 'display_url', 'name', 'description', 'groups', 'users',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'description')


class SubscriptionSerializer(ValidatedModelSerializer):
    object_type = ContentTypeField(
        queryset=ObjectType.objects.with_feature('notifications'),
    )
    object = GFKSerializerField(read_only=True)
    user = UserSerializer(nested=True)

    class Meta:
        model = Subscription
        fields = [
            'id', 'url', 'display', 'object_type', 'object_id', 'object', 'user', 'created',
        ]
        brief_fields = ('id', 'url', 'display', 'object_type', 'object_id', 'user')
