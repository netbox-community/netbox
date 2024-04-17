from rest_framework.routers import APIRootView

from netbox.api.viewsets import NetBoxModelViewSet, MPTTLockedMixin
from wireless import filtersets
from wireless.models import *
from . import serializers


class WirelessRootView(APIRootView):
    """
    Wireless API root view
    """
    def get_view_name(self):
        return 'Wireless'


class WirelessLANGroupViewSet(MPTTLockedMixin, NetBoxModelViewSet):
    queryset = WirelessLANGroup.objects.add_related_count(
        WirelessLANGroup.objects.all(),
        WirelessLAN,
        'group',
        'wirelesslan_count',
        cumulative=True
    )
    serializer_class = serializers.WirelessLANGroupSerializer
    filterset_class = filtersets.WirelessLANGroupFilterSet


class WirelessLANViewSet(NetBoxModelViewSet):
    queryset = WirelessLAN.objects.prefetch_related('vlan', 'tenant', 'tags')
    serializer_class = serializers.WirelessLANSerializer
    filterset_class = filtersets.WirelessLANFilterSet


class WirelessLinkViewSet(NetBoxModelViewSet):
    queryset = WirelessLink.objects.prefetch_related('interface_a', 'interface_b', 'tenant', 'tags')
    serializer_class = serializers.WirelessLinkSerializer
    filterset_class = filtersets.WirelessLinkFilterSet
