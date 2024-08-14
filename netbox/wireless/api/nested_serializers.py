import warnings

from netbox.api.serializers import WritableNestedSerializer
from wireless.models import *
from .serializers_.nested import NestedWirelessLANGroupSerializer, NestedWirelessLinkSerializer

__all__ = (
    'NestedWirelessLANSerializer',
    'NestedWirelessLANGroupSerializer',
    'NestedWirelessLinkSerializer',
)

# TODO: Remove in v4.2
warnings.warn(
    f"Dedicated nested serializers will be removed in NetBox v4.2. Use Serializer(nested=True) instead.",
    DeprecationWarning
)


class NestedWirelessLANSerializer(WritableNestedSerializer):

    class Meta:
        model = WirelessLAN
        fields = ['id', 'url', 'display_url', 'display', 'ssid']
