from core.choices import *
from core.models import Job
from netbox.api.fields import ChoiceField, ContentTypeField
from netbox.api.serializers import BaseModelSerializer
from users.api.serializers_.users import UserSerializer

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

    class Meta:
        model = Job
        fields = [
            'id', 'url', 'display_url', 'display', 'object_type', 'object_id', 'name', 'status', 'created', 'scheduled',
            'interval', 'started', 'completed', 'user', 'data', 'error', 'job_id',
        ]
        brief_fields = ('url', 'created', 'completed', 'user', 'status')
