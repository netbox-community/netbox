from rest_framework.routers import APIRootView

from netbox.api.viewsets import NetBoxModelViewSet
from vpn import filtersets
from vpn.models import *
from . import serializers

__all__ = (
    'IKEPolicyViewSet',
    'IKEProposalViewSet',
    'IPSecPolicyViewSet',
    'IPSecProfileViewSet',
    'IPSecProposalViewSet',
    'L2VPNViewSet',
    'L2VPNTerminationViewSet',
    'TunnelGroupViewSet',
    'TunnelTerminationViewSet',
    'TunnelViewSet',
    'VPNRootView',
)


class VPNRootView(APIRootView):
    """
    VPN API root view
    """
    def get_view_name(self):
        return 'VPN'


#
# Viewsets
#

class TunnelGroupViewSet(NetBoxModelViewSet):
    queryset = TunnelGroup.objects.all()
    serializer_class = serializers.TunnelGroupSerializer
    filterset_class = filtersets.TunnelGroupFilterSet


class TunnelViewSet(NetBoxModelViewSet):
    queryset = Tunnel.objects.all()
    serializer_class = serializers.TunnelSerializer
    filterset_class = filtersets.TunnelFilterSet


class TunnelTerminationViewSet(NetBoxModelViewSet):
    queryset = TunnelTermination.objects.all()
    serializer_class = serializers.TunnelTerminationSerializer
    filterset_class = filtersets.TunnelTerminationFilterSet


class IKEProposalViewSet(NetBoxModelViewSet):
    queryset = IKEProposal.objects.all()
    serializer_class = serializers.IKEProposalSerializer
    filterset_class = filtersets.IKEProposalFilterSet


class IKEPolicyViewSet(NetBoxModelViewSet):
    queryset = IKEPolicy.objects.all()
    serializer_class = serializers.IKEPolicySerializer
    filterset_class = filtersets.IKEPolicyFilterSet


class IPSecProposalViewSet(NetBoxModelViewSet):
    queryset = IPSecProposal.objects.all()
    serializer_class = serializers.IPSecProposalSerializer
    filterset_class = filtersets.IPSecProposalFilterSet


class IPSecPolicyViewSet(NetBoxModelViewSet):
    queryset = IPSecPolicy.objects.all()
    serializer_class = serializers.IPSecPolicySerializer
    filterset_class = filtersets.IPSecPolicyFilterSet


class IPSecProfileViewSet(NetBoxModelViewSet):
    queryset = IPSecProfile.objects.all()
    serializer_class = serializers.IPSecProfileSerializer
    filterset_class = filtersets.IPSecProfileFilterSet


class L2VPNViewSet(NetBoxModelViewSet):
    queryset = L2VPN.objects.all()
    serializer_class = serializers.L2VPNSerializer
    filterset_class = filtersets.L2VPNFilterSet


class L2VPNTerminationViewSet(NetBoxModelViewSet):
    queryset = L2VPNTermination.objects.all()
    serializer_class = serializers.L2VPNTerminationSerializer
    filterset_class = filtersets.L2VPNTerminationFilterSet
