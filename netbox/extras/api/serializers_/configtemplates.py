from core.api.serializers_.data import DataFileSerializer, DataSourceSerializer
from extras.models import ConfigTemplate
from netbox.api.serializers import ChangeLogMessageSerializer, ValidatedModelSerializer
from netbox.api.serializers.features import TaggableModelSerializer
from users.api.serializers_.mixins import OwnerMixin

__all__ = (
    'ConfigTemplateSerializer',
)


class ConfigTemplateSerializer(
    OwnerMixin,
    ChangeLogMessageSerializer,
    TaggableModelSerializer,
    ValidatedModelSerializer
):
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
            'mime_type', 'file_name', 'file_extension', 'as_attachment', 'data_source', 'data_path', 'data_file',
            'auto_sync_enabled', 'data_synced', 'owner', 'tags', 'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'description')
