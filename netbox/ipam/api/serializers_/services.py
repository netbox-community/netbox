from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from ipam.choices import *
from ipam.constants import SERVICE_ASSIGNMENT_MODELS, SERVICE_PORT_MAX, SERVICE_PORT_MIN
from ipam.models import IPAddress, Service, ServiceTemplate
from netbox.api.fields import ChoiceField, ContentTypeField, SerializedPKRelatedField
from netbox.api.gfk_fields import GFKSerializerField
from netbox.api.serializers import PrimaryModelSerializer

from .ip import IPAddressSerializer

__all__ = (
    'ServicePortSerializer',
    'ServiceSerializer',
    'ServiceTemplateSerializer',
)


class ServicePortSerializer(serializers.Serializer):
    """
    A single protocol/port assignment on a service.
    """
    protocol = ChoiceField(choices=ServiceProtocolChoices)
    port = serializers.IntegerField(min_value=SERVICE_PORT_MIN, max_value=SERVICE_PORT_MAX)


class ServiceSerializerBase(PrimaryModelSerializer):
    port_assignments = ServicePortSerializer(many=True, required=False)

    # Deprecated fields, retained for backward compatibility. On read they are derived from
    # port_assignments (protocol is null when the service mixes protocols). On write they are
    # translated into port_assignments, unless port_assignments is provided explicitly.
    protocol = ChoiceField(choices=ServiceProtocolChoices, required=False, allow_null=True)
    ports = serializers.ListField(
        child=serializers.IntegerField(min_value=SERVICE_PORT_MIN, max_value=SERVICE_PORT_MAX),
        required=False
    )

    def validate(self, data):
        # Translate the deprecated protocol/ports fields into port_assignments before model
        # validation runs (the model has no protocol/ports attributes to assign).
        if 'port_assignments' in data:
            data.pop('protocol', None)
            data.pop('ports', None)
        else:
            protocol = data.pop('protocol', None)
            ports = data.pop('ports', None)
            if protocol is not None and ports is not None:
                data['port_assignments'] = [
                    {'protocol': protocol, 'port': port} for port in ports
                ]
        return super().validate(data)


class ServiceTemplateSerializer(ServiceSerializerBase):

    class Meta:
        model = ServiceTemplate
        fields = [
            'id', 'url', 'display_url', 'display', 'name', 'port_assignments', 'protocol', 'ports', 'description',
            'owner', 'comments', 'tags', 'custom_fields', 'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'port_assignments', 'protocol', 'ports', 'description')


class ServiceSerializer(ServiceSerializerBase):
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
            'port_assignments', 'protocol', 'ports', 'ipaddresses', 'description', 'owner', 'comments', 'tags',
            'custom_fields', 'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'port_assignments', 'protocol', 'ports', 'description')
