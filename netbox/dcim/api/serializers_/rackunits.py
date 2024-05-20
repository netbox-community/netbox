from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from dcim.choices import *
from netbox.api.fields import ChoiceField
from .devices import DeviceSerializer

__all__ = (
    'RackUnitSerializer',
)


class RackUnitSerializer(serializers.Serializer):
    """
    A rack unit is an abstraction formed by the set (rack, position, face); it does not exist as a row in the database.
    """
    id = serializers.DecimalField(
        max_digits=4,
        decimal_places=1,
        read_only=True
    )
    name = serializers.CharField(read_only=True)
    face = ChoiceField(choices=DeviceFaceChoices, read_only=True)
    device = DeviceSerializer(nested=True, read_only=True)
    occupied = serializers.BooleanField(read_only=True)
    display = serializers.SerializerMethodField(read_only=True)

    @extend_schema_field(OpenApiTypes.STR)
    def get_display(self, obj):
        return obj['name']
