from netbox.search import SearchIndex, register_search
from . import models


@register_search
class CircuitIndex(SearchIndex):
    model = models.Circuit
    fields = (
        ('cid', 100),
        ('description', 500),
        ('comments', 5000),
    )


@register_search
class CircuitTerminationIndex(SearchIndex):
    model = models.CircuitTermination
    fields = (
        ('xconnect_id', 300),
        ('pp_info', 300),
        ('description', 500),
        ('port_speed', 2000),
        ('upstream_speed', 2000),
    )


@register_search
class CircuitTypeIndex(SearchIndex):
    model = models.CircuitType
    fields = (
        ('name', 100),
        ('slug', 110),
        ('description', 500),
    )


@register_search
class ProviderIndex(SearchIndex):
    model = models.Provider
    fields = (
        ('name', 100),
        ('account', 200),
        ('description', 500),
        ('comments', 5000),
    )


@register_search
class ProviderNetworkIndex(SearchIndex):
    model = models.ProviderNetwork
    fields = (
        ('name', 100),
        ('service_id', 200),
        ('description', 500),
        ('comments', 5000),
    )
