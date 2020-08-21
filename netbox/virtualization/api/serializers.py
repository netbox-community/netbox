from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers

from dcim.api.nested_serializers import NestedDeviceRoleSerializer, NestedPlatformSerializer, NestedSiteSerializer
from dcim.choices import InterfaceModeChoices
from extras.api.customfields import CustomFieldModelSerializer
from extras.api.serializers import TaggedObjectSerializer
from ipam.api.nested_serializers import NestedIPAddressSerializer, NestedVLANSerializer
from ipam.models import VLAN
from tenancy.api.nested_serializers import NestedTenantSerializer
from utilities.api import ChoiceField, SerializedPKRelatedField, ValidatedModelSerializer
from virtualization.choices import *
from virtualization.models import Cluster, ClusterGroup, ClusterType, VirtualMachine, VMInterface
from .nested_serializers import *


#
# Clusters
#

class ClusterTypeSerializer(ValidatedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='virtualization-api:clustertype-detail')
    cluster_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = ClusterType
        fields = ['id', 'url', 'name', 'slug', 'description', 'cluster_count']


class ClusterGroupSerializer(ValidatedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='virtualization-api:clustergroup-detail')
    cluster_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = ClusterGroup
        fields = ['id', 'url', 'name', 'slug', 'description', 'cluster_count']


class ClusterSerializer(TaggedObjectSerializer, CustomFieldModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='virtualization-api:cluster-detail')
    type = NestedClusterTypeSerializer()
    group = NestedClusterGroupSerializer(required=False, allow_null=True)
    tenant = NestedTenantSerializer(required=False, allow_null=True)
    site = NestedSiteSerializer(required=False, allow_null=True)
    device_count = serializers.IntegerField(read_only=True)
    virtualmachine_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Cluster
        fields = [
            'id', 'url', 'name', 'type', 'group', 'tenant', 'site', 'comments', 'tags', 'custom_fields', 'created',
            'last_updated', 'device_count', 'virtualmachine_count',
        ]


#
# Virtual machines
#

class VirtualMachineSerializer(TaggedObjectSerializer, CustomFieldModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='virtualization-api:virtualmachine-detail')
    status = ChoiceField(choices=VirtualMachineStatusChoices, required=False)
    site = NestedSiteSerializer(read_only=True)
    cluster = NestedClusterSerializer()
    role = NestedDeviceRoleSerializer(required=False, allow_null=True)
    tenant = NestedTenantSerializer(required=False, allow_null=True)
    platform = NestedPlatformSerializer(required=False, allow_null=True)
    primary_ip = NestedIPAddressSerializer(read_only=True)
    primary_ip4 = NestedIPAddressSerializer(required=False, allow_null=True)
    primary_ip6 = NestedIPAddressSerializer(required=False, allow_null=True)

    class Meta:
        model = VirtualMachine
        fields = [
            'id', 'url', 'name', 'status', 'site', 'cluster', 'role', 'tenant', 'platform', 'primary_ip', 'primary_ip4',
            'primary_ip6', 'vcpus', 'memory', 'disk', 'comments', 'local_context_data', 'tags', 'custom_fields',
            'created', 'last_updated',
        ]
        validators = []


class VirtualMachineWithConfigContextSerializer(VirtualMachineSerializer):
    config_context = serializers.SerializerMethodField()

    class Meta(VirtualMachineSerializer.Meta):
        fields = [
            'id', 'url', 'name', 'status', 'site', 'cluster', 'role', 'tenant', 'platform', 'primary_ip', 'primary_ip4',
            'primary_ip6', 'vcpus', 'memory', 'disk', 'comments', 'local_context_data', 'tags', 'custom_fields',
            'config_context', 'created', 'last_updated',
        ]

    @swagger_serializer_method(serializer_or_field=serializers.DictField)
    def get_config_context(self, obj):
        return obj.get_config_context()


#
# VM interfaces
#

class VMInterfaceSerializer(TaggedObjectSerializer, ValidatedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='virtualization-api:vminterface-detail')
    virtual_machine = NestedVirtualMachineSerializer()
    mode = ChoiceField(choices=InterfaceModeChoices, allow_blank=True, required=False)
    untagged_vlan = NestedVLANSerializer(required=False, allow_null=True)
    tagged_vlans = SerializedPKRelatedField(
        queryset=VLAN.objects.all(),
        serializer=NestedVLANSerializer,
        required=False,
        many=True
    )

    class Meta:
        model = VMInterface
        fields = [
            'id', 'url', 'virtual_machine', 'name', 'enabled', 'mtu', 'mac_address', 'description', 'mode',
            'untagged_vlan', 'tagged_vlans', 'tags',
        ]
