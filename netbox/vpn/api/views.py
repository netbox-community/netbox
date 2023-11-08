from rest_framework.routers import APIRootView

from netbox.api.viewsets import NetBoxModelViewSet
from utilities.utils import count_related
from vpn import filtersets
from vpn.models import *
from . import serializers

__all__ = (
    'IPSecProfileViewSet',
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

class TunnelViewSet(NetBoxModelViewSet):
    queryset = Tunnel.objects.prefetch_related('ipsec_profile', 'tenant').annotate(
        terminations_count=count_related(TunnelTermination, 'tunnel')
    )
    serializer_class = serializers.TunnelSerializer
    filterset_class = filtersets.TunnelFilterSet


class TunnelTerminationViewSet(NetBoxModelViewSet):
    queryset = TunnelTermination.objects.prefetch_related('tunnel')
    serializer_class = serializers.TunnelTerminationSerializer
    filterset_class = filtersets.TunnelTerminationFilterSet


class IPSecProfileViewSet(NetBoxModelViewSet):
    queryset = IPSecProfile.objects.all()
    serializer_class = serializers.IPSecProfileSerializer
    filterset_class = filtersets.IPSecProfileFilterSet
