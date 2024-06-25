from rest_framework import serializers

from core.choices import JobStatusChoices
from core.models import *
from netbox.api.fields import ChoiceField
from netbox.api.serializers import WritableNestedSerializer
from users.api.serializers import UserSerializer

__all__ = (
    'NestedDataFileSerializer',
    'NestedDataSourceSerializer',
    'NestedJobSerializer',
)


class NestedDataSourceSerializer(WritableNestedSerializer):

    class Meta:
        model = DataSource
        fields = ['id', 'url', 'display_url', 'display', 'name']


class NestedDataFileSerializer(WritableNestedSerializer):

    class Meta:
        model = DataFile
        fields = ['id', 'url', 'display_url', 'display', 'path']


class NestedJobSerializer(serializers.ModelSerializer):
    status = ChoiceField(choices=JobStatusChoices)
    user = UserSerializer(
        nested=True,
        read_only=True
    )

    class Meta:
        model = Job
        fields = ['url', 'display_url', 'created', 'completed', 'user', 'status']
