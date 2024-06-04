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
    url = serializers.HyperlinkedIdentityField(view_name='core-api:datasource-detail')
    display_url = serializers.HyperlinkedIdentityField(view_name='core:datasource')

    class Meta:
        model = DataSource
        fields = ['id', 'url', 'display_url', 'display', 'name']


class NestedDataFileSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='core-api:datafile-detail')
    display_url = serializers.HyperlinkedIdentityField(view_name='core:datafile')

    class Meta:
        model = DataFile
        fields = ['id', 'url', 'display_url', 'display', 'path']


class NestedJobSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='core-api:job-detail')
    display_url = serializers.HyperlinkedIdentityField(view_name='core:job')
    status = ChoiceField(choices=JobStatusChoices)
    user = UserSerializer(
        nested=True,
        read_only=True
    )

    class Meta:
        model = Job
        fields = ['url', 'display_url', 'created', 'completed', 'user', 'status']
