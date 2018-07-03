from __future__ import unicode_literals

from rest_framework import serializers
from taggit.models import Tag

from dcim.api.serializers import NestedDeviceRoleSerializer, NestedPlatformSerializer, NestedSiteSerializer
from dcim.constants import IFACE_MODE_CHOICES
from dcim.models import Interface
from extras.api.customfields import CustomFieldModelSerializer
from ipam.models import IPAddress, VLAN
from tenancy.api.serializers import NestedTenantSerializer
from utilities.api import ChoiceFieldSerializer, TagField, ValidatedModelSerializer, WritableNestedSerializer
from virtualization.constants import VM_STATUS_CHOICES
from virtualization.models import Cluster, ClusterGroup, ClusterType, VirtualMachine


#
# Cluster types
#

class ClusterTypeSerializer(ValidatedModelSerializer):

    class Meta:
        model = ClusterType
        fields = ['id', 'name', 'slug']


class NestedClusterTypeSerializer(WritableNestedSerializer):
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


class NestedClusterGroupSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='virtualization-api:clustergroup-detail')

    class Meta:
        model = ClusterGroup
        fields = ['id', 'url', 'name', 'slug']


#
# Clusters
#

class ClusterSerializer(CustomFieldModelSerializer):
    type = NestedClusterTypeSerializer()
    group = NestedClusterGroupSerializer(required=False, allow_null=True)
    site = NestedSiteSerializer(required=False, allow_null=True)
    tags = TagField(queryset=Tag.objects.all(), required=False, many=True)

    class Meta:
        model = Cluster
        fields = [
            'id', 'name', 'type', 'group', 'site', 'comments', 'tags', 'custom_fields', 'created', 'last_updated',
        ]


class NestedClusterSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='virtualization-api:cluster-detail')

    class Meta:
        model = Cluster
        fields = ['id', 'url', 'name']


#
# Virtual machines
#

# Cannot import ipam.api.NestedIPAddressSerializer due to circular dependency
class VirtualMachineIPAddressSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:ipaddress-detail')

    class Meta:
        model = IPAddress
        fields = ['id', 'url', 'family', 'address']


class VirtualMachineSerializer(CustomFieldModelSerializer):
    status = ChoiceFieldSerializer(choices=VM_STATUS_CHOICES, required=False)
    cluster = NestedClusterSerializer(required=False, allow_null=True)
    role = NestedDeviceRoleSerializer(required=False, allow_null=True)
    tenant = NestedTenantSerializer(required=False, allow_null=True)
    platform = NestedPlatformSerializer(required=False, allow_null=True)
    primary_ip = VirtualMachineIPAddressSerializer(read_only=True)
    primary_ip4 = VirtualMachineIPAddressSerializer(required=False, allow_null=True)
    primary_ip6 = VirtualMachineIPAddressSerializer(required=False, allow_null=True)
    tags = TagField(queryset=Tag.objects.all(), required=False, many=True)

    class Meta:
        model = VirtualMachine
        fields = [
            'id', 'name', 'status', 'cluster', 'role', 'tenant', 'platform', 'primary_ip', 'primary_ip4', 'primary_ip6',
            'vcpus', 'memory', 'disk', 'comments', 'tags', 'custom_fields', 'created', 'last_updated',
        ]


class VirtualMachineWithConfigContextSerializer(VirtualMachineSerializer):
    config_context = serializers.SerializerMethodField()

    class Meta(VirtualMachineSerializer.Meta):
        fields = [
            'id', 'name', 'status', 'cluster', 'role', 'tenant', 'platform', 'primary_ip', 'primary_ip4', 'primary_ip6',
            'vcpus', 'memory', 'disk', 'comments', 'tags', 'custom_fields', 'config_context', 'created', 'last_updated',
        ]

    def get_config_context(self, obj):
        return obj.get_config_context()


class NestedVirtualMachineSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='virtualization-api:virtualmachine-detail')

    class Meta:
        model = VirtualMachine
        fields = ['id', 'url', 'name']


#
# VM interfaces
#

# Cannot import ipam.api.serializers.NestedVLANSerializer due to circular dependency
class InterfaceVLANSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:vlan-detail')

    class Meta:
        model = VLAN
        fields = ['id', 'url', 'vid', 'name', 'display_name']


class InterfaceSerializer(serializers.ModelSerializer):
    virtual_machine = NestedVirtualMachineSerializer()
    mode = ChoiceFieldSerializer(choices=IFACE_MODE_CHOICES)
    untagged_vlan = InterfaceVLANSerializer()
    tagged_vlans = InterfaceVLANSerializer(many=True)

    class Meta:
        model = Interface
        fields = [
            'id', 'name', 'virtual_machine', 'enabled', 'mac_address', 'mtu', 'mode', 'untagged_vlan', 'tagged_vlans',
            'description',
        ]


class NestedInterfaceSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='virtualization-api:interface-detail')

    class Meta:
        model = Interface
        fields = ['id', 'url', 'name']
