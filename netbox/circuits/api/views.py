from __future__ import unicode_literals

from django.shortcuts import get_object_or_404
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from circuits import filters
from circuits.models import Provider, CircuitTermination, CircuitType, Circuit
from extras.api.serializers import RenderedGraphSerializer
from extras.api.views import CustomFieldModelViewSet
from extras.models import Graph, GRAPH_TYPE_PROVIDER
from utilities.api import FieldChoicesViewSet, WritableSerializerMixin
from . import serializers


#
# Field choices
#

class CircuitsFieldChoicesViewSet(FieldChoicesViewSet):
    fields = (
        (CircuitTermination, ['term_side']),
    )


#
# Providers
#

class ProviderViewSet(WritableSerializerMixin, CustomFieldModelViewSet):
    queryset = Provider.objects.all()
    serializer_class = serializers.ProviderSerializer
    write_serializer_class = serializers.WritableProviderSerializer
    filter_class = filters.ProviderFilter

    @detail_route()
    def graphs(self, request, pk=None):
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
    queryset = CircuitType.objects.all()
    serializer_class = serializers.CircuitTypeSerializer
    filter_class = filters.CircuitTypeFilter


#
# Circuits
#

class CircuitViewSet(WritableSerializerMixin, CustomFieldModelViewSet):
    queryset = Circuit.objects.select_related('type', 'tenant', 'provider')
    serializer_class = serializers.CircuitSerializer
    write_serializer_class = serializers.WritableCircuitSerializer
    filter_class = filters.CircuitFilter


#
# Circuit Terminations
#

class CircuitTerminationViewSet(WritableSerializerMixin, ModelViewSet):
    queryset = CircuitTermination.objects.select_related('circuit', 'site', 'interface__device')
    serializer_class = serializers.CircuitTerminationSerializer
    write_serializer_class = serializers.WritableCircuitTerminationSerializer
    filter_class = filters.CircuitTerminationFilter
