from rest_framework import serializers

from dcim.choices import LinkStatusChoices
from dcim.api.serializers import NestedInterfaceSerializer
from ipam.api.serializers import NestedVLANSerializer
from netbox.api.fields import ChoiceField
from netbox.api.serializers import NestedGroupModelSerializer, NetBoxModelSerializer
from tenancy.api.nested_serializers import NestedTenantSerializer
from wireless.choices import *
from wireless.models import *
from .nested_serializers import *

__all__ = (
    'WirelessLANGroupSerializer',
    'WirelessLANSerializer',
    'WirelessLinkSerializer',
)


class WirelessLANGroupSerializer(NestedGroupModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='wireless-api:wirelesslangroup-detail')
    parent = NestedWirelessLANGroupSerializer(required=False, allow_null=True, default=None)
    wirelesslan_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = WirelessLANGroup
        fields = [
            'id', 'url', 'display', 'name', 'slug', 'parent', 'description', 'tags', 'custom_fields', 'created',
            'last_updated', 'wirelesslan_count', '_depth',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'slug', 'description', 'wirelesslan_count', '_depth')


class WirelessLANSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='wireless-api:wirelesslan-detail')
    group = NestedWirelessLANGroupSerializer(required=False, allow_null=True)
    status = ChoiceField(choices=WirelessLANStatusChoices, required=False, allow_blank=True)
    vlan = NestedVLANSerializer(required=False, allow_null=True)
    tenant = NestedTenantSerializer(required=False, allow_null=True)
    auth_type = ChoiceField(choices=WirelessAuthTypeChoices, required=False, allow_blank=True)
    auth_cipher = ChoiceField(choices=WirelessAuthCipherChoices, required=False, allow_blank=True)

    class Meta:
        model = WirelessLAN
        fields = [
            'id', 'url', 'display', 'ssid', 'description', 'group', 'status', 'vlan', 'tenant', 'auth_type',
            'auth_cipher', 'auth_psk', 'description', 'comments', 'tags', 'custom_fields', 'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'ssid', 'description')


class WirelessLinkSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='wireless-api:wirelesslink-detail')
    status = ChoiceField(choices=LinkStatusChoices, required=False)
    interface_a = NestedInterfaceSerializer()
    interface_b = NestedInterfaceSerializer()
    tenant = NestedTenantSerializer(required=False, allow_null=True)
    auth_type = ChoiceField(choices=WirelessAuthTypeChoices, required=False, allow_blank=True)
    auth_cipher = ChoiceField(choices=WirelessAuthCipherChoices, required=False, allow_blank=True)

    class Meta:
        model = WirelessLink
        fields = [
            'id', 'url', 'display', 'interface_a', 'interface_b', 'ssid', 'status', 'tenant', 'auth_type',
            'auth_cipher', 'auth_psk', 'description', 'comments', 'tags', 'custom_fields', 'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'ssid', 'description')
