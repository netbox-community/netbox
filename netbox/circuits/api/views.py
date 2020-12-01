from django.db.models import Prefetch
from rest_framework.routers import APIRootView

from circuits import filters
from circuits.models import Provider, CircuitTermination, CircuitType, Circuit
from dcim.api.views import PathEndpointMixin
from extras.api.views import CustomFieldModelViewSet
from netbox.api.views import ModelViewSet
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
        Prefetch('terminations', queryset=CircuitTermination.objects.prefetch_related('site')),
        'type', 'tenant', 'provider',
    ).prefetch_related('tags')
    serializer_class = serializers.CircuitSerializer
    filterset_class = filters.CircuitFilterSet


#
# Circuit Terminations
#

class CircuitTerminationViewSet(PathEndpointMixin, ModelViewSet):
    queryset = CircuitTermination.objects.prefetch_related(
        'circuit', 'site', '_path__destination', 'cable'
    )
    serializer_class = serializers.CircuitTerminationSerializer
    filterset_class = filters.CircuitTerminationFilterSet
