from dcim.graphql.types import ComponentObjectType
from ipam.graphql.mixins import IPAddressesMixin, VLANGroupsMixin
from virtualization import filtersets, models
from netbox.graphql.types import OrganizationalObjectType, PrimaryObjectType

__all__ = (
    'ClusterType',
    'ClusterGroupType',
    'ClusterTypeType',
    'VirtualMachineType',
    'VMInterfaceType',
)


class ClusterType(VLANGroupsMixin, PrimaryObjectType):

    class Meta:
        model = models.Cluster
        fields = '__all__'
        filterset_class = filtersets.ClusterFilterSet


class ClusterGroupType(VLANGroupsMixin, OrganizationalObjectType):

    class Meta:
        model = models.ClusterGroup
        fields = '__all__'
        filterset_class = filtersets.ClusterGroupFilterSet


class ClusterTypeType(OrganizationalObjectType):

    class Meta:
        model = models.ClusterType
        fields = '__all__'
        filterset_class = filtersets.ClusterTypeFilterSet


class VirtualMachineType(PrimaryObjectType):

    class Meta:
        model = models.VirtualMachine
        fields = '__all__'
        filterset_class = filtersets.VirtualMachineFilterSet


class VMInterfaceType(IPAddressesMixin, ComponentObjectType):

    class Meta:
        model = models.VMInterface
        fields = '__all__'
        filterset_class = filtersets.VMInterfaceFilterSet

    def resolve_mode(self, info):
        return self.mode or None
