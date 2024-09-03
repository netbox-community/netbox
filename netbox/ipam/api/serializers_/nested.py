from rest_framework import serializers

from ipam import models
from netbox.api.serializers import WritableNestedSerializer
from ..field_serializers import IPAddressField

__all__ = (
    'NestedIPAddressSerializer',
)


class NestedIPAddressSerializer(WritableNestedSerializer):
    family = serializers.IntegerField(read_only=True)
    address = IPAddressField()

    class Meta:
        model = models.IPAddress
        fields = ['id', 'url', 'display_url', 'display', 'family', 'address']
