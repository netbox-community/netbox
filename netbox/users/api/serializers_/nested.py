from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field

from netbox.api.serializers import WritableNestedSerializer
from users import models

__all__ = (
    'NestedGroupSerializer',
    'NestedUserSerializer',
)


class NestedGroupSerializer(WritableNestedSerializer):

    class Meta:
        model = models.Group
        fields = ['id', 'url', 'display_url', 'display', 'name']


class NestedUserSerializer(WritableNestedSerializer):

    class Meta:
        model = models.User
        fields = ['id', 'url', 'display_url', 'display', 'username']

    @extend_schema_field(OpenApiTypes.STR)
    def get_display(self, obj):
        if full_name := obj.get_full_name():
            return f"{obj.username} ({full_name})"
        return obj.username
