import strawberry_django

from circuits import filtersets, models
from netbox.graphql.filter_mixins import autotype_decorator, BaseFilterMixin

__all__ = (
    'CircuitTerminationFilter',
    'CircuitFilter',
    'CircuitGroupAssignmentFilter',
    'CircuitGroupFilter',
    'CircuitTypeFilter',
    'ProviderFilter',
    'ProviderAccountFilter',
    'ProviderNetworkFilter',
)


@strawberry_django.filter(models.CircuitTermination, lookups=True)
@autotype_decorator(filtersets.CircuitTerminationFilterSet)
class CircuitTerminationFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.Circuit, lookups=True)
@autotype_decorator(filtersets.CircuitFilterSet)
class CircuitFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.CircuitType, lookups=True)
@autotype_decorator(filtersets.CircuitTypeFilterSet)
class CircuitTypeFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.CircuitGroup, lookups=True)
@autotype_decorator(filtersets.CircuitGroupFilterSet)
class CircuitGroupFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.CircuitGroupAssignment, lookups=True)
@autotype_decorator(filtersets.CircuitGroupAssignmentFilterSet)
class CircuitGroupAssignmentFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.Provider, lookups=True)
@autotype_decorator(filtersets.ProviderFilterSet)
class ProviderFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.ProviderAccount, lookups=True)
@autotype_decorator(filtersets.ProviderAccountFilterSet)
class ProviderAccountFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.ProviderNetwork, lookups=True)
@autotype_decorator(filtersets.ProviderNetworkFilterSet)
class ProviderNetworkFilter(BaseFilterMixin):
    pass
