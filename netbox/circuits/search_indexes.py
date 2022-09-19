import dcim.filtersets
import dcim.tables
from circuits.models import Circuit, Provider, ProviderNetwork
from django.db import models
from search.models import SearchMixin


class ProviderIndex(SearchMixin):
    def __init__(self):
        self.model = Provider
        self.queryset = (Provider.objects.annotate(count_circuits=count_related(Circuit, 'provider')),)
        self.filterset = circuits.filtersets.ProviderFilterSet
        self.table = circuits.tables.ProviderTable
        self.url = 'circuits:provider_list'


class CircuitIndex(SearchMixin):
    def __init__(self):
        self.model = Circuit
        self.queryset = Circuit.objects.prefetch_related(
            'type', 'provider', 'tenant', 'tenant__group', 'terminations__site'
        )
        self.filterset = circuits.filtersets.CircuitFilterSet
        self.table = circuits.tables.CircuitTable
        self.url = 'circuits:circuit_list'


class ProviderNetworkIndex(SearchMixin):
    def __init__(self):
        self.model = ProviderNetwork
        self.queryset = ProviderNetwork.objects.prefetch_related('provider')
        self.filterset = circuits.filtersets.ProviderNetworkFilterSet
        self.table = circuits.tables.ProviderNetworkTable
        self.url = 'circuits:providernetwork_list'


CIRCUIT_SEARCH_TYPES = {
    'provider': ProviderIndex(),
    'circuit': CircuitIndex(),
    'providernetwork': ProviderNetworkIndex(),
}
