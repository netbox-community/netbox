from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from core.choices import *
from core.models import Job
from netbox.api.exceptions import SerializerNotFound
from netbox.api.fields import ChoiceField, ContentTypeField
from netbox.api.serializers import BaseModelSerializer
from users.api.serializers_.users import UserSerializer
from utilities.api import get_serializer_for_model

__all__ = (
    'JobSerializer',
)


class JobSerializer(BaseModelSerializer):
    user = UserSerializer(
        nested=True,
        read_only=True
    )
    status = ChoiceField(choices=JobStatusChoices, read_only=True)
    object_type = ContentTypeField(
        read_only=True
    )
    object = serializers.SerializerMethodField(
        read_only=True
    )

    class Meta:
        model = Job
        fields = [
            'id', 'url', 'display_url', 'display', 'object_type', 'object_id', 'object', 'name', 'status', 'created',
            'scheduled', 'interval', 'started', 'completed', 'user', 'data', 'error', 'job_id', 'queue_name',
            'log_entries',
        ]
        brief_fields = ('url', 'created', 'completed', 'user', 'status')

    @extend_schema_field(serializers.JSONField(allow_null=True))
    def get_object(self, obj):
        """
        Serialize a nested representation of the object.
        """
        if obj.object is None:
            return None
        try:
            serializer = get_serializer_for_model(obj.object)
        except SerializerNotFound:
            return obj.object_repr
        context = {'request': self.context['request']}
        return serializer(obj.object, nested=True, context=context).data
