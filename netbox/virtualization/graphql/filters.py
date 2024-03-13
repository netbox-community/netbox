import strawberry
import strawberry_django
from virtualization import filtersets, models

from netbox.graphql.filter_mixins import autotype_decorator, BaseFilterMixin


__all__ = (
    'ClusterFilter',
    'ClusterGroupFilter',
    'ClusterTypeFilter',
    'VirtualMachineFilter',
    'VMInterfaceFilter',
    'VirtualDiskFilter',
)


@strawberry_django.filter(models.Cluster, lookups=True)
@autotype_decorator(filtersets.ClusterFilterSet)
class ClusterFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.ClusterGroup, lookups=True)
@autotype_decorator(filtersets.ClusterGroupFilterSet)
class ClusterGroupFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.ClusterType, lookups=True)
@autotype_decorator(filtersets.ClusterTypeFilterSet)
class ClusterTypeFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.VirtualMachine, lookups=True)
@autotype_decorator(filtersets.VirtualMachineFilterSet)
class VirtualMachineFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.VMInterface, lookups=True)
@autotype_decorator(filtersets.VMInterfaceFilterSet)
class VMInterfaceFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.VirtualDisk, lookups=True)
@autotype_decorator(filtersets.VirtualDiskFilterSet)
class VirtualDiskFilter(BaseFilterMixin):
    pass
