from functools import lru_cache

from rest_framework import serializers

from .features import ChangeLogMessageSerializer

__all__ = (
    'BulkOperationSerializer',
    'BulkPartialUpdateSchemaMixin',
    'get_bulk_update_serializer_class'
)


class BulkPartialUpdateSchemaMixin:
    def get_fields(self):
        fields = super().get_fields()
        fields['id'] = serializers.IntegerField(required=True)

        for name, field in fields.items():
            if name != 'id':
                field.required = False

        return fields


@lru_cache
def get_bulk_update_serializer_class(serializer_class, *, partial=False):
    """
    Return a schema-only serializer for bulk PUT/PATCH requests.

    Bulk update requests to a list endpoint require each object to include
    the target object's numeric ID, even though `id` is read-only on the
    normal model serializer. The runtime code consumes `id` before invoking
    the model serializer for each object.
    """
    meta = getattr(serializer_class, 'Meta')

    class Meta(meta):
        fields = ('id', *[f for f in meta.fields if f != 'id'])

    bases = (
        (BulkPartialUpdateSchemaMixin, serializer_class)
        if partial
        else (serializer_class,)
    )

    attrs = {
        'id': serializers.IntegerField(required=True),
        'Meta': Meta,
        '__module__': serializer_class.__module__,
    }

    prefix = 'PatchedBulk' if partial else 'Bulk'
    return type(f'{prefix}{serializer_class.__name__}', bases, attrs)


class BulkOperationSerializer(ChangeLogMessageSerializer):
    id = serializers.IntegerField()
