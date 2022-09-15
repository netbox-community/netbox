from django.contrib.contenttypes.models import ContentType
from drf_yasg.utils import swagger_serializer_method
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

    @swagger_serializer_method(serializer_or_field=serializers.JSONField)
    def get_object(self, obj):
        serializer = get_serializer_for_model(obj, prefix=NESTED_SERIALIZER_PREFIX)
        # context = {'request': self.context['request']}
        return serializer(obj, context=self.context).data
