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
    display_attrs = ('provider', 'provider_account', 'type', 'status', 'tenant', 'description')


@register_search
class CircuitGroupIndex(SearchIndex):
    model = models.CircuitGroup
    fields = (
        ('name', 100),
        ('slug', 110),
        ('description', 500),
    )
    display_attrs = ('description',)


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
    display_attrs = ('circuit', 'site', 'provider_network', 'description')


@register_search
class CircuitTypeIndex(SearchIndex):
    model = models.CircuitType
    fields = (
        ('name', 100),
        ('slug', 110),
        ('description', 500),
    )
    display_attrs = ('description',)


@register_search
class ProviderIndex(SearchIndex):
    model = models.Provider
    fields = (
        ('name', 100),
        ('description', 500),
        ('comments', 5000),
    )
    display_attrs = ('description',)


@register_search
class ProviderAccountIndex(SearchIndex):
    model = models.ProviderAccount
    fields = (
        ('name', 100),
        ('account', 200),
        ('comments', 5000),
    )
    display_attrs = ('provider', 'account', 'description')


@register_search
class ProviderNetworkIndex(SearchIndex):
    model = models.ProviderNetwork
    fields = (
        ('name', 100),
        ('service_id', 200),
        ('description', 500),
        ('comments', 5000),
    )
    display_attrs = ('provider', 'service_id', 'description')
