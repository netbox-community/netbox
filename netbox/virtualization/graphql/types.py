from virtualization import filtersets, models
from netbox.graphql.types import ObjectType, TaggedObjectType

__all__ = (
    'ClusterType',
    'ClusterGroupType',
    'ClusterTypeType',
    'VirtualMachineType',
    'VMInterfaceType',
)


class ClusterType(TaggedObjectType):

    class Meta:
        model = models.Cluster
        fields = '__all__'
        filterset_class = filtersets.ClusterFilterSet


class ClusterGroupType(ObjectType):

    class Meta:
        model = models.ClusterGroup
        fields = '__all__'
        filterset_class = filtersets.ClusterGroupFilterSet


class ClusterTypeType(ObjectType):

    class Meta:
        model = models.ClusterType
        fields = '__all__'
        filterset_class = filtersets.ClusterTypeFilterSet


class VirtualMachineType(TaggedObjectType):

    class Meta:
        model = models.VirtualMachine
        fields = '__all__'
        filterset_class = filtersets.VirtualMachineFilterSet


class VMInterfaceType(ObjectType):

    class Meta:
        model = models.VMInterface
        fields = '__all__'
        filterset_class = filtersets.VMInterfaceFilterSet
