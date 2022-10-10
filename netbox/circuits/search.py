import circuits.filtersets
import circuits.tables
from circuits.models import Circuit, Provider, ProviderNetwork
from netbox.search.models import SearchMixin
from netbox.search import register_search
from utilities.utils import count_related


@register_search(Provider)
class ProviderIndex(SearchMixin):
    queryset = Provider.objects.annotate(count_circuits=count_related(Circuit, 'provider'))
    filterset = circuits.filtersets.ProviderFilterSet
    table = circuits.tables.ProviderTable
    url = 'circuits:provider_list'
    choice_header = 'Circuits'


@register_search(Circuit)
class CircuitIndex(SearchMixin):
    queryset = Circuit.objects.prefetch_related(
        'type', 'provider', 'tenant', 'tenant__group', 'terminations__site'
    )
    filterset = circuits.filtersets.CircuitFilterSet
    table = circuits.tables.CircuitTable
    url = 'circuits:circuit_list'
    choice_header = 'Circuits'


@register_search(ProviderNetwork)
class ProviderNetworkIndex(SearchMixin):
    queryset = ProviderNetwork.objects.prefetch_related('provider')
    filterset = circuits.filtersets.ProviderNetworkFilterSet
    table = circuits.tables.ProviderNetworkTable
    url = 'circuits:providernetwork_list'
    choice_header = 'Circuits'
