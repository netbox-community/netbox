from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response

from circuits import filters
from circuits.models import Provider, CircuitTermination, CircuitType, Circuit
from extras.api.serializers import RenderedGraphSerializer
from extras.api.views import CustomFieldModelViewSet
from extras.models import Graph, GRAPH_TYPE_PROVIDER
from utilities.api import FieldChoicesViewSet, ModelViewSet
from . import serializers


#
# Field choices
#

class CircuitsFieldChoicesViewSet(FieldChoicesViewSet):
    fields = (
        (Circuit, ['status']),
        (CircuitTermination, ['term_side']),
    )


#
# Providers
#

class ProviderViewSet(CustomFieldModelViewSet):
    queryset = Provider.objects.prefetch_related('tags').annotate(
        circuit_count=Count('circuits')
    )
    serializer_class = serializers.ProviderSerializer
    filterset_class = filters.ProviderFilter

    @action(detail=True)
    def graphs(self, request, pk):
        """
        A convenience method for rendering graphs for a particular provider.
        """
        provider = get_object_or_404(Provider, pk=pk)
        queryset = Graph.objects.filter(type=GRAPH_TYPE_PROVIDER)
        serializer = RenderedGraphSerializer(queryset, many=True, context={'graphed_object': provider})
        return Response(serializer.data)


#
#  Circuit Types
#

class CircuitTypeViewSet(ModelViewSet):
    queryset = CircuitType.objects.annotate(
        circuit_count=Count('circuits')
    )
    serializer_class = serializers.CircuitTypeSerializer
    filterset_class = filters.CircuitTypeFilter


#
# Circuits
#

class CircuitViewSet(CustomFieldModelViewSet):
    queryset = Circuit.objects.prefetch_related('type', 'tenant', 'provider').prefetch_related('tags')
    serializer_class = serializers.CircuitSerializer
    filterset_class = filters.CircuitFilter


#
# Circuit Terminations
#

class CircuitTerminationViewSet(ModelViewSet):
    queryset = CircuitTermination.objects.prefetch_related(
        'circuit', 'site', 'connected_endpoint__device', 'cable'
    )
    serializer_class = serializers.CircuitTerminationSerializer
    filterset_class = filters.CircuitTerminationFilter
