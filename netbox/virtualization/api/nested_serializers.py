import warnings

from drf_spectacular.utils import extend_schema_serializer

from netbox.api.fields import RelatedObjectCountField
from netbox.api.serializers import WritableNestedSerializer
from virtualization.models import *
from .serializers_.nested import NestedVirtualMachineSerializer, NestedVMInterfaceSerializer

__all__ = [
    'NestedClusterGroupSerializer',
    'NestedClusterSerializer',
    'NestedClusterTypeSerializer',
    'NestedVirtualDiskSerializer',
    'NestedVMInterfaceSerializer',
    'NestedVirtualMachineSerializer',
]

# TODO: Remove in v4.2
warnings.warn(
    "Dedicated nested serializers will be removed in NetBox v4.2. Use Serializer(nested=True) instead.",
    DeprecationWarning
)


#
# Clusters
#

@extend_schema_serializer(
    exclude_fields=('cluster_count',),
)
class NestedClusterTypeSerializer(WritableNestedSerializer):
    cluster_count = RelatedObjectCountField('clusters')

    class Meta:
        model = ClusterType
        fields = ['id', 'url', 'display_url', 'display', 'name', 'slug', 'cluster_count']


@extend_schema_serializer(
    exclude_fields=('cluster_count',),
)
class NestedClusterGroupSerializer(WritableNestedSerializer):
    cluster_count = RelatedObjectCountField('clusters')

    class Meta:
        model = ClusterGroup
        fields = ['id', 'url', 'display_url', 'display', 'name', 'slug', 'cluster_count']


@extend_schema_serializer(
    exclude_fields=('virtualmachine_count',),
)
class NestedClusterSerializer(WritableNestedSerializer):
    virtualmachine_count = RelatedObjectCountField('virtual_machines')

    class Meta:
        model = Cluster
        fields = ['id', 'url', 'display_url', 'display', 'name', 'virtualmachine_count']


#
# Virtual machines
#

class NestedVirtualDiskSerializer(WritableNestedSerializer):
    virtual_machine = NestedVirtualMachineSerializer(read_only=True)

    class Meta:
        model = VirtualDisk
        fields = ['id', 'url', 'display_url', 'display', 'virtual_machine', 'name', 'size']
