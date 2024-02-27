from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from netbox.constants import NESTED_SERIALIZER_PREFIX
from utilities.api import get_serializer_for_model

__all__ = (
    'ConnectedEndpointsSerializer',
)


class ConnectedEndpointsSerializer(serializers.ModelSerializer):
    """
    Legacy serializer for pre-v3.3 connections
    """
    connected_endpoints_type = serializers.SerializerMethodField(read_only=True)
    connected_endpoints = serializers.SerializerMethodField(read_only=True)
    connected_endpoints_reachable = serializers.SerializerMethodField(read_only=True)

    @extend_schema_field(OpenApiTypes.STR)
    def get_connected_endpoints_type(self, obj):
        if endpoints := obj.connected_endpoints:
            return f'{endpoints[0]._meta.app_label}.{endpoints[0]._meta.model_name}'

    @extend_schema_field(serializers.ListField)
    def get_connected_endpoints(self, obj):
        """
        Return the appropriate serializer for the type of connected object.
        """
        if endpoints := obj.connected_endpoints:
            serializer = get_serializer_for_model(endpoints[0], prefix=NESTED_SERIALIZER_PREFIX)
            context = {'request': self.context['request']}
            return serializer(endpoints, many=True, context=context).data

    @extend_schema_field(serializers.BooleanField)
    def get_connected_endpoints_reachable(self, obj):
        return obj._path and obj._path.is_complete and obj._path.is_active
