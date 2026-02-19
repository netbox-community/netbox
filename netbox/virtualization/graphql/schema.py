import strawberry
import strawberry_django

from .types import *


@strawberry.type(name="Query")
class VirtualizationQuery:
    cluster: ClusterType = strawberry_django.field()
    cluster_list: list[ClusterType] = strawberry_django.field()

    cluster_group: ClusterGroupType = strawberry_django.field()
    cluster_group_list: list[ClusterGroupType] = strawberry_django.field()

    cluster_type: ClusterTypeType = strawberry_django.field()
    cluster_type_list: list[ClusterTypeType] = strawberry_django.field()

    virtual_machine: VirtualMachineType = strawberry_django.field()
    virtual_machine_list: list[VirtualMachineType] = strawberry_django.field()

    vm_interface: VMInterfaceType = strawberry_django.field()
    vm_interface_list: list[VMInterfaceType] = strawberry_django.field()

    virtual_disk: VirtualDiskType = strawberry_django.field()
    virtual_disk_list: list[VirtualDiskType] = strawberry_django.field()
