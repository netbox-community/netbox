from rest_framework import serializers

from core.choices import *
from core.models import DataFile, DataSource
from netbox.api.fields import ChoiceField, RelatedObjectCountField
from netbox.api.serializers import NetBoxModelSerializer
from netbox.utils import get_data_backend_choices

__all__ = (
    'DataFileSerializer',
    'DataSourceSerializer',
)


class DataSourceSerializer(NetBoxModelSerializer):
    type = ChoiceField(
        choices=get_data_backend_choices()
    )
    status = ChoiceField(
        choices=DataSourceStatusChoices,
        read_only=True
    )

    # Related object counts
    file_count = RelatedObjectCountField('datafiles')

    class Meta:
        model = DataSource
        fields = [
            'id', 'url', 'display_url', 'display', 'name', 'type', 'source_url', 'enabled', 'status', 'description', 'comments',
            'parameters', 'ignore_rules', 'custom_fields', 'created', 'last_updated', 'file_count',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'description')


class DataFileSerializer(NetBoxModelSerializer):
    source = DataSourceSerializer(
        nested=True,
        read_only=True
    )

    class Meta:
        model = DataFile
        fields = [
            'id', 'url', 'display_url', 'display', 'source', 'path', 'last_updated', 'size', 'hash',
        ]
        brief_fields = ('id', 'url', 'display', 'path')
