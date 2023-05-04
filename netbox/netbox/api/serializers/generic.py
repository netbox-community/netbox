from django.contrib.contenttypes.models import ContentType
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from netbox.api.fields import ContentTypeField
from netbox.constants import NESTED_SERIALIZER_PREFIX
from utilities.api import get_serializer_for_model
from utilities.utils import content_type_identifier

__all__ = (
    'GenericObjectSerializer',
)


class GenericObjectSerializer(serializers.Serializer):
    """
    Minimal representation of some generic object identified by ContentType and PK.
    """
    object_type = ContentTypeField(
        queryset=ContentType.objects.all()
    )
    object_id = serializers.IntegerField()
    object = serializers.SerializerMethodField(read_only=True)

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        model = data['object_type'].model_class()
        return model.objects.get(pk=data['object_id'])

    def to_representation(self, instance):
        ct = ContentType.objects.get_for_model(instance)
        data = {
            'object_type': content_type_identifier(ct),
            'object_id': instance.pk,
        }
        if 'request' in self.context:
            data['object'] = self.get_object(instance)

        return data

    @extend_schema_field(serializers.JSONField(allow_null=True))
    def get_object(self, obj):
        serializer = get_serializer_for_model(obj, prefix=NESTED_SERIALIZER_PREFIX)
        # context = {'request': self.context['request']}
        return serializer(obj, context=self.context).data
