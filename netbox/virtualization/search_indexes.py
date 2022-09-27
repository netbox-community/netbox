import virtualization.filtersets
import virtualization.tables
from django.db import models
from search.models import SearchMixin
from utilities.utils import count_related
from virtualization.models import Cluster, Device, VirtualMachine


class ClusterIndex(SearchMixin):
    model = Cluster
    queryset = Cluster.objects.prefetch_related('type', 'group').annotate(
        device_count=count_related(Device, 'cluster'), vm_count=count_related(VirtualMachine, 'cluster')
    )
    filterset = virtualization.filtersets.ClusterFilterSet
    table = virtualization.tables.ClusterTable
    url = 'virtualization:cluster_list'
    choice_header = 'Virtualization'


class VirtualMachineIndex(SearchMixin):
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
    choice_header = 'Virtualization'


VIRTUALIZATION_SEARCH_TYPES = {
    'cluster': ClusterIndex,
    'virtualmachine': VirtualMachineIndex,
}
