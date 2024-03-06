from rest_framework import serializers

from core.models import ContentType
from netbox.api.serializers import BaseModelSerializer

__all__ = (
    'ContentTypeSerializer',
)


class ContentTypeSerializer(BaseModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='extras-api:contenttype-detail')

    class Meta:
        model = ContentType
        fields = ['id', 'url', 'display', 'app_label', 'model']
