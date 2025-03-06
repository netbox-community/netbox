from django.db.models import Sum
from rest_framework.routers import APIRootView

from extras.api.mixins import ConfigContextQuerySetMixin, RenderConfigMixin
from netbox.api.viewsets import NetBoxModelViewSet
from utilities.query_functions import CollateAsChar
from virtualization import filtersets
from virtualization.models import *
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

class ClusterTypeViewSet(NetBoxModelViewSet):
    queryset = ClusterType.objects.all()
    serializer_class = serializers.ClusterTypeSerializer
    filterset_class = filtersets.ClusterTypeFilterSet


class ClusterGroupViewSet(NetBoxModelViewSet):
    queryset = ClusterGroup.objects.all()
    serializer_class = serializers.ClusterGroupSerializer
    filterset_class = filtersets.ClusterGroupFilterSet


class ClusterViewSet(NetBoxModelViewSet):
    queryset = Cluster.objects.prefetch_related('virtual_machines').annotate(
        allocated_vcpus=Sum('virtual_machines__vcpus'),
        allocated_memory=Sum('virtual_machines__memory'),
        allocated_disk=Sum('virtual_machines__disk'),
    )
    serializer_class = serializers.ClusterSerializer
    filterset_class = filtersets.ClusterFilterSet


#
# Virtual machines
#

class VirtualMachineViewSet(ConfigContextQuerySetMixin, RenderConfigMixin, NetBoxModelViewSet):
    queryset = VirtualMachine.objects.all()
    filterset_class = filtersets.VirtualMachineFilterSet

    def get_serializer_class(self):
        """
        Select the specific serializer based on the request context.

        If the `brief` query param equates to True, return the NestedVirtualMachineSerializer

        If the `exclude` query param includes `config_context` as a value, return the VirtualMachineSerializer

        Else, return the VirtualMachineWithConfigContextSerializer
        """
        request = self.get_serializer_context()['request']
        if self.brief or 'config_context' in request.query_params.get('exclude', []):
            return serializers.VirtualMachineSerializer

        return serializers.VirtualMachineWithConfigContextSerializer


class VMInterfaceViewSet(NetBoxModelViewSet):
    queryset = VMInterface.objects.prefetch_related(
        'l2vpn_terminations',  # Referenced by VMInterfaceSerializer.l2vpn_termination
        'ip_addresses',  # Referenced by VMInterface.count_ipaddresses()
        'fhrp_group_assignments',  # Referenced by VMInterface.count_fhrp_groups()
    )
    serializer_class = serializers.VMInterfaceSerializer
    filterset_class = filtersets.VMInterfaceFilterSet

    def get_bulk_destroy_queryset(self):
        # Ensure child interfaces are deleted prior to their parents
        return self.get_queryset().order_by('virtual_machine', 'parent', CollateAsChar('_name'))


class VirtualDiskViewSet(NetBoxModelViewSet):
    queryset = VirtualDisk.objects.all()
    serializer_class = serializers.VirtualDiskSerializer
    filterset_class = filtersets.VirtualDiskFilterSet
