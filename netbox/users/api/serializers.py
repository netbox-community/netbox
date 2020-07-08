from django.contrib.auth.models import Group, User
from django.contrib.contenttypes.models import ContentType

from users.models import ObjectPermission
from utilities.api import ContentTypeField, SerializedPKRelatedField, ValidatedModelSerializer
from .nested_serializers import *


class ObjectPermissionSerializer(ValidatedModelSerializer):
    object_types = ContentTypeField(
        queryset=ContentType.objects.all(),
        many=True
    )
    groups = SerializedPKRelatedField(
        queryset=Group.objects.all(),
        serializer=NestedGroupSerializer,
        required=False,
        many=True
    )
    users = SerializedPKRelatedField(
        queryset=User.objects.all(),
        serializer=NestedUserSerializer,
        required=False,
        many=True
    )

    class Meta:
        model = ObjectPermission
        fields = ('id', 'name', 'enabled', 'object_types', 'groups', 'users', 'actions', 'constraints')
