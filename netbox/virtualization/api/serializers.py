from __future__ import unicode_literals

from rest_framework import serializers

from dcim.api.serializers import NestedDeviceRoleSerializer, NestedPlatformSerializer, NestedSiteSerializer
from dcim.constants import VIFACE_FF_CHOICES
from dcim.models import Interface
from extras.api.customfields import CustomFieldModelSerializer
from tenancy.api.serializers import NestedTenantSerializer
from utilities.api import ChoiceFieldSerializer, ValidatedModelSerializer
from virtualization.constants import STATUS_CHOICES
from virtualization.models import Cluster, ClusterGroup, ClusterType, VirtualMachine


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
    site = NestedSiteSerializer()

    class Meta:
        model = Cluster
        fields = ['id', 'name', 'type', 'group', 'site', 'comments', 'custom_fields']


class NestedClusterSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='virtualization-api:cluster-detail')

    class Meta:
        model = Cluster
        fields = ['id', 'url', 'name']


class WritableClusterSerializer(CustomFieldModelSerializer):

    class Meta:
        model = Cluster
        fields = ['id', 'name', 'type', 'group', 'site', 'comments', 'custom_fields']


#
# Virtual machines
#

class VirtualMachineSerializer(CustomFieldModelSerializer):
    status = ChoiceFieldSerializer(choices=STATUS_CHOICES)
    cluster = NestedClusterSerializer()
    role = NestedDeviceRoleSerializer()
    tenant = NestedTenantSerializer()
    platform = NestedPlatformSerializer()

    class Meta:
        model = VirtualMachine
        fields = [
            'id', 'name', 'status', 'cluster', 'role', 'tenant', 'platform', 'primary_ip4', 'primary_ip6', 'vcpus',
            'memory', 'disk', 'comments', 'custom_fields',
        ]


class NestedVirtualMachineSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='virtualization-api:virtualmachine-detail')

    class Meta:
        model = VirtualMachine
        fields = ['id', 'url', 'name']


class WritableVirtualMachineSerializer(CustomFieldModelSerializer):

    class Meta:
        model = VirtualMachine
        fields = [
            'id', 'name', 'status', 'cluster', 'role', 'tenant', 'platform', 'primary_ip4', 'primary_ip6', 'vcpus',
            'memory', 'disk', 'comments', 'custom_fields',
        ]


#
# VM interfaces
#

class InterfaceSerializer(serializers.ModelSerializer):
    virtual_machine = NestedVirtualMachineSerializer()
    form_factor = ChoiceFieldSerializer(choices=VIFACE_FF_CHOICES)

    class Meta:
        model = Interface
        fields = [
            'id', 'name', 'virtual_machine', 'form_factor', 'enabled', 'mac_address', 'mtu', 'description',
        ]


class NestedInterfaceSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='virtualization-api:interface-detail')

    class Meta:
        model = Interface
        fields = ['id', 'url', 'name']


class WritableInterfaceSerializer(ValidatedModelSerializer):

    class Meta:
        model = Interface
        fields = [
            'id', 'name', 'virtual_machine', 'form_factor', 'enabled', 'mac_address', 'mtu', 'description',
        ]
