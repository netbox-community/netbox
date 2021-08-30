import graphene

from netbox.graphql.fields import ObjectField, ObjectListField
from .types import *


class VirtualizationQuery(graphene.ObjectType):
    cluster = ObjectField(ClusterType)
    cluster_list = ObjectListField(ClusterType)

    cluster_group = ObjectField(ClusterGroupType)
    cluster_group_list = ObjectListField(ClusterGroupType)

    cluster_type = ObjectField(ClusterTypeType)
    cluster_type_list = ObjectListField(ClusterTypeType)

    virtual_machine = ObjectField(VirtualMachineType)
    virtual_machine_list = ObjectListField(VirtualMachineType)

    vm_interface = ObjectField(VMInterfaceType)
    vm_interface_list = ObjectListField(VMInterfaceType)
