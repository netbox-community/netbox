from rest_framework.routers import APIRootView

from circuits import filtersets
from circuits.models import *
from dcim.api.views import PassThroughPortMixin
from netbox.api.viewsets import NetBoxModelViewSet
from utilities.utils import count_related
from . import serializers


class CircuitsRootView(APIRootView):
    """
    Circuits API root view
    """
    def get_view_name(self):
        return 'Circuits'


#
# Providers
#

class ProviderViewSet(NetBoxModelViewSet):
    queryset = Provider.objects.prefetch_related('asns', 'tags').annotate(
        circuit_count=count_related(Circuit, 'provider')
    )
    serializer_class = serializers.ProviderSerializer
    filterset_class = filtersets.ProviderFilterSet


#
#  Circuit Types
#

class CircuitTypeViewSet(NetBoxModelViewSet):
    queryset = CircuitType.objects.prefetch_related('tags').annotate(
        circuit_count=count_related(Circuit, 'type')
    )
    serializer_class = serializers.CircuitTypeSerializer
    filterset_class = filtersets.CircuitTypeFilterSet


#
# Circuits
#

class CircuitViewSet(NetBoxModelViewSet):
    queryset = Circuit.objects.prefetch_related(
        'type', 'tenant', 'provider', 'termination_a', 'termination_z'
    ).prefetch_related('tags')
    serializer_class = serializers.CircuitSerializer
    filterset_class = filtersets.CircuitFilterSet


#
# Circuit Terminations
#

class CircuitTerminationViewSet(PassThroughPortMixin, NetBoxModelViewSet):
    queryset = CircuitTermination.objects.prefetch_related(
        'circuit', 'site', 'provider_network', 'cable__terminations'
    )
    serializer_class = serializers.CircuitTerminationSerializer
    filterset_class = filtersets.CircuitTerminationFilterSet
    brief_prefetch_fields = ['circuit']


#
# Provider networks
#

class ProviderNetworkViewSet(NetBoxModelViewSet):
    queryset = ProviderNetwork.objects.prefetch_related('tags')
    serializer_class = serializers.ProviderNetworkSerializer
    filterset_class = filtersets.ProviderNetworkFilterSet
