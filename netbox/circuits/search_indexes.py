import circuits.filtersets
import circuits.tables
from circuits.models import Circuit, Provider, ProviderNetwork
from django.db import models
from search.models import SearchMixin
from utilities.utils import count_related


class ProviderIndex(SearchMixin):
    model = Provider
    queryset = Provider.objects.annotate(count_circuits=count_related(Circuit, 'provider'))
    filterset = circuits.filtersets.ProviderFilterSet
    table = circuits.tables.ProviderTable
    url = 'circuits:provider_list'


class CircuitIndex(SearchMixin):
    model = Circuit
    queryset = Circuit.objects.prefetch_related(
        'type', 'provider', 'tenant', 'tenant__group', 'terminations__site'
    )
    filterset = circuits.filtersets.CircuitFilterSet
    table = circuits.tables.CircuitTable
    url = 'circuits:circuit_list'


class ProviderNetworkIndex(SearchMixin):
    model = ProviderNetwork
    queryset = ProviderNetwork.objects.prefetch_related('provider')
    filterset = circuits.filtersets.ProviderNetworkFilterSet
    table = circuits.tables.ProviderNetworkTable
    url = 'circuits:providernetwork_list'


CIRCUIT_SEARCH_TYPES = {
    'provider': ProviderIndex(),
    'circuit': CircuitIndex(),
    'providernetwork': ProviderNetworkIndex(),
}
