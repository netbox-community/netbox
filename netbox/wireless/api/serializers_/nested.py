from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers

from netbox.api.serializers import WritableNestedSerializer
from wireless import models

__all__ = (
    'NestedWirelessLANGroupSerializer',
    'NestedWirelessLinkSerializer',
)


@extend_schema_serializer(
    exclude_fields=('wirelesslan_count',),
)
class NestedWirelessLANGroupSerializer(WritableNestedSerializer):
    wirelesslan_count = serializers.IntegerField(read_only=True)
    _depth = serializers.IntegerField(source='level', read_only=True)

    class Meta:
        model = models.WirelessLANGroup
        fields = ['id', 'url', 'display_url', 'display', 'name', 'slug', 'wirelesslan_count', '_depth']


class NestedWirelessLinkSerializer(WritableNestedSerializer):

    class Meta:
        model = models.WirelessLink
        fields = ['id', 'url', 'display_url', 'display', 'ssid']
