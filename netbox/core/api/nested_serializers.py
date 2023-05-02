from rest_framework import serializers

from core.choices import JobStatusChoices
from core.models import *
from netbox.api.fields import ChoiceField
from netbox.api.serializers import WritableNestedSerializer
from users.api.nested_serializers import NestedUserSerializer

__all__ = (
    'NestedDataFileSerializer',
    'NestedDataSourceSerializer',
    'NestedJobSerializer',
)


class NestedDataSourceSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='core-api:datasource-detail')

    class Meta:
        model = DataSource
        fields = ['id', 'url', 'display', 'name']


class NestedDataFileSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='core-api:datafile-detail')

    class Meta:
        model = DataFile
        fields = ['id', 'url', 'display', 'path']


class NestedJobSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='core-api:job-detail')
    status = ChoiceField(choices=JobStatusChoices)
    user = NestedUserSerializer(
        read_only=True
    )

    class Meta:
        model = Job
        fields = ['url', 'created', 'completed', 'user', 'status']
