from __future__ import unicode_literals

from rest_framework.viewsets import ModelViewSet

from extras.api.views import CustomFieldModelViewSet
from utilities.api import WritableSerializerMixin
from virtualization import filters
from virtualization.models import Cluster, ClusterGroup, ClusterType, VirtualMachine, VMInterface
from . import serializers


#
# Clusters
#

class ClusterTypeViewSet(ModelViewSet):
    queryset = ClusterType.objects.all()
    serializer_class = serializers.ClusterTypeSerializer


class ClusterGroupViewSet(ModelViewSet):
    queryset = ClusterGroup.objects.all()
    serializer_class = serializers.ClusterGroupSerializer


class ClusterViewSet(WritableSerializerMixin, CustomFieldModelViewSet):
    queryset = Cluster.objects.select_related('type', 'group')
    serializer_class = serializers.ClusterSerializer
    write_serializer_class = serializers.WritableClusterSerializer
    filter_class = filters.ClusterFilter


#
# Virtual machines
#

class VirtualMachineViewSet(WritableSerializerMixin, CustomFieldModelViewSet):
    queryset = VirtualMachine.objects.all()
    serializer_class = serializers.VirtualMachineSerializer
    write_serializer_class = serializers.WritableVirtualMachineSerializer
    filter_class = filters.VirtualMachineFilter


class VMInterfaceViewSet(WritableSerializerMixin, ModelViewSet):
    queryset = VMInterface.objects.select_related('virtual_machine')
    serializer_class = serializers.VMInterfaceSerializer
    write_serializer_class = serializers.WritableVMInterfaceSerializer
