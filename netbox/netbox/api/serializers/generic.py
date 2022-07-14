from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from netbox.api.fields import ContentTypeField
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

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        model = data['object_type'].model_class()
        return model.objects.get(pk=data['object_id'])

    def to_representation(self, instance):
        ct = ContentType.objects.get_for_model(instance)
        return {
            'object_type': content_type_identifier(ct),
            'object_id': instance.pk,
        }
