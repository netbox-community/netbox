from rest_framework import generics

from circuits.models import Provider, CircuitType, Circuit
from circuits.filters import CircuitFilter

from extras.api.views import CustomFieldModelAPIView
from . import serializers


class ProviderListView(CustomFieldModelAPIView, generics.ListAPIView):
    """
    List all providers
    """
    queryset = Provider.objects.prefetch_related('custom_field_values__field')
    serializer_class = serializers.ProviderSerializer


class ProviderDetailView(CustomFieldModelAPIView, generics.RetrieveAPIView):
    """
    Retrieve a single provider
    """
    queryset = Provider.objects.prefetch_related('custom_field_values__field')
    serializer_class = serializers.ProviderSerializer


class CircuitTypeListView(generics.ListAPIView):
    """
    List all circuit types
    """
    queryset = CircuitType.objects.all()
    serializer_class = serializers.CircuitTypeSerializer


class CircuitTypeDetailView(generics.RetrieveAPIView):
    """
    Retrieve a single circuit type
    """
    queryset = CircuitType.objects.all()
    serializer_class = serializers.CircuitTypeSerializer


class CircuitListView(CustomFieldModelAPIView, generics.ListAPIView):
    """
    List circuits (filterable)
    """
    queryset = Circuit.objects.select_related('type', 'tenant', 'provider', 'site', 'interface__device')\
        .prefetch_related('custom_field_values__field')
    serializer_class = serializers.CircuitSerializer
    filter_class = CircuitFilter


class CircuitDetailView(CustomFieldModelAPIView, generics.RetrieveAPIView):
    """
    Retrieve a single circuit
    """
    queryset = Circuit.objects.select_related('type', 'tenant', 'provider', 'site', 'interface__device')\
        .prefetch_related('custom_field_values__field')
    serializer_class = serializers.CircuitSerializer
