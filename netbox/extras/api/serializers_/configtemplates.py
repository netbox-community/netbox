from django.utils.translation import gettext_lazy as _
from drf_spectacular.extensions import OpenApiSerializerExtension
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from core.api.serializers_.data import DataFileSerializer, DataSourceSerializer
from extras.models import ConfigTemplate
from netbox.api.serializers import ChangeLogMessageSerializer, ValidatedModelSerializer
from netbox.api.serializers.features import TaggableModelSerializer
from users.api.serializers_.mixins import OwnerMixin

__all__ = (
    'ConfigTemplateSerializer',
    'RenderConfigInputSerializer',
    'RenderedConfigSerializer',
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
            'mime_type', 'file_name', 'file_extension', 'as_attachment', 'debug', 'data_source', 'data_path',
            'data_file', 'auto_sync_enabled', 'data_synced', 'owner', 'tags', 'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'description')

    def validate_debug(self, value):
        # Restrict debug mode to superusers only (CWE-209: exposes install paths via traceback)
        if value and not self.context['request'].user.is_superuser:
            raise ValidationError(_("Debug mode may only be enabled by superusers."))
        return value


class RenderConfigInputSerializer(serializers.Serializer):
    """
    Describes the request body for the device/VM /render-config/ endpoints. Any additional keys
    supplied are passed through as context variables to the rendered template.
    """
    config_template_id = serializers.IntegerField(
        required=False,
        help_text=_(
            "Optional ID of the ConfigTemplate to render. If omitted, the object's assigned "
            "config template is used."
        )
    )


class RenderConfigInputSerializerExtension(OpenApiSerializerExtension):
    """
    Augment the schema for `RenderConfigInputSerializer` to advertise that additional keys
    (beyond `config_template_id`) are accepted and forwarded as template context variables.
    """
    target_class = 'extras.api.serializers_.configtemplates.RenderConfigInputSerializer'

    def map_serializer(self, auto_schema, direction):
        schema = auto_schema._map_serializer(self.target, direction, bypass_extensions=True)
        schema['additionalProperties'] = True
        return schema


class RenderedConfigSerializer(serializers.Serializer):
    """
    Describes the JSON response returned by the /render-config/ and /render/ endpoints.
    """
    configtemplate = ConfigTemplateSerializer(read_only=True, nested=True)
    content = serializers.CharField(
        read_only=True,
        help_text=_("The rendered template output.")
    )
