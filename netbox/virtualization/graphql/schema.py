from typing import List

import strawberry
import strawberry_django

from virtualization import models
from .types import *


@strawberry.type
class VirtualizationQuery:
    @strawberry.field
    def cluster(self, id: int) -> ClusterType:
        return models.Cluster.objects.get(id=id)
    cluster_list: List[ClusterType] = strawberry_django.field()

    @strawberry.field
    def cluster_group(self, id: int) -> ClusterGroupType:
        return models.ClusterGroup.objects.get(id=id)
    cluster_group_list: List[ClusterGroupType] = strawberry_django.field()

    @strawberry.field
    def cluster_type(self, id: int) -> ClusterTypeType:
        return models.ClusterType.objects.get(id=id)
    cluster_type_list: List[ClusterTypeType] = strawberry_django.field()

    @strawberry.field
    def virtual_machine(self, id: int) -> VirtualMachineType:
        return models.VirtualMachine.objects.get(id=id)
    virtual_machine_list: List[VirtualMachineType] = strawberry_django.field()

    @strawberry.field
    def vm_interface(self, id: int) -> VMInterfaceType:
        return models.VMInterface.objects.get(id=id)
    vm_interface_list: List[VMInterfaceType] = strawberry_django.field()

    @strawberry.field
    def virtual_disk(self, id: int) -> VirtualDiskType:
        return models.VirtualDisk.objects.get(id=id)
    virtual_disk_list: List[VirtualDiskType] = strawberry_django.field()
