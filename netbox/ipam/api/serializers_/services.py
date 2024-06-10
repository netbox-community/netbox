from rest_framework import serializers

from dcim.api.serializers_.devices import DeviceSerializer
from ipam.choices import *
from ipam.models import IPAddress, Service, ServiceTemplate
from netbox.api.fields import ChoiceField, SerializedPKRelatedField
from netbox.api.serializers import NetBoxModelSerializer
from virtualization.api.serializers_.virtualmachines import VirtualMachineSerializer
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
    device = DeviceSerializer(nested=True, required=False, allow_null=True)
    virtual_machine = VirtualMachineSerializer(nested=True, required=False, allow_null=True)
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
            'id', 'url', 'display_url', 'display', 'device', 'virtual_machine', 'name', 'protocol', 'ports',
            'ipaddresses', 'description', 'comments', 'tags', 'custom_fields', 'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'protocol', 'ports', 'description')
