from typing import List

import strawberry
import strawberry_django

from .types_v1 import *


@strawberry.type(name="Query")
class VirtualizationQueryV1:
    cluster: ClusterTypeV1 = strawberry_django.field()
    cluster_list: List[ClusterTypeV1] = strawberry_django.field()

    cluster_group: ClusterGroupTypeV1 = strawberry_django.field()
    cluster_group_list: List[ClusterGroupTypeV1] = strawberry_django.field()

    cluster_type: ClusterTypeTypeV1 = strawberry_django.field()
    cluster_type_list: List[ClusterTypeTypeV1] = strawberry_django.field()

    virtual_machine: VirtualMachineTypeV1 = strawberry_django.field()
    virtual_machine_list: List[VirtualMachineTypeV1] = strawberry_django.field()

    vm_interface: VMInterfaceTypeV1 = strawberry_django.field()
    vm_interface_list: List[VMInterfaceTypeV1] = strawberry_django.field()

    virtual_disk: VirtualDiskTypeV1 = strawberry_django.field()
    virtual_disk_list: List[VirtualDiskTypeV1] = strawberry_django.field()
