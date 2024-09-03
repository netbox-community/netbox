import warnings

from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from core.models import ObjectType
from netbox.api.fields import ContentTypeField
from netbox.api.serializers import WritableNestedSerializer
from serializers_.nested import NestedGroupSerializer, NestedUserSerializer
from users.models import ObjectPermission, Token

__all__ = [
    'NestedGroupSerializer',
    'NestedObjectPermissionSerializer',
    'NestedTokenSerializer',
    'NestedUserSerializer',
]

# TODO: Remove in v4.2
warnings.warn(
    f"Dedicated nested serializers will be removed in NetBox v4.2. Use Serializer(nested=True) instead.",
    DeprecationWarning
)


class NestedTokenSerializer(WritableNestedSerializer):

    class Meta:
        model = Token
        fields = ['id', 'url', 'display_url', 'display', 'key', 'write_enabled']


class NestedObjectPermissionSerializer(WritableNestedSerializer):
    object_types = ContentTypeField(
        queryset=ObjectType.objects.all(),
        many=True
    )
    groups = serializers.SerializerMethodField(read_only=True)
    users = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ObjectPermission
        fields = [
            'id', 'url', 'display_url', 'display', 'name', 'enabled', 'object_types', 'groups', 'users', 'actions'
        ]

    @extend_schema_field(serializers.ListField)
    def get_groups(self, obj):
        return [g.name for g in obj.groups.all()]

    @extend_schema_field(serializers.ListField)
    def get_users(self, obj):
        return [u.username for u in obj.users.all()]
