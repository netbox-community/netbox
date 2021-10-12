from rest_framework import serializers

from ipam.api.serializers import NestedVLANSerializer
from netbox.api.serializers import PrimaryModelSerializer
from wireless.models import *

__all__ = (
    'WirelessLANSerializer',
)


class WirelessLANSerializer(PrimaryModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='wireless-api:ssid-detail')
    vlan = NestedVLANSerializer(required=False, allow_null=True)

    class Meta:
        model = WirelessLAN
        fields = [
            'id', 'url', 'display', 'ssid', 'description', 'vlan',
        ]
