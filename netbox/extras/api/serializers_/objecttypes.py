from rest_framework import serializers

from core.models import ObjectType
from netbox.api.serializers import BaseModelSerializer

__all__ = (
    'ObjectTypeSerializer',
)


class ObjectTypeSerializer(BaseModelSerializer):
    display_url = serializers.CharField(allow_null=True, read_only=True)

    class Meta:
        model = ObjectType
        fields = ['id', 'url', 'display_url', 'display', 'app_label', 'model']
