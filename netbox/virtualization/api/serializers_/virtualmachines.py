from django.utils.translation import gettext as _
from drf_spectacular.utils import extend_schema_field
from netaddr import EUI, AddrFormatError
from rest_framework import serializers

from dcim.api.serializers_.devices import DeviceSerializer, MACAddressSerializer
from dcim.api.serializers_.platforms import PlatformSerializer
from dcim.api.serializers_.roles import DeviceRoleSerializer
from dcim.api.serializers_.sites import SiteSerializer
from dcim.choices import InterfaceModeChoices
from dcim.models import MACAddress
from extras.api.serializers_.configtemplates import ConfigTemplateSerializer
from ipam.api.serializers_.ip import IPAddressSerializer
from ipam.api.serializers_.vlans import VLANSerializer, VLANTranslationPolicySerializer
from ipam.api.serializers_.vrfs import VRFSerializer
from ipam.models import VLAN
from netbox.api.fields import ChoiceField, SerializedPKRelatedField
from netbox.api.serializers import NetBoxModelSerializer, PrimaryModelSerializer
from tenancy.api.serializers_.tenants import TenantSerializer
from users.api.serializers_.mixins import OwnerMixin
from vpn.api.serializers_.l2vpn import L2VPNTerminationSerializer

from ...choices import *
from ...models import VirtualDisk, VirtualMachine, VirtualMachineType, VMInterface
from .clusters import ClusterSerializer
from .nested import NestedVMInterfaceSerializer

_UNSET = object()

__all__ = (
    'VMInterfaceSerializer',
    'VirtualDiskSerializer',
    'VirtualMachineSerializer',
    'VirtualMachineTypeSerializer',
)


class VirtualMachineTypeSerializer(PrimaryModelSerializer):
    default_platform = PlatformSerializer(nested=True, required=False, allow_null=True)

    # Counter fields
    virtual_machine_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = VirtualMachineType
        fields = [
            'id', 'url', 'display_url', 'display', 'name', 'slug', 'default_platform', 'default_vcpus',
            'default_memory', 'description', 'owner', 'comments', 'tags',
            'custom_fields', 'created', 'last_updated', 'virtual_machine_count',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'slug', 'description')


class VirtualMachineSerializer(PrimaryModelSerializer):
    virtual_machine_type = VirtualMachineTypeSerializer(nested=True, required=False, allow_null=True, default=None)
    status = ChoiceField(choices=VirtualMachineStatusChoices, required=False)
    start_on_boot = ChoiceField(choices=VirtualMachineStartOnBootChoices, required=False)
    site = SiteSerializer(nested=True, required=False, allow_null=True, default=None)
    cluster = ClusterSerializer(nested=True, required=False, allow_null=True, default=None)
    device = DeviceSerializer(nested=True, required=False, allow_null=True, default=None)
    role = DeviceRoleSerializer(nested=True, required=False, allow_null=True)
    tenant = TenantSerializer(nested=True, required=False, allow_null=True, default=None)
    platform = PlatformSerializer(nested=True, required=False, allow_null=True)
    primary_ip = IPAddressSerializer(
        nested=True,
        read_only=True,
        allow_null=True,
        fields=[*IPAddressSerializer.Meta.brief_fields, 'nat_inside', 'nat_outside'],
    )
    primary_ip4 = IPAddressSerializer(
        nested=True,
        required=False,
        allow_null=True,
        fields=[*IPAddressSerializer.Meta.brief_fields, 'nat_inside', 'nat_outside'],
    )
    primary_ip6 = IPAddressSerializer(
        nested=True,
        required=False,
        allow_null=True,
        fields=[*IPAddressSerializer.Meta.brief_fields, 'nat_inside', 'nat_outside'],
    )
    config_template = ConfigTemplateSerializer(nested=True, required=False, allow_null=True, default=None)
    config_context = serializers.SerializerMethodField(read_only=True)

    # Counter fields
    interface_count = serializers.IntegerField(read_only=True)
    virtual_disk_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = VirtualMachine
        fields = [
            'id', 'url', 'display_url', 'display', 'name', 'virtual_machine_type', 'role', 'status', 'start_on_boot',
            'site', 'cluster', 'device', 'platform', 'primary_ip', 'primary_ip4', 'primary_ip6', 'vcpus', 'memory',
            'disk', 'description', 'serial', 'tenant', 'owner', 'comments', 'tags', 'local_context_data',
            'config_template', 'custom_fields', 'created', 'last_updated', 'interface_count', 'virtual_disk_count',
            'config_context',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'description')

    @extend_schema_field(serializers.JSONField(allow_null=True))
    def get_config_context(self, obj):
        return obj.get_config_context()


#
# VM interfaces
#

class VMInterfaceSerializer(OwnerMixin, NetBoxModelSerializer):
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
    # Maintains backward compatibility with NetBox <v4.2; also accepts a MAC string on write to
    # create/update the primary MAC address in a single request.
    mac_address = serializers.CharField(allow_null=True, required=False)
    primary_mac_address = MACAddressSerializer(nested=True, required=False, allow_null=True)
    mac_addresses = MACAddressSerializer(many=True, nested=True, read_only=True, allow_null=True)

    class Meta:
        model = VMInterface
        fields = [
            'id', 'url', 'display_url', 'display', 'virtual_machine', 'name', 'enabled', 'parent', 'bridge', 'mtu',
            'mac_address', 'primary_mac_address', 'mac_addresses', 'description', 'mode', 'untagged_vlan',
            'tagged_vlans', 'qinq_svlan', 'vlan_translation_policy', 'vrf', 'l2vpn_termination', 'owner', 'tags',
            'custom_fields', 'created', 'last_updated', 'count_ipaddresses', 'count_fhrp_groups',
        ]
        brief_fields = ('id', 'url', 'display', 'virtual_machine', 'name', 'description')

    def validate(self, data):
        # Pop mac_address before model validation — it's a cached_property, not a model field.
        # data may be a VMInterface instance (not a dict) in some custom field code paths (#18887).
        mac_address = _UNSET
        if isinstance(data, dict):
            mac_address = data.pop('mac_address', _UNSET)

        if not self.nested and isinstance(data, dict) and mac_address not in (_UNSET, None):
            try:
                EUI(mac_address, version=48)
            except (AddrFormatError, ValueError, TypeError):
                raise serializers.ValidationError({
                    'mac_address': _('Enter a valid MAC address (e.g. 00:11:22:33:44:55).')
                })

        # Validate many-to-many VLAN assignments
        virtual_machine = None
        tagged_vlans = []

        # #18887
        # There seem to be multiple code paths coming through here. Previously, we might either get
        # the VirtualMachine instance from self.instance or from incoming data. However, #18887
        # illustrated that this is also being called when a custom field pointing to an object_type
        # of VMInterface is on the right side of a custom-field assignment coming in from an API
        # request. As such, we need to check a third way to access the VirtualMachine
        # instance--where `data` is the VMInterface instance itself and we can get the associated
        # VirtualMachine via attribute access.
        if isinstance(data, dict):
            virtual_machine = self.instance.virtual_machine if self.instance else data.get('virtual_machine')
            tagged_vlans = data.get('tagged_vlans', [])
        elif isinstance(data, VMInterface):
            virtual_machine = data.virtual_machine
            tagged_vlans = data.tagged_vlans.all()

        if virtual_machine:
            for vlan in tagged_vlans:
                if vlan.site not in [virtual_machine.site, None]:
                    raise serializers.ValidationError({
                        'tagged_vlans': f"VLAN {vlan} must belong to the same site as the interface's parent virtual "
                                        f"machine, or it must be global."
                    })

        data = super().validate(data)

        if mac_address is not _UNSET:
            data['mac_address'] = mac_address

        return data

    def create(self, validated_data):
        mac_address = validated_data.pop('mac_address', None)
        instance = super().create(validated_data)
        if mac_address is not None:
            mac = MACAddress.objects.create(mac_address=mac_address, assigned_object=instance)
            instance.primary_mac_address = mac
            instance.save()
            instance.__dict__.pop('mac_address', None)
        return instance

    def update(self, instance, validated_data):
        mac_address = validated_data.pop('mac_address', _UNSET)
        instance = super().update(instance, validated_data)
        if mac_address is _UNSET:
            pass
        elif mac_address is None:
            instance.primary_mac_address = None
            instance.save()
            instance.__dict__.pop('mac_address', None)
        else:
            # Find an existing MACAddress on this interface with the target value, or create one.
            # Using find-or-create avoids duplicating a MAC that already exists on this interface.
            mac = instance.mac_addresses.filter(mac_address=mac_address).first()
            if mac is None:
                mac = MACAddress.objects.create(mac_address=mac_address, assigned_object=instance)
            if instance.primary_mac_address_id != mac.pk:
                instance.primary_mac_address = mac
                instance.save()
            instance.__dict__.pop('mac_address', None)
        return instance


#
# Virtual Disk
#

class VirtualDiskSerializer(OwnerMixin, NetBoxModelSerializer):
    virtual_machine = VirtualMachineSerializer(nested=True)

    class Meta:
        model = VirtualDisk
        fields = [
            'id', 'url', 'display_url', 'display', 'virtual_machine', 'name', 'description', 'size', 'owner', 'tags',
            'custom_fields', 'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'virtual_machine', 'name', 'description', 'size')
