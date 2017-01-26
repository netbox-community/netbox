from rest_framework.viewsets import ModelViewSet

from circuits.models import Provider, CircuitType, Circuit
from circuits.filters import CircuitFilter

from extras.api.views import CustomFieldModelViewSet
from . import serializers


#
# Providers
#

class ProviderViewSet(CustomFieldModelViewSet):
    """
    List and retrieve circuit providers
    """
    queryset = Provider.objects.all()
    serializer_class = serializers.ProviderSerializer


#
#  Circuit Types
#

class CircuitTypeViewSet(ModelViewSet):
    """
    List and retrieve circuit types
    """
    queryset = CircuitType.objects.all()
    serializer_class = serializers.CircuitTypeSerializer


#
# Circuits
#

class CircuitViewSet(CustomFieldModelViewSet):
    """
    List and retrieve circuits
    """
    queryset = Circuit.objects.select_related('type', 'tenant', 'provider')
    filter_class = CircuitFilter

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return serializers.CircuitDetailSerializer
        return serializers.CircuitSerializer
