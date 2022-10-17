from dcim.models import Device
from netbox.search import SearchIndex, register_search
from utilities.utils import count_related
from . import filtersets, models


@register_search()
class ClusterIndex(SearchIndex):
    model = models.Cluster
    fields = (
        ('name', 100),
        ('comments', 5000),
    )
    queryset = models.Cluster.objects.prefetch_related('type', 'group').annotate(
        device_count=count_related(Device, 'cluster'),
        vm_count=count_related(models.VirtualMachine, 'cluster')
    )
    filterset = filtersets.ClusterFilterSet


@register_search()
class ClusterGroupIndex(SearchIndex):
    model = models.ClusterGroup
    fields = (
        ('name', 100),
        ('slug', 110),
        ('description', 500),
    )


@register_search()
class ClusterTypeIndex(SearchIndex):
    model = models.ClusterType
    fields = (
        ('name', 100),
        ('slug', 110),
        ('description', 500),
    )


@register_search()
class VirtualMachineIndex(SearchIndex):
    model = models.VirtualMachine
    fields = (
        ('name', 100),
        ('comments', 5000),
    )
    queryset = models.VirtualMachine.objects.prefetch_related(
        'cluster',
        'tenant',
        'tenant__group',
        'platform',
        'primary_ip4',
        'primary_ip6',
    )
    filterset = filtersets.VirtualMachineFilterSet


@register_search()
class VMInterfaceIndex(SearchIndex):
    model = models.VMInterface
    fields = (
        ('name', 100),
        ('description', 500),
    )
