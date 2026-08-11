import copy
import functools

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from .features import ChangeLogMessageSerializer

__all__ = (
    'BulkOperationEntryErrorSerializer',
    'BulkOperationErrorSerializer',
    'BulkOperationSerializer',
    'BulkPartialUpdateSchemaMixin',
    'BulkUpdateSchemaMixin',
    'get_bulk_update_serializer_class'
)


class BulkOperationSerializer(ChangeLogMessageSerializer):
    id = serializers.IntegerField()


# The two serializers below are schema-only: they are never used to validate or render data. The
# bulk actions in netbox.api.viewsets.mixins assemble these payloads directly; these exist so that
# their error responses are a documented part of the OpenAPI schema rather than an untyped body.
# Note that a class docstring becomes the component's description in the published schema, so keep
# it user-facing.
class BulkOperationEntryErrorSerializer(serializers.Serializer):
    """
    The failure of a single object within a bulk operation.
    """
    id = serializers.IntegerField(
        required=False,
        help_text=_(
            "The ID of the object which failed. Present once the entry has been matched to an "
            "object; mutually exclusive with `index`."
        )
    )
    index = serializers.IntegerField(
        required=False,
        help_text=_(
            "The zero-based position of the entry within the submitted list. Used where no object "
            "has been identified for the entry: always for creations, and for updates and deletions "
            "where the entry itself could not be interpreted (e.g. a missing or non-numeric `id`). "
            "Mutually exclusive with `id`."
        )
    )
    errors = serializers.DictField(
        help_text=_(
            "The errors for this entry, keyed by field name. Values are ordinarily arrays of "
            "messages. Errors which pertain to no particular field -- model validation, protection "
            "rules, restricted tags, object-level permissions, or the shape of the entry itself -- "
            "all appear under the single key `__all__`."
        )
    )


class BulkOperationErrorSerializer(serializers.Serializer):
    """
    The body returned when a bulk operation fails, correlating each failure with the object
    responsible for it.
    """
    detail = serializers.CharField(
        help_text=_('A summary of the failure, e.g. "1 of 3 objects could not be updated."')
    )
    errors = BulkOperationEntryErrorSerializer(
        many=True,
        required=False,
        help_text=_(
            "One entry per object which failed; objects which would have succeeded are omitted, as "
            "a bulk operation is all-or-none. Absent where the request could not be attributed to "
            "individual entries at all (e.g. a request body which is not a list)."
        )
    )


class BulkUpdateSchemaMixin:
    def get_fields(self):
        fields = super().get_fields()
        # Reuse the runtime bulk-operation ID field so the schema stays in sync
        # with the validator that consumes `id` before model serialization.
        _id = copy.deepcopy(BulkOperationSerializer().fields['id'])
        _id.required = True
        fields['id'] = _id

        return fields


class BulkPartialUpdateSchemaMixin(BulkUpdateSchemaMixin):
    def get_fields(self):
        fields = super().get_fields()

        for name, field in fields.items():
            if name != 'id':
                field.required = False

        return fields


@functools.cache
def get_bulk_update_serializer_class(serializer_class, *, partial=False):
    """
    Return a schema-only serializer for bulk PUT/PATCH requests.

    Bulk update requests to a list endpoint require each object to include
    the target object's numeric ID, even though `id` is read-only on the
    normal model serializer. The runtime code consumes `id` before invoking
    the model serializer for each object.
    """

    meta = getattr(serializer_class, 'Meta')

    if meta.fields == '__all__':
        fields = '__all__'
    else:
        fields = ('id', *[f for f in meta.fields if f != 'id'])

    class Meta(meta):
        pass

    # intentional; this is different than setting fields = fields within class Meta above
    Meta.fields = fields

    bases = (
        (BulkPartialUpdateSchemaMixin, serializer_class)
        if partial
        else (BulkUpdateSchemaMixin, serializer_class)
    )

    attrs = {
        'Meta': Meta,
        '__module__': serializer_class.__module__,
    }

    prefix = 'PatchedBulk' if partial else 'Bulk'
    return type(f'{prefix}{serializer_class.__name__}', bases, attrs)
