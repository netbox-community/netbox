from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers

from netbox.api.serializers import WritableNestedSerializer
from virtualization.models import *

__all__ = [
    'NestedClusterGroupSerializer',
    'NestedClusterSerializer',
    'NestedClusterTypeSerializer',
    'NestedVirtualDiskSerializer',
    'NestedVMInterfaceSerializer',
    'NestedVirtualMachineSerializer',
]

#
# Clusters
#


@extend_schema_serializer(
    exclude_fields=('cluster_count',),
)
class NestedClusterTypeSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='virtualization-api:clustertype-detail')
    cluster_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = ClusterType
        fields = ['id', 'url', 'display', 'name', 'slug', 'cluster_count']


@extend_schema_serializer(
    exclude_fields=('cluster_count',),
)
class NestedClusterGroupSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='virtualization-api:clustergroup-detail')
    cluster_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = ClusterGroup
        fields = ['id', 'url', 'display', 'name', 'slug', 'cluster_count']


@extend_schema_serializer(
    exclude_fields=('virtualmachine_count',),
)
class NestedClusterSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='virtualization-api:cluster-detail')
    virtualmachine_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Cluster
        fields = ['id', 'url', 'display', 'name', 'virtualmachine_count']


#
# Virtual machines
#

class NestedVirtualMachineSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='virtualization-api:virtualmachine-detail')

    class Meta:
        model = VirtualMachine
        fields = ['id', 'url', 'display', 'name']


class NestedVMInterfaceSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='virtualization-api:vminterface-detail')
    virtual_machine = NestedVirtualMachineSerializer(read_only=True)

    class Meta:
        model = VMInterface
        fields = ['id', 'url', 'display', 'virtual_machine', 'name']


class NestedVirtualDiskSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='virtualization-api:virtualdisk-detail')
    virtual_machine = NestedVirtualMachineSerializer(read_only=True)

    class Meta:
        model = VirtualDisk
        fields = ['id', 'url', 'display', 'virtual_machine', 'name', 'size']
