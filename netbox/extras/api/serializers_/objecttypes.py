from rest_framework import serializers

from core.models import ObjectType
from netbox.api.serializers import BaseModelSerializer

__all__ = (
    'ObjectTypeSerializer',
)


class ObjectTypeSerializer(BaseModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='extras-api:objecttype-detail')

    class Meta:
        model = ObjectType
        fields = ['id', 'url', 'display', 'app_label', 'model']
