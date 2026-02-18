from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from utilities.api import get_serializer_for_model

__all__ = (
    'GFKSerializerField',
)


@extend_schema_field(serializers.JSONField(allow_null=True, read_only=True))
class GFKSerializerField(serializers.Field):

    def to_representation(self, instance, **kwargs):
        if instance is None:
            return None
        serializer = get_serializer_for_model(instance)
        context = {'request': self.context['request']}
        return serializer(instance, nested=True, context=context).data
