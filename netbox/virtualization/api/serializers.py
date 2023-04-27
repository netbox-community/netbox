from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from dcim.api.nested_serializers import (
    NestedDeviceSerializer, NestedDeviceRoleSerializer, NestedPlatformSerializer, NestedSiteSerializer,
)
from dcim.choices import InterfaceModeChoices
from ipam.api.nested_serializers import (
    NestedIPAddressSerializer, NestedL2VPNTerminationSerializer, NestedVLANSerializer, NestedVRFSerializer,
)
from ipam.models import VLAN
from netbox.api.fields import ChoiceField, SerializedPKRelatedField
from netbox.api.serializers import NetBoxModelSerializer
from tenancy.api.nested_serializers import NestedTenantSerializer
from virtualization.choices import *
from virtualization.models import Cluster, ClusterGroup, ClusterType, VirtualMachine, VMInterface
from .nested_serializers import *


#
# Clusters
#

class ClusterTypeSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='virtualization-api:clustertype-detail')
    cluster_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = ClusterType
        fields = [
            'id', 'url', 'display', 'name', 'slug', 'description', 'tags', 'custom_fields', 'created', 'last_updated',
            'cluster_count',
        ]


class ClusterGroupSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='virtualization-api:clustergroup-detail')
    cluster_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = ClusterGroup
        fields = [
            'id', 'url', 'display', 'name', 'slug', 'description', 'tags', 'custom_fields', 'created', 'last_updated',
            'cluster_count',
        ]


class ClusterSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='virtualization-api:cluster-detail')
    type = NestedClusterTypeSerializer()
    group = NestedClusterGroupSerializer(required=False, allow_null=True, default=None)
    status = ChoiceField(choices=ClusterStatusChoices, required=False)
    tenant = NestedTenantSerializer(required=False, allow_null=True)
    site = NestedSiteSerializer(required=False, allow_null=True, default=None)
    device_count = serializers.IntegerField(read_only=True)
    virtualmachine_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Cluster
        fields = [
            'id', 'url', 'display', 'name', 'type', 'group', 'status', 'tenant', 'site', 'description', 'comments',
            'tags', 'custom_fields', 'created', 'last_updated', 'device_count', 'virtualmachine_count',
        ]


#
# Virtual machines
#

class VirtualMachineSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='virtualization-api:virtualmachine-detail')
    status = ChoiceField(choices=VirtualMachineStatusChoices, required=False)
    site = NestedSiteSerializer(required=False, allow_null=True)
    cluster = NestedClusterSerializer(required=False, allow_null=True)
    device = NestedDeviceSerializer(required=False, allow_null=True)
    role = NestedDeviceRoleSerializer(required=False, allow_null=True)
    tenant = NestedTenantSerializer(required=False, allow_null=True)
    platform = NestedPlatformSerializer(required=False, allow_null=True)
    primary_ip = NestedIPAddressSerializer(read_only=True)
    primary_ip4 = NestedIPAddressSerializer(required=False, allow_null=True)
    primary_ip6 = NestedIPAddressSerializer(required=False, allow_null=True)

    class Meta:
        model = VirtualMachine
        fields = [
            'id', 'url', 'display', 'name', 'status', 'site', 'cluster', 'device', 'role', 'tenant', 'platform',
            'primary_ip', 'primary_ip4', 'primary_ip6', 'vcpus', 'memory', 'disk', 'description', 'comments',
            'local_context_data', 'tags', 'custom_fields', 'created', 'last_updated',
        ]
        validators = []


class VirtualMachineWithConfigContextSerializer(VirtualMachineSerializer):
    config_context = serializers.SerializerMethodField()

    class Meta(VirtualMachineSerializer.Meta):
        fields = [
            'id', 'url', 'display', 'name', 'status', 'site', 'cluster', 'device', 'role', 'tenant', 'platform',
            'primary_ip', 'primary_ip4', 'primary_ip6', 'vcpus', 'memory', 'disk', 'description', 'comments',
            'local_context_data', 'tags', 'custom_fields', 'config_context', 'created', 'last_updated',
        ]

    @extend_schema_field(serializers.JSONField(allow_null=True))
    def get_config_context(self, obj):
        return obj.get_config_context()


#
# VM interfaces
#

class VMInterfaceSerializer(NetBoxModelSerializer):
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
    vrf = NestedVRFSerializer(required=False, allow_null=True)
    l2vpn_termination = NestedL2VPNTerminationSerializer(read_only=True, allow_null=True)
    count_ipaddresses = serializers.IntegerField(read_only=True)
    count_fhrp_groups = serializers.IntegerField(read_only=True)
    mac_address = serializers.CharField(required=False, default=None)

    class Meta:
        model = VMInterface
        fields = [
            'id', 'url', 'display', 'virtual_machine', 'name', 'enabled', 'parent', 'bridge', 'mtu', 'mac_address',
            'description', 'mode', 'untagged_vlan', 'tagged_vlans', 'vrf', 'l2vpn_termination', 'tags', 'custom_fields',
            'created', 'last_updated', 'count_ipaddresses', 'count_fhrp_groups',
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
