from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from dcim.models import Device
from ipam.choices import *
from ipam.models import IPAddress, FHRPGroup, Service, ServiceTemplate
from netbox.api.fields import ChoiceField, SerializedPKRelatedField
from netbox.api.serializers import NetBoxModelSerializer
from utilities.api import get_serializer_for_model
from virtualization.models import VirtualMachine
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
    device = serializers.SerializerMethodField(read_only=True)
    virtual_machine = serializers.SerializerMethodField(read_only=True)
    fhrp_group = serializers.SerializerMethodField(read_only=True)
    protocol = ChoiceField(choices=ServiceProtocolChoices, required=False)
    ipaddresses = SerializedPKRelatedField(
        queryset=IPAddress.objects.all(),
        serializer=IPAddressSerializer,
        nested=True,
        required=False,
        many=True
    )

    class Meta:
        model = Service
        fields = [
            'id', 'url', 'display_url', 'display', 'device', 'virtual_machine', 'fhrp_group', 'name',
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

    @extend_schema_field(serializers.JSONField(allow_null=True))
    def get_device(self, obj):
        if isinstance(obj.parent, Device):
            return self.get_parent(obj)
        return None

    @extend_schema_field(serializers.JSONField(allow_null=True))
    def get_virtual_machine(self, obj):
        if isinstance(obj.parent, VirtualMachine):
            return self.get_parent(obj)
        return None

    @extend_schema_field(serializers.JSONField(allow_null=True))
    def get_fhrp_group(self, obj):
        if isinstance(obj.parent, FHRPGroup):
            return self.get_parent(obj)
        return None
