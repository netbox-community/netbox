from rest_framework import serializers

from ipam.api.serializers_.vlans import VLANSerializer
from netbox.api.fields import ChoiceField
from netbox.api.serializers import NestedGroupModelSerializer, NetBoxModelSerializer
from tenancy.api.serializers_.tenants import TenantSerializer
from wireless.choices import *
from wireless.models import WirelessLAN, WirelessLANGroup
from ..nested_serializers import *

__all__ = (
    'WirelessLANGroupSerializer',
    'WirelessLANSerializer',
)


class WirelessLANGroupSerializer(NestedGroupModelSerializer):
    parent = NestedWirelessLANGroupSerializer(required=False, allow_null=True, default=None)
    wirelesslan_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = WirelessLANGroup
        fields = [
            'id', 'url', 'display_url', 'display', 'name', 'slug', 'parent', 'description', 'tags', 'custom_fields',
            'created', 'last_updated', 'wirelesslan_count', '_depth',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'slug', 'description', 'wirelesslan_count', '_depth')


class WirelessLANSerializer(NetBoxModelSerializer):
    group = WirelessLANGroupSerializer(nested=True, required=False, allow_null=True)
    status = ChoiceField(choices=WirelessLANStatusChoices, required=False, allow_blank=True)
    vlan = VLANSerializer(nested=True, required=False, allow_null=True)
    tenant = TenantSerializer(nested=True, required=False, allow_null=True)
    auth_type = ChoiceField(choices=WirelessAuthTypeChoices, required=False, allow_blank=True)
    auth_cipher = ChoiceField(choices=WirelessAuthCipherChoices, required=False, allow_blank=True)

    class Meta:
        model = WirelessLAN
        fields = [
            'id', 'url', 'display_url', 'display', 'ssid', 'description', 'group', 'status', 'vlan', 'tenant',
            'auth_type', 'auth_cipher', 'auth_psk', 'description', 'comments', 'tags', 'custom_fields',
            'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'ssid', 'description')
