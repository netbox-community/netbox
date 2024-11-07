import re
import typing
from collections import OrderedDict

from drf_spectacular.extensions import OpenApiSerializerFieldExtension
from drf_spectacular.openapi import AutoSchema
from drf_spectacular.plumbing import (
    build_basic_type, build_choice_field, build_media_type_object, build_object_type, get_doc,
)
from drf_spectacular.types import OpenApiTypes

from netbox.api.fields import ChoiceField
from netbox.api.serializers import WritableNestedSerializer

# see netbox.api.routers.NetBoxRouter
BULK_ACTIONS = ("bulk_destroy", "bulk_partial_update", "bulk_update")
WRITABLE_ACTIONS = ("PATCH", "POST", "PUT")


class FixTimeZoneSerializerField(OpenApiSerializerFieldExtension):
    target_class = 'timezone_field.rest_framework.TimeZoneSerializerField'

    def map_serializer_field(self, auto_schema, direction):
        return build_basic_type(OpenApiTypes.STR)


class ChoiceFieldFix(OpenApiSerializerFieldExtension):
    target_class = 'netbox.api.fields.ChoiceField'

    def map_serializer_field(self, auto_schema, direction):
        build_cf = build_choice_field(self.target)

        if direction == 'request':
            return build_cf

        elif direction == "response":
            value = build_cf
            label = {**build_basic_type(OpenApiTypes.STR), "enum": list(OrderedDict.fromkeys(self.target.choices.values()))}

            return build_object_type(
                properties={
                    "value": value,
                    "label": label
                }
            )


class NetBoxAutoSchema(AutoSchema):
    """
    Overrides to drf_spectacular.openapi.AutoSchema to fix following issues:
        1. bulk serializers cause operation_id conflicts with non-bulk ones
        2. bulk operations should specify a list
        3. bulk operations don't have filter params
        4. bulk operations don't have pagination
        5. bulk delete should specify input
    """

    writable_serializers = {}

    @property
    def is_bulk_action(self):
        if hasattr(self.view, "action") and self.view.action in BULK_ACTIONS:
            return True
        else:
            return False

    def get_operation_id(self):
        """
        bulk serializers cause operation_id conflicts with non-bulk ones
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

    def get_request_serializer(self) -> typing.Any:
        # bulk operations should specify a list
        serializer = super().get_request_serializer()

        if self.is_bulk_action:
            return type(serializer)(many=True)

        # handle mapping for Writable serializers - adapted from dansheps original code
        # for drf-yasg
        if serializer is not None and self.method in WRITABLE_ACTIONS:
            writable_class = self.get_writable_class(serializer)
            if writable_class is not None:
                if hasattr(serializer, "child"):
                    child_serializer = self.get_writable_class(serializer.child)
                    serializer = writable_class(context=serializer.context, child=child_serializer)
                else:
                    serializer = writable_class(context=serializer.context)

        return serializer

    def get_response_serializers(self) -> typing.Any:
        # bulk operations should specify a list
        response_serializers = super().get_response_serializers()

        if self.is_bulk_action:
            return type(response_serializers)(many=True)

        return response_serializers

    def _get_serializer_name(self, serializer, direction, bypass_extensions=False) -> str:
        name = super()._get_serializer_name(serializer, direction, bypass_extensions)

        # If this serializer is nested, prepend its name with "Brief"
        if getattr(serializer, 'nested', False):
            name = f'Brief{name}'

        return name

    def get_serializer_ref_name(self, serializer):
        # from drf-yasg.utils
        """Get serializer's ref_name
        :param serializer: Serializer instance
        :return: Serializer's ``ref_name`` or ``None`` for inline serializer
        :rtype: str or None
        """
        serializer_meta = getattr(serializer, 'Meta', None)
        serializer_name = type(serializer).__name__
        if hasattr(serializer_meta, 'ref_name'):
            ref_name = serializer_meta.ref_name
        else:
            ref_name = serializer_name
            if ref_name.endswith('Serializer'):
                ref_name = ref_name[: -len('Serializer')]
        return ref_name

    def get_writable_class(self, serializer):
        properties = {}
        fields = {} if hasattr(serializer, 'child') else serializer.fields
        remove_fields = []

        for child_name, child in fields.items():
            # read_only fields don't need to be in writable (write only) serializers
            if 'read_only' in dir(child) and child.read_only:
                remove_fields.append(child_name)
            if isinstance(child, (ChoiceField, WritableNestedSerializer)):
                properties[child_name] = None

        if not properties:
            return None

        if type(serializer) not in self.writable_serializers:
            writable_name = 'Writable' + type(serializer).__name__
            meta_class = getattr(type(serializer), 'Meta', None)
            if meta_class:
                ref_name = 'Writable' + self.get_serializer_ref_name(serializer)
                # remove read_only fields from write-only serializers
                fields = list(meta_class.fields)
                for field in remove_fields:
                    fields.remove(field)
                writable_meta = type('Meta', (meta_class,), {'ref_name': ref_name, 'fields': fields})

                properties['Meta'] = writable_meta

            self.writable_serializers[type(serializer)] = type(writable_name, (type(serializer),), properties)

        writable_class = self.writable_serializers[type(serializer)]
        return writable_class

    def get_filter_backends(self):
        # bulk operations don't have filter params
        if self.is_bulk_action:
            return []
        return super().get_filter_backends()

    def _get_paginator(self):
        # bulk operations don't have pagination
        if self.is_bulk_action:
            return None
        return super()._get_paginator()

    def _get_request_body(self, direction='request'):
        # bulk delete should specify input
        if (not self.is_bulk_action) or (self.method != 'DELETE'):
            return super()._get_request_body(direction)

        # rest from drf_spectacular.openapi.AutoSchema._get_request_body
        # but remove the unsafe method check

        request_serializer = self.get_request_serializer()

        if isinstance(request_serializer, dict):
            content = []
            request_body_required = True
            for media_type, serializer in request_serializer.items():
                schema, partial_request_body_required = self._get_request_for_media_type(serializer, direction)
                examples = self._get_examples(serializer, direction, media_type)
                if schema is None:
                    continue
                content.append((media_type, schema, examples))
                request_body_required &= partial_request_body_required
        else:
            schema, request_body_required = self._get_request_for_media_type(request_serializer, direction)
            if schema is None:
                return None
            content = [
                (media_type, schema, self._get_examples(request_serializer, direction, media_type))
                for media_type in self.map_parsers()
            ]

        request_body = {
            'content': {
                media_type: build_media_type_object(schema, examples) for media_type, schema, examples in content
            }
        }
        if request_body_required:
            request_body['required'] = request_body_required
        return request_body

    def get_description(self):
        """
        Return a string description for the ViewSet.
        """

        # If a docstring is provided, use it.
        if self.view.__doc__:
            return get_doc(self.view.__class__)

        # When the action method is decorated with @action, use the docstring of the method.
        action_or_method = getattr(self.view, getattr(self.view, 'action', self.method.lower()), None)
        if action_or_method and action_or_method.__doc__:
            return get_doc(action_or_method)

        # Else, generate a description from the class name.
        return self._generate_description()

    def _generate_description(self):
        """
        Generate a docstring for the method. It also takes into account whether the method is for list or detail.
        """
        model_name = self.view.queryset.model._meta.verbose_name

        # Determine if the method is for list or detail.
        if '{id}' in self.path:
            return f"{self.method.capitalize()} a {model_name} object."
        return f"{self.method.capitalize()} a list of {model_name} objects."


class FixSerializedPKRelatedField(OpenApiSerializerFieldExtension):
    target_class = 'netbox.api.fields.SerializedPKRelatedField'

    def map_serializer_field(self, auto_schema, direction):
        if direction == "response":
            component = auto_schema.resolve_serializer(self.target.serializer, direction)
            return component.ref if component else None
        else:
            return build_basic_type(OpenApiTypes.INT)
