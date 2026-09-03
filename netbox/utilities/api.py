import logging

from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.exceptions import (
    FieldDoesNotExist,
    FieldError,
    MultipleObjectsReturned,
    ObjectDoesNotExist,
    ValidationError,
)
from django.db.models.fields.related import ManyToManyRel, ManyToOneRel, RelatedField
from django.urls import reverse
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _
from rest_framework.permissions import BasePermission
from rest_framework.relations import ManyRelatedField
from rest_framework.serializers import ListSerializer, Serializer
from rest_framework.views import get_view_name as drf_get_view_name

from extras.constants import HTTP_CONTENT_TYPE_JSON
from netbox.api.exceptions import GraphQLTypeNotFound, SerializerNotFound
from netbox.api.fields import RelatedObjectCountField, SerializedPKRelatedField
from netbox.registry import registry

from .query import count_related, dict_to_filter_params
from .string import title

logger = logging.getLogger('netbox.utilities.api')

__all__ = (
    'IsSuperuser',
    'get_annotations_for_serializer',
    'get_graphql_type_for_model',
    'get_positional_errors',
    'get_prefetches_for_serializer',
    'get_related_object_by_attrs',
    'get_serializer_for_model',
    'get_view_name',
    'is_api_request',
    'is_graphql_request',
)


class IsSuperuser(BasePermission):
    """
    Allows access only to superusers.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_active and request.user.is_superuser)


def get_serializer_for_model(model, prefix=''):
    """
    Return the appropriate REST API serializer for the given model.

    A plugin (or internal app) may register a custom resolver for its own
    app via netbox.plugins.register_serializer_resolver() to handle
    dynamically generated models or to override serializer resolution. If
    a resolver is registered for the model's app and returns a Serializer
    subclass, that result is used. Otherwise, the default import-path
    lookup runs.
    """
    app_label, model_name = model._meta.label.split('.')

    if resolver := registry['serializer_resolvers'].get(app_label):
        try:
            serializer = resolver(model, prefix=prefix)
        except Exception:
            # A buggy resolver must not break serializer lookup for the rest of NetBox.
            logger.exception("Serializer resolver %r raised an exception; falling through to default lookup.", resolver)
            serializer = None
        if serializer is not None:
            if isinstance(serializer, type) and issubclass(serializer, Serializer):
                return serializer
            logger.warning(
                "Serializer resolver %r returned %r, which is not a Serializer subclass; "
                "falling through to default lookup.",
                resolver, serializer,
            )

    serializer_name = f'{app_label}.api.serializers.{prefix}{model_name}Serializer'
    try:
        return import_string(serializer_name)
    except ImportError:
        raise SerializerNotFound(
            f"Could not determine serializer for {app_label}.{model_name} with prefix '{prefix}'"
        )


def get_graphql_type_for_model(model):
    """
    Return the GraphQL type class for the given model.
    """
    app_label, model_name = model._meta.label.split('.')
    class_name = f'{app_label}.graphql.types.{model_name}Type'
    try:
        return import_string(class_name)
    except ImportError:
        raise GraphQLTypeNotFound(f"Could not find GraphQL type for {app_label}.{model_name}")


def is_api_request(request):
    """
    Return True of the request is being made via the REST API.
    """
    return request.path_info.startswith(reverse('api-root'))


def is_graphql_request(request):
    """
    Return True of the request is being made via the GraphQL API.
    """
    return request.path_info == reverse('graphql') and request.content_type == HTTP_CONTENT_TYPE_JSON


def get_view_name(view):
    """
    Derive the view name from its associated model, if it has one. Fall back to DRF's built-in `get_view_name()`.
    This function is provided to DRF as its VIEW_NAME_FUNCTION.
    """
    if hasattr(view, 'queryset') and view.queryset is not None:
        # Derive the model name from the queryset.
        name = title(view.queryset.model._meta.verbose_name)
        if suffix := getattr(view, 'suffix', None):
            name = f'{name} {suffix}'
        return name

    # Fall back to DRF's default behavior
    return drf_get_view_name(view)


def get_positional_errors(errors, count):
    """
    Return the errors reported by a serializer bound to a list of `count` entries as a list
    correlated to the positions of those entries, with an empty dict standing in for each entry
    which validated.

    DRF 3.18 reports the errors of a ListSerializer as a mapping of the index of each failed entry
    to that entry's errors, omitting the entries which passed; earlier releases reported a list
    aligned with the request body. Restoring the positional form keeps the response shape stable for
    API consumers which index into it.

    Errors which pertain to the list as a whole rather than to any one entry (e.g. a body which is
    not a list at all) carry no position, and are returned unchanged.

    :param errors: The `errors` of a serializer instantiated with many=True.
    :param count: The number of entries the serializer was bound to.
    """
    if not isinstance(errors, dict) or not any(isinstance(index, int) for index in errors):
        return errors

    return [errors.get(index, {}) for index in range(count)]


def _get_nested_serializer(serializer_field):
    """
    Return the nested serializer instance for a declared serializer field.
    """
    if isinstance(serializer_field, ListSerializer):
        serializer_field = serializer_field.child

    # DRF wraps a many-valued related field, keeping the original field on child_relation
    if isinstance(serializer_field, ManyRelatedField):
        serializer_field = serializer_field.child_relation

    if isinstance(serializer_field, SerializedPKRelatedField):
        return serializer_field.serializer(nested=serializer_field.nested)

    if isinstance(serializer_field, Serializer) and hasattr(serializer_field, 'nested'):
        return serializer_field

    return None


def _get_serializer_fields(serializer: Serializer):
    """
    Return the effective field names for a serializer instance, honoring any
    field-level fields=/omit= overrides.
    """
    fields = getattr(serializer, '_include_fields', None) or serializer.Meta.fields
    omit = getattr(serializer, '_omit_fields', []) or []

    return [field_name for field_name in fields if field_name not in omit]


def get_prefetches_for_serializer(serializer_class, fields=None, omit=None, _serializer_states=None):
    """
    Compile and return a list of fields which should be prefetched on the queryset for a serializer.
    """
    if fields is not None and omit is not None:
        raise TypeError("Cannot specify both 'fields' and 'omit' parameters.")

    model = serializer_class.Meta.model

    # If fields are not specified, default to all
    fields_to_include = fields or serializer_class.Meta.fields
    fields_to_omit = omit or []
    effective_fields = tuple(name for name in fields_to_include if name not in fields_to_omit)

    # Break reference cycles on the current path. The field set is in the key because re-entry at a
    # narrower depth is finite, and the states are copied per frame to keep sibling fields independent.
    serializer_states = set(_serializer_states or ())
    serializer_state = (serializer_class, effective_fields)
    if serializer_state in serializer_states:
        return []
    serializer_states.add(serializer_state)

    prefetch_fields = []
    for field_name in effective_fields:
        serializer_field = serializer_class._declared_fields.get(field_name)

        # Determine the name of the model field referenced by the serializer field
        model_field_name = field_name
        if serializer_field and getattr(serializer_field, 'source', None):
            model_field_name = serializer_field.source

        # If the serializer field does not map to a discrete model field, skip it.
        try:
            field = model._meta.get_field(model_field_name)
            if isinstance(field, (RelatedField, ManyToOneRel, ManyToManyRel, GenericForeignKey)):
                prefetch_fields.append(field.name)
        except FieldDoesNotExist:
            continue

        # If this field is represented by a nested serializer, recurse to resolve
        # prefetches for the related object, honoring any field-level fields=/omit=
        # constraints set on that serializer field instance.
        if nested_serializer := _get_nested_serializer(serializer_field):
            subfields = _get_serializer_fields(nested_serializer)
            for subfield in get_prefetches_for_serializer(
                type(nested_serializer), fields=subfields, _serializer_states=serializer_states
            ):
                prefetch_fields.append(f'{field.name}__{subfield}')

    return prefetch_fields


def get_annotations_for_serializer(serializer_class, fields=None, omit=None):
    """
    Return a mapping of field names to annotations to be applied to the queryset for a serializer.
    """
    if fields is not None and omit is not None:
        raise TypeError("Cannot specify both 'fields' and 'omit' parameters.")

    model = serializer_class.Meta.model

    # If fields are not specified, default to all
    fields_to_include = fields or serializer_class.Meta.fields
    fields_to_omit = omit or []

    annotations = {}
    for field_name, field in serializer_class._declared_fields.items():
        if field_name in fields_to_omit:
            continue
        if field_name in fields_to_include and type(field) is RelatedObjectCountField:
            related_field = getattr(model, field.relation).field
            annotations[field_name] = count_related(related_field.model, related_field.name)

    return annotations


def get_related_object_by_attrs(queryset, attrs, user=None):
    """
    Return an object identified by either a dictionary of attributes or its numeric primary key (ID). This is used
    for referencing related objects when creating/updating objects via the REST API.

    When a dictionary of attributes is provided, the queryset is first restricted to only those objects on which the
    given user has been granted view permission. This prevents an unprivileged user from enumerating objects by their
    attributes. Referencing an object directly by its numeric ID is always permitted, regardless of the user's view
    permissions.

    :param queryset: The base queryset from which to retrieve the related object
    :param attrs: A dictionary of attributes or a numeric primary key identifying the related object
    :param user: The user making the request (used to enforce view permissions on attribute-based lookups)
    """
    if attrs is None:
        return None

    # Dictionary of related object attributes
    if isinstance(attrs, dict):
        # Restrict the queryset to only those objects the user is permitted to view. This ensures that filtering by
        # attributes cannot be used to enumerate objects which the user is not otherwise permitted to see. Referencing
        # an object solely by its numeric ID (e.g. {"id": 123}) is equivalent to passing the ID directly, and is
        # always permitted regardless of the user's view permissions.
        if list(attrs) != ['id'] and user is not None and hasattr(queryset, 'restrict'):
            queryset = queryset.restrict(user, 'view')
        params = dict_to_filter_params(attrs)
        try:
            return queryset.get(**params)
        except ObjectDoesNotExist:
            raise ValidationError(
                _("Related object not found using the provided attributes: {params}").format(params=params))
        except MultipleObjectsReturned:
            raise ValidationError(
                _("Multiple objects match the provided attributes: {params}").format(params=params)
            )
        except FieldError as e:
            raise ValidationError(e)

    # Integer PK of related object
    try:
        # Cast as integer in case a PK was mistakenly sent as a string
        pk = int(attrs)
    except (TypeError, ValueError):
        raise ValidationError(
            _(
                "Related objects must be referenced by numeric ID or by dictionary of attributes. Received an "
                "unrecognized value: {value}"
            ).format(value=attrs)
        )

    # Look up object by PK
    try:
        return queryset.get(pk=pk)
    except ObjectDoesNotExist:
        raise ValidationError(_("Related object not found using the provided numeric ID: {id}").format(id=pk))
