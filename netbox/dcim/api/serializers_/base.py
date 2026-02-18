from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from dcim.models import FrontPort, FrontPortTemplate, PortMapping, PortTemplateMapping, RearPort, RearPortTemplate
from utilities.api import get_serializer_for_model

__all__ = (
    'ConnectedEndpointsSerializer',
    'PortSerializer',
)


class ConnectedEndpointsSerializer(serializers.ModelSerializer):
    """
    Legacy serializer for pre-v3.3 connections
    """
    connected_endpoints_type = serializers.SerializerMethodField(read_only=True, allow_null=True)
    connected_endpoints = serializers.SerializerMethodField(read_only=True)
    connected_endpoints_reachable = serializers.SerializerMethodField(read_only=True)

    @extend_schema_field(OpenApiTypes.STR)
    def get_connected_endpoints_type(self, obj):
        if endpoints := obj.connected_endpoints:
            return f'{endpoints[0]._meta.app_label}.{endpoints[0]._meta.model_name}'
        return None

    @extend_schema_field(serializers.ListField(allow_null=True))
    def get_connected_endpoints(self, obj):
        """
        Return the appropriate serializer for the type of connected object.
        """
        if endpoints := obj.connected_endpoints:
            serializer = get_serializer_for_model(endpoints[0])
            context = {'request': self.context['request']}
            return serializer(endpoints, nested=True, many=True, context=context).data
        return None

    @extend_schema_field(serializers.BooleanField)
    def get_connected_endpoints_reachable(self, obj):
        return obj._path and obj._path.is_complete and obj._path.is_active


class PortSerializer(serializers.ModelSerializer):
    """
    Base serializer for front & rear port and port templates.
    """
    @property
    def _mapper(self):
        """
        Return the model and ForeignKey field name used to track port mappings for this model.
        """
        if self.Meta.model is FrontPort:
            return PortMapping, 'front_port'
        if self.Meta.model is RearPort:
            return PortMapping, 'rear_port'
        if self.Meta.model is FrontPortTemplate:
            return PortTemplateMapping, 'front_port'
        if self.Meta.model is RearPortTemplate:
            return PortTemplateMapping, 'rear_port'
        raise ValueError(f"Could not determine mapping details for {self.__class__}")

    def create(self, validated_data):
        mappings = validated_data.pop('mappings', [])
        instance = super().create(validated_data)

        # Create port mappings
        mapping_model, fk_name = self._mapper
        for attrs in mappings:
            mapping_model.objects.create(**{
                fk_name: instance,
                **attrs,
            })

        return instance

    def update(self, instance, validated_data):
        mappings = validated_data.pop('mappings', None)
        instance = super().update(instance, validated_data)

        if mappings is not None:
            # Update port mappings
            mapping_model, fk_name = self._mapper
            mapping_model.objects.filter(**{fk_name: instance}).delete()
            for attrs in mappings:
                mapping_model.objects.create(**{
                    fk_name: instance,
                    **attrs,
                })

        return instance
