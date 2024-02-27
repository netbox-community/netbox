from django.contrib.contenttypes.models import ContentType
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from dcim.choices import *
from dcim.constants import *
from dcim.models import (
    ConsolePort, ConsoleServerPort, DeviceBay, FrontPort, Interface, InventoryItem, ModuleBay, PowerOutlet, PowerPort,
    RearPort, VirtualDeviceContext,
)
from ipam.api.serializers_.vlans import VLANSerializer
from ipam.api.serializers_.vrfs import VRFSerializer
from ipam.models import VLAN
from netbox.api.fields import ChoiceField, ContentTypeField, SerializedPKRelatedField
from netbox.api.serializers import NetBoxModelSerializer, WritableNestedSerializer
from utilities.api import get_serializer_for_model
from vpn.api.serializers_.l2vpn import L2VPNTerminationSerializer
from wireless.api.nested_serializers import NestedWirelessLinkSerializer
from wireless.api.serializers_.wirelesslans import WirelessLANSerializer
from wireless.choices import *
from wireless.models import WirelessLAN
from .base import ConnectedEndpointsSerializer
from .cables import CabledObjectSerializer
from .devices import DeviceSerializer, ModuleSerializer, VirtualDeviceContextSerializer
from .manufacturers import ManufacturerSerializer
from .roles import InventoryItemRoleSerializer
from ..nested_serializers import *

__all__ = (
    'ConsolePortSerializer',
    'ConsoleServerPortSerializer',
    'DeviceBaySerializer',
    'FrontPortSerializer',
    'InterfaceSerializer',
    'InventoryItemSerializer',
    'ModuleBaySerializer',
    'PowerOutletSerializer',
    'PowerPortSerializer',
    'RearPortSerializer',
)


class ConsoleServerPortSerializer(NetBoxModelSerializer, CabledObjectSerializer, ConnectedEndpointsSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:consoleserverport-detail')
    device = DeviceSerializer(nested=True)
    module = ModuleSerializer(
        nested=True,
        requested_fields=('id', 'url', 'display', 'device', 'module_bay'),
        required=False,
        allow_null=True
    )
    type = ChoiceField(
        choices=ConsolePortTypeChoices,
        allow_blank=True,
        required=False
    )
    speed = ChoiceField(
        choices=ConsolePortSpeedChoices,
        allow_null=True,
        required=False
    )

    class Meta:
        model = ConsoleServerPort
        fields = [
            'id', 'url', 'display', 'device', 'module', 'name', 'label', 'type', 'speed', 'description',
            'mark_connected', 'cable', 'cable_end', 'link_peers', 'link_peers_type', 'connected_endpoints',
            'connected_endpoints_type', 'connected_endpoints_reachable', 'tags', 'custom_fields', 'created',
            'last_updated', '_occupied',
        ]
        brief_fields = ('id', 'url', 'display', 'device', 'name', 'description', 'cable', '_occupied')


class ConsolePortSerializer(NetBoxModelSerializer, CabledObjectSerializer, ConnectedEndpointsSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:consoleport-detail')
    device = DeviceSerializer(nested=True)
    module = ModuleSerializer(
        nested=True,
        requested_fields=('id', 'url', 'display', 'device', 'module_bay'),
        required=False,
        allow_null=True
    )
    type = ChoiceField(
        choices=ConsolePortTypeChoices,
        allow_blank=True,
        required=False
    )
    speed = ChoiceField(
        choices=ConsolePortSpeedChoices,
        allow_null=True,
        required=False
    )

    class Meta:
        model = ConsolePort
        fields = [
            'id', 'url', 'display', 'device', 'module', 'name', 'label', 'type', 'speed', 'description',
            'mark_connected', 'cable', 'cable_end', 'link_peers', 'link_peers_type', 'connected_endpoints',
            'connected_endpoints_type', 'connected_endpoints_reachable', 'tags', 'custom_fields', 'created',
            'last_updated', '_occupied',
        ]
        brief_fields = ('id', 'url', 'display', 'device', 'name', 'description', 'cable', '_occupied')


class PowerPortSerializer(NetBoxModelSerializer, CabledObjectSerializer, ConnectedEndpointsSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:powerport-detail')
    device = DeviceSerializer(nested=True)
    module = ModuleSerializer(
        nested=True,
        requested_fields=('id', 'url', 'display', 'device', 'module_bay'),
        required=False,
        allow_null=True
    )
    type = ChoiceField(
        choices=PowerPortTypeChoices,
        allow_blank=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = PowerPort
        fields = [
            'id', 'url', 'display', 'device', 'module', 'name', 'label', 'type', 'maximum_draw', 'allocated_draw',
            'description', 'mark_connected', 'cable', 'cable_end', 'link_peers', 'link_peers_type',
            'connected_endpoints', 'connected_endpoints_type', 'connected_endpoints_reachable', 'tags', 'custom_fields',
            'created', 'last_updated', '_occupied',
        ]
        brief_fields = ('id', 'url', 'display', 'device', 'name', 'description', 'cable', '_occupied')


class PowerOutletSerializer(NetBoxModelSerializer, CabledObjectSerializer, ConnectedEndpointsSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:poweroutlet-detail')
    device = DeviceSerializer(nested=True)
    module = ModuleSerializer(
        nested=True,
        requested_fields=('id', 'url', 'display', 'device', 'module_bay'),
        required=False,
        allow_null=True
    )
    type = ChoiceField(
        choices=PowerOutletTypeChoices,
        allow_blank=True,
        required=False,
        allow_null=True
    )
    power_port = PowerPortSerializer(
        nested=True,
        required=False,
        allow_null=True
    )
    feed_leg = ChoiceField(
        choices=PowerOutletFeedLegChoices,
        allow_blank=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = PowerOutlet
        fields = [
            'id', 'url', 'display', 'device', 'module', 'name', 'label', 'type', 'power_port', 'feed_leg',
            'description', 'mark_connected', 'cable', 'cable_end', 'link_peers', 'link_peers_type',
            'connected_endpoints', 'connected_endpoints_type', 'connected_endpoints_reachable', 'tags', 'custom_fields',
            'created', 'last_updated', '_occupied',
        ]
        brief_fields = ('id', 'url', 'display', 'device', 'name', 'description', 'cable', '_occupied')


class InterfaceSerializer(NetBoxModelSerializer, CabledObjectSerializer, ConnectedEndpointsSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:interface-detail')
    device = DeviceSerializer(nested=True)
    vdcs = SerializedPKRelatedField(
        queryset=VirtualDeviceContext.objects.all(),
        serializer=VirtualDeviceContextSerializer,
        nested=True,
        required=False,
        many=True
    )
    module = ModuleSerializer(
        nested=True,
        requested_fields=('id', 'url', 'display', 'device', 'module_bay'),
        required=False,
        allow_null=True
    )
    type = ChoiceField(choices=InterfaceTypeChoices)
    parent = NestedInterfaceSerializer(required=False, allow_null=True)
    bridge = NestedInterfaceSerializer(required=False, allow_null=True)
    lag = NestedInterfaceSerializer(required=False, allow_null=True)
    mode = ChoiceField(choices=InterfaceModeChoices, required=False, allow_blank=True)
    duplex = ChoiceField(choices=InterfaceDuplexChoices, required=False, allow_blank=True, allow_null=True)
    rf_role = ChoiceField(choices=WirelessRoleChoices, required=False, allow_blank=True)
    rf_channel = ChoiceField(choices=WirelessChannelChoices, required=False, allow_blank=True)
    poe_mode = ChoiceField(choices=InterfacePoEModeChoices, required=False, allow_blank=True)
    poe_type = ChoiceField(choices=InterfacePoETypeChoices, required=False, allow_blank=True)
    untagged_vlan = VLANSerializer(nested=True, required=False, allow_null=True)
    tagged_vlans = SerializedPKRelatedField(
        queryset=VLAN.objects.all(),
        serializer=VLANSerializer,
        nested=True,
        required=False,
        many=True
    )
    vrf = VRFSerializer(nested=True, required=False, allow_null=True)
    l2vpn_termination = L2VPNTerminationSerializer(nested=True, read_only=True, allow_null=True)
    wireless_link = NestedWirelessLinkSerializer(read_only=True, allow_null=True)
    wireless_lans = SerializedPKRelatedField(
        queryset=WirelessLAN.objects.all(),
        serializer=WirelessLANSerializer,
        nested=True,
        required=False,
        many=True
    )
    count_ipaddresses = serializers.IntegerField(read_only=True)
    count_fhrp_groups = serializers.IntegerField(read_only=True)
    mac_address = serializers.CharField(
        required=False,
        default=None,
        allow_blank=True,
        allow_null=True
    )
    wwn = serializers.CharField(required=False, default=None, allow_blank=True, allow_null=True)

    class Meta:
        model = Interface
        fields = [
            'id', 'url', 'display', 'device', 'vdcs', 'module', 'name', 'label', 'type', 'enabled', 'parent', 'bridge',
            'lag', 'mtu', 'mac_address', 'speed', 'duplex', 'wwn', 'mgmt_only', 'description', 'mode', 'rf_role',
            'rf_channel', 'poe_mode', 'poe_type', 'rf_channel_frequency', 'rf_channel_width', 'tx_power',
            'untagged_vlan', 'tagged_vlans', 'mark_connected', 'cable', 'cable_end', 'wireless_link', 'link_peers',
            'link_peers_type', 'wireless_lans', 'vrf', 'l2vpn_termination', 'connected_endpoints',
            'connected_endpoints_type', 'connected_endpoints_reachable', 'tags', 'custom_fields', 'created',
            'last_updated', 'count_ipaddresses', 'count_fhrp_groups', '_occupied',
        ]
        brief_fields = ('id', 'url', 'display', 'device', 'name', 'description', 'cable', '_occupied')

    def validate(self, data):

        # Validate many-to-many VLAN assignments
        if not self.nested:
            device = self.instance.device if self.instance else data.get('device')
            for vlan in data.get('tagged_vlans', []):
                if vlan.site not in [device.site, None]:
                    raise serializers.ValidationError({
                        'tagged_vlans': f"VLAN {vlan} must belong to the same site as the interface's parent device, "
                                        f"or it must be global."
                    })

        return super().validate(data)


class RearPortSerializer(NetBoxModelSerializer, CabledObjectSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:rearport-detail')
    device = DeviceSerializer(nested=True)
    module = ModuleSerializer(
        nested=True,
        requested_fields=('id', 'url', 'display', 'device', 'module_bay'),
        required=False,
        allow_null=True
    )
    type = ChoiceField(choices=PortTypeChoices)

    class Meta:
        model = RearPort
        fields = [
            'id', 'url', 'display', 'device', 'module', 'name', 'label', 'type', 'color', 'positions', 'description',
            'mark_connected', 'cable', 'cable_end', 'link_peers', 'link_peers_type', 'tags', 'custom_fields', 'created',
            'last_updated', '_occupied',
        ]
        brief_fields = ('id', 'url', 'display', 'device', 'name', 'description', 'cable', '_occupied')


class FrontPortRearPortSerializer(WritableNestedSerializer):
    """
    NestedRearPortSerializer but with parent device omitted (since front and rear ports must belong to same device)
    """
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:rearport-detail')

    class Meta:
        model = RearPort
        fields = ['id', 'url', 'display', 'name', 'label', 'description']


class FrontPortSerializer(NetBoxModelSerializer, CabledObjectSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:frontport-detail')
    device = DeviceSerializer(nested=True)
    module = ModuleSerializer(
        nested=True,
        requested_fields=('id', 'url', 'display', 'device', 'module_bay'),
        required=False,
        allow_null=True
    )
    type = ChoiceField(choices=PortTypeChoices)
    rear_port = FrontPortRearPortSerializer()

    class Meta:
        model = FrontPort
        fields = [
            'id', 'url', 'display', 'device', 'module', 'name', 'label', 'type', 'color', 'rear_port',
            'rear_port_position', 'description', 'mark_connected', 'cable', 'cable_end', 'link_peers',
            'link_peers_type', 'tags', 'custom_fields', 'created', 'last_updated', '_occupied',
        ]
        brief_fields = ('id', 'url', 'display', 'device', 'name', 'description', 'cable', '_occupied')


class ModuleBaySerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:modulebay-detail')
    device = DeviceSerializer(nested=True)
    installed_module = ModuleSerializer(
        nested=True,
        requested_fields=('id', 'url', 'display', 'serial', 'description'),
        required=False,
        allow_null=True
    )

    class Meta:
        model = ModuleBay
        fields = [
            'id', 'url', 'display', 'device', 'name', 'installed_module', 'label', 'position', 'description', 'tags',
            'custom_fields', 'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'installed_module', 'name', 'description')


class DeviceBaySerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:devicebay-detail')
    device = DeviceSerializer(nested=True)
    installed_device = DeviceSerializer(nested=True, required=False, allow_null=True)

    class Meta:
        model = DeviceBay
        fields = [
            'id', 'url', 'display', 'device', 'name', 'label', 'description', 'installed_device', 'tags',
            'custom_fields', 'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'device', 'name', 'description')


class InventoryItemSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:inventoryitem-detail')
    device = DeviceSerializer(nested=True)
    parent = serializers.PrimaryKeyRelatedField(queryset=InventoryItem.objects.all(), allow_null=True, default=None)
    role = InventoryItemRoleSerializer(nested=True, required=False, allow_null=True)
    manufacturer = ManufacturerSerializer(nested=True, required=False, allow_null=True, default=None)
    component_type = ContentTypeField(
        queryset=ContentType.objects.filter(MODULAR_COMPONENT_MODELS),
        required=False,
        allow_null=True
    )
    component = serializers.SerializerMethodField(read_only=True)
    _depth = serializers.IntegerField(source='level', read_only=True)

    class Meta:
        model = InventoryItem
        fields = [
            'id', 'url', 'display', 'device', 'parent', 'name', 'label', 'role', 'manufacturer', 'part_id', 'serial',
            'asset_tag', 'discovered', 'description', 'component_type', 'component_id', 'component', 'tags',
            'custom_fields', 'created', 'last_updated', '_depth',
        ]
        brief_fields = ('id', 'url', 'display', 'device', 'name', 'description', '_depth')

    @extend_schema_field(serializers.JSONField(allow_null=True))
    def get_component(self, obj):
        if obj.component is None:
            return None
        serializer = get_serializer_for_model(obj.component)
        context = {'request': self.context['request']}
        return serializer(obj.component, nested=True, context=context).data
