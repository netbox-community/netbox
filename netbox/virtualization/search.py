import virtualization.filtersets
import virtualization.tables
from dcim.models import Device
from netbox.search import SearchIndex, register_search
from utilities.utils import count_related
from virtualization.models import Cluster, VirtualMachine


@register_search()
class ClusterIndex(SearchIndex):
    model = Cluster
    queryset = Cluster.objects.prefetch_related('type', 'group').annotate(
        device_count=count_related(Device, 'cluster'), vm_count=count_related(VirtualMachine, 'cluster')
    )
    filterset = virtualization.filtersets.ClusterFilterSet
    table = virtualization.tables.ClusterTable
    url = 'virtualization:cluster_list'


@register_search()
class VirtualMachineIndex(SearchIndex):
    model = VirtualMachine
    queryset = VirtualMachine.objects.prefetch_related(
        'cluster',
        'tenant',
        'tenant__group',
        'platform',
        'primary_ip4',
        'primary_ip6',
    )
    filterset = virtualization.filtersets.VirtualMachineFilterSet
    table = virtualization.tables.VirtualMachineTable
    url = 'virtualization:virtualmachine_list'
