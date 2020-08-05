from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response

from dcim.models import Device
from extras.api.serializers import RenderedGraphSerializer
from extras.api.views import CustomFieldModelViewSet
from extras.models import Graph
from utilities.api import ModelViewSet
from utilities.utils import get_subquery
from virtualization import filters
from virtualization.models import Cluster, ClusterGroup, ClusterType, VirtualMachine, VMInterface
from . import serializers


#
# Clusters
#

class ClusterTypeViewSet(ModelViewSet):
    queryset = ClusterType.objects.annotate(
        cluster_count=Count('clusters')
    ).order_by(*ClusterType._meta.ordering)
    serializer_class = serializers.ClusterTypeSerializer
    filterset_class = filters.ClusterTypeFilterSet


class ClusterGroupViewSet(ModelViewSet):
    queryset = ClusterGroup.objects.annotate(
        cluster_count=Count('clusters')
    ).order_by(*ClusterGroup._meta.ordering)
    serializer_class = serializers.ClusterGroupSerializer
    filterset_class = filters.ClusterGroupFilterSet


class ClusterViewSet(CustomFieldModelViewSet):
    queryset = Cluster.objects.prefetch_related(
        'type', 'group', 'tenant', 'site', 'tags'
    ).annotate(
        device_count=get_subquery(Device, 'cluster'),
        virtualmachine_count=get_subquery(VirtualMachine, 'cluster')
    ).order_by(*Cluster._meta.ordering)
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


class VMInterfaceViewSet(ModelViewSet):
    queryset = VMInterface.objects.prefetch_related(
        'virtual_machine', 'tags', 'tagged_vlans'
    )
    serializer_class = serializers.VMInterfaceSerializer
    filterset_class = filters.VMInterfaceFilterSet

    @action(detail=True)
    def graphs(self, request, pk):
        """
        A convenience method for rendering graphs for a particular VM interface.
        """
        vminterface = get_object_or_404(self.queryset, pk=pk)
        queryset = Graph.objects.restrict(request.user).filter(type__model='vminterface')
        serializer = RenderedGraphSerializer(queryset, many=True, context={'graphed_object': vminterface})
        return Response(serializer.data)
