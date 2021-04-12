from rest_framework.routers import APIRootView

from dcim.models import Device
from extras.api.views import ConfigContextQuerySetMixin, CustomFieldModelViewSet, ModelViewSet
from utilities.utils import count_related
from virtualization import filters
from virtualization.models import Cluster, ClusterGroup, ClusterType, VirtualMachine, VMInterface
from . import serializers


class VirtualizationRootView(APIRootView):
    """
    Virtualization API root view
    """
    def get_view_name(self):
        return 'Virtualization'


#
# Clusters
#

class ClusterTypeViewSet(ModelViewSet):
    queryset = ClusterType.objects.annotate(
        cluster_count=count_related(Cluster, 'type')
    )
    serializer_class = serializers.ClusterTypeSerializer
    filterset_class = filters.ClusterTypeFilterSet


class ClusterGroupViewSet(ModelViewSet):
    queryset = ClusterGroup.objects.annotate(
        cluster_count=count_related(Cluster, 'group')
    )
    serializer_class = serializers.ClusterGroupSerializer
    filterset_class = filters.ClusterGroupFilterSet


class ClusterViewSet(CustomFieldModelViewSet):
    queryset = Cluster.objects.prefetch_related(
        'type', 'group', 'tenant', 'site', 'tags'
    ).annotate(
        device_count=count_related(Device, 'cluster'),
        virtualmachine_count=count_related(VirtualMachine, 'cluster')
    )
    serializer_class = serializers.ClusterSerializer
    filterset_class = filters.ClusterFilterSet


#
# Virtual machines
#

class VirtualMachineViewSet(ConfigContextQuerySetMixin, CustomFieldModelViewSet):
    queryset = VirtualMachine.objects.prefetch_related(
        'cluster__site', 'role', 'tenant', 'platform', 'primary_ip4', 'primary_ip6', 'tags'
    )
    filterset_class = filters.VirtualMachineFilterSet

    def get_serializer_class(self):
        """
        Select the specific serializer based on the request context.

        If the `brief` query param equates to True, return the NestedVirtualMachineSerializer

        If the `exclude` query param includes `config_context` as a value, return the VirtualMachineSerializer

        Else, return the VirtualMachineWithConfigContextSerializer
        """

        request = self.get_serializer_context()['request']
        if request.query_params.get('brief', False):
            return serializers.NestedVirtualMachineSerializer

        elif 'config_context' in request.query_params.get('exclude', []):
            return serializers.VirtualMachineSerializer

        return serializers.VirtualMachineWithConfigContextSerializer


class VMInterfaceViewSet(ModelViewSet):
    queryset = VMInterface.objects.prefetch_related(
        'virtual_machine', 'tags', 'tagged_vlans', 'ip_addresses',
    )
    serializer_class = serializers.VMInterfaceSerializer
    filterset_class = filters.VMInterfaceFilterSet
    brief_prefetch_fields = ['virtual_machine']
