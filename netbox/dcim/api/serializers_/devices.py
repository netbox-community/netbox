import decimal

from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext as _
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from dcim.choices import *
from dcim.constants import MACADDRESS_ASSIGNMENT_MODELS
from dcim.models import Device, DeviceBay, MACAddress, Module, VirtualDeviceContext
from extras.api.serializers_.configtemplates import ConfigTemplateSerializer
from ipam.api.serializers_.ip import IPAddressSerializer
from netbox.api.fields import ChoiceField, ContentTypeField, RelatedObjectCountField
from netbox.api.serializers import NetBoxModelSerializer
from tenancy.api.serializers_.tenants import TenantSerializer
from utilities.api import get_serializer_for_model
from virtualization.api.serializers_.clusters import ClusterSerializer
from .devicetypes import *
from .platforms import PlatformSerializer
from .racks import RackSerializer
from .roles import DeviceRoleSerializer
from .nested import NestedDeviceBaySerializer, NestedDeviceSerializer, NestedModuleBaySerializer
from .sites import LocationSerializer, SiteSerializer
from .virtualchassis import VirtualChassisSerializer

__all__ = (
    'DeviceSerializer',
    'DeviceWithConfigContextSerializer',
    'MACAddressSerializer',
    'ModuleSerializer',
    'VirtualDeviceContextSerializer',
)


class DeviceSerializer(NetBoxModelSerializer):
    device_type = DeviceTypeSerializer(nested=True)
    role = DeviceRoleSerializer(nested=True)
    tenant = TenantSerializer(
        nested=True,
        required=False,
        allow_null=True,
        default=None
    )
    platform = PlatformSerializer(nested=True, required=False, allow_null=True)
    site = SiteSerializer(nested=True)
    location = LocationSerializer(nested=True, required=False, allow_null=True, default=None)
    rack = RackSerializer(nested=True, required=False, allow_null=True, default=None)
    face = ChoiceField(choices=DeviceFaceChoices, allow_blank=True, default=lambda: '')
    position = serializers.DecimalField(
        max_digits=4,
        decimal_places=1,
        allow_null=True,
        label=_('Position (U)'),
        min_value=decimal.Decimal(0.5),
        default=None
    )
    status = ChoiceField(choices=DeviceStatusChoices, required=False)
    airflow = ChoiceField(choices=DeviceAirflowChoices, allow_blank=True, required=False)
    primary_ip = IPAddressSerializer(nested=True, read_only=True, allow_null=True)
    primary_ip4 = IPAddressSerializer(nested=True, required=False, allow_null=True)
    primary_ip6 = IPAddressSerializer(nested=True, required=False, allow_null=True)
    oob_ip = IPAddressSerializer(nested=True, required=False, allow_null=True)
    parent_device = serializers.SerializerMethodField()
    cluster = ClusterSerializer(nested=True, required=False, allow_null=True)
    virtual_chassis = VirtualChassisSerializer(nested=True, required=False, allow_null=True, default=None)
    vc_position = serializers.IntegerField(allow_null=True, max_value=255, min_value=0, default=None)
    config_template = ConfigTemplateSerializer(nested=True, required=False, allow_null=True, default=None)

    # Counter fields
    console_port_count = serializers.IntegerField(read_only=True)
    console_server_port_count = serializers.IntegerField(read_only=True)
    power_port_count = serializers.IntegerField(read_only=True)
    power_outlet_count = serializers.IntegerField(read_only=True)
    interface_count = serializers.IntegerField(read_only=True)
    front_port_count = serializers.IntegerField(read_only=True)
    rear_port_count = serializers.IntegerField(read_only=True)
    device_bay_count = serializers.IntegerField(read_only=True)
    module_bay_count = serializers.IntegerField(read_only=True)
    inventory_item_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Device
        fields = [
            'id', 'url', 'display_url', 'display', 'name', 'device_type', 'role', 'tenant', 'platform', 'serial',
            'asset_tag', 'site', 'location', 'rack', 'position', 'face', 'latitude', 'longitude', 'parent_device',
            'status', 'airflow', 'primary_ip', 'primary_ip4', 'primary_ip6', 'oob_ip', 'cluster', 'virtual_chassis',
            'vc_position', 'vc_priority', 'description', 'comments', 'config_template', 'local_context_data', 'tags',
            'custom_fields', 'created', 'last_updated', 'console_port_count', 'console_server_port_count',
            'power_port_count', 'power_outlet_count', 'interface_count', 'front_port_count', 'rear_port_count',
            'device_bay_count', 'module_bay_count', 'inventory_item_count',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'description')

    @extend_schema_field(NestedDeviceSerializer(allow_null=True))
    def get_parent_device(self, obj):
        try:
            device_bay = obj.parent_bay
        except DeviceBay.DoesNotExist:
            return None
        context = {'request': self.context['request']}
        data = NestedDeviceSerializer(instance=device_bay.device, context=context).data
        data['device_bay'] = NestedDeviceBaySerializer(instance=device_bay, context=context).data
        return data


class DeviceWithConfigContextSerializer(DeviceSerializer):
    config_context = serializers.SerializerMethodField(read_only=True, allow_null=True)

    class Meta(DeviceSerializer.Meta):
        fields = [
            'id', 'url', 'display_url', 'display', 'name', 'device_type', 'role', 'tenant', 'platform', 'serial',
            'asset_tag', 'site', 'location', 'rack', 'position', 'face', 'latitude', 'longitude', 'parent_device',
            'status', 'airflow', 'primary_ip', 'primary_ip4', 'primary_ip6', 'oob_ip', 'cluster', 'virtual_chassis',
            'vc_position', 'vc_priority', 'description', 'comments', 'config_template', 'config_context',
            'local_context_data', 'tags', 'custom_fields', 'created', 'last_updated', 'console_port_count',
            'console_server_port_count', 'power_port_count', 'power_outlet_count', 'interface_count',
            'front_port_count', 'rear_port_count', 'device_bay_count', 'module_bay_count', 'inventory_item_count',
        ]

    @extend_schema_field(serializers.JSONField(allow_null=True))
    def get_config_context(self, obj):
        return obj.get_config_context()


class VirtualDeviceContextSerializer(NetBoxModelSerializer):
    device = DeviceSerializer(nested=True)
    identifier = serializers.IntegerField(allow_null=True, max_value=32767, min_value=0, required=False, default=None)
    tenant = TenantSerializer(nested=True, required=False, allow_null=True, default=None)
    primary_ip = IPAddressSerializer(nested=True, read_only=True, allow_null=True)
    primary_ip4 = IPAddressSerializer(nested=True, required=False, allow_null=True)
    primary_ip6 = IPAddressSerializer(nested=True, required=False, allow_null=True)
    status = ChoiceField(choices=VirtualDeviceContextStatusChoices)

    # Related object counts
    interface_count = RelatedObjectCountField('interfaces')

    class Meta:
        model = VirtualDeviceContext
        fields = [
            'id', 'url', 'display_url', 'display', 'name', 'device', 'identifier', 'tenant', 'primary_ip',
            'primary_ip4', 'primary_ip6', 'status', 'description', 'comments', 'tags', 'custom_fields',
            'created', 'last_updated', 'interface_count',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'identifier', 'device', 'description')


class ModuleSerializer(NetBoxModelSerializer):
    device = DeviceSerializer(nested=True)
    module_bay = NestedModuleBaySerializer()
    module_type = ModuleTypeSerializer(nested=True)
    status = ChoiceField(choices=ModuleStatusChoices, required=False)

    class Meta:
        model = Module
        fields = [
            'id', 'url', 'display_url', 'display', 'device', 'module_bay', 'module_type', 'status', 'serial',
            'asset_tag', 'description', 'comments', 'tags', 'custom_fields', 'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'device', 'module_bay', 'module_type', 'description')


class MACAddressSerializer(NetBoxModelSerializer):
    assigned_object_type = ContentTypeField(
        queryset=ContentType.objects.filter(MACADDRESS_ASSIGNMENT_MODELS),
        required=False,
        allow_null=True
    )
    assigned_object = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = MACAddress
        fields = [
            'id', 'url', 'display_url', 'display', 'mac_address', 'assigned_object_type', 'assigned_object',
            'description', 'comments',
        ]
        brief_fields = ('id', 'url', 'display', 'mac_address', 'description')

    @extend_schema_field(serializers.JSONField(allow_null=True))
    def get_assigned_object(self, obj):
        if obj.assigned_object is None:
            return None
        serializer = get_serializer_for_model(obj.assigned_object)
        context = {'request': self.context['request']}
        return serializer(obj.assigned_object, nested=True, context=context).data
