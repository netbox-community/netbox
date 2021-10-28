from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers

from dcim.api.nested_serializers import NestedDeviceRoleSerializer, NestedPlatformSerializer, NestedSiteSerializer
from dcim.choices import InterfaceModeChoices
from ipam.api.nested_serializers import NestedIPAddressSerializer, NestedVLANSerializer
from ipam.models import VLAN
from netbox.api import ChoiceField, SerializedPKRelatedField
from netbox.api.serializers import PrimaryModelSerializer
from tenancy.api.nested_serializers import NestedTenantSerializer
from virtualization.choices import *
from virtualization.models import Cluster, ClusterGroup, ClusterType, VirtualMachine, VMInterface
from .nested_serializers import *


#
# Clusters
#

class ClusterTypeSerializer(PrimaryModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='virtualization-api:clustertype-detail')
    cluster_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = ClusterType
        fields = [
            'id', 'url', 'display', 'name', 'slug', 'description', 'tags', 'custom_fields', 'created', 'last_updated',
            'cluster_count',
        ]


class ClusterGroupSerializer(PrimaryModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='virtualization-api:clustergroup-detail')
    cluster_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = ClusterGroup
        fields = [
            'id', 'url', 'display', 'name', 'slug', 'description', 'tags', 'custom_fields', 'created', 'last_updated',
            'cluster_count',
        ]


class ClusterSerializer(PrimaryModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='virtualization-api:cluster-detail')
    type = NestedClusterTypeSerializer()
    group = NestedClusterGroupSerializer(required=False, allow_null=True, default=None)
    tenant = NestedTenantSerializer(required=False, allow_null=True)
    site = NestedSiteSerializer(required=False, allow_null=True, default=None)
    device_count = serializers.IntegerField(read_only=True)
    virtualmachine_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Cluster
        fields = [
            'id', 'url', 'display', 'name', 'type', 'group', 'tenant', 'site', 'comments', 'tags', 'custom_fields',
            'created', 'last_updated', 'device_count', 'virtualmachine_count',
        ]


#
# Virtual machines
#

class VirtualMachineSerializer(PrimaryModelSerializer):
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
            'id', 'url', 'display', 'name', 'status', 'site', 'cluster', 'role', 'tenant', 'platform', 'primary_ip',
            'primary_ip4', 'primary_ip6', 'vcpus', 'memory', 'disk', 'comments', 'local_context_data', 'tags',
            'custom_fields', 'created', 'last_updated',
        ]
        validators = []


class VirtualMachineWithConfigContextSerializer(VirtualMachineSerializer):
    config_context = serializers.SerializerMethodField()

    class Meta(VirtualMachineSerializer.Meta):
        fields = [
            'id', 'url', 'display', 'name', 'status', 'site', 'cluster', 'role', 'tenant', 'platform', 'primary_ip',
            'primary_ip4', 'primary_ip6', 'vcpus', 'memory', 'disk', 'comments', 'local_context_data', 'tags',
            'custom_fields', 'config_context', 'created', 'last_updated',
        ]

    @swagger_serializer_method(serializer_or_field=serializers.DictField)
    def get_config_context(self, obj):
        return obj.get_config_context()


#
# VM interfaces
#

class VMInterfaceSerializer(PrimaryModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='virtualization-api:vminterface-detail')
    virtual_machine = NestedVirtualMachineSerializer()
    parent = NestedVMInterfaceSerializer(required=False, allow_null=True)
    bridge = NestedVMInterfaceSerializer(required=False, allow_null=True)
    mode = ChoiceField(choices=InterfaceModeChoices, allow_blank=True, required=False)
    untagged_vlan = NestedVLANSerializer(required=False, allow_null=True)
    tagged_vlans = SerializedPKRelatedField(
        queryset=VLAN.objects.all(),
        serializer=NestedVLANSerializer,
        required=False,
        many=True
    )
    count_ipaddresses = serializers.IntegerField(read_only=True)

    class Meta:
        model = VMInterface
        fields = [
            'id', 'url', 'display', 'virtual_machine', 'name', 'enabled', 'parent', 'bridge', 'mtu', 'mac_address',
            'description', 'mode', 'untagged_vlan', 'tagged_vlans', 'tags', 'custom_fields', 'created', 'last_updated',
            'count_ipaddresses',
        ]

    def validate(self, data):

        # Validate many-to-many VLAN assignments
        virtual_machine = self.instance.virtual_machine if self.instance else data.get('virtual_machine')
        for vlan in data.get('tagged_vlans', []):
            if vlan.site not in [virtual_machine.site, None]:
                raise serializers.ValidationError({
                    'tagged_vlans': f"VLAN {vlan} must belong to the same site as the interface's parent virtual "
                                    f"machine, or it must be global."
                })

        return super().validate(data)
