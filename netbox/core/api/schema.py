import copy
import re
import typing
from collections import OrderedDict

from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import gettext_lazy as _
from drf_spectacular.contrib.django_filters import DjangoFilterExtension
from drf_spectacular.extensions import OpenApiSerializerExtension, OpenApiSerializerFieldExtension, _SchemaType
from drf_spectacular.openapi import AutoSchema
from drf_spectacular.plumbing import (
    build_basic_type,
    build_choice_field,
    build_media_type_object,
    build_object_type,
    follow_field_source,
    get_doc,
)
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import Direction, OpenApiParameter, OpenApiResponse
from rest_framework.fields import ReadOnlyField
from rest_framework.utils import model_meta

from netbox.api.fields import ChoiceField
from netbox.api.serializers import BulkOperationErrorSerializer, WritableNestedSerializer
from netbox.api.viewsets import NetBoxModelViewSet

# see netbox.api.routers.NetBoxRouter
BULK_ACTIONS = ("bulk_destroy", "bulk_partial_update", "bulk_update")
WRITABLE_ACTIONS = ("PATCH", "POST", "PUT")


class NetBoxDjangoFilterExtension(DjangoFilterExtension):
    """
    Overrides drf-spectacular's DjangoFilterExtension to fix a regression in v0.29.0 where
    _get_model_field() incorrectly double-appends to_field_name when field_name already ends
    with that value (e.g. field_name='tags__slug', to_field_name='slug' produces the invalid
    path ['tags', 'slug', 'slug']). This caused hundreds of spurious warnings during schema
    generation for filters such as TagFilter, TenancyFilterSet.tenant, and OwnerFilterMixin.owner.

    See: https://github.com/netbox-community/netbox/issues/20787
         https://github.com/tfranzel/drf-spectacular/issues/1475
    """
    priority = 1

    def _get_model_field(self, filter_field, model):
        if not filter_field.field_name:
            return None
        path = filter_field.field_name.split('__')
        to_field_name = filter_field.extra.get('to_field_name')
        if to_field_name is not None and path[-1] != to_field_name:
            path.append(to_field_name)
        return follow_field_source(model, path, emit_warnings=False)


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

        if direction == "response":
            value = build_cf
            label = {
                **build_basic_type(OpenApiTypes.STR),
                "enum": list(OrderedDict.fromkeys(self.target.choices.values()))
            }

            return build_object_type(
                properties={
                    "value": value,
                    "label": label
                }
            )

        # TODO: This function should never implicitly/explicitly return `None`
        # The fallback should be well-defined (drf-spectacular expects request/response naming).
        return None


def viewset_handles_bulk_create(view):
    """Check if view automatically provides list-based bulk create"""
    return isinstance(view, NetBoxModelViewSet)


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
        serializer = super().get_request_serializer()

        # Bulk update/partial-update has a special request shape: a list of
        # writable objects plus a required `id` field. The normal writable
        # serializer omits `id` because it is read-only, so don't use the generic
        # bulk handling for these actions.
        action = getattr(self.view, 'action', None)
        if action in ('bulk_update', 'bulk_partial_update'):
            get_bulk_update_request_serializer = getattr(
                self.view,
                'get_bulk_update_request_serializer',
                None,
            )
            if get_bulk_update_request_serializer is not None:
                return get_bulk_update_request_serializer(
                    partial=(action == 'bulk_partial_update' or self.method == 'PATCH')
                )

        # Bulk creates/deletes should specify a list.
        if self.is_bulk_action:
            return type(serializer)(many=True)

        # handle mapping for Writable serializers - adapted from dansheps original
        # code for drf-yasg.
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

    def _get_bulk_error_responses(self, direction) -> typing.Any:
        """
        Return the error responses of the current bulk write action, keyed by status code, or an
        empty dict if this action is not a bulk write.

        A failed bulk write returns a structured body correlating each failure with the object (or,
        where no object could be identified, the request position) responsible for it. This is a
        documented part of the API contract, but drf-spectacular cannot infer it: responses are
        derived from the request/response serializer alone, which describes only the success case.
        """
        action = getattr(self.view, 'action', None)

        if action in ('bulk_update', 'bulk_partial_update'):
            return {
                '400': OpenApiResponse(
                    response=BulkOperationErrorSerializer,
                    description=_(
                        "One or more of the objects specified could not be updated. No objects were "
                        "modified: a bulk update is an all-or-none operation."
                    ),
                ),
                '403': OpenApiResponse(
                    response=BulkOperationErrorSerializer,
                    description=_(
                        "The requesting user is not permitted to apply one or more of the "
                        "modifications specified. No objects were modified."
                    ),
                ),
            }

        if action == 'bulk_destroy':
            return {
                '400': OpenApiResponse(
                    response=BulkOperationErrorSerializer,
                    description=_(
                        "The request was malformed, one or more of the objects specified could not "
                        "be found, or the deletion of one of them was prevented by a protection "
                        "rule. No objects were deleted."
                    ),
                ),
                '403': OpenApiResponse(
                    response=BulkOperationErrorSerializer,
                    description=_(
                        "The requesting user is not permitted to delete one or more of the objects "
                        "specified. No objects were deleted."
                    ),
                ),
                '409': OpenApiResponse(
                    response=BulkOperationErrorSerializer,
                    description=_(
                        "One or more of the objects specified could not be deleted, because a "
                        "dependent object prevents it. No objects were deleted: a bulk deletion is "
                        "an all-or-none operation."
                    ),
                ),
            }

        if action == 'create' and viewset_handles_bulk_create(self.view):
            # A POST to a list endpoint accepts either a single object or a list of them (see
            # _get_request_for_media_type()), so its error body takes one of two shapes
            # accordingly: field-keyed errors for a single object, or the bulk envelope for a list.
            component = self.resolve_serializer(BulkOperationErrorSerializer, direction)
            return {
                '400': OpenApiResponse(
                    response={
                        'oneOf': [
                            build_basic_type(OpenApiTypes.OBJECT),
                            component.ref if component else build_basic_type(OpenApiTypes.OBJECT),
                        ],
                    },
                    description=_(
                        "The object could not be created. Where a list was submitted, no objects "
                        "were created: a bulk creation is an all-or-none operation."
                    ),
                ),
                # A 403 always carries a `detail`, and BulkOperationError's `errors` is optional, so
                # the one component covers both the single-object and the bulk shape here.
                '403': OpenApiResponse(
                    response=BulkOperationErrorSerializer,
                    description=_(
                        "The requesting user is not permitted to create one or more of the objects "
                        "specified. No objects were created."
                    ),
                ),
            }

        return {}

    def _get_response_bodies(self, direction='response') -> typing.Any:
        responses = super()._get_response_bodies(direction=direction)

        # Document the error responses of the bulk write actions, which cannot be inferred (see
        # _get_bulk_error_responses). A status code already present -- for instance one declared
        # via @extend_schema on a custom action -- is left as it is.
        for code, response in self._get_bulk_error_responses(direction).items():
            if code not in responses:
                responses[code] = self._get_response_for_code(response, code, direction=direction)

        return responses

    def _get_request_for_media_type(self, serializer, direction='request'):
        """
        Override to generate oneOf schema for serializers that support both
        single object and array input (NetBoxModelViewSet POST operations).

        Refs: #20638
        """
        # Get the standard schema first
        schema, required = super()._get_request_for_media_type(serializer, direction)

        # If this serializer supports arrays (marked in get_request_serializer),
        # wrap the schema in oneOf to allow single object OR array
        if (
            direction == 'request' and
            schema is not None and
            getattr(self.view, 'action', None) == 'create' and
            viewset_handles_bulk_create(self.view)
        ):
            return {
                'oneOf': [
                    schema,  # Single object
                    {
                        'type': 'array',
                        'items': schema,  # Array of objects
                    }
                ]
            }, required

        return schema, required

    def _get_serializer_name(self, serializer, direction, bypass_extensions=False) -> str:
        name = super()._get_serializer_name(serializer, direction, bypass_extensions)

        # If this serializer is nested, prepend its name with "Brief". Serializers which declare an explicit
        # Meta.ref_name are exempt: those are brief by design and have no complete form in the schema, so the
        # prefix would only rename an existing component to no purpose. See #22989.
        if getattr(serializer, 'nested', False) and not getattr(getattr(serializer, 'Meta', None), 'ref_name', None):
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

    @staticmethod
    def _rebuilds_as_writable(serializer, field_name):
        """
        Return True if DRF would rebuild the named field in writable form if the field declared on
        the serializer class were removed (see get_writable_class()).

        This defers to ModelSerializer.build_field(), which is what get_fields() itself calls for
        any field not explicitly declared on the class -- rather than testing the model for a field
        of that name, which is a weaker condition. A name backed only by a model property, by a
        non-editable model field, or by a generic foreign key (which lives in Meta.private_fields
        and so is absent from DRF's field info) is rebuilt read-only, and is then dropped from the
        request body altogether.
        """
        model = getattr(getattr(serializer, 'Meta', None), 'model', None)
        if model is None or not hasattr(serializer, 'build_field'):
            return False

        depth = getattr(serializer.Meta, 'depth', 0)
        try:
            field_class, field_kwargs = serializer.build_field(
                field_name, model_meta.get_field_info(model), model, depth
            )
        except ImproperlyConfigured:
            # build_unknown_field(): the model has nothing of this name at all
            return False

        if isinstance(field_class, type) and issubclass(field_class, ReadOnlyField):
            return False
        return not field_kwargs.get('read_only', False)

    def get_writable_class(self, serializer):
        properties = {}
        fields = {} if hasattr(serializer, 'child') else serializer.fields
        remove_fields = []

        # If you get a failure here for "AttributeError: 'cached_property' object has no attribute 'items'"
        # it is probably because you are using a viewsets.ViewSet for the API View and are defining a
        # serializer_class. You will also need to define a get_serializer() method like for GenericAPIView.
        for child_name, child in fields.items():
            # read_only fields don't need to be in writable (write only) serializers
            if 'read_only' in dir(child) and child.read_only:
                remove_fields.append(child_name)
            if isinstance(child, (ChoiceField, WritableNestedSerializer)):
                if child.read_only or self._rebuilds_as_writable(serializer, child_name):
                    properties[child_name] = None
                else:
                    # DRF cannot rebuild this one writably: it is backed by a read-only property
                    # (e.g. Service.protocol, derived from port_mappings). Nulling it would leave
                    # DRF to rebuild it as a ReadOnlyField, which is then omitted from the request
                    # body altogether -- silently dropping a field the serializer does accept on
                    # write. Keep the declared field instead; ChoiceFieldFix already renders it
                    # correctly for the request direction. The copy leaves the bound original
                    # untouched (Field.__deepcopy__ returns an unbound field built from the same
                    # arguments), and keeps `properties` non-empty so the writable variant is still
                    # generated rather than collapsing to None below.
                    properties[child_name] = copy.deepcopy(child)

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

    def get_override_parameters(self):
        params = super().get_override_parameters()
        # Expose the ?fields, ?omit, and ?brief query parameters supported by NetBoxModelViewSet
        # for all non-bulk GET operations (both list and detail).
        if not self.is_bulk_action and self.method == 'GET':
            params = list(params) + [
                OpenApiParameter(
                    name='fields',
                    location=OpenApiParameter.QUERY,
                    required=False,
                    type=OpenApiTypes.STR,
                    description='Comma-separated list of fields to include in the response. Example: `fields=id,name`.',
                ),
                OpenApiParameter(
                    name='omit',
                    location=OpenApiParameter.QUERY,
                    required=False,
                    type=OpenApiTypes.STR,
                    description='Comma-separated list of fields to exclude from the response. '
                                'Example: `omit=description,tags`.',
                ),
                OpenApiParameter(
                    name='brief',
                    location=OpenApiParameter.QUERY,
                    required=False,
                    type=OpenApiTypes.BOOL,
                    description='Return only brief fields for each object.',
                ),
            ]
        return params

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
            # Resolve an instance of the serializer carrying the field's nested setting, so that the brief
            # component is referenced wherever the field renders a brief representation. (The field's
            # to_representation() passes nested in the same manner.) See #22989.
            serializer = self.target.serializer(nested=self.target.nested)
            component = auto_schema.resolve_serializer(serializer, direction)
            return component.ref if component else None
        return build_basic_type(OpenApiTypes.INT)


class FixIntegerRangeSerializerSchema(OpenApiSerializerExtension):
    target_class = 'netbox.api.fields.IntegerRangeSerializer'
    match_subclasses = True

    def map_serializer(self, auto_schema: 'AutoSchema', direction: Direction) -> _SchemaType:
        # One range = two integers; many=True will wrap this in an outer array
        return {
            'type': 'array',
            'items': {
                'type': 'integer',
            },
            'minItems': 2,
            'maxItems': 2,
            'example': [10, 20],
        }


# Nested models can be passed by ID in requests
# The logic for this is handled in `BaseModelSerializer.to_internal_value`
class FixWritableNestedSerializerAllowPK(OpenApiSerializerFieldExtension):
    target_class = 'netbox.api.serializers.BaseModelSerializer'
    match_subclasses = True

    def map_serializer_field(self, auto_schema, direction):
        schema = auto_schema._map_serializer_field(self.target, direction, bypass_extensions=True)
        if schema is None:
            return schema
        if direction == 'request' and self.target.nested:
            return {
                'oneOf': [
                    build_basic_type(OpenApiTypes.INT),
                    schema,
                ]
            }
        return schema
