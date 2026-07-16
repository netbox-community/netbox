from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.translation import gettext as _
from rest_framework import serializers

from ipam.choices import *
from ipam.constants import SERVICE_ASSIGNMENT_MODELS
from ipam.models import IPAddress, Service, ServiceTemplate
from ipam.validators import validate_port_mappings
from netbox.api.fields import ContentTypeField, SerializedPKRelatedField
from netbox.api.gfk_fields import GFKSerializerField
from netbox.api.serializers import PrimaryModelSerializer

from .ip import IPAddressSerializer

__all__ = (
    'ServiceSerializer',
    'ServiceTemplateSerializer',
)


class PortMappingsValidationMixin:
    def validate_port_mappings(self, value):
        # Enforce the same rules as the model/UI form so invalid input returns a 400 keyed under
        # port_mappings (rather than surfacing as a non-field error from the model's full_clean()).
        # The non-empty check lives here rather than in the shared validator because the shared
        # validator is also used by the create-from-template form field, which is legitimately empty
        # until clean() copies the template's mappings.
        try:
            validate_port_mappings(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.messages)
        if not value:
            raise serializers.ValidationError(_("At least one port mapping is required."))
        return value


class ServiceTemplateSerializer(PortMappingsValidationMixin, PrimaryModelSerializer):

    class Meta:
        model = ServiceTemplate
        fields = [
            'id', 'url', 'display_url', 'display', 'name', 'port_mappings', 'description', 'owner', 'comments',
            'tags', 'custom_fields', 'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'port_mappings', 'description')


class ServiceSerializer(PortMappingsValidationMixin, PrimaryModelSerializer):
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

    class Meta:
        model = Service
        fields = [
            'id', 'url', 'display_url', 'display', 'parent_object_type', 'parent_object_id', 'parent', 'name',
            'port_mappings', 'ipaddresses', 'description', 'owner', 'comments', 'tags', 'custom_fields',
            'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'port_mappings', 'description')
