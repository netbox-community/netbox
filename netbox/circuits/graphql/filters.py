from typing import List

import strawberry
import strawberry_django
from circuits import filtersets, models
from strawberry import auto
from strawberry_django.filters import FilterLookup
from tenancy.graphql.filter_mixins import ContactModelFilterMixin, TenancyFilterMixin

from netbox.graphql.filter_mixins import NetBoxModelFilterMixin

__all__ = (
    'CircuitTerminationFilter',
    'CircuitFilter',
    'CircuitTypeFilter',
    'ProviderFilter',
    'ProviderAccountFilter',
    'ProviderNetworkFilter',
)


@strawberry_django.filter(models.CircuitTermination, lookups=True)
class CircuitTerminationFilter(filtersets.CircuitTerminationFilterSet):
    id: auto
    term_side: auto
    port_speed: auto
    upstream_speed: auto
    xconnect_id: auto
    description: auto
    cable_end: auto
    # q: auto
    circuit_id: auto
    site_id: auto
    site: auto
    # provider_network_id: auto


@strawberry_django.filter(models.Circuit, lookups=True)
class CircuitFilter(NetBoxModelFilterMixin, TenancyFilterMixin, ContactModelFilterMixin):
    filterset = filtersets.CircuitFilterSet

    cid: auto
    description: auto
    install_date: auto
    termination_date: auto
    commit_rate: auto

    provider_id: List[str] | None
    provider: List[str] | None
    provider_account_id: List[str] | None
    provider_network_id: List[str] | None
    type_id: List[str] | None
    type: List[str] | None
    status: auto
    region_id: List[str] | None
    region: List[str] | None
    site_group_id: List[str] | None
    site_group: List[str] | None
    site_id: List[str] | None
    site: List[str] | None

    def filter_provider_id(self, queryset):
        return self.filter_by_filterset(queryset, 'provider_id')

    def filter_provider(self, queryset):
        return self.filter_by_filterset(queryset, 'provider')

    def filter_provider_account_id(self, queryset):
        return self.filter_by_filterset(queryset, 'provider_account_id')

    def filter_provider_network_id(self, queryset):
        return self.filter_by_filterset(queryset, 'provider_network_id')

    def filter_type_id(self, queryset):
        return self.filter_by_filterset(queryset, 'type_id')

    def filter_type(self, queryset):
        return self.filter_by_filterset(queryset, 'type')

    def filter_region_id(self, queryset):
        return self.filter_by_filterset(queryset, 'region_id')

    def filter_region(self, queryset):
        return self.filter_by_filterset(queryset, 'region')

    def filter_site_group_id(self, queryset):
        return self.filter_by_filterset(queryset, 'site_group_id')

    def filter_site_group(self, queryset):
        return self.filter_by_filterset(queryset, 'site_group')

    def filter_site_id(self, queryset):
        return self.filter_by_filterset(queryset, 'site_id')

    def filter_site(self, queryset):
        return self.filter_by_filterset(queryset, 'site')


# @strawberry_django.filter(models.Circuit, lookups=True)
# class CircuitFilter(filtersets.CircuitFilterSet):
#     id: auto
#     cid: auto
#     description: auto
#     install_date: auto
#     termination_date: auto
#     commit_rate: auto
#     provider_id: auto
#     provider: auto
#     provider_account_id: auto
#     # provider_network_id: auto
#     type_id: auto
#     type: auto
#     status: auto
#     # region_id: auto
#     # region: auto
#     # site_group_id: auto
#     # site_group: auto
#     # site_id: auto
#     # site: auto


@strawberry_django.filter(models.CircuitType, lookups=True)
class CircuitTypeFilter(filtersets.CircuitTypeFilterSet):
    id: auto
    name: auto
    slug: auto
    description: auto


@strawberry_django.filter(models.Provider, lookups=True)
class ProviderFilter(filtersets.ProviderFilterSet):
    id: auto
    name: auto
    slug: auto
    # region_id: auto
    # region: auto
    # site_group_id: auto
    # site_group: auto
    # site_id: auto
    # site: auto
    # asn_id: auto


@strawberry_django.filter(models.ProviderAccount, lookups=True)
class ProviderAccountFilter(filtersets.ProviderAccountFilterSet):
    id: auto
    name: auto
    account: auto
    description: auto
    # provider_id: auto
    # provider: auto


@strawberry_django.filter(models.ProviderNetwork, lookups=True)
class ProviderNetworkFilter(filtersets.ProviderNetworkFilterSet):
    id: auto
    name: auto
    service_id: auto
    description: auto
    # provider_id: auto
    # provider: auto
