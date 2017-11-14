from __future__ import unicode_literals

from collections import OrderedDict

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from circuits.models import Circuit, CircuitTermination
from dcim.constants import (
    CONNECTION_STATUS_CHOICES, IFACE_FF_CHOICES, IFACE_ORDERING_CHOICES, RACK_FACE_CHOICES, RACK_TYPE_CHOICES,
    RACK_WIDTH_CHOICES, STATUS_CHOICES, SUBDEVICE_ROLE_CHOICES,
)
from dcim.models import (
    ConsolePort, ConsolePortTemplate, ConsoleServerPort, ConsoleServerPortTemplate, Device, DeviceBay,
    DeviceBayTemplate, DeviceType, DeviceRole, Interface, InterfaceConnection, InterfaceTemplate, Manufacturer,
    InventoryItem, Platform, PowerOutlet, PowerOutletTemplate, PowerPort, PowerPortTemplate, Rack, RackGroup,
    RackReservation, RackRole, Region, Site,
)
from extras.api.customfields import CustomFieldModelSerializer
from ipam.models import IPAddress
from tenancy.api.serializers import NestedTenantSerializer
from utilities.api import ChoiceFieldSerializer, ValidatedModelSerializer
from virtualization.models import Cluster


#
# Regions
#

class NestedRegionSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:region-detail')

    class Meta:
        model = Region
        fields = ['id', 'url', 'name', 'slug']


class RegionSerializer(serializers.ModelSerializer):
    parent = NestedRegionSerializer()

    class Meta:
        model = Region
        fields = ['id', 'name', 'slug', 'parent']


class WritableRegionSerializer(ValidatedModelSerializer):

    class Meta:
        model = Region
        fields = ['id', 'name', 'slug', 'parent']


#
# Sites
#

class SiteSerializer(CustomFieldModelSerializer):
    region = NestedRegionSerializer()
    tenant = NestedTenantSerializer()

    class Meta:
        model = Site
        fields = [
            'id', 'name', 'slug', 'region', 'tenant', 'facility', 'asn', 'physical_address', 'shipping_address',
            'contact_name', 'contact_phone', 'contact_email', 'comments', 'custom_fields', 'count_prefixes',
            'count_vlans', 'count_racks', 'count_devices', 'count_circuits',
        ]


class NestedSiteSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:site-detail')

    class Meta:
        model = Site
        fields = ['id', 'url', 'name', 'slug']


class WritableSiteSerializer(CustomFieldModelSerializer):

    class Meta:
        model = Site
        fields = [
            'id', 'name', 'slug', 'region', 'tenant', 'facility', 'asn', 'physical_address', 'shipping_address',
            'contact_name', 'contact_phone', 'contact_email', 'comments', 'custom_fields',
        ]


#
# Rack groups
#

class RackGroupSerializer(serializers.ModelSerializer):
    site = NestedSiteSerializer()

    class Meta:
        model = RackGroup
        fields = ['id', 'name', 'slug', 'site']


class NestedRackGroupSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:rackgroup-detail')

    class Meta:
        model = RackGroup
        fields = ['id', 'url', 'name', 'slug']


class WritableRackGroupSerializer(ValidatedModelSerializer):

    class Meta:
        model = RackGroup
        fields = ['id', 'name', 'slug', 'site']


#
# Rack roles
#

class RackRoleSerializer(ValidatedModelSerializer):

    class Meta:
        model = RackRole
        fields = ['id', 'name', 'slug', 'color']


class NestedRackRoleSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:rackrole-detail')

    class Meta:
        model = RackRole
        fields = ['id', 'url', 'name', 'slug']


#
# Racks
#

class RackSerializer(CustomFieldModelSerializer):
    site = NestedSiteSerializer()
    group = NestedRackGroupSerializer()
    tenant = NestedTenantSerializer()
    role = NestedRackRoleSerializer()
    type = ChoiceFieldSerializer(choices=RACK_TYPE_CHOICES)
    width = ChoiceFieldSerializer(choices=RACK_WIDTH_CHOICES)

    class Meta:
        model = Rack
        fields = [
            'id', 'name', 'facility_id', 'display_name', 'site', 'group', 'tenant', 'role', 'serial', 'type', 'width',
            'u_height', 'desc_units', 'comments', 'custom_fields',
        ]


class NestedRackSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:rack-detail')

    class Meta:
        model = Rack
        fields = ['id', 'url', 'name', 'display_name']


class WritableRackSerializer(CustomFieldModelSerializer):

    class Meta:
        model = Rack
        fields = [
            'id', 'name', 'facility_id', 'site', 'group', 'tenant', 'role', 'serial', 'type', 'width', 'u_height',
            'desc_units', 'comments', 'custom_fields',
        ]
        # Omit the UniqueTogetherValidator that would be automatically added to validate (site, facility_id). This
        # prevents facility_id from being interpreted as a required field.
        validators = [
            UniqueTogetherValidator(queryset=Rack.objects.all(), fields=('site', 'name'))
        ]

    def validate(self, data):

        # Validate uniqueness of (site, facility_id) since we omitted the automatically-created validator from Meta.
        if data.get('facility_id', None):
            validator = UniqueTogetherValidator(queryset=Rack.objects.all(), fields=('site', 'facility_id'))
            validator.set_context(self)
            validator(data)

        # Enforce model validation
        super(WritableRackSerializer, self).validate(data)

        return data


#
# Rack units
#

class NestedDeviceSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:device-detail')

    class Meta:
        model = Device
        fields = ['id', 'url', 'name', 'display_name']


class RackUnitSerializer(serializers.Serializer):
    """
    A rack unit is an abstraction formed by the set (rack, position, face); it does not exist as a row in the database.
    """
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    face = serializers.IntegerField(read_only=True)
    device = NestedDeviceSerializer(read_only=True)


#
# Rack reservations
#

class RackReservationSerializer(serializers.ModelSerializer):
    rack = NestedRackSerializer()

    class Meta:
        model = RackReservation
        fields = ['id', 'rack', 'units', 'created', 'user', 'description']


class WritableRackReservationSerializer(ValidatedModelSerializer):

    class Meta:
        model = RackReservation
        fields = ['id', 'rack', 'units', 'user', 'description']


#
# Manufacturers
#

class ManufacturerSerializer(ValidatedModelSerializer):

    class Meta:
        model = Manufacturer
        fields = ['id', 'name', 'slug']


class NestedManufacturerSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:manufacturer-detail')

    class Meta:
        model = Manufacturer
        fields = ['id', 'url', 'name', 'slug']


#
# Device types
#

class DeviceTypeSerializer(CustomFieldModelSerializer):
    manufacturer = NestedManufacturerSerializer()
    interface_ordering = ChoiceFieldSerializer(choices=IFACE_ORDERING_CHOICES)
    subdevice_role = ChoiceFieldSerializer(choices=SUBDEVICE_ROLE_CHOICES)
    instance_count = serializers.IntegerField(source='instances.count', read_only=True)

    class Meta:
        model = DeviceType
        fields = [
            'id', 'manufacturer', 'model', 'slug', 'part_number', 'u_height', 'is_full_depth', 'interface_ordering',
            'is_console_server', 'is_pdu', 'is_network_device', 'subdevice_role', 'comments', 'custom_fields',
            'instance_count',
        ]


class NestedDeviceTypeSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:devicetype-detail')
    manufacturer = NestedManufacturerSerializer()

    class Meta:
        model = DeviceType
        fields = ['id', 'url', 'manufacturer', 'model', 'slug']


class WritableDeviceTypeSerializer(CustomFieldModelSerializer):

    class Meta:
        model = DeviceType
        fields = [
            'id', 'manufacturer', 'model', 'slug', 'part_number', 'u_height', 'is_full_depth', 'interface_ordering',
            'is_console_server', 'is_pdu', 'is_network_device', 'subdevice_role', 'comments', 'custom_fields',
        ]


#
# Console port templates
#

class ConsolePortTemplateSerializer(serializers.ModelSerializer):
    device_type = NestedDeviceTypeSerializer()

    class Meta:
        model = ConsolePortTemplate
        fields = ['id', 'device_type', 'name']


class WritableConsolePortTemplateSerializer(ValidatedModelSerializer):

    class Meta:
        model = ConsolePortTemplate
        fields = ['id', 'device_type', 'name']


#
# Console server port templates
#

class ConsoleServerPortTemplateSerializer(serializers.ModelSerializer):
    device_type = NestedDeviceTypeSerializer()

    class Meta:
        model = ConsoleServerPortTemplate
        fields = ['id', 'device_type', 'name']


class WritableConsoleServerPortTemplateSerializer(ValidatedModelSerializer):

    class Meta:
        model = ConsoleServerPortTemplate
        fields = ['id', 'device_type', 'name']


#
# Power port templates
#

class PowerPortTemplateSerializer(serializers.ModelSerializer):
    device_type = NestedDeviceTypeSerializer()

    class Meta:
        model = PowerPortTemplate
        fields = ['id', 'device_type', 'name']


class WritablePowerPortTemplateSerializer(ValidatedModelSerializer):

    class Meta:
        model = PowerPortTemplate
        fields = ['id', 'device_type', 'name']


#
# Power outlet templates
#

class PowerOutletTemplateSerializer(serializers.ModelSerializer):
    device_type = NestedDeviceTypeSerializer()

    class Meta:
        model = PowerOutletTemplate
        fields = ['id', 'device_type', 'name']


class WritablePowerOutletTemplateSerializer(ValidatedModelSerializer):

    class Meta:
        model = PowerOutletTemplate
        fields = ['id', 'device_type', 'name']


#
# Interface templates
#

class InterfaceTemplateSerializer(serializers.ModelSerializer):
    device_type = NestedDeviceTypeSerializer()
    form_factor = ChoiceFieldSerializer(choices=IFACE_FF_CHOICES)

    class Meta:
        model = InterfaceTemplate
        fields = ['id', 'device_type', 'name', 'form_factor', 'mgmt_only']


class WritableInterfaceTemplateSerializer(ValidatedModelSerializer):

    class Meta:
        model = InterfaceTemplate
        fields = ['id', 'device_type', 'name', 'form_factor', 'mgmt_only']


#
# Device bay templates
#

class DeviceBayTemplateSerializer(serializers.ModelSerializer):
    device_type = NestedDeviceTypeSerializer()

    class Meta:
        model = DeviceBayTemplate
        fields = ['id', 'device_type', 'name']


class WritableDeviceBayTemplateSerializer(ValidatedModelSerializer):

    class Meta:
        model = DeviceBayTemplate
        fields = ['id', 'device_type', 'name']


#
# Device roles
#

class DeviceRoleSerializer(ValidatedModelSerializer):

    class Meta:
        model = DeviceRole
        fields = ['id', 'name', 'slug', 'color', 'vm_role']


class NestedDeviceRoleSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:devicerole-detail')

    class Meta:
        model = DeviceRole
        fields = ['id', 'url', 'name', 'slug']


#
# Platforms
#

class PlatformSerializer(ValidatedModelSerializer):

    class Meta:
        model = Platform
        fields = ['id', 'name', 'slug', 'napalm_driver', 'rpc_client']


class NestedPlatformSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:platform-detail')

    class Meta:
        model = Platform
        fields = ['id', 'url', 'name', 'slug']


#
# Devices
#

# Cannot import ipam.api.NestedIPAddressSerializer due to circular dependency
class DeviceIPAddressSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:ipaddress-detail')

    class Meta:
        model = IPAddress
        fields = ['id', 'url', 'family', 'address']


# Cannot import virtualization.api.NestedClusterSerializer due to circular dependency
class NestedClusterSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='virtualization-api:cluster-detail')

    class Meta:
        model = Cluster
        fields = ['id', 'url', 'name']


class DeviceSerializer(CustomFieldModelSerializer):
    device_type = NestedDeviceTypeSerializer()
    device_role = NestedDeviceRoleSerializer()
    tenant = NestedTenantSerializer()
    platform = NestedPlatformSerializer()
    site = NestedSiteSerializer()
    rack = NestedRackSerializer()
    face = ChoiceFieldSerializer(choices=RACK_FACE_CHOICES)
    status = ChoiceFieldSerializer(choices=STATUS_CHOICES)
    primary_ip = DeviceIPAddressSerializer()
    primary_ip4 = DeviceIPAddressSerializer()
    primary_ip6 = DeviceIPAddressSerializer()
    parent_device = serializers.SerializerMethodField()
    cluster = NestedClusterSerializer()

    class Meta:
        model = Device
        fields = [
            'id', 'name', 'display_name', 'device_type', 'device_role', 'tenant', 'platform', 'serial', 'asset_tag',
            'site', 'rack', 'position', 'face', 'parent_device', 'status', 'primary_ip', 'primary_ip4', 'primary_ip6',
            'cluster', 'comments', 'custom_fields',
        ]

    def get_parent_device(self, obj):
        try:
            device_bay = obj.parent_bay
        except DeviceBay.DoesNotExist:
            return None
        context = {'request': self.context['request']}
        data = NestedDeviceSerializer(instance=device_bay.device, context=context).data
        data['device_bay'] = NestedDeviceBaySerializer(instance=device_bay, context=context).data
        return data


class WritableDeviceSerializer(CustomFieldModelSerializer):

    class Meta:
        model = Device
        fields = [
            'id', 'name', 'device_type', 'device_role', 'tenant', 'platform', 'serial', 'asset_tag', 'site', 'rack',
            'position', 'face', 'status', 'primary_ip4', 'primary_ip6', 'cluster', 'comments', 'custom_fields',
        ]
        validators = []

    def validate(self, data):

        # Validate uniqueness of (rack, position, face) since we omitted the automatically-created validator from Meta.
        if data.get('rack') and data.get('position') and data.get('face'):
            validator = UniqueTogetherValidator(queryset=Device.objects.all(), fields=('rack', 'position', 'face'))
            validator.set_context(self)
            validator(data)

        # Enforce model validation
        super(WritableDeviceSerializer, self).validate(data)

        return data


#
# Console server ports
#

class ConsoleServerPortSerializer(serializers.ModelSerializer):
    device = NestedDeviceSerializer()

    class Meta:
        model = ConsoleServerPort
        fields = ['id', 'device', 'name', 'connected_console']
        read_only_fields = ['connected_console']


class WritableConsoleServerPortSerializer(ValidatedModelSerializer):

    class Meta:
        model = ConsoleServerPort
        fields = ['id', 'device', 'name']


#
# Console ports
#

class ConsolePortSerializer(serializers.ModelSerializer):
    device = NestedDeviceSerializer()
    cs_port = ConsoleServerPortSerializer()

    class Meta:
        model = ConsolePort
        fields = ['id', 'device', 'name', 'cs_port', 'connection_status']


class WritableConsolePortSerializer(ValidatedModelSerializer):

    class Meta:
        model = ConsolePort
        fields = ['id', 'device', 'name', 'cs_port', 'connection_status']


#
# Power outlets
#

class PowerOutletSerializer(serializers.ModelSerializer):
    device = NestedDeviceSerializer()

    class Meta:
        model = PowerOutlet
        fields = ['id', 'device', 'name', 'connected_port']
        read_only_fields = ['connected_port']


class WritablePowerOutletSerializer(ValidatedModelSerializer):

    class Meta:
        model = PowerOutlet
        fields = ['id', 'device', 'name']


#
# Power ports
#

class PowerPortSerializer(serializers.ModelSerializer):
    device = NestedDeviceSerializer()
    power_outlet = PowerOutletSerializer()

    class Meta:
        model = PowerPort
        fields = ['id', 'device', 'name', 'power_outlet', 'connection_status']


class WritablePowerPortSerializer(ValidatedModelSerializer):

    class Meta:
        model = PowerPort
        fields = ['id', 'device', 'name', 'power_outlet', 'connection_status']


#
# Interfaces
#

class NestedInterfaceSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:interface-detail')

    class Meta:
        model = Interface
        fields = ['id', 'url', 'name']


class InterfaceNestedCircuitSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='circuits-api:circuit-detail')

    class Meta:
        model = Circuit
        fields = ['id', 'url', 'cid']


class InterfaceCircuitTerminationSerializer(serializers.ModelSerializer):
    circuit = InterfaceNestedCircuitSerializer()

    class Meta:
        model = CircuitTermination
        fields = [
            'id', 'circuit', 'term_side', 'port_speed', 'upstream_speed', 'xconnect_id', 'pp_info',
        ]


class InterfaceSerializer(serializers.ModelSerializer):
    device = NestedDeviceSerializer()
    form_factor = ChoiceFieldSerializer(choices=IFACE_FF_CHOICES)
    lag = NestedInterfaceSerializer()
    is_connected = serializers.SerializerMethodField(read_only=True)
    interface_connection = serializers.SerializerMethodField(read_only=True)
    circuit_termination = InterfaceCircuitTerminationSerializer()

    class Meta:
        model = Interface
        fields = [
            'id', 'device', 'name', 'form_factor', 'enabled', 'lag', 'mtu', 'mac_address', 'mgmt_only', 'description',
            'is_connected', 'interface_connection', 'circuit_termination',
        ]

    def get_is_connected(self, obj):
        """
        Return True if the interface has a connected interface or circuit termination.
        """
        if obj.connection:
            return True
        try:
            circuit_termination = obj.circuit_termination
            return True
        except CircuitTermination.DoesNotExist:
            pass
        return False

    def get_interface_connection(self, obj):
        if obj.connection:
            return OrderedDict((
                ('interface', PeerInterfaceSerializer(obj.connected_interface, context=self.context).data),
                ('status', obj.connection.connection_status),
            ))
        return None


class PeerInterfaceSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:interface-detail')
    device = NestedDeviceSerializer()
    form_factor = ChoiceFieldSerializer(choices=IFACE_FF_CHOICES)
    lag = NestedInterfaceSerializer()

    class Meta:
        model = Interface
        fields = [
            'id', 'url', 'device', 'name', 'form_factor', 'enabled', 'lag', 'mtu', 'mac_address', 'mgmt_only',
            'description',
        ]


class WritableInterfaceSerializer(ValidatedModelSerializer):

    class Meta:
        model = Interface
        fields = [
            'id', 'device', 'name', 'form_factor', 'enabled', 'lag', 'mtu', 'mac_address', 'mgmt_only', 'description',
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


class NestedDeviceBaySerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:devicebay-detail')

    class Meta:
        model = DeviceBay
        fields = ['id', 'url', 'name']


class WritableDeviceBaySerializer(ValidatedModelSerializer):

    class Meta:
        model = DeviceBay
        fields = ['id', 'device', 'name', 'installed_device']


#
# Inventory items
#

class InventoryItemSerializer(serializers.ModelSerializer):
    device = NestedDeviceSerializer()
    manufacturer = NestedManufacturerSerializer()

    class Meta:
        model = InventoryItem
        fields = [
            'id', 'device', 'parent', 'name', 'manufacturer', 'part_id', 'serial', 'asset_tag', 'discovered',
            'description',
        ]


class WritableInventoryItemSerializer(ValidatedModelSerializer):

    class Meta:
        model = InventoryItem
        fields = [
            'id', 'device', 'parent', 'name', 'manufacturer', 'part_id', 'serial', 'asset_tag', 'discovered',
            'description',
        ]


#
# Interface connections
#

class InterfaceConnectionSerializer(serializers.ModelSerializer):
    interface_a = PeerInterfaceSerializer()
    interface_b = PeerInterfaceSerializer()
    connection_status = ChoiceFieldSerializer(choices=CONNECTION_STATUS_CHOICES)

    class Meta:
        model = InterfaceConnection
        fields = ['id', 'interface_a', 'interface_b', 'connection_status']


class NestedInterfaceConnectionSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:interfaceconnection-detail')

    class Meta:
        model = InterfaceConnection
        fields = ['id', 'url', 'connection_status']


class WritableInterfaceConnectionSerializer(ValidatedModelSerializer):

    class Meta:
        model = InterfaceConnection
        fields = ['id', 'interface_a', 'interface_b', 'connection_status']
