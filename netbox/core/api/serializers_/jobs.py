from core.choices import *
from core.models import Job
from netbox.api.fields import ChoiceField, ContentTypeField, RelatedObjectCountField
from netbox.api.gfk_fields import GFKSerializerField
from netbox.api.serializers import BaseModelSerializer
from users.api.serializers_.users import UserSerializer

__all__ = (
    'JobSerializer',
    'NestedJobSerializer',
)


class NestedJobSerializer(BaseModelSerializer):
    """
    Represents a Job related to another Job (e.g. its parent).
    """
    status = ChoiceField(choices=JobStatusChoices, read_only=True)

    class Meta:
        model = Job
        fields = ['id', 'url', 'display_url', 'display', 'name', 'status', 'created', 'completed']


class JobSerializer(BaseModelSerializer):
    user = UserSerializer(
        nested=True,
        read_only=True
    )
    status = ChoiceField(choices=JobStatusChoices, read_only=True)
    object_type = ContentTypeField(
        read_only=True
    )
    # A plugin model can support jobs without a REST API serializer
    object = GFKSerializerField(
        read_only=True,
        allow_missing_serializer=True
    )
    notifications = ChoiceField(choices=JobNotificationChoices, read_only=True)
    parent = NestedJobSerializer(read_only=True, allow_null=True)
    # Falls back to a query where unannotated (e.g. a script's result)
    child_count = RelatedObjectCountField('children', fallback_source='children.count')

    class Meta:
        model = Job
        fields = [
            'id', 'url', 'display_url', 'display', 'object_type', 'object_id', 'object', 'name', 'status', 'created',
            'scheduled', 'interval', 'started', 'completed', 'execution_time', 'user', 'data', 'error', 'job_id',
            'queue_name', 'notifications', 'parent', 'child_count', 'log_entries',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'created', 'completed', 'user', 'status')
