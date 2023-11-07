from rest_framework import serializers

from netbox.api.serializers import WritableNestedSerializer
from vpn import models

__all__ = (
    'NestedIPSecProfileSerializer',
    'NestedTunnelSerializer',
    'NestedTunnelTerminationSerializer',
)


class NestedTunnelSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='vpn-api:tunnel-detail'
    )

    class Meta:
        model = models.Tunnel
        fields = ('id', 'url', 'display', 'name')


class NestedTunnelTerminationSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='vpn-api:tunneltermination-detail'
    )

    class Meta:
        model = models.TunnelTermination
        fields = ('id', 'url', 'display')


class NestedIPSecProfileSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='vpn-api:ipsecprofile-detail'
    )

    class Meta:
        model = models.IPSecProfile
        fields = ('id', 'url', 'display', 'name')
