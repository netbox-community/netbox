from rest_framework import serializers

from dcim.api.serializers import NestedInterfaceSerializer
from ipam.api.serializers import NestedVLANSerializer
from netbox.api.serializers import PrimaryModelSerializer
from wireless.models import *

__all__ = (
    'SSIDSerializer',
)


class SSIDSerializer(PrimaryModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='wireless-api:ssid-detail')
    vlan = NestedVLANSerializer(required=False, allow_null=True)

    class Meta:
        model = SSID
        fields = [
            'id', 'url', 'display', 'name', 'description', 'vlan',
        ]
