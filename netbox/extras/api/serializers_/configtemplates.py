from rest_framework import serializers

from core.api.serializers_.data import DataFileSerializer, DataSourceSerializer
from extras.models import ConfigTemplate
from netbox.api.serializers import ValidatedModelSerializer
from netbox.api.serializers.features import TaggableModelSerializer

__all__ = (
    'ConfigTemplateSerializer',
)


class ConfigTemplateSerializer(TaggableModelSerializer, ValidatedModelSerializer):
    data_source = DataSourceSerializer(
        nested=True,
        required=False
    )
    data_file = DataFileSerializer(
        nested=True,
        required=False
    )

    class Meta:
        model = ConfigTemplate
        fields = [
            'id', 'url', 'display_url', 'display', 'name', 'description', 'environment_params', 'template_code',
            'data_source', 'data_path', 'data_file', 'data_synced', 'tags', 'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'description')
