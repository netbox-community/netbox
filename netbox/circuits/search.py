from circuits import filtersets, models
from netbox.search import SearchIndex, register_search
from utilities.utils import count_related


@register_search()
class CircuitIndex(SearchIndex):
    model = models.Circuit
    fields = (
        ('cid', 100),
        ('description', 500),
        ('comments', 1000),
    )
    queryset = models.Circuit.objects.prefetch_related(
        'type', 'provider', 'tenant', 'tenant__group', 'terminations__site'
    )
    filterset = filtersets.CircuitFilterSet


@register_search()
class CircuitTerminationIndex(SearchIndex):
    model = models.CircuitTermination
    fields = (
        ('xconnect_id', 300),
        ('pp_info', 300),
        ('description', 500),
        ('port_speed', 2000),
        ('upstream_speed', 2000),
    )


@register_search()
class CircuitTypeIndex(SearchIndex):
    model = models.CircuitType
    fields = (
        ('name', 100),
        ('slug', 100),
        ('description', 500),
    )


@register_search()
class ProviderIndex(SearchIndex):
    model = models.Provider
    fields = (
        ('name', 100),
        ('account', 200),
        ('comments', 1000),
    )
    queryset = models.Provider.objects.annotate(
        count_circuits=count_related(models.Circuit, 'provider')
    )
    filterset = filtersets.ProviderFilterSet


@register_search()
class ProviderNetworkIndex(SearchIndex):
    model = models.ProviderNetwork
    fields = (
        ('name', 100),
        ('service_id', 200),
        ('description', 500),
        ('comments', 1000),
    )
    queryset = models.ProviderNetwork.objects.prefetch_related('provider')
    filterset = filtersets.ProviderNetworkFilterSet
