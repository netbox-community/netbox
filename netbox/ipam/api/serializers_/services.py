from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from ipam.choices import *
from ipam.constants import SERVICE_ASSIGNMENT_MODELS
from ipam.models import (
    IPAddress,
    Service,
    ServicePortMapping,
    ServiceTemplate,
    ServiceTemplatePortMapping,
)
from ipam.validators import validate_port_mappings
from netbox.api.fields import ContentTypeField, SerializedPKRelatedField
from netbox.api.gfk_fields import GFKSerializerField
from netbox.api.serializers import NetBoxModelSerializer, PrimaryModelSerializer

from .ip import IPAddressSerializer

__all__ = (
    'ServicePortMappingSerializer',
    'ServiceSerializer',
    'ServiceTemplatePortMappingSerializer',
    'ServiceTemplateSerializer',
)


class PortMappingNestedSerializer(serializers.ModelSerializer):
    """
    Minimal serializer used to read/write port mappings nested within a Service or ServiceTemplate.
    """
    class Meta:
        fields = ('id', 'protocol', 'ports')


class ServicePortMappingNestedSerializer(PortMappingNestedSerializer):
    class Meta(PortMappingNestedSerializer.Meta):
        model = ServicePortMapping


class ServiceTemplatePortMappingNestedSerializer(PortMappingNestedSerializer):
    class Meta(PortMappingNestedSerializer.Meta):
        model = ServiceTemplatePortMapping


class PortMappingSyncMixin:
    """
    Handles create/update of the nested ``port_mappings`` list on the parent serializer. On update the
    mappings are replaced wholesale when provided.
    """
    port_mapping_model = None
    port_mapping_fk = None

    def validate_port_mappings(self, value):
        # Enforce the same rules as the UI form (unique protocol per mapping, ports within range) so
        # invalid input returns a 400 instead of a database IntegrityError.
        try:
            validate_port_mappings(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.messages)
        return value

    def _sync_port_mappings(self, instance, mappings):
        instance.port_mappings.all().delete()
        for mapping in mappings:
            self.port_mapping_model.objects.create(**{self.port_mapping_fk: instance, **mapping})

    def create(self, validated_data):
        mappings = validated_data.pop('port_mappings', [])
        instance = super().create(validated_data)
        self._sync_port_mappings(instance, mappings)
        return instance

    def update(self, instance, validated_data):
        mappings = validated_data.pop('port_mappings', None)
        instance = super().update(instance, validated_data)
        if mappings is not None:
            self._sync_port_mappings(instance, mappings)
        return instance


class ServiceTemplateSerializer(PortMappingSyncMixin, PrimaryModelSerializer):
    port_mappings = ServiceTemplatePortMappingNestedSerializer(many=True, required=False)

    port_mapping_model = ServiceTemplatePortMapping
    port_mapping_fk = 'service_template'

    class Meta:
        model = ServiceTemplate
        fields = [
            'id', 'url', 'display_url', 'display', 'name', 'port_mappings', 'description', 'owner', 'comments',
            'tags', 'custom_fields', 'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'description')


class ServiceSerializer(PortMappingSyncMixin, PrimaryModelSerializer):
    port_mappings = ServicePortMappingNestedSerializer(many=True, required=False)
    ipaddresses = SerializedPKRelatedField(
        queryset=IPAddress.objects.all(),
        serializer=IPAddressSerializer,
        nested=True,
        required=False,
        many=True
    )
    parent_object_type = ContentTypeField(
        queryset=ContentType.objects.filter(SERVICE_ASSIGNMENT_MODELS)
    )
    parent = GFKSerializerField(read_only=True)

    port_mapping_model = ServicePortMapping
    port_mapping_fk = 'service'

    class Meta:
        model = Service
        fields = [
            'id', 'url', 'display_url', 'display', 'parent_object_type', 'parent_object_id', 'parent', 'name',
            'port_mappings', 'ipaddresses', 'description', 'owner', 'comments', 'tags', 'custom_fields',
            'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'description')


class ServicePortMappingSerializer(NetBoxModelSerializer):
    service = ServiceSerializer(nested=True)

    class Meta:
        model = ServicePortMapping
        fields = [
            'id', 'url', 'display', 'service', 'protocol', 'ports', 'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'protocol', 'ports')


class ServiceTemplatePortMappingSerializer(NetBoxModelSerializer):
    service_template = ServiceTemplateSerializer(nested=True)

    class Meta:
        model = ServiceTemplatePortMapping
        fields = [
            'id', 'url', 'display', 'service_template', 'protocol', 'ports', 'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'protocol', 'ports')
