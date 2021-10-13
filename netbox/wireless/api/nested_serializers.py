from rest_framework import serializers

from netbox.api import WritableNestedSerializer
from wireless.models import *

__all__ = (
    'NestedWirelessLANSerializer',
    'NestedWirelessLinkSerializer',
)


class NestedWirelessLANSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='wireless-api:wirelesslan-detail')

    class Meta:
        model = WirelessLAN
        fields = ['id', 'url', 'display', 'ssid']


class NestedWirelessLinkSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='wireless-api:wirelesslink-detail')

    class Meta:
        model = WirelessLink
        fields = ['id', 'url', 'display', 'ssid']
