from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers

from netbox.api.serializers import WritableNestedSerializer
from wireless.models import *

__all__ = (
    'NestedWirelessLANSerializer',
    'NestedWirelessLANGroupSerializer',
    'NestedWirelessLinkSerializer',
)


@extend_schema_serializer(
    exclude_fields=('wirelesslan_count',),
)
class NestedWirelessLANGroupSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='wireless-api:wirelesslangroup-detail')
    wirelesslan_count = serializers.IntegerField(read_only=True)
    _depth = serializers.IntegerField(source='level', read_only=True)

    class Meta:
        model = WirelessLANGroup
        fields = ['id', 'url', 'display', 'name', 'slug', 'wirelesslan_count', '_depth']


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
