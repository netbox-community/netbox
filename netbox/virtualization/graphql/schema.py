from typing import List

import strawberry
import strawberry_django
from strawberry_django.pagination import OffsetPaginated

from .types import *


@strawberry.type(name="Query")
class VirtualizationQueryV1:
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


@strawberry.type(name="Query")
class VirtualizationQuery:
    cluster: ClusterType = strawberry_django.field()
    cluster_list: OffsetPaginated[ClusterType] = strawberry_django.offset_paginated()

    cluster_group: ClusterGroupType = strawberry_django.field()
    cluster_group_list: OffsetPaginated[ClusterGroupType] = strawberry_django.offset_paginated()

    cluster_type: ClusterTypeType = strawberry_django.field()
    cluster_type_list: OffsetPaginated[ClusterTypeType] = strawberry_django.offset_paginated()

    virtual_machine: VirtualMachineType = strawberry_django.field()
    virtual_machine_list: OffsetPaginated[VirtualMachineType] = strawberry_django.offset_paginated()

    vm_interface: VMInterfaceType = strawberry_django.field()
    vm_interface_list: OffsetPaginated[VMInterfaceType] = strawberry_django.offset_paginated()

    virtual_disk: VirtualDiskType = strawberry_django.field()
    virtual_disk_list: OffsetPaginated[VirtualDiskType] = strawberry_django.offset_paginated()
