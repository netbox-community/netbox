from rest_framework.routers import APIRootView

from extras.api.views import CustomFieldModelViewSet
from wireless import filtersets
from wireless.models import *
from . import serializers


class WirelessRootView(APIRootView):
    """
    Wireless API root view
    """
    def get_view_name(self):
        return 'Wireless'


class WirelessLANViewSet(CustomFieldModelViewSet):
    queryset = WirelessLAN.objects.prefetch_related('vlan', 'tags')
    serializer_class = serializers.WirelessLANSerializer
    filterset_class = filtersets.WirelessLANFilterSet


class WirelessLinkViewSet(CustomFieldModelViewSet):
    queryset = WirelessLink.objects.prefetch_related('interface_a', 'interface_b', 'tags')
    serializer_class = serializers.WirelessLinkSerializer
    filterset_class = filtersets.WirelessLinkFilterSet
