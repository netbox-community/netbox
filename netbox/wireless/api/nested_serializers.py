from rest_framework import serializers

from netbox.api import WritableNestedSerializer
from wireless.models import *

__all__ = (
    'NestedWirelessLANSerializer',
)


class NestedWirelessLANSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='wireless-api:ssid-detail')

    class Meta:
        model = WirelessLAN
        fields = ['id', 'url', 'display', 'ssid']
