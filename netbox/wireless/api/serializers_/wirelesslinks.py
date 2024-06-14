from rest_framework import serializers

from dcim.api.serializers_.device_components import InterfaceSerializer
from dcim.choices import LinkStatusChoices
from netbox.api.fields import ChoiceField
from netbox.api.serializers import NetBoxModelSerializer
from tenancy.api.serializers_.tenants import TenantSerializer
from wireless.choices import *
from wireless.models import WirelessLink

__all__ = (
    'WirelessLinkSerializer',
)


class WirelessLinkSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='wireless-api:wirelesslink-detail')
    status = ChoiceField(choices=LinkStatusChoices, required=False)
    interface_a = InterfaceSerializer(nested=True)
    interface_b = InterfaceSerializer(nested=True)
    tenant = TenantSerializer(nested=True, required=False, allow_null=True)
    auth_type = ChoiceField(choices=WirelessAuthTypeChoices, required=False, allow_blank=True)
    auth_cipher = ChoiceField(choices=WirelessAuthCipherChoices, required=False, allow_blank=True)
    distance_unit = ChoiceField(choices=WirelessLinkDistanceUnitChoices, allow_blank=True, required=False, allow_null=True)

    class Meta:
        model = WirelessLink
        fields = [
            'id', 'url', 'display', 'interface_a', 'interface_b', 'ssid', 'status', 'tenant', 'auth_type',
            'auth_cipher', 'auth_psk', 'distance', 'distance_unit', 'description', 'comments', 'tags', 'custom_fields',
            'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'ssid', 'description')
