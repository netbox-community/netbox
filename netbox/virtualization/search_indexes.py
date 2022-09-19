import dcim.filtersets
import dcim.tables
from dcim.models import (
    Cable,
    Device,
    DeviceType,
    Interface,
    Location,
    Module,
    ModuleType,
    PowerFeed,
    Rack,
    RackReservation,
    Site,
    VirtualChassis,
)
from django.db import models
from search.models import SearchMixin


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
