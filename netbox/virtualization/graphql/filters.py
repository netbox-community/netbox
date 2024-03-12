import strawberry
import strawberry_django
from strawberry import auto
from virtualization import models, filtersets


__all__ = (
    'ClusterFilter',
    'ClusterGroupFilter',
    'ClusterTypeFilter',
    'VirtualMachineFilter',
    'VMInterfaceFilter',
    'VirtualDiskFilter',
)


@strawberry_django.filter(models.Cluster, lookups=True)
class ClusterFilter(filtersets.ClusterFilterSet):
    id: auto


@strawberry_django.filter(models.ClusterGroup, lookups=True)
class ClusterGroupFilter(filtersets.ClusterGroupFilterSet):
    id: auto


@strawberry_django.filter(models.ClusterType, lookups=True)
class ClusterTypeFilter(filtersets.ClusterTypeFilterSet):
    id: auto


@strawberry_django.filter(models.VirtualMachine, lookups=True)
class VirtualMachineFilter(filtersets.VirtualMachineFilterSet):
    id: auto


@strawberry_django.filter(models.VMInterface, lookups=True)
class VMInterfaceFilter(filtersets.VMInterfaceFilterSet):
    id: auto


@strawberry_django.filter(models.VirtualDisk, lookups=True)
class VirtualDiskFilter(filtersets.VirtualDiskFilterSet):
    id: auto
