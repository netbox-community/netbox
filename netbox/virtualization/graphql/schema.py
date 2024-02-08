from typing import List
import strawberry
import strawberry_django

from virtualization import models
from .types import *


@strawberry.type
class VirtualizationQuery:
    cluster: ClusterType = strawberry_django.field()
    cluster_list: List[ClusterType] = strawberry_django.field()

    cluster_group: ClusterGroupType = strawberry_django.field()
    cluster_group_list: List[ClusterGroupType] = strawberry_django.field()

    cluster_type: ClusterTypeType = strawberry_django.field()
    cluster_type_list: List[ClusterTypeType] = strawberry_django.field()

    virtual_machine: VirtualMachineType = strawberry_django.field()
    virtual_machine_list: List[VirtualMachineType] = strawberry_django.field()

    vm_interface: VMInterfaceType = strawberry_django.field()
    vm_interface_list: List[VMInterfaceType] = strawberry_django.field()

    virtual_disk: VirtualDiskType = strawberry_django.field()
    virtual_disk_list: List[VirtualDiskType] = strawberry_django.field()
