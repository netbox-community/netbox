import logging
import re
import typing

from drf_spectacular.extensions import (
    OpenApiSerializerFieldExtension,
    OpenApiViewExtension,
)
from drf_spectacular.openapi import AutoSchema
from drf_spectacular.plumbing import (
    ComponentRegistry,
    ResolvedComponent,
    build_basic_type,
    build_object_type,
    is_serializer,
)
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema

BULK_ACTIONS = ["bulk_destroy", "bulk_partial_update", "bulk_update"]


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


class NetBoxAutoSchema(AutoSchema):
    """
    Overrides to spectaculars AutoSchema to fix following issues:
        1. bulk serializers cause operation_id conflicts with non-bulk ones
        2. bulk operations don't have filter params
    """

    @property
    def is_bulk_action(self):
        if hasattr(self.view, "action") and self.view.action in BULK_ACTIONS:
            return True
        else:
            return False

    def get_operation(self, path, path_regex, path_prefix, method, registry: ComponentRegistry):
        operation = super().get_operation(path, path_regex, path_prefix, method, registry)
        return operation

    def get_operation_id(self):
        """
        Fix: bulk serializers cause operation_id conflicts with non-bulk ones
        bulk operations cause id conflicts in spectacular resulting in numerous:
        Warning: operationId "xxx" has collisions [xxx]. "resolving with numeral suffixes"
        code is modified from drf_spectacular.openapi.AutoSchema.get_operation_id
        """
        if self.is_bulk_action:
            tokenized_path = self._tokenize_path()
            # replace dashes as they can be problematic later in code generation
            tokenized_path = [t.replace('-', '_') for t in tokenized_path]

            if self.method == 'GET' and self._is_list_view():
                # this shouldn't happen, but keeping it here to follow base code
                action = 'list'
            else:
                # action = self.method_mapping[self.method.lower()]
                # use bulk name so partial_update -> bulk_partial_update
                action = self.view.action.lower()

            if not tokenized_path:
                tokenized_path.append('root')

            if re.search(r'<drf_format_suffix\w*:\w+>', self.path_regex):
                tokenized_path.append('formatted')

            return '_'.join(tokenized_path + [action])

        # if not bulk - just return normal id
        return super().get_operation_id()

    def get_filter_backends(self):
        # Fix: bulk operations don't have filter params
        if self.is_bulk_action:
            return []
        return super().get_filter_backends()
