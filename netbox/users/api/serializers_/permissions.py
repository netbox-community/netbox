from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from netbox.api.fields import ContentTypeField, SerializedPKRelatedField
from netbox.api.serializers import ValidatedModelSerializer
from users.models import ObjectPermission
from ..nested_serializers import *

__all__ = (
    'ObjectPermissionSerializer',
)


class ObjectPermissionSerializer(ValidatedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='users-api:objectpermission-detail')
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
        queryset=get_user_model().objects.all(),
        serializer=NestedUserSerializer,
        required=False,
        many=True
    )

    class Meta:
        model = ObjectPermission
        fields = (
            'id', 'url', 'display', 'name', 'description', 'enabled', 'object_types', 'groups', 'users', 'actions',
            'constraints',
        )
        brief_fields = (
            'id', 'url', 'display', 'name', 'description', 'enabled', 'object_types', 'groups', 'users', 'actions',
        )
