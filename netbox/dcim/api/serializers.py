from rest_framework import serializers

from ipam.models import IPAddress
from dcim.models import (
    ConsolePort, ConsolePortTemplate, ConsoleServerPort, ConsoleServerPortTemplate, Device, DeviceBay, DeviceType,
    DeviceRole, Interface, InterfaceConnection, InterfaceTemplate, Manufacturer, Module, Platform, PowerOutlet,
    PowerOutletTemplate, PowerPort, PowerPortTemplate, Rack, RackGroup, RackReservation, RackRole, RACK_FACE_FRONT,
    RACK_FACE_REAR, Site, SUBDEVICE_ROLE_CHILD, SUBDEVICE_ROLE_PARENT,
)
from extras.api.serializers import CustomFieldSerializer
from tenancy.api.serializers import TenantNestedSerializer


#
# Sites
#

class SiteSerializer(CustomFieldSerializer, serializers.ModelSerializer):
    tenant = TenantNestedSerializer()

    class Meta:
        model = Site
        fields = ['id', 'name', 'slug', 'tenant', 'facility', 'asn', 'physical_address', 'shipping_address',
                  'contact_name', 'contact_phone', 'contact_email', 'comments', 'custom_fields', 'count_prefixes',
                  'count_vlans', 'count_racks', 'count_devices', 'count_circuits']


class SiteNestedSerializer(SiteSerializer):

    class Meta(SiteSerializer.Meta):
        fields = ['id', 'name', 'slug']


#
# Rack groups
#

class RackGroupSerializer(serializers.ModelSerializer):
    site = SiteNestedSerializer()

    class Meta:
        model = RackGroup
        fields = ['id', 'name', 'slug', 'site']


class RackGroupNestedSerializer(RackGroupSerializer):

    class Meta(SiteSerializer.Meta):
        fields = ['id', 'name', 'slug']


#
# Rack roles
#

class RackRoleSerializer(serializers.ModelSerializer):

    class Meta:
        model = RackRole
        fields = ['id', 'name', 'slug', 'color']


class RackRoleNestedSerializer(RackRoleSerializer):

    class Meta(RackRoleSerializer.Meta):
        fields = ['id', 'name', 'slug']


#
# Racks
#

class RackReservationNestedSerializer(serializers.ModelSerializer):

    class Meta:
        model = RackReservation
        fields = ['id', 'units', 'created', 'user', 'description']


class RackSerializer(CustomFieldSerializer, serializers.ModelSerializer):
    site = SiteNestedSerializer()
    group = RackGroupNestedSerializer()
    tenant = TenantNestedSerializer()
    role = RackRoleNestedSerializer()

    class Meta:
        model = Rack
        fields = ['id', 'name', 'facility_id', 'display_name', 'site', 'group', 'tenant', 'role', 'type', 'width',
                  'u_height', 'desc_units', 'comments', 'custom_fields']


class RackNestedSerializer(RackSerializer):

    class Meta(RackSerializer.Meta):
        fields = ['id', 'name', 'facility_id', 'display_name']


class RackDetailSerializer(RackSerializer):
    front_units = serializers.SerializerMethodField()
    rear_units = serializers.SerializerMethodField()
    reservations = RackReservationNestedSerializer(many=True)

    class Meta(RackSerializer.Meta):
        fields = ['id', 'name', 'facility_id', 'display_name', 'site', 'group', 'tenant', 'role', 'type', 'width',
                  'u_height', 'desc_units', 'reservations', 'comments', 'custom_fields', 'front_units', 'rear_units']

    def get_front_units(self, obj):
        units = obj.get_rack_units(face=RACK_FACE_FRONT)
        for u in units:
            u['device'] = DeviceNestedSerializer(u['device']).data if u['device'] else None
        return units

    def get_rear_units(self, obj):
        units = obj.get_rack_units(face=RACK_FACE_REAR)
        for u in units:
            u['device'] = DeviceNestedSerializer(u['device']).data if u['device'] else None
        return units


#
# Rack reservations
#

class RackReservationSerializer(serializers.ModelSerializer):
    rack = RackNestedSerializer()

    class Meta:
        model = RackReservation
        fields = ['id', 'rack', 'units', 'created', 'user', 'description']


#
# Manufacturers
#

class ManufacturerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Manufacturer
        fields = ['id', 'name', 'slug']


class ManufacturerNestedSerializer(ManufacturerSerializer):

    class Meta(ManufacturerSerializer.Meta):
        pass


#
# Device types
#

class DeviceTypeSerializer(CustomFieldSerializer, serializers.ModelSerializer):
    manufacturer = ManufacturerNestedSerializer()
    subdevice_role = serializers.SerializerMethodField()
    instance_count = serializers.IntegerField(source='instances.count', read_only=True)

    class Meta:
        model = DeviceType
        fields = ['id', 'manufacturer', 'model', 'slug', 'part_number', 'u_height', 'is_full_depth',
                  'interface_ordering', 'is_console_server', 'is_pdu', 'is_network_device', 'subdevice_role',
                  'comments', 'custom_fields', 'instance_count']

    def get_subdevice_role(self, obj):
        return {
            SUBDEVICE_ROLE_PARENT: 'parent',
            SUBDEVICE_ROLE_CHILD: 'child',
            None: None,
        }[obj.subdevice_role]


class DeviceTypeNestedSerializer(DeviceTypeSerializer):

    class Meta(DeviceTypeSerializer.Meta):
        fields = ['id', 'manufacturer', 'model', 'slug']


class ConsolePortTemplateNestedSerializer(serializers.ModelSerializer):

    class Meta:
        model = ConsolePortTemplate
        fields = ['id', 'name']


class ConsoleServerPortTemplateNestedSerializer(serializers.ModelSerializer):

    class Meta:
        model = ConsoleServerPortTemplate
        fields = ['id', 'name']


class PowerPortTemplateNestedSerializer(serializers.ModelSerializer):

    class Meta:
        model = PowerPortTemplate
        fields = ['id', 'name']


class PowerOutletTemplateNestedSerializer(serializers.ModelSerializer):

    class Meta:
        model = PowerOutletTemplate
        fields = ['id', 'name']


class InterfaceTemplateNestedSerializer(serializers.ModelSerializer):

    class Meta:
        model = InterfaceTemplate
        fields = ['id', 'name', 'form_factor', 'mgmt_only']


class DeviceTypeDetailSerializer(DeviceTypeSerializer):
    console_port_templates = ConsolePortTemplateNestedSerializer(many=True, read_only=True)
    cs_port_templates = ConsoleServerPortTemplateNestedSerializer(many=True, read_only=True)
    power_port_templates = PowerPortTemplateNestedSerializer(many=True, read_only=True)
    power_outlet_templates = PowerPortTemplateNestedSerializer(many=True, read_only=True)
    interface_templates = InterfaceTemplateNestedSerializer(many=True, read_only=True)

    class Meta(DeviceTypeSerializer.Meta):
        fields = ['id', 'manufacturer', 'model', 'slug', 'part_number', 'u_height', 'is_full_depth',
                  'interface_ordering', 'is_console_server', 'is_pdu', 'is_network_device', 'subdevice_role',
                  'comments', 'custom_fields', 'console_port_templates', 'cs_port_templates', 'power_port_templates',
                  'power_outlet_templates', 'interface_templates']


#
# Device roles
#

class DeviceRoleSerializer(serializers.ModelSerializer):

    class Meta:
        model = DeviceRole
        fields = ['id', 'name', 'slug', 'color']


class DeviceRoleNestedSerializer(DeviceRoleSerializer):

    class Meta(DeviceRoleSerializer.Meta):
        fields = ['id', 'name', 'slug']


#
# Platforms
#

class PlatformSerializer(serializers.ModelSerializer):

    class Meta:
        model = Platform
        fields = ['id', 'name', 'slug', 'rpc_client']


class PlatformNestedSerializer(PlatformSerializer):

    class Meta(PlatformSerializer.Meta):
        fields = ['id', 'name', 'slug']


#
# Devices
#

# Cannot import ipam.api.IPAddressNestedSerializer due to circular dependency
class DeviceIPAddressNestedSerializer(serializers.ModelSerializer):

    class Meta:
        model = IPAddress
        fields = ['id', 'family', 'address']


class DeviceSerializer(CustomFieldSerializer, serializers.ModelSerializer):
    device_type = DeviceTypeNestedSerializer()
    device_role = DeviceRoleNestedSerializer()
    tenant = TenantNestedSerializer()
    platform = PlatformNestedSerializer()
    site = SiteNestedSerializer()
    rack = RackNestedSerializer()
    primary_ip = DeviceIPAddressNestedSerializer()
    primary_ip4 = DeviceIPAddressNestedSerializer()
    primary_ip6 = DeviceIPAddressNestedSerializer()
    parent_device = serializers.SerializerMethodField()

    class Meta:
        model = Device
        fields = [
            'id', 'name', 'display_name', 'device_type', 'device_role', 'tenant', 'platform', 'serial', 'asset_tag',
            'site', 'rack', 'position', 'face', 'parent_device', 'status', 'primary_ip', 'primary_ip4', 'primary_ip6',
            'comments', 'custom_fields',
        ]

    def get_parent_device(self, obj):
        try:
            device_bay = obj.parent_bay
        except DeviceBay.DoesNotExist:
            return None
        return {
            'id': device_bay.device.pk,
            'name': device_bay.device.name,
            'device_bay': {
                'id': device_bay.pk,
                'name': device_bay.name,
            }
        }


class DeviceNestedSerializer(serializers.ModelSerializer):

    class Meta:
        model = Device
        fields = ['id', 'name', 'display_name']


#
# Console server ports
#

class ConsoleServerPortSerializer(serializers.ModelSerializer):
    device = DeviceNestedSerializer()

    class Meta:
        model = ConsoleServerPort
        fields = ['id', 'device', 'name', 'connected_console']


class ConsoleServerPortNestedSerializer(ConsoleServerPortSerializer):

    class Meta(ConsoleServerPortSerializer.Meta):
        fields = ['id', 'device', 'name']


#
# Console ports
#

class ConsolePortSerializer(serializers.ModelSerializer):
    device = DeviceNestedSerializer()
    cs_port = ConsoleServerPortNestedSerializer()

    class Meta:
        model = ConsolePort
        fields = ['id', 'device', 'name', 'cs_port', 'connection_status']


class ConsolePortNestedSerializer(ConsolePortSerializer):

    class Meta(ConsolePortSerializer.Meta):
        fields = ['id', 'device', 'name']


#
# Power outlets
#

class PowerOutletSerializer(serializers.ModelSerializer):
    device = DeviceNestedSerializer()

    class Meta:
        model = PowerOutlet
        fields = ['id', 'device', 'name', 'connected_port']


class PowerOutletNestedSerializer(PowerOutletSerializer):

    class Meta(PowerOutletSerializer.Meta):
        fields = ['id', 'device', 'name']


#
# Power ports
#

class PowerPortSerializer(serializers.ModelSerializer):
    device = DeviceNestedSerializer()
    power_outlet = PowerOutletNestedSerializer()

    class Meta:
        model = PowerPort
        fields = ['id', 'device', 'name', 'power_outlet', 'connection_status']


class PowerPortNestedSerializer(PowerPortSerializer):

    class Meta(PowerPortSerializer.Meta):
        fields = ['id', 'device', 'name']


#
# Interfaces
#

class InterfaceSerializer(serializers.ModelSerializer):
    device = DeviceNestedSerializer()
    form_factor = serializers.ReadOnlyField(source='get_form_factor_display')

    class Meta:
        model = Interface
        fields = ['id', 'device', 'name', 'form_factor', 'mac_address', 'mgmt_only', 'description', 'is_connected']


class InterfaceNestedSerializer(InterfaceSerializer):
    form_factor = serializers.ReadOnlyField(source='get_form_factor_display')

    class Meta(InterfaceSerializer.Meta):
        fields = ['id', 'device', 'name']


class InterfaceDetailSerializer(InterfaceSerializer):
    connected_interface = InterfaceSerializer()

    class Meta(InterfaceSerializer.Meta):
        fields = ['id', 'device', 'name', 'form_factor', 'mac_address', 'mgmt_only', 'description', 'is_connected',
                  'connected_interface']


#
# Device bays
#

class DeviceBaySerializer(serializers.ModelSerializer):
    device = DeviceNestedSerializer()

    class Meta:
        model = DeviceBay
        fields = ['id', 'device', 'name']


class DeviceBayNestedSerializer(DeviceBaySerializer):
    installed_device = DeviceNestedSerializer()

    class Meta(DeviceBaySerializer.Meta):
        fields = ['id', 'name', 'installed_device']


class DeviceBayDetailSerializer(DeviceBaySerializer):
    installed_device = DeviceNestedSerializer()

    class Meta(DeviceBaySerializer.Meta):
        fields = ['id', 'device', 'name', 'installed_device']


#
# Modules
#

class ModuleSerializer(serializers.ModelSerializer):
    device = DeviceNestedSerializer()
    manufacturer = ManufacturerNestedSerializer()

    class Meta:
        model = Module
        fields = ['id', 'device', 'parent', 'name', 'manufacturer', 'part_id', 'serial', 'discovered']


class ModuleNestedSerializer(ModuleSerializer):

    class Meta(ModuleSerializer.Meta):
        fields = ['id', 'device', 'parent', 'name']


#
# Interface connections
#

class InterfaceConnectionSerializer(serializers.ModelSerializer):

    class Meta:
        model = InterfaceConnection
        fields = ['id', 'interface_a', 'interface_b', 'connection_status']
