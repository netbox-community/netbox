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
    url = serializers.HyperlinkedIdentityField(view_name='vpn-api:tunnelgroup-detail')
    display_url = serializers.HyperlinkedIdentityField(view_name='vpn:tunnelgroup')
    tunnel_count = RelatedObjectCountField('tunnels')

    class Meta:
        model = models.TunnelGroup
        fields = ['id', 'url', 'display_url', 'display', 'name', 'slug', 'tunnel_count']


class NestedTunnelSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='vpn-api:tunnel-detail'
    )
    display_url = serializers.HyperlinkedIdentityField(
        view_name='vpn:tunnel'
    )

    class Meta:
        model = models.Tunnel
        fields = ('id', 'url', 'display_url', 'display', 'name')


class NestedTunnelTerminationSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='vpn-api:tunneltermination-detail'
    )
    display_url = serializers.HyperlinkedIdentityField(
        view_name='vpn:tunneltermination'
    )

    class Meta:
        model = models.TunnelTermination
        fields = ('id', 'url', 'display_url', 'display')


class NestedIKEProposalSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='vpn-api:ikeproposal-detail'
    )
    display_url = serializers.HyperlinkedIdentityField(
        view_name='vpn:ikeproposal'
    )

    class Meta:
        model = models.IKEProposal
        fields = ('id', 'url', 'display_url', 'display', 'name')


class NestedIKEPolicySerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='vpn-api:ikepolicy-detail'
    )
    display_url = serializers.HyperlinkedIdentityField(
        view_name='vpn:ikepolicy'
    )

    class Meta:
        model = models.IKEPolicy
        fields = ('id', 'url', 'display_url', 'display', 'name')


class NestedIPSecProposalSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='vpn-api:ipsecproposal-detail'
    )
    display_url = serializers.HyperlinkedIdentityField(
        view_name='vpn:ipsecproposal'
    )

    class Meta:
        model = models.IPSecProposal
        fields = ('id', 'url', 'display_url', 'display', 'name')


class NestedIPSecPolicySerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='vpn-api:ipsecpolicy-detail'
    )
    display_url = serializers.HyperlinkedIdentityField(
        view_name='vpn:ipsecpolicy'
    )

    class Meta:
        model = models.IPSecPolicy
        fields = ('id', 'url', 'display_url', 'display', 'name')


class NestedIPSecProfileSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='vpn-api:ipsecprofile-detail'
    )
    display_url = serializers.HyperlinkedIdentityField(
        view_name='vpn:ipsecprofile'
    )

    class Meta:
        model = models.IPSecProfile
        fields = ('id', 'url', 'display_url', 'display', 'name')


#
# L2VPN
#

class NestedL2VPNSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='vpn-api:l2vpn-detail')
    display_url = serializers.HyperlinkedIdentityField(view_name='vpn:l2vpn')

    class Meta:
        model = models.L2VPN
        fields = [
            'id', 'url', 'display', 'display_url', 'identifier', 'name', 'slug', 'type'
        ]


class NestedL2VPNTerminationSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='vpn-api:l2vpntermination-detail')
    display_url = serializers.HyperlinkedIdentityField(view_name='vpn:l2vpntermination')
    l2vpn = NestedL2VPNSerializer()

    class Meta:
        model = models.L2VPNTermination
        fields = [
            'id', 'url', 'display_url', 'display', 'l2vpn'
        ]
