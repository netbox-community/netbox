import graphene

from netbox.graphql.fields import ObjectField, ObjectListField
from .types import *
from utilities.graphql_optimizer import gql_query_optimizer
from virtualization import models


class VirtualizationQuery(graphene.ObjectType):
    cluster = ObjectField(ClusterType)
    cluster_list = ObjectListField(ClusterType)

    def resolve_cluster_list(root, info, **kwargs):
        return gql_query_optimizer(models.Cluster.objects.all(), info)

    cluster_group = ObjectField(ClusterGroupType)
    cluster_group_list = ObjectListField(ClusterGroupType)

    def resolve_cluster_group_list(root, info, **kwargs):
        return gql_query_optimizer(models.ClusterGroup.objects.all(), info)

    cluster_type = ObjectField(ClusterTypeType)
    cluster_type_list = ObjectListField(ClusterTypeType)

    def resolve_cluster_type_list(root, info, **kwargs):
        return gql_query_optimizer(models.ClusterType.objects.all(), info)

    virtual_machine = ObjectField(VirtualMachineType)
    virtual_machine_list = ObjectListField(VirtualMachineType)

    def resolve_virtual_machine_list(root, info, **kwargs):
        return gql_query_optimizer(models.VirtualMachine.objects.all(), info)

    vm_interface = ObjectField(VMInterfaceType)
    vm_interface_list = ObjectListField(VMInterfaceType)

    def resolve_vm_interface_list(root, info, **kwargs):
        return gql_query_optimizer(models.VMInterface.objects.all(), info)

    virtual_disk = ObjectField(VirtualDiskType)
    virtual_disk_list = ObjectListField(VirtualDiskType)

    def resolve_virtual_disk_list(root, info, **kwargs):
        return gql_query_optimizer(models.VirtualDisk.objects.all(), info)
