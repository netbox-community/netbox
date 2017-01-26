from django.shortcuts import get_object_or_404

from rest_framework.mixins import (
    CreateModelMixin, DestroyModelMixin, ListModelMixin, RetrieveModelMixin, UpdateModelMixin,
)
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from circuits.models import Provider, CircuitTermination, CircuitType, Circuit
from circuits.filters import CircuitFilter

from extras.api.views import CustomFieldModelViewSet
from . import serializers


#
# Providers
#

class ProviderViewSet(CustomFieldModelViewSet):
    queryset = Provider.objects.all()
    serializer_class = serializers.ProviderSerializer


#
#  Circuit Types
#

class CircuitTypeViewSet(ModelViewSet):
    queryset = CircuitType.objects.all()
    serializer_class = serializers.CircuitTypeSerializer


#
# Circuits
#

class CircuitViewSet(CustomFieldModelViewSet):
    queryset = Circuit.objects.select_related('type', 'tenant', 'provider')
    filter_class = CircuitFilter

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return serializers.CircuitDetailSerializer
        return serializers.CircuitSerializer


class NestedCircuitTerminationViewSet(CreateModelMixin, ListModelMixin, GenericViewSet):
    serializer_class = serializers.CircuitTerminationSerializer

    def get_queryset(self):
        circuit = get_object_or_404(Circuit, pk=self.kwargs['pk'])
        return CircuitTermination.objects.filter(circuit=circuit).select_related('site', 'interface__device')


#
# Circuit Terminations
#

class CircuitTerminationViewSet(RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, GenericViewSet):
    queryset = CircuitTermination.objects.select_related('site', 'interface__device')
    serializer_class = serializers.CircuitTerminationSerializer
