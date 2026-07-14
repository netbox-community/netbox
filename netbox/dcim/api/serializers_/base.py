from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from dcim.models import FrontPort, FrontPortTemplate, PortMapping, PortTemplateMapping, RearPort, RearPortTemplate
from dcim.utils import reconcile_port_mappings
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
        """
        Return whether the connected endpoints are reachable via a complete, active cable path.
        """
        # Use the public `path` accessor rather than dereferencing `_path`
        # directly. `path` already handles the stale in-memory relation case
        # that can occur while CablePath rows are rebuilt during cable edits.
        if path := obj.path:
            return path.is_complete and path.is_active
        return False


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

    def _reconcile_mappings(self, instance, mappings):
        mapping_model, fk_name = self._mapper
        other_field = 'rear_port' if fk_name == 'front_port' else 'front_port'

        # Normalize the opposite-port FK from a model instance to its id so the mappings can be
        # reconciled by value.
        desired = []
        for attrs in mappings:
            attrs = dict(attrs)
            if other_field in attrs:
                attrs[f'{other_field}_id'] = attrs.pop(other_field).pk
            desired.append(attrs)

        reconcile_port_mappings(mapping_model, parent_field=fk_name, parent=instance, desired=desired)

    def create(self, validated_data):
        mappings = validated_data.pop('mappings', [])
        instance = super().create(validated_data)
        self._reconcile_mappings(instance, mappings)

        return instance

    def update(self, instance, validated_data):
        mappings = validated_data.pop('mappings', None)
        instance = super().update(instance, validated_data)

        # Only reconcile when the client supplied rear_ports; a PATCH that omits it leaves the
        # existing mappings untouched.
        if mappings is not None:
            self._reconcile_mappings(instance, mappings)

        return instance
