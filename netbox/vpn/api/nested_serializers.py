from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers

from netbox.api.fields import RelatedObjectCountField
from netbox.api.serializers import WritableNestedSerializer
from vpn import models

__all__ = (
    'NestedIKEPolicySerializer',
    'NestedIKEProposalSerializer',
    'NestedIPSecPolicySerializer',
    'NestedIPSecProfileSerializer',
    'NestedIPSecProposalSerializer',
    'NestedL2VPNSerializer',
    'NestedL2VPNTerminationSerializer',
    'NestedTunnelGroupSerializer',
    'NestedTunnelSerializer',
    'NestedTunnelTerminationSerializer',
)


@extend_schema_serializer(
    exclude_fields=('tunnel_count',),
)
class NestedTunnelGroupSerializer(WritableNestedSerializer):
    tunnel_count = RelatedObjectCountField('tunnels')

    class Meta:
        model = models.TunnelGroup
        fields = ['id', 'url', 'display_url', 'display', 'name', 'slug', 'tunnel_count']


class NestedTunnelSerializer(WritableNestedSerializer):

    class Meta:
        model = models.Tunnel
        fields = ('id', 'url', 'display_url', 'display', 'name')


class NestedTunnelTerminationSerializer(WritableNestedSerializer):

    class Meta:
        model = models.TunnelTermination
        fields = ('id', 'url', 'display_url', 'display')


class NestedIKEProposalSerializer(WritableNestedSerializer):

    class Meta:
        model = models.IKEProposal
        fields = ('id', 'url', 'display_url', 'display', 'name')


class NestedIKEPolicySerializer(WritableNestedSerializer):

    class Meta:
        model = models.IKEPolicy
        fields = ('id', 'url', 'display_url', 'display', 'name')


class NestedIPSecProposalSerializer(WritableNestedSerializer):

    class Meta:
        model = models.IPSecProposal
        fields = ('id', 'url', 'display_url', 'display', 'name')


class NestedIPSecPolicySerializer(WritableNestedSerializer):

    class Meta:
        model = models.IPSecPolicy
        fields = ('id', 'url', 'display_url', 'display', 'name')


class NestedIPSecProfileSerializer(WritableNestedSerializer):

    class Meta:
        model = models.IPSecProfile
        fields = ('id', 'url', 'display_url', 'display', 'name')


#
# L2VPN
#

class NestedL2VPNSerializer(WritableNestedSerializer):

    class Meta:
        model = models.L2VPN
        fields = [
            'id', 'url', 'display', 'display_url', 'identifier', 'name', 'slug', 'type'
        ]


class NestedL2VPNTerminationSerializer(WritableNestedSerializer):
    l2vpn = NestedL2VPNSerializer()

    class Meta:
        model = models.L2VPNTermination
        fields = [
            'id', 'url', 'display_url', 'display', 'l2vpn'
        ]
