from django.contrib.auth.models import Group, User
from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from users.models import ObjectPermission
from utilities.api import ContentTypeField, WritableNestedSerializer

__all__ = [
    'NestedGroupSerializer',
    'NestedObjectPermissionSerializer',
    'NestedUserSerializer',
]


class NestedGroupSerializer(WritableNestedSerializer):

    class Meta:
        model = Group
        fields = ['id', 'name']


class NestedUserSerializer(WritableNestedSerializer):

    class Meta:
        model = User
        fields = ['id', 'username']


class NestedObjectPermissionSerializer(WritableNestedSerializer):
    object_types = ContentTypeField(
        queryset=ContentType.objects.all(),
        many=True
    )
    groups = serializers.SerializerMethodField(read_only=True)
    users = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ObjectPermission
        fields = ['id', 'object_types', 'groups', 'users', 'actions']

    def get_groups(self, obj):
        return [g.name for g in obj.groups.all()]

    def get_users(self, obj):
        return [u.username for u in obj.users.all()]
