from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from dcim.api.serializers_.devices import DeviceSerializer
from dcim.api.serializers_.device_components import MACAddressSerializer
from dcim.api.serializers_.platforms import PlatformSerializer
from dcim.api.serializers_.roles import DeviceRoleSerializer
from dcim.api.serializers_.sites import SiteSerializer
from dcim.choices import InterfaceModeChoices
from extras.api.serializers_.configtemplates import ConfigTemplateSerializer
from ipam.api.serializers_.ip import IPAddressSerializer
from ipam.api.serializers_.vlans import VLANSerializer, VLANTranslationPolicySerializer
from ipam.api.serializers_.vrfs import VRFSerializer
from ipam.models import VLAN
from netbox.api.fields import ChoiceField, SerializedPKRelatedField
from netbox.api.serializers import NetBoxModelSerializer
from tenancy.api.serializers_.tenants import TenantSerializer
from virtualization.choices import *
from virtualization.models import VirtualDisk, VirtualMachine, VMInterface
from vpn.api.serializers_.l2vpn import L2VPNTerminationSerializer
from .clusters import ClusterSerializer
from .nested import NestedVMInterfaceSerializer

__all__ = (
    'VMInterfaceSerializer',
    'VirtualDiskSerializer',
    'VirtualMachineSerializer',
    'VirtualMachineWithConfigContextSerializer',
)


class VirtualMachineSerializer(NetBoxModelSerializer):
    status = ChoiceField(choices=VirtualMachineStatusChoices, required=False)
    site = SiteSerializer(nested=True, required=False, allow_null=True, default=None)
    cluster = ClusterSerializer(nested=True, required=False, allow_null=True, default=None)
    device = DeviceSerializer(nested=True, required=False, allow_null=True, default=None)
    role = DeviceRoleSerializer(nested=True, required=False, allow_null=True)
    tenant = TenantSerializer(nested=True, required=False, allow_null=True, default=None)
    platform = PlatformSerializer(nested=True, required=False, allow_null=True)
    primary_ip = IPAddressSerializer(nested=True, read_only=True, allow_null=True)
    primary_ip4 = IPAddressSerializer(nested=True, required=False, allow_null=True)
    primary_ip6 = IPAddressSerializer(nested=True, required=False, allow_null=True)
    config_template = ConfigTemplateSerializer(nested=True, required=False, allow_null=True, default=None)

    # Counter fields
    interface_count = serializers.IntegerField(read_only=True)
    virtual_disk_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = VirtualMachine
        fields = [
            'id', 'url', 'display_url', 'display', 'name', 'status', 'site', 'cluster', 'device', 'serial', 'role',
            'tenant', 'platform', 'primary_ip', 'primary_ip4', 'primary_ip6', 'vcpus', 'memory', 'disk', 'description',
            'comments', 'config_template', 'local_context_data', 'tags', 'custom_fields', 'created', 'last_updated',
            'interface_count', 'virtual_disk_count',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'description')


class VirtualMachineWithConfigContextSerializer(VirtualMachineSerializer):
    config_context = serializers.SerializerMethodField()

    class Meta(VirtualMachineSerializer.Meta):
        fields = [
            'id', 'url', 'display_url', 'display', 'name', 'status', 'site', 'cluster', 'device', 'serial', 'role',
            'tenant', 'platform', 'primary_ip', 'primary_ip4', 'primary_ip6', 'vcpus', 'memory', 'disk', 'description',
            'comments', 'config_template', 'local_context_data', 'tags', 'custom_fields', 'config_context', 'created',
            'last_updated', 'interface_count', 'virtual_disk_count',
        ]

    @extend_schema_field(serializers.JSONField(allow_null=True))
    def get_config_context(self, obj):
        return obj.get_config_context()


#
# VM interfaces
#

class VMInterfaceSerializer(NetBoxModelSerializer):
    virtual_machine = VirtualMachineSerializer(nested=True)
    parent = NestedVMInterfaceSerializer(required=False, allow_null=True)
    bridge = NestedVMInterfaceSerializer(required=False, allow_null=True)
    mode = ChoiceField(choices=InterfaceModeChoices, allow_blank=True, required=False)
    untagged_vlan = VLANSerializer(nested=True, required=False, allow_null=True)
    tagged_vlans = SerializedPKRelatedField(
        queryset=VLAN.objects.all(),
        serializer=VLANSerializer,
        nested=True,
        required=False,
        many=True
    )
    qinq_svlan = VLANSerializer(nested=True, required=False, allow_null=True)
    vlan_translation_policy = VLANTranslationPolicySerializer(nested=True, required=False, allow_null=True)
    vrf = VRFSerializer(nested=True, required=False, allow_null=True)
    l2vpn_termination = L2VPNTerminationSerializer(nested=True, read_only=True, allow_null=True)
    count_ipaddresses = serializers.IntegerField(read_only=True)
    count_fhrp_groups = serializers.IntegerField(read_only=True)
    # Maintains backward compatibility with NetBox <v4.2
    mac_address = serializers.CharField(allow_null=True, read_only=True)
    primary_mac_address = MACAddressSerializer(nested=True, required=False, allow_null=True)
    mac_addresses = MACAddressSerializer(many=True, nested=True, read_only=True, allow_null=True)

    class Meta:
        model = VMInterface
        fields = [
            'id', 'url', 'display_url', 'display', 'virtual_machine', 'name', 'enabled', 'parent', 'bridge', 'mtu',
            'mac_address', 'primary_mac_address', 'mac_addresses', 'description', 'mode', 'untagged_vlan',
            'tagged_vlans', 'qinq_svlan', 'vlan_translation_policy', 'vrf', 'l2vpn_termination', 'tags',
            'custom_fields', 'created', 'last_updated', 'count_ipaddresses', 'count_fhrp_groups',
        ]
        brief_fields = ('id', 'url', 'display', 'virtual_machine', 'name', 'description')

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


#
# Virtual Disk
#

class VirtualDiskSerializer(NetBoxModelSerializer):
    virtual_machine = VirtualMachineSerializer(nested=True)

    class Meta:
        model = VirtualDisk
        fields = [
            'id', 'url', 'display_url', 'display', 'virtual_machine', 'name', 'description', 'size', 'tags',
            'custom_fields', 'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'virtual_machine', 'name', 'description', 'size')
