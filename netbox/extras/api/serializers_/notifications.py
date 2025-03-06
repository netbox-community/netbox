from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from core.models import ObjectType
from extras.models import Notification, NotificationGroup, Subscription
from netbox.api.fields import ContentTypeField, SerializedPKRelatedField
from netbox.api.serializers import ValidatedModelSerializer
from users.api.serializers_.users import GroupSerializer, UserSerializer
from users.models import Group, User
from utilities.api import get_serializer_for_model

__all__ = (
    'NotificationSerializer',
    'NotificationGroupSerializer',
    'SubscriptionSerializer',
)


class NotificationSerializer(ValidatedModelSerializer):
    object_type = ContentTypeField(
        queryset=ObjectType.objects.with_feature('notifications'),
    )
    object = serializers.SerializerMethodField(read_only=True)
    user = UserSerializer(nested=True)

    class Meta:
        model = Notification
        fields = [
            'id', 'url', 'display', 'object_type', 'object_id', 'object', 'user', 'created', 'read', 'event_type',
        ]
        brief_fields = ('id', 'url', 'display', 'object_type', 'object_id', 'user', 'read', 'event_type')

    @extend_schema_field(serializers.JSONField(allow_null=True))
    def get_object(self, instance):
        serializer = get_serializer_for_model(instance.object)
        context = {'request': self.context['request']}
        return serializer(instance.object, nested=True, context=context).data


class NotificationGroupSerializer(ValidatedModelSerializer):
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
    object = serializers.SerializerMethodField(read_only=True)
    user = UserSerializer(nested=True)

    class Meta:
        model = Subscription
        fields = [
            'id', 'url', 'display', 'object_type', 'object_id', 'object', 'user', 'created',
        ]
        brief_fields = ('id', 'url', 'display', 'object_type', 'object_id', 'user')

    @extend_schema_field(serializers.JSONField(allow_null=True))
    def get_object(self, instance):
        serializer = get_serializer_for_model(instance.object)
        context = {'request': self.context['request']}
        return serializer(instance.object, nested=True, context=context).data
