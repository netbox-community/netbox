from django.db.models import Count

from dcim.models import Device, Interface
from extras.api.views import CustomFieldModelViewSet
from utilities.api import ModelViewSet
from utilities.utils import get_subquery
from virtualization import filters
from virtualization.models import Cluster, ClusterGroup, ClusterType, VirtualMachine
from . import serializers


#
# Clusters
#

class ClusterTypeViewSet(ModelViewSet):
    queryset = ClusterType.objects.annotate(
        cluster_count=Count('clusters')
    )
    serializer_class = serializers.ClusterTypeSerializer
    filterset_class = filters.ClusterTypeFilterSet


class ClusterGroupViewSet(ModelViewSet):
    queryset = ClusterGroup.objects.annotate(
        cluster_count=Count('clusters')
    )
    serializer_class = serializers.ClusterGroupSerializer
    filterset_class = filters.ClusterGroupFilterSet


class ClusterViewSet(CustomFieldModelViewSet):
    queryset = Cluster.objects.prefetch_related(
        'type', 'group', 'tenant', 'site', 'tags'
    ).annotate(
        device_count=get_subquery(Device, 'cluster'),
        virtualmachine_count=get_subquery(VirtualMachine, 'cluster')
    )
    serializer_class = serializers.ClusterSerializer
    filterset_class = filters.ClusterFilterSet


#
# Virtual machines
#

class VirtualMachineViewSet(CustomFieldModelViewSet):
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


class InterfaceViewSet(ModelViewSet):
    queryset = Interface.objects.filter(
        virtual_machine__isnull=False
    ).prefetch_related(
        'virtual_machine', 'tags'
    )
    serializer_class = serializers.InterfaceSerializer
    filterset_class = filters.InterfaceFilterSet

    def get_serializer_class(self):
        request = self.get_serializer_context()['request']
        if request.query_params.get('brief', False):
            # Override get_serializer_for_model(), which will return the DCIM NestedInterfaceSerializer
            return serializers.NestedInterfaceSerializer
        return serializers.InterfaceSerializer
