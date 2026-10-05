from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from netbox.api.exceptions import SerializerNotFound
from utilities.api import get_serializer_for_model

__all__ = (
    'GFKSerializerField',
)


@extend_schema_field(serializers.JSONField(allow_null=True, read_only=True))
class GFKSerializerField(serializers.Field):
    """
    Represents a generic foreign key using the nested serializer for the related object's model.

    Args:
        allow_missing_serializer: If True, return None for objects whose model has no REST API serializer,
            rather than raising SerializerNotFound.
    """
    def __init__(self, allow_missing_serializer=False, **kwargs):
        super().__init__(**kwargs)
        self.allow_missing_serializer = allow_missing_serializer
        self._serializer_cache = {}

    def to_representation(self, instance, **kwargs):
        if instance is None:
            return None
        context = {'request': self.context['request']}
        if instance.__class__ not in self._serializer_cache:
            try:
                serializer = get_serializer_for_model(instance)(nested=True, context=context)
            except SerializerNotFound:
                if not self.allow_missing_serializer:
                    raise
                serializer = None
            self._serializer_cache[instance.__class__] = serializer
        else:
            serializer = self._serializer_cache[instance.__class__]
        if serializer is None:
            return None
        return serializer.to_representation(instance)
