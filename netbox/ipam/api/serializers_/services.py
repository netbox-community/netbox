from django.contrib.contenttypes.models import ContentType
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from ipam.choices import *
from ipam.constants import SERVICE_ASSIGNMENT_MODELS
from ipam.models import IPAddress, Service, ServiceTemplate
from netbox.api.fields import ChoiceField, ContentTypeField, SerializedPKRelatedField
from netbox.api.serializers import NetBoxModelSerializer
from utilities.api import get_serializer_for_model
from .ip import IPAddressSerializer

__all__ = (
    'ServiceSerializer',
    'ServiceTemplateSerializer',
)


class ServiceTemplateSerializer(NetBoxModelSerializer):
    protocol = ChoiceField(choices=ServiceProtocolChoices, required=False)

    class Meta:
        model = ServiceTemplate
        fields = [
            'id', 'url', 'display_url', 'display', 'name', 'protocol', 'ports', 'description', 'comments', 'tags',
            'custom_fields', 'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'protocol', 'ports', 'description')


class ServiceSerializer(NetBoxModelSerializer):
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
    parent = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Service
        fields = [
            'id', 'url', 'display_url', 'display', 'parent_object_type', 'parent_object_id', 'parent', 'name',
            'protocol', 'ports', 'ipaddresses', 'description', 'comments', 'tags', 'custom_fields',
            'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'protocol', 'ports', 'description')

    @extend_schema_field(serializers.JSONField(allow_null=True))
    def get_parent(self, obj):
        if obj.parent is None:
            return None
        serializer = get_serializer_for_model(obj.parent)
        context = {'request': self.context['request']}
        return serializer(obj.parent, nested=True, context=context).data
