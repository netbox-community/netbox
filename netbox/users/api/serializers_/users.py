from django.contrib.auth import get_user_model
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from netbox.api.fields import SerializedPKRelatedField
from netbox.api.serializers import ValidatedModelSerializer
from users.models import Group, ObjectPermission
from .permissions import ObjectPermissionSerializer

__all__ = (
    'GroupSerializer',
    'UserSerializer',
)


class GroupSerializer(ValidatedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='users-api:group-detail')
    user_count = serializers.IntegerField(read_only=True)
    permissions = SerializedPKRelatedField(
        source='object_permissions',
        queryset=ObjectPermission.objects.all(),
        serializer=ObjectPermissionSerializer,
        nested=True,
        required=False,
        many=True
    )

    class Meta:
        model = Group
        fields = ('id', 'url', 'display', 'name', 'permissions', 'user_count')
        brief_fields = ('id', 'url', 'display', 'name', 'description')


class UserSerializer(ValidatedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='users-api:user-detail')
    groups = SerializedPKRelatedField(
        queryset=Group.objects.all(),
        serializer=GroupSerializer,
        nested=True,
        required=False,
        many=True
    )
    permissions = SerializedPKRelatedField(
        source='object_permissions',
        queryset=ObjectPermission.objects.all(),
        serializer=ObjectPermissionSerializer,
        nested=True,
        required=False,
        many=True
    )

    class Meta:
        model = get_user_model()
        fields = (
            'id', 'url', 'display', 'username', 'password', 'first_name', 'last_name', 'email', 'is_staff', 'is_active',
            'date_joined', 'last_login', 'groups', 'permissions',
        )
        brief_fields = ('id', 'url', 'display', 'username')
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        """
        Extract the password from validated data and set it separately to ensure proper hash generation.
        """
        password = validated_data.pop('password')
        user = super().create(validated_data)
        user.set_password(password)
        user.save()

        return user

    def update(self, instance, validated_data):
        """
        Ensure proper updated password hash generation.
        """
        password = validated_data.pop('password', None)
        if password is not None:
            instance.set_password(password)

        return super().update(instance, validated_data)

    @extend_schema_field(OpenApiTypes.STR)
    def get_display(self, obj):
        if full_name := obj.get_full_name():
            return f"{obj.username} ({full_name})"
        return obj.username
