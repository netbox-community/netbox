from django.shortcuts import get_object_or_404

from rest_framework.decorators import detail_route
from rest_framework.mixins import (
    CreateModelMixin, DestroyModelMixin, ListModelMixin, RetrieveModelMixin, UpdateModelMixin,
)
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from circuits.models import Provider, CircuitTermination, CircuitType, Circuit
from circuits.filters import CircuitFilter

from extras.models import Graph, GRAPH_TYPE_PROVIDER
from extras.api.serializers import GraphSerializer
from extras.api.views import CustomFieldModelViewSet
from utilities.api import WritableSerializerMixin
from . import serializers


#
# Providers
#

class ProviderViewSet(CustomFieldModelViewSet):
    queryset = Provider.objects.all()
    serializer_class = serializers.ProviderSerializer

    @detail_route()
    def graphs(self, request, pk=None):
        provider = get_object_or_404(Provider, pk=pk)
        queryset = Graph.objects.filter(type=GRAPH_TYPE_PROVIDER)
        serializer = GraphSerializer(queryset, many=True, context={'graphed_object': provider})
        return Response(serializer.data)


#
#  Circuit Types
#

class CircuitTypeViewSet(ModelViewSet):
    queryset = CircuitType.objects.all()
    serializer_class = serializers.CircuitTypeSerializer


#
# Circuits
#

class CircuitViewSet(WritableSerializerMixin, CustomFieldModelViewSet):
    queryset = Circuit.objects.select_related('type', 'tenant', 'provider')
    serializer_class = serializers.CircuitSerializer
    filter_class = CircuitFilter


#
# Circuit Terminations
#

class CircuitTerminationViewSet(RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, WritableSerializerMixin,
                                GenericViewSet):
    queryset = CircuitTermination.objects.select_related('site', 'interface__device')
    serializer_class = serializers.CircuitTerminationSerializer


class NestedCircuitTerminationViewSet(CreateModelMixin, ListModelMixin ,WritableSerializerMixin, GenericViewSet):
    serializer_class = serializers.CircuitTerminationSerializer

    def get_queryset(self):
        circuit = get_object_or_404(Circuit, pk=self.kwargs['pk'])
        return CircuitTermination.objects.filter(circuit=circuit).select_related('site', 'interface__device')
