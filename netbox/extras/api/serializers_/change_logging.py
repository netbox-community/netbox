from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from extras.choices import *
from extras.models import ObjectChange
from netbox.api.exceptions import SerializerNotFound
from netbox.api.fields import ChoiceField, ContentTypeField
from netbox.api.serializers import BaseModelSerializer
from users.api.serializers_.users import UserSerializer
from utilities.api import get_serializer_for_model

__all__ = (
    'ObjectChangeSerializer',
)


class ObjectChangeSerializer(BaseModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='extras-api:objectchange-detail')
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
    changed_object = serializers.SerializerMethodField(
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
            'id', 'url', 'display', 'time', 'user', 'user_name', 'request_id', 'action', 'changed_object_type',
            'changed_object_id', 'changed_object', 'prechange_data', 'postchange_data',
        ]

    @extend_schema_field(serializers.JSONField(allow_null=True))
    def get_changed_object(self, obj):
        """
        Serialize a nested representation of the changed object.
        """
        if obj.changed_object is None:
            return None

        try:
            serializer = get_serializer_for_model(obj.changed_object)
        except SerializerNotFound:
            return obj.object_repr
        data = serializer(obj.changed_object, nested=True, context={'request': self.context['request']}).data

        return data
