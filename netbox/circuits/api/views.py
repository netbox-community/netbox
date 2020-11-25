from django.db.models import Count, Prefetch
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.routers import APIRootView

from circuits import filters
from circuits.models import Provider, CircuitTermination, CircuitType, Circuit
from extras.api.serializers import RenderedGraphSerializer
from extras.api.views import CustomFieldModelViewSet
from extras.models import Graph
from utilities.api import ModelViewSet
from utilities.utils import get_subquery
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

class ProviderViewSet(CustomFieldModelViewSet):
    queryset = Provider.objects.prefetch_related('tags').annotate(
        circuit_count=get_subquery(Circuit, 'provider')
    )
    serializer_class = serializers.ProviderSerializer
    filterset_class = filters.ProviderFilterSet

    @action(detail=True)
    def graphs(self, request, pk):
        """
        A convenience method for rendering graphs for a particular provider.
        """
        provider = get_object_or_404(self.queryset, pk=pk)
        queryset = Graph.objects.restrict(request.user).filter(type__model='provider')
        serializer = RenderedGraphSerializer(queryset, many=True, context={'graphed_object': provider})
        return Response(serializer.data)


#
#  Circuit Types
#

class CircuitTypeViewSet(ModelViewSet):
    queryset = CircuitType.objects.annotate(
        circuit_count=get_subquery(Circuit, 'type')
    )
    serializer_class = serializers.CircuitTypeSerializer
    filterset_class = filters.CircuitTypeFilterSet


#
# Circuits
#

class CircuitViewSet(CustomFieldModelViewSet):
    queryset = Circuit.objects.prefetch_related(
        Prefetch('terminations', queryset=CircuitTermination.objects.prefetch_related(
            'site', 'connected_endpoint__device'
        )),
        'type', 'tenant', 'provider',
    ).prefetch_related('tags')
    serializer_class = serializers.CircuitSerializer
    filterset_class = filters.CircuitFilterSet


#
# Circuit Terminations
#

class CircuitTerminationViewSet(ModelViewSet):
    queryset = CircuitTermination.objects.prefetch_related(
        'circuit', 'site', 'connected_endpoint__device', 'cable'
    )
    serializer_class = serializers.CircuitTerminationSerializer
    filterset_class = filters.CircuitTerminationFilterSet
