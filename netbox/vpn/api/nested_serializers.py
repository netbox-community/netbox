from rest_framework import serializers

from netbox.api.serializers import WritableNestedSerializer
from vpn import models

__all__ = (
    'NestedIKEPolicySerializer',
    'NestedIKEProposalSerializer',
    'NestedIPSecPolicySerializer',
    'NestedIPSecProfileSerializer',
    'NestedIPSecProposalSerializer',
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


class NestedIKEProposalSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='vpn-api:ikeproposal-detail'
    )

    class Meta:
        model = models.IKEProposal
        fields = ('id', 'url', 'display', 'name')


class NestedIKEPolicySerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='vpn-api:ikepolicy-detail'
    )

    class Meta:
        model = models.IKEProposal
        fields = ('id', 'url', 'display', 'name')


class NestedIPSecProposalSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='vpn-api:ipsecproposal-detail'
    )

    class Meta:
        model = models.IPSecProposal
        fields = ('id', 'url', 'display', 'name')


class NestedIPSecPolicySerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='vpn-api:ipsecpolicy-detail'
    )

    class Meta:
        model = models.IPSecProposal
        fields = ('id', 'url', 'display', 'name')


class NestedIPSecProfileSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='vpn-api:ipsecprofile-detail'
    )

    class Meta:
        model = models.IPSecProfile
        fields = ('id', 'url', 'display', 'name')
