import circuits.filtersets
import circuits.tables
from circuits.models import Circuit, Provider, ProviderNetwork
from netbox.search import SearchIndex, register_search
from utilities.utils import count_related


@register_search()
class ProviderIndex(SearchIndex):
    model = Provider
    queryset = Provider.objects.annotate(count_circuits=count_related(Circuit, 'provider'))
    filterset = circuits.filtersets.ProviderFilterSet
    table = circuits.tables.ProviderTable
    url = 'circuits:provider_list'


@register_search()
class CircuitIndex(SearchIndex):
    model = Circuit
    queryset = Circuit.objects.prefetch_related(
        'type', 'provider', 'tenant', 'tenant__group', 'terminations__site'
    )
    filterset = circuits.filtersets.CircuitFilterSet
    table = circuits.tables.CircuitTable
    url = 'circuits:circuit_list'


@register_search()
class ProviderNetworkIndex(SearchIndex):
    model = ProviderNetwork
    queryset = ProviderNetwork.objects.prefetch_related('provider')
    filterset = circuits.filtersets.ProviderNetworkFilterSet
    table = circuits.tables.ProviderNetworkTable
    url = 'circuits:providernetwork_list'
