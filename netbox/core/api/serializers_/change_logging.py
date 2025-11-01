from rest_framework import serializers

from core.choices import *
from core.models import ObjectChange
from netbox.api.fields import ChoiceField, ContentTypeField
from netbox.api.gfk_fields import GFKSerializerField
from netbox.api.serializers import BaseModelSerializer
from users.api.serializers_.users import UserSerializer

__all__ = (
    'ObjectChangeSerializer',
)


class ObjectChangeSerializer(BaseModelSerializer):
    user = UserSerializer(
        nested=True,
        read_only=True
    )
    action = ChoiceField(
        choices=ObjectChangeActionChoices,
        read_only=True
    )
    changed_object_type = ContentTypeField(
        read_only=True
    )
    changed_object = GFKSerializerField(
        read_only=True
    )
    object_repr = serializers.CharField(
        read_only=True
    )
    prechange_data = serializers.JSONField(
        source='prechange_data_clean',
        read_only=True,
        allow_null=True
    )
    postchange_data = serializers.JSONField(
        source='postchange_data_clean',
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = ObjectChange
        fields = [
            'id', 'url', 'display_url', 'display', 'time', 'user', 'user_name', 'request_id', 'action',
            'changed_object_type', 'changed_object_id', 'changed_object', 'object_repr', 'message',
            'prechange_data', 'postchange_data',
        ]
