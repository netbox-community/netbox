from __future__ import unicode_literals

from rest_framework import serializers

from dcim.api.serializers import NestedPlatformSerializer
from extras.api.customfields import CustomFieldModelSerializer
from tenancy.api.serializers import NestedTenantSerializer
from utilities.api import ValidatedModelSerializer
from virtualization.models import Cluster, ClusterGroup, ClusterType, VirtualMachine, VMInterface


#
# Cluster types
#

class ClusterTypeSerializer(ValidatedModelSerializer):

    class Meta:
        model = ClusterType
        fields = ['id', 'name', 'slug']


class NestedClusterTypeSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='virtualization-api:clustertype-detail')

    class Meta:
        model = ClusterType
        fields = ['id', 'url', 'name', 'slug']


#
# Cluster groups
#

class ClusterGroupSerializer(ValidatedModelSerializer):

    class Meta:
        model = ClusterGroup
        fields = ['id', 'name', 'slug']


class NestedClusterGroupSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='virtualization-api:clustergroup-detail')

    class Meta:
        model = ClusterGroup
        fields = ['id', 'url', 'name', 'slug']


#
# Clusters
#

class ClusterSerializer(CustomFieldModelSerializer):
    type = NestedClusterTypeSerializer()
    group = NestedClusterGroupSerializer()

    class Meta:
        model = Cluster
        fields = ['id', 'name', 'type', 'group', 'comments', 'custom_fields']


class NestedClusterSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='virtualization-api:cluster-detail')

    class Meta:
        model = Cluster
        fields = ['id', 'url', 'name']


class WritableClusterSerializer(CustomFieldModelSerializer):

    class Meta:
        model = Cluster
        fields = ['id', 'name', 'type', 'group', 'comments', 'custom_fields']


#
# Virtual machines
#

class VirtualMachineSerializer(CustomFieldModelSerializer):
    cluster = NestedClusterSerializer()
    tenant = NestedTenantSerializer()
    platform = NestedPlatformSerializer()

    class Meta:
        model = VirtualMachine
        fields = [
            'id', 'name', 'cluster', 'tenant', 'platform', 'primary_ip4', 'primary_ip6', 'comments', 'custom_fields',
        ]


class NestedVirtualMachineSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='virtualization-api:virtualmachine-detail')

    class Meta:
        model = VirtualMachine
        fields = ['id', 'url', 'name']


class WritableVirtualMachineSerializer(CustomFieldModelSerializer):

    class Meta:
        model = Cluster
        fields = [
            'id', 'name', 'cluster', 'tenant', 'platform', 'primary_ip4', 'primary_ip6', 'comments', 'custom_fields',
        ]


#
# VM interfaces
#

class VMInterfaceSerializer(serializers.ModelSerializer):
    virtual_machine = NestedVirtualMachineSerializer()

    class Meta:
        model = VMInterface
        fields = [
            'id', 'name', 'virtual_machine', 'enabled', 'mac_address', 'mtu', 'description',
        ]


class NestedVMInterfaceSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='virtualization-api:vminterface-detail')

    class Meta:
        model = VMInterface
        fields = ['id', 'url', 'name']


class WritableVMInterfaceSerializer(ValidatedModelSerializer):

    class Meta:
        model = VMInterface
        fields = [
            'id', 'name', 'virtual_machine', 'enabled', 'mac_address', 'mtu', 'description',
        ]
