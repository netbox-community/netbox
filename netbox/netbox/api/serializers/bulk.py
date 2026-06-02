import copy
import functools

from rest_framework import serializers

from .features import ChangeLogMessageSerializer

__all__ = (
    'BulkOperationSerializer',
    'BulkPartialUpdateSchemaMixin',
    'BulkUpdateSchemaMixin',
    'get_bulk_update_serializer_class'
)


class BulkOperationSerializer(ChangeLogMessageSerializer):
    id = serializers.IntegerField()


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
