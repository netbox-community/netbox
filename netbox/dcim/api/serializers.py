from rest_framework import serializers

from ipam.models import IPAddress
from dcim.models import (
    ConsolePort, ConsolePortTemplate, ConsoleServerPort, ConsoleServerPortTemplate, Device, DeviceBay, DeviceType,
    DeviceRole, Interface, InterfaceConnection, InterfaceTemplate, Manufacturer, Module, Platform, PowerOutlet,
    PowerOutletTemplate, PowerPort, PowerPortTemplate, Rack, RackGroup, RackRole, RACK_FACE_FRONT, RACK_FACE_REAR, Site,
    SUBDEVICE_ROLE_CHILD, SUBDEVICE_ROLE_PARENT,
)
from extras.api.serializers import CustomFieldSerializer
from tenancy.api.serializers import NestedTenantSerializer


#
# Sites
#

class SiteSerializer(CustomFieldSerializer, serializers.ModelSerializer):
    tenant = NestedTenantSerializer()

    class Meta:
        model = Site
        fields = [
            'id', 'name', 'slug', 'tenant', 'facility', 'asn', 'physical_address', 'shipping_address', 'contact_name',
            'contact_phone', 'contact_email', 'comments', 'custom_fields', 'count_prefixes', 'count_vlans',
            'count_racks', 'count_devices', 'count_circuits',
        ]


class NestedSiteSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Site
        fields = ['id', 'url', 'name', 'slug']


#
# Rack groups
#

class RackGroupSerializer(serializers.ModelSerializer):
    site = NestedSiteSerializer()

    class Meta:
        model = RackGroup
        fields = ['id', 'name', 'slug', 'site']


class NestedRackGroupSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = RackGroup
        fields = ['id', 'url', 'name', 'slug']


#
# Rack roles
#

class RackRoleSerializer(serializers.ModelSerializer):

    class Meta:
        model = RackRole
        fields = ['id', 'name', 'slug', 'color']


class NestedRackRoleSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = RackRole
        fields = ['id', 'url', 'name', 'slug']


#
# Racks
#


class RackSerializer(CustomFieldSerializer, serializers.ModelSerializer):
    site = NestedSiteSerializer()
    group = NestedRackGroupSerializer()
    tenant = NestedTenantSerializer()
    role = NestedRackRoleSerializer()

    class Meta:
        model = Rack
        fields = [
            'id', 'name', 'facility_id', 'display_name', 'site', 'group', 'tenant', 'role', 'type', 'width', 'u_height',
            'desc_units', 'comments', 'custom_fields',
        ]


class NestedRackSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Rack
        fields = ['id', 'url', 'name', 'display_name']


class RackDetailSerializer(RackSerializer):
    front_units = serializers.SerializerMethodField()
    rear_units = serializers.SerializerMethodField()

    class Meta(RackSerializer.Meta):
        fields = [
            'id', 'name', 'facility_id', 'display_name', 'site', 'group', 'tenant', 'role', 'type', 'width', 'u_height',
            'desc_units', 'comments', 'custom_fields', 'front_units', 'rear_units',
        ]

    def get_front_units(self, obj):
        units = obj.get_rack_units(face=RACK_FACE_FRONT)
        for u in units:
            u['device'] = NestedDeviceSerializer(u['device']).data if u['device'] else None
        return units

    def get_rear_units(self, obj):
        units = obj.get_rack_units(face=RACK_FACE_REAR)
        for u in units:
            u['device'] = NestedDeviceSerializer(u['device']).data if u['device'] else None
        return units


#
# Manufacturers
#

class ManufacturerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Manufacturer
        fields = ['id', 'name', 'slug']


class NestedManufacturerSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Manufacturer
        fields = ['id', 'url', 'name', 'slug']


#
# Device types
#

class DeviceTypeSerializer(CustomFieldSerializer, serializers.ModelSerializer):
    manufacturer = NestedManufacturerSerializer()
    subdevice_role = serializers.SerializerMethodField()
    instance_count = serializers.IntegerField(source='instances.count', read_only=True)

    class Meta:
        model = DeviceType
        fields = [
            'id', 'manufacturer', 'model', 'slug', 'part_number', 'u_height', 'is_full_depth', 'interface_ordering',
            'is_console_server', 'is_pdu', 'is_network_device', 'subdevice_role', 'comments', 'custom_fields',
            'instance_count',
        ]

    def get_subdevice_role(self, obj):
        return {
            SUBDEVICE_ROLE_PARENT: 'parent',
            SUBDEVICE_ROLE_CHILD: 'child',
            None: None,
        }[obj.subdevice_role]


class NestedDeviceTypeSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = DeviceType
        fields = ['id', 'url', 'manufacturer', 'model', 'slug']


class ConsolePortTemplateSerializer(serializers.ModelSerializer):

    class Meta:
        model = ConsolePortTemplate
        fields = ['id', 'name']


class ConsoleServerPortTemplateSerializer(serializers.ModelSerializer):

    class Meta:
        model = ConsoleServerPortTemplate
        fields = ['id', 'name']


class PowerPortTemplateSerializer(serializers.ModelSerializer):

    class Meta:
        model = PowerPortTemplate
        fields = ['id', 'name']


class PowerOutletTemplateSerializer(serializers.ModelSerializer):

    class Meta:
        model = PowerOutletTemplate
        fields = ['id', 'name']


class InterfaceTemplateSerializer(serializers.ModelSerializer):

    class Meta:
        model = InterfaceTemplate
        fields = ['id', 'name', 'form_factor', 'mgmt_only']


class DeviceBayTemplateSerializer(serializers.ModelSerializer):

    class Meta:
        model = DeviceBay
        fields = ['id', 'name',]


#
# Device roles
#

class DeviceRoleSerializer(serializers.ModelSerializer):

    class Meta:
        model = DeviceRole
        fields = ['id', 'name', 'slug', 'color']


class NestedDeviceRoleSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = DeviceRole
        fields = ['id', 'url', 'name', 'slug']


#
# Platforms
#

class PlatformSerializer(serializers.ModelSerializer):

    class Meta:
        model = Platform
        fields = ['id', 'name', 'slug', 'rpc_client']


class NestedPlatformSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Platform
        fields = ['id', 'url', 'name', 'slug']


#
# Devices
#

# Cannot import ipam.api.NestedIPAddressSerializer due to circular dependency
class DeviceIPAddressSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = IPAddress
        fields = ['id', 'url', 'family', 'address']


class DeviceSerializer(CustomFieldSerializer, serializers.ModelSerializer):
    device_type = NestedDeviceTypeSerializer()
    device_role = NestedDeviceRoleSerializer()
    tenant = NestedTenantSerializer()
    platform = NestedPlatformSerializer()
    rack = NestedRackSerializer()
    primary_ip = DeviceIPAddressSerializer()
    primary_ip4 = DeviceIPAddressSerializer()
    primary_ip6 = DeviceIPAddressSerializer()
    parent_device = serializers.SerializerMethodField()

    class Meta:
        model = Device
        fields = [
            'id', 'name', 'display_name', 'device_type', 'device_role', 'tenant', 'platform', 'serial',  'asset_tag',
            'rack', 'position', 'face', 'parent_device', 'status', 'primary_ip', 'primary_ip4', 'primary_ip6',
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


class NestedDeviceSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Device
        fields = ['id', 'url', 'name', 'display_name']


#
# Console server ports
#

class ConsoleServerPortSerializer(serializers.ModelSerializer):
    device = NestedDeviceSerializer()

    class Meta:
        model = ConsoleServerPort
        fields = ['id', 'device', 'name', 'connected_console']


class ChildConsoleServerPortSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = ConsoleServerPort
        fields = ['id', 'url', 'name', 'connected_console']


#
# Console ports
#

class ConsolePortSerializer(serializers.ModelSerializer):
    device = NestedDeviceSerializer()
    cs_port = ConsoleServerPortSerializer()

    class Meta:
        model = ConsolePort
        fields = ['id', 'device', 'name', 'cs_port', 'connection_status']


class ChildConsolePortSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = ConsolePort
        fields = ['id', 'url', 'name', 'cs_port', 'connection_status']


#
# Power outlets
#

class PowerOutletSerializer(serializers.ModelSerializer):
    device = NestedDeviceSerializer()

    class Meta:
        model = PowerOutlet
        fields = ['id', 'device', 'name', 'connected_port']


class ChildPowerOutletSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = PowerOutlet
        fields = ['id', 'url', 'name', 'connected_port']


#
# Power ports
#

class PowerPortSerializer(serializers.ModelSerializer):
    device = NestedDeviceSerializer()
    power_outlet = PowerOutletSerializer()

    class Meta:
        model = PowerPort
        fields = ['id', 'device', 'name', 'power_outlet', 'connection_status']


class ChildPowerPortSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = PowerPort
        fields = ['id', 'url', 'name', 'power_outlet', 'connection_status']


#
# Interfaces
#

class InterfaceSerializer(serializers.ModelSerializer):
    device = NestedDeviceSerializer()
    form_factor = serializers.ReadOnlyField(source='get_form_factor_display')

    class Meta:
        model = Interface
        fields = ['id', 'device', 'name', 'form_factor', 'mac_address', 'mgmt_only', 'description', 'is_connected']


class ChildInterfaceSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Interface
        fields = ['id', 'url', 'name', 'form_factor', 'mac_address', 'mgmt_only', 'description', 'is_connected']


# TODO: Remove this
class InterfaceDetailSerializer(InterfaceSerializer):

    class Meta(InterfaceSerializer.Meta):
        fields = [
            'id', 'device', 'name', 'form_factor', 'mac_address', 'mgmt_only', 'description', 'is_connected',
            'connected_interface',
        ]


#
# Device bays
#

class DeviceBaySerializer(serializers.ModelSerializer):
    device = NestedDeviceSerializer()
    installed_device = NestedDeviceSerializer()

    class Meta:
        model = DeviceBay
        fields = ['id', 'device', 'name', 'installed_device']


class ChildDeviceBaySerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = DeviceBay
        fields = ['id', 'url', 'name', 'installed_device']


#
# Modules
#

class ModuleSerializer(serializers.ModelSerializer):
    device = NestedDeviceSerializer()
    manufacturer = NestedManufacturerSerializer()

    class Meta:
        model = Module
        fields = ['id', 'device', 'parent', 'name', 'manufacturer', 'part_id', 'serial', 'discovered']


class ChildModuleSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Module
        fields = ['id', 'url', 'parent', 'name', 'manufacturer', 'part_id', 'serial', 'discovered']


#
# Interface connections
#

class InterfaceConnectionSerializer(serializers.ModelSerializer):

    class Meta:
        model = InterfaceConnection
        fields = ['id', 'interface_a', 'interface_b', 'connection_status']
