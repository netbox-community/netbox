import graphene

from netbox.graphql.fields import ObjectField, ObjectListField
from .types import *


class VirtualizationQuery(graphene.ObjectType):
    cluster = ObjectField(ClusterType)
    clusters = ObjectListField(ClusterType)

    cluster_group = ObjectField(ClusterGroupType)
    cluster_groups = ObjectListField(ClusterGroupType)

    cluster_type = ObjectField(ClusterTypeType)
    cluster_types = ObjectListField(ClusterTypeType)

    virtual_machine = ObjectField(VirtualMachineType)
    virtual_machines = ObjectListField(VirtualMachineType)

    vm_interface = ObjectField(VMInterfaceType)
    vm_interfaces = ObjectListField(VMInterfaceType)
