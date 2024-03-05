from rest_framework import serializers

from core.models import ObjectType
from netbox.api.serializers import BaseModelSerializer

__all__ = (
    'ContentTypeSerializer',
)


class ContentTypeSerializer(BaseModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='extras-api:contenttype-detail')

    class Meta:
        model = ObjectType
        fields = ['id', 'url', 'display', 'app_label', 'model']
