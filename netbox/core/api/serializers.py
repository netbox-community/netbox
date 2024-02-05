from rest_framework import serializers

from core.choices import *
from core.models import *
from netbox.api.fields import ChoiceField, ContentTypeField
from netbox.api.serializers import BaseModelSerializer, NetBoxModelSerializer
from netbox.utils import get_data_backend_choices
from users.api.nested_serializers import NestedUserSerializer
from .nested_serializers import *

__all__ = (
    'DataFileSerializer',
    'DataSourceSerializer',
    'JobSerializer',
)


class DataSourceSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='core-api:datasource-detail'
    )
    type = ChoiceField(
        choices=get_data_backend_choices()
    )
    status = ChoiceField(
        choices=DataSourceStatusChoices,
        read_only=True
    )

    # Related object counts
    file_count = serializers.IntegerField(
        read_only=True
    )

    class Meta:
        model = DataSource
        fields = [
            'id', 'url', 'display', 'name', 'type', 'source_url', 'enabled', 'status', 'description', 'comments',
            'parameters', 'ignore_rules', 'custom_fields', 'created', 'last_updated', 'file_count',
        ]


class DataFileSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='core-api:datafile-detail'
    )
    source = NestedDataSourceSerializer(
        read_only=True
    )

    class Meta:
        model = DataFile
        fields = [
            'id', 'url', 'display', 'source', 'path', 'last_updated', 'size', 'hash',
        ]


class JobSerializer(BaseModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='core-api:job-detail')
    user = NestedUserSerializer(
        read_only=True
    )
    status = ChoiceField(choices=JobStatusChoices, read_only=True)
    object_type = ContentTypeField(
        read_only=True
    )

    class Meta:
        model = Job
        fields = [
            'id', 'url', 'display', 'object_type', 'object_id', 'name', 'status', 'created', 'scheduled', 'interval',
            'started', 'completed', 'user', 'data', 'error', 'job_id',
        ]
