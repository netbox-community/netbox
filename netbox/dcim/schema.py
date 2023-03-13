from drf_spectacular.extensions import (
    OpenApiSerializerFieldExtension,
    OpenApiViewExtension,
)
from drf_spectacular.plumbing import build_basic_type, build_object_type
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema


class FixTimeZoneSerializerField(OpenApiSerializerFieldExtension):
    target_class = 'timezone_field.rest_framework.TimeZoneSerializerField'

    def map_serializer_field(self, auto_schema, direction):
        return build_basic_type(OpenApiTypes.STR)


class ChoiceFieldFix(OpenApiSerializerFieldExtension):
    target_class = 'netbox.api.fields.ChoiceField'

    def map_serializer_field(self, auto_schema, direction):
        if direction == 'request':
            return build_basic_type(OpenApiTypes.STR)

        elif direction == "response":
            return build_object_type(
                properties={
                    "value": build_basic_type(OpenApiTypes.STR),
                    "label": build_basic_type(OpenApiTypes.STR),
                }
            )
