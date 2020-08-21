from django.db.models import Count, Prefetch
from rest_framework.routers import APIRootView

from circuits import filters
from circuits.models import Provider, CircuitTermination, CircuitType, Circuit
from extras.api.views import CustomFieldModelViewSet
from utilities.api import ModelViewSet
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
        circuit_count=Count('circuits')
    ).order_by(*Provider._meta.ordering)
    serializer_class = serializers.ProviderSerializer
    filterset_class = filters.ProviderFilterSet


#
#  Circuit Types
#

class CircuitTypeViewSet(ModelViewSet):
    queryset = CircuitType.objects.annotate(
        circuit_count=Count('circuits')
    ).order_by(*CircuitType._meta.ordering)
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
