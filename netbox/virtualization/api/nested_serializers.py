from rest_framework import serializers

from dcim.models import Interface
from netbox.api import WritableNestedSerializer
from virtualization.models import Cluster, ClusterGroup, ClusterType, VirtualMachine

__all__ = [
    'NestedClusterGroupSerializer',
    'NestedClusterSerializer',
    'NestedClusterTypeSerializer',
    'NestedVMInterfaceSerializer',
    'NestedVirtualMachineSerializer',
]

#
# Clusters
#


class NestedClusterTypeSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='virtualization-api:clustertype-detail')
    cluster_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = ClusterType
        fields = ['id', 'url', 'name', 'slug', 'cluster_count']


class NestedClusterGroupSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='virtualization-api:clustergroup-detail')
    cluster_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = ClusterGroup
        fields = ['id', 'url', 'name', 'slug', 'cluster_count']


class NestedClusterSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='virtualization-api:cluster-detail')
    virtualmachine_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Cluster
        fields = ['id', 'url', 'name', 'virtualmachine_count']


#
# Virtual machines
#

class NestedVirtualMachineSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='virtualization-api:virtualmachine-detail')

    class Meta:
        model = VirtualMachine
        fields = ['id', 'url', 'name']


class NestedVMInterfaceSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='virtualization-api:vminterface-detail')
    virtual_machine = NestedVirtualMachineSerializer(read_only=True)

    class Meta:
        model = Interface
        fields = ['id', 'url', 'virtual_machine', 'name']
