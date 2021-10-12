from rest_framework import serializers

from netbox.api import WritableNestedSerializer
from wireless.models import *

__all__ = (
    'NestedSSIDSerializer',
)


class NestedSSIDSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='wireless-api:ssid-detail')

    class Meta:
        model = SSID
        fields = ['id', 'url', 'display', 'name']
