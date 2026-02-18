from django.contrib.contenttypes.models import ContentType

from ipam.choices import *
from ipam.constants import SERVICE_ASSIGNMENT_MODELS
from ipam.models import IPAddress, Service, ServiceTemplate
from netbox.api.fields import ChoiceField, ContentTypeField, SerializedPKRelatedField
from netbox.api.gfk_fields import GFKSerializerField
from netbox.api.serializers import PrimaryModelSerializer

from .ip import IPAddressSerializer

__all__ = (
    'ServiceSerializer',
    'ServiceTemplateSerializer',
)


class ServiceTemplateSerializer(PrimaryModelSerializer):
    protocol = ChoiceField(choices=ServiceProtocolChoices, required=False)

    class Meta:
        model = ServiceTemplate
        fields = [
            'id', 'url', 'display_url', 'display', 'name', 'protocol', 'ports', 'description', 'owner', 'comments',
            'tags', 'custom_fields', 'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'protocol', 'ports', 'description')


class ServiceSerializer(PrimaryModelSerializer):
    protocol = ChoiceField(choices=ServiceProtocolChoices, required=False)
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
            'protocol', 'ports', 'ipaddresses', 'description', 'owner', 'comments', 'tags', 'custom_fields',
            'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'protocol', 'ports', 'description')
