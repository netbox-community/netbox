import virtualization.filtersets
import virtualization.tables
from django.db import models
from search.models import SearchMixin
from utilities.utils import count_related
from virtualization.models import Cluster, Device, VirtualMachine


class ClusterIndex(SearchMixin):
    def __init__(self):
        self.model = Cluster
        self.queryset = Cluster.objects.prefetch_related('type', 'group').annotate(
            device_count=count_related(Device, 'cluster'), vm_count=count_related(VirtualMachine, 'cluster')
        )
        self.filterset = virtualization.filtersets.ClusterFilterSet
        self.table = virtualization.tables.ClusterTable
        self.url = 'virtualization:cluster_list'


class VirtualMachineIndex(SearchMixin):
    def __init__(self):
        self.model = VirtualMachine
        self.queryset = VirtualMachine.objects.prefetch_related(
            'cluster',
            'tenant',
            'tenant__group',
            'platform',
            'primary_ip4',
            'primary_ip6',
        )
        self.filterset = virtualization.filtersets.VirtualMachineFilterSet
        self.table = virtualization.tables.VirtualMachineTable
        self.url = 'virtualization:virtualmachine_list'


VIRTUALIZATION_SEARCH_TYPES = {
    'cluster': ClusterIndex(),
    'virtualmachine': VirtualMachineIndex(),
}
