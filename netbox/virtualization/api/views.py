from dcim.models import Interface
from extras.api.views import CustomFieldModelViewSet
from utilities.api import FieldChoicesViewSet, ModelViewSet
from virtualization import filters
from virtualization.models import Cluster, ClusterGroup, ClusterType, VirtualMachine
from . import serializers


#
# Field choices
#

class VirtualizationFieldChoicesViewSet(FieldChoicesViewSet):
    fields = (
        (VirtualMachine, ['status']),
    )


#
# Clusters
#

class ClusterTypeViewSet(ModelViewSet):
    queryset = ClusterType.objects.all()
    serializer_class = serializers.ClusterTypeSerializer
    filter_class = filters.ClusterTypeFilter


class ClusterGroupViewSet(ModelViewSet):
    queryset = ClusterGroup.objects.all()
    serializer_class = serializers.ClusterGroupSerializer
    filter_class = filters.ClusterGroupFilter


class ClusterViewSet(CustomFieldModelViewSet):
    queryset = Cluster.objects.select_related('type', 'group')
    serializer_class = serializers.ClusterSerializer
    filter_class = filters.ClusterFilter


#
# Virtual machines
#

class VirtualMachineViewSet(CustomFieldModelViewSet):
    queryset = VirtualMachine.objects.select_related(
        'cluster__site', 'role', 'tenant', 'platform', 'primary_ip4', 'primary_ip6'
    )
    filter_class = filters.VirtualMachineFilter

    def get_serializer_class(self):
        """
        Include rendered config context when retrieving a single VirtualMachine.
        """
        if self.action == 'retrieve':
            return serializers.VirtualMachineWithConfigContextSerializer
        return serializers.VirtualMachineSerializer


class InterfaceViewSet(ModelViewSet):
    queryset = Interface.objects.filter(virtual_machine__isnull=False).select_related('virtual_machine')
    serializer_class = serializers.InterfaceSerializer
    filter_class = filters.InterfaceFilter
