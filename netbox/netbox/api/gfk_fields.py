from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from utilities.api import get_serializer_for_model

__all__ = (
    'GFKSerializerField',
)


@extend_schema_field(serializers.JSONField(allow_null=True, read_only=True))
class GFKSerializerField(serializers.Field):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._serializer_cache = {}

    def to_representation(self, instance, **kwargs):
        if instance is None:
            return None
        context = {'request': self.context['request']}
        if instance.__class__ not in self._serializer_cache:
            serializer = get_serializer_for_model(instance)(nested=True, context=context)
            self._serializer_cache[instance.__class__] = serializer
        else:
            serializer = self._serializer_cache[instance.__class__]
        return serializer.to_representation(instance)
