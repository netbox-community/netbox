from rest_framework import serializers

from core.models import ObjectType
from extras.models import SavedFilter
from netbox.api.fields import ContentTypeField
from netbox.api.serializers import ValidatedModelSerializer

__all__ = (
    'SavedFilterSerializer',
)


class SavedFilterSerializer(ValidatedModelSerializer):
    object_types = ContentTypeField(
        queryset=ObjectType.objects.all(),
        many=True
    )

    class Meta:
        model = SavedFilter
        fields = [
            'id', 'url', 'display_url', 'display', 'object_types', 'name', 'slug', 'description', 'user', 'weight',
            'enabled', 'shared', 'parameters', 'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'slug', 'description')
