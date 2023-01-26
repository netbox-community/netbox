from rest_framework import serializers

from core.choices import *
from core.models import *
from netbox.api.fields import ChoiceField
from netbox.api.serializers import NetBoxModelSerializer
from .nested_serializers import *

__all__ = (
    'DataSourceSerializer',
)


class DataSourceSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='core-api:datasource-detail')
    type = ChoiceField(choices=DataSourceTypeChoices, required=False)

    # Related object counts
    file_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = DataSource
        fields = [
            'id', 'url', 'display', 'name', 'type', 'url', 'enabled', 'description', 'git_branch', 'ignore_rules',
            'username', 'password', 'created', 'last_updated', 'file_count',
        ]


class DataFileSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='core-api:datafile-detail')
    source = NestedDataSourceSerializer(read_only=True)

    class Meta:
        model = DataFile
        fields = [
            'id', 'url', 'display', 'source', 'path', 'last_updated', 'size', 'hash',
        ]
