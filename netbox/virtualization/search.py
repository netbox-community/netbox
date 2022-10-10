import virtualization.filtersets
import virtualization.tables
from dcim.models import Device
from netbox.search.models import SearchMixin
from netbox.search import register_search
from utilities.utils import count_related
from virtualization.models import Cluster, VirtualMachine


@register_search(Cluster)
class ClusterIndex(SearchMixin):
    queryset = Cluster.objects.prefetch_related('type', 'group').annotate(
        device_count=count_related(Device, 'cluster'), vm_count=count_related(VirtualMachine, 'cluster')
    )
    filterset = virtualization.filtersets.ClusterFilterSet
    table = virtualization.tables.ClusterTable
    url = 'virtualization:cluster_list'
    choice_header = 'Virtualization'


@register_search(VirtualMachine)
class VirtualMachineIndex(SearchMixin):
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
    choice_header = 'Virtualization'
