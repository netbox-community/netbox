from django.shortcuts import get_object_or_404

from rest_framework.mixins import (
    CreateModelMixin, DestroyModelMixin, ListModelMixin, RetrieveModelMixin, UpdateModelMixin,
)
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from circuits.models import Provider, CircuitTermination, CircuitType, Circuit
from circuits.filters import CircuitFilter

from extras.api.views import CustomFieldModelViewSet
from utilities.api import WritableSerializerMixin
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
