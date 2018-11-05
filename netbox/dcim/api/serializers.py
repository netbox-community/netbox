from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from taggit_serializer.serializers import TaggitSerializer, TagListSerializerField

from circuits.models import Circuit, CircuitTermination
from dcim.constants import *
from dcim.models import (
    Cable, ConsolePort, ConsolePortTemplate, ConsoleServerPort, ConsoleServerPortTemplate, Device, DeviceBay,
    DeviceBayTemplate, DeviceType, DeviceRole, FrontPort, FrontPortTemplate, Interface, InterfaceTemplate,
    Manufacturer, InventoryItem, Platform, PowerOutlet, PowerOutletTemplate, PowerPort, PowerPortTemplate, Rack,
    RackGroup, RackReservation, RackRole, RearPort, RearPortTemplate, Region, Site, VirtualChassis,
)
from extras.api.customfields import CustomFieldModelSerializer
from ipam.models import IPAddress, VLAN
from tenancy.api.serializers import NestedTenantSerializer
from users.api.serializers import NestedUserSerializer
from utilities.api import (
    ChoiceField, ContentTypeField, SerializedPKRelatedField, TimeZoneField, ValidatedModelSerializer,
    WritableNestedSerializer, get_serializer_for_model,
)
from virtualization.models import Cluster


#
# Regions
#

class NestedRegionSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:region-detail')

    class Meta:
        model = Region
        fields = ['id', 'url', 'name', 'slug']


class RegionSerializer(serializers.ModelSerializer):
    parent = NestedRegionSerializer(required=False, allow_null=True)

    class Meta:
        model = Region
        fields = ['id', 'name', 'slug', 'parent']


#
# Sites
#

class SiteSerializer(TaggitSerializer, CustomFieldModelSerializer):
    status = ChoiceField(choices=SITE_STATUS_CHOICES, required=False)
    region = NestedRegionSerializer(required=False, allow_null=True)
    tenant = NestedTenantSerializer(required=False, allow_null=True)
    time_zone = TimeZoneField(required=False)
    tags = TagListSerializerField(required=False)

    class Meta:
        model = Site
        fields = [
            'id', 'name', 'slug', 'status', 'region', 'tenant', 'facility', 'asn', 'time_zone', 'description',
            'physical_address', 'shipping_address', 'latitude', 'longitude', 'contact_name', 'contact_phone',
            'contact_email', 'comments', 'tags', 'custom_fields', 'created', 'last_updated', 'count_prefixes',
            'count_vlans', 'count_racks', 'count_devices', 'count_circuits',
        ]


class NestedSiteSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:site-detail')

    class Meta:
        model = Site
        fields = ['id', 'url', 'name', 'slug']


#
# Rack groups
#

class RackGroupSerializer(ValidatedModelSerializer):
    site = NestedSiteSerializer()

    class Meta:
        model = RackGroup
        fields = ['id', 'name', 'slug', 'site']


class NestedRackGroupSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:rackgroup-detail')

    class Meta:
        model = RackGroup
        fields = ['id', 'url', 'name', 'slug']


#
# Rack roles
#

class RackRoleSerializer(ValidatedModelSerializer):

    class Meta:
        model = RackRole
        fields = ['id', 'name', 'slug', 'color']


class NestedRackRoleSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:rackrole-detail')

    class Meta:
        model = RackRole
        fields = ['id', 'url', 'name', 'slug']


#
# Racks
#

class RackSerializer(TaggitSerializer, CustomFieldModelSerializer):
    site = NestedSiteSerializer()
    group = NestedRackGroupSerializer(required=False, allow_null=True, default=None)
    tenant = NestedTenantSerializer(required=False, allow_null=True)
    status = ChoiceField(choices=RACK_STATUS_CHOICES, required=False)
    role = NestedRackRoleSerializer(required=False, allow_null=True)
    type = ChoiceField(choices=RACK_TYPE_CHOICES, required=False, allow_null=True)
    width = ChoiceField(choices=RACK_WIDTH_CHOICES, required=False)
    outer_unit = ChoiceField(choices=RACK_DIMENSION_UNIT_CHOICES, required=False)
    tags = TagListSerializerField(required=False)

    class Meta:
        model = Rack
        fields = [
            'id', 'name', 'facility_id', 'display_name', 'site', 'group', 'tenant', 'status', 'role', 'serial',
            'asset_tag', 'type', 'width', 'u_height', 'desc_units', 'outer_width', 'outer_depth', 'outer_unit',
            'comments', 'tags', 'custom_fields', 'created', 'last_updated',
        ]
        # Omit the UniqueTogetherValidator that would be automatically added to validate (group, facility_id). This
        # prevents facility_id from being interpreted as a required field.
        validators = [
            UniqueTogetherValidator(queryset=Rack.objects.all(), fields=('group', 'name'))
        ]

    def validate(self, data):

        # Validate uniqueness of (group, facility_id) since we omitted the automatically-created validator from Meta.
        if data.get('facility_id', None):
            validator = UniqueTogetherValidator(queryset=Rack.objects.all(), fields=('group', 'facility_id'))
            validator.set_context(self)
            validator(data)

        # Enforce model validation
        super(RackSerializer, self).validate(data)

        return data


class NestedRackSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:rack-detail')

    class Meta:
        model = Rack
        fields = ['id', 'url', 'name', 'display_name']


#
# Rack units
#

class NestedDeviceSerializer(WritableNestedSerializer):
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

class RackReservationSerializer(ValidatedModelSerializer):
    rack = NestedRackSerializer()
    user = NestedUserSerializer()
    tenant = NestedTenantSerializer(required=False, allow_null=True)

    class Meta:
        model = RackReservation
        fields = ['id', 'rack', 'units', 'created', 'user', 'tenant', 'description']


#
# Manufacturers
#

class ManufacturerSerializer(ValidatedModelSerializer):

    class Meta:
        model = Manufacturer
        fields = ['id', 'name', 'slug']


class NestedManufacturerSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:manufacturer-detail')

    class Meta:
        model = Manufacturer
        fields = ['id', 'url', 'name', 'slug']


#
# Device types
#

class DeviceTypeSerializer(TaggitSerializer, CustomFieldModelSerializer):
    manufacturer = NestedManufacturerSerializer()
    subdevice_role = ChoiceField(choices=SUBDEVICE_ROLE_CHOICES, required=False, allow_null=True)
    instance_count = serializers.IntegerField(source='instances.count', read_only=True)
    tags = TagListSerializerField(required=False)

    class Meta:
        model = DeviceType
        fields = [
            'id', 'manufacturer', 'model', 'slug', 'part_number', 'u_height', 'is_full_depth', 'subdevice_role',
            'comments', 'tags', 'custom_fields', 'created', 'last_updated', 'instance_count',
        ]


class NestedDeviceTypeSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:devicetype-detail')
    manufacturer = NestedManufacturerSerializer(read_only=True)

    class Meta:
        model = DeviceType
        fields = ['id', 'url', 'manufacturer', 'model', 'slug']


#
# Console port templates
#

class ConsolePortTemplateSerializer(ValidatedModelSerializer):
    device_type = NestedDeviceTypeSerializer()

    class Meta:
        model = ConsolePortTemplate
        fields = ['id', 'device_type', 'name']


#
# Console server port templates
#

class ConsoleServerPortTemplateSerializer(ValidatedModelSerializer):
    device_type = NestedDeviceTypeSerializer()

    class Meta:
        model = ConsoleServerPortTemplate
        fields = ['id', 'device_type', 'name']


#
# Power port templates
#

class PowerPortTemplateSerializer(ValidatedModelSerializer):
    device_type = NestedDeviceTypeSerializer()

    class Meta:
        model = PowerPortTemplate
        fields = ['id', 'device_type', 'name']


#
# Power outlet templates
#

class PowerOutletTemplateSerializer(ValidatedModelSerializer):
    device_type = NestedDeviceTypeSerializer()

    class Meta:
        model = PowerOutletTemplate
        fields = ['id', 'device_type', 'name']


#
# Interface templates
#

class InterfaceTemplateSerializer(ValidatedModelSerializer):
    device_type = NestedDeviceTypeSerializer()
    form_factor = ChoiceField(choices=IFACE_FF_CHOICES, required=False)

    class Meta:
        model = InterfaceTemplate
        fields = ['id', 'device_type', 'name', 'form_factor', 'mgmt_only']


#
# Rear port templates
#

class RearPortTemplateSerializer(ValidatedModelSerializer):
    device_type = NestedDeviceTypeSerializer()
    type = ChoiceField(choices=PORT_TYPE_CHOICES)

    class Meta:
        model = RearPortTemplate
        fields = ['id', 'device_type', 'name', 'type', 'positions']


class NestedRearPortTemplateSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:rearporttemplate-detail')

    class Meta:
        model = RearPortTemplate
        fields = ['id', 'url', 'name']


#
# Front port templates
#

class FrontPortTemplateSerializer(ValidatedModelSerializer):
    device_type = NestedDeviceTypeSerializer()
    type = ChoiceField(choices=PORT_TYPE_CHOICES)
    rear_port = NestedRearPortTemplateSerializer()

    class Meta:
        model = FrontPortTemplate
        fields = ['id', 'device_type', 'name', 'type', 'rear_port', 'rear_port_position']


class NestedFrontPortTemplateSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:frontporttemplate-detail')

    class Meta:
        model = FrontPortTemplate
        fields = ['id', 'url', 'name']


#
# Device bay templates
#

class DeviceBayTemplateSerializer(ValidatedModelSerializer):
    device_type = NestedDeviceTypeSerializer()

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


class NestedDeviceRoleSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:devicerole-detail')

    class Meta:
        model = DeviceRole
        fields = ['id', 'url', 'name', 'slug']


#
# Platforms
#

class PlatformSerializer(ValidatedModelSerializer):
    manufacturer = NestedManufacturerSerializer(required=False, allow_null=True)

    class Meta:
        model = Platform
        fields = ['id', 'name', 'slug', 'manufacturer', 'napalm_driver', 'napalm_args']


class NestedPlatformSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:platform-detail')

    class Meta:
        model = Platform
        fields = ['id', 'url', 'name', 'slug']


#
# Devices
#

# Cannot import ipam.api.NestedIPAddressSerializer due to circular dependency
class DeviceIPAddressSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:ipaddress-detail')

    class Meta:
        model = IPAddress
        fields = ['id', 'url', 'family', 'address']


# Cannot import virtualization.api.NestedClusterSerializer due to circular dependency
class NestedClusterSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='virtualization-api:cluster-detail')

    class Meta:
        model = Cluster
        fields = ['id', 'url', 'name']


# Cannot import NestedVirtualChassisSerializer due to circular dependency
class DeviceVirtualChassisSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:virtualchassis-detail')
    master = NestedDeviceSerializer()

    class Meta:
        model = VirtualChassis
        fields = ['id', 'url', 'master']


class DeviceSerializer(TaggitSerializer, CustomFieldModelSerializer):
    device_type = NestedDeviceTypeSerializer()
    device_role = NestedDeviceRoleSerializer()
    tenant = NestedTenantSerializer(required=False, allow_null=True)
    platform = NestedPlatformSerializer(required=False, allow_null=True)
    site = NestedSiteSerializer()
    rack = NestedRackSerializer(required=False, allow_null=True)
    face = ChoiceField(choices=RACK_FACE_CHOICES, required=False, allow_null=True)
    status = ChoiceField(choices=DEVICE_STATUS_CHOICES, required=False)
    primary_ip = DeviceIPAddressSerializer(read_only=True)
    primary_ip4 = DeviceIPAddressSerializer(required=False, allow_null=True)
    primary_ip6 = DeviceIPAddressSerializer(required=False, allow_null=True)
    parent_device = serializers.SerializerMethodField()
    cluster = NestedClusterSerializer(required=False, allow_null=True)
    virtual_chassis = DeviceVirtualChassisSerializer(required=False, allow_null=True)
    tags = TagListSerializerField(required=False)

    class Meta:
        model = Device
        fields = [
            'id', 'name', 'display_name', 'device_type', 'device_role', 'tenant', 'platform', 'serial', 'asset_tag',
            'site', 'rack', 'position', 'face', 'parent_device', 'status', 'primary_ip', 'primary_ip4', 'primary_ip6',
            'cluster', 'virtual_chassis', 'vc_position', 'vc_priority', 'comments', 'tags', 'custom_fields', 'created',
            'last_updated', 'local_context_data',
        ]
        validators = []

    def validate(self, data):

        # Validate uniqueness of (rack, position, face) since we omitted the automatically-created validator from Meta.
        if data.get('rack') and data.get('position') and data.get('face'):
            validator = UniqueTogetherValidator(queryset=Device.objects.all(), fields=('rack', 'position', 'face'))
            validator.set_context(self)
            validator(data)

        # Enforce model validation
        super(DeviceSerializer, self).validate(data)

        return data

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
    config_context = serializers.SerializerMethodField()

    class Meta(DeviceSerializer.Meta):
        fields = [
            'id', 'name', 'display_name', 'device_type', 'device_role', 'tenant', 'platform', 'serial', 'asset_tag',
            'site', 'rack', 'position', 'face', 'parent_device', 'status', 'primary_ip', 'primary_ip4', 'primary_ip6',
            'cluster', 'virtual_chassis', 'vc_position', 'vc_priority', 'comments', 'tags', 'custom_fields',
            'config_context', 'created', 'last_updated', 'local_context_data',
        ]

    def get_config_context(self, obj):
        return obj.get_config_context()


#
# Cables
#

class CableSerializer(ValidatedModelSerializer):
    termination_a_type = ContentTypeField()
    termination_b_type = ContentTypeField()
    termination_a = serializers.SerializerMethodField(read_only=True)
    termination_b = serializers.SerializerMethodField(read_only=True)
    status = ChoiceField(choices=CONNECTION_STATUS_CHOICES, required=False)
    length_unit = ChoiceField(choices=CABLE_LENGTH_UNIT_CHOICES, required=False)

    class Meta:
        model = Cable
        fields = [
            'id', 'termination_a_type', 'termination_a_id', 'termination_a', 'termination_b_type', 'termination_b_id',
            'termination_b', 'type', 'status', 'label', 'color', 'length', 'length_unit',
        ]

    def _get_termination(self, obj, side):
        """
        Serialize a nested representation of a termination.
        """
        if side.lower() not in ['a', 'b']:
            raise ValueError("Termination side must be either A or B.")
        termination = getattr(obj, 'termination_{}'.format(side.lower()))
        if termination is None:
            return None
        serializer = get_serializer_for_model(termination, prefix='Nested')
        context = {'request': self.context['request']}
        data = serializer(termination, context=context).data

        return data

    def get_termination_a(self, obj):
        return self._get_termination(obj, 'a')

    def get_termination_b(self, obj):
        return self._get_termination(obj, 'b')


class TracedCableSerializer(serializers.ModelSerializer):
    """
    Used only while tracing a cable path.
    """
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:cable-detail')

    class Meta:
        model = Cable
        fields = [
            'id', 'url', 'type', 'status', 'label', 'color', 'length', 'length_unit',
        ]


class NestedCableSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:cable-detail')

    class Meta:
        model = Cable
        fields = ['id', 'url', 'label']


#
# Console server ports
#

class ConsoleServerPortSerializer(TaggitSerializer, ValidatedModelSerializer):
    device = NestedDeviceSerializer()
    cable = NestedCableSerializer(read_only=True)
    tags = TagListSerializerField(required=False)

    class Meta:
        model = ConsoleServerPort
        fields = ['id', 'device', 'name', 'connected_endpoint', 'cable', 'tags']
        read_only_fields = ['connected_endpoint']


class NestedConsoleServerPortSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:consoleserverport-detail')
    device = NestedDeviceSerializer(read_only=True)

    class Meta:
        model = ConsoleServerPort
        fields = ['id', 'url', 'device', 'name', 'cable']


#
# Console ports
#

class ConsolePortSerializer(TaggitSerializer, ValidatedModelSerializer):
    device = NestedDeviceSerializer()
    connected_endpoint = NestedConsoleServerPortSerializer(read_only=True)
    cable = NestedCableSerializer(read_only=True)
    tags = TagListSerializerField(required=False)

    class Meta:
        model = ConsolePort
        fields = ['id', 'device', 'name', 'connected_endpoint', 'connection_status', 'cable', 'tags']


class NestedConsolePortSerializer(TaggitSerializer, ValidatedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:consoleport-detail')
    device = NestedDeviceSerializer(read_only=True)

    class Meta:
        model = ConsolePort
        fields = ['id', 'url', 'device', 'name', 'cable']


#
# Power outlets
#

class PowerOutletSerializer(TaggitSerializer, ValidatedModelSerializer):
    device = NestedDeviceSerializer()
    cable = NestedCableSerializer(read_only=True)
    tags = TagListSerializerField(required=False)

    class Meta:
        model = PowerOutlet
        fields = ['id', 'device', 'name', 'connected_endpoint', 'cable', 'tags']
        read_only_fields = ['connected_endpoint']


class NestedPowerOutletSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:poweroutlet-detail')
    device = NestedDeviceSerializer(read_only=True)

    class Meta:
        model = PowerOutlet
        fields = ['id', 'url', 'device', 'name', 'cable']


#
# Power ports
#

class PowerPortSerializer(TaggitSerializer, ValidatedModelSerializer):
    device = NestedDeviceSerializer()
    connected_endpoint = NestedPowerOutletSerializer(read_only=True)
    cable = NestedCableSerializer(read_only=True)
    tags = TagListSerializerField(required=False)

    class Meta:
        model = PowerPort
        fields = ['id', 'device', 'name', 'connected_endpoint', 'connection_status', 'cable', 'tags']


class NestedPowerPortSerializer(TaggitSerializer, ValidatedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:powerport-detail')
    device = NestedDeviceSerializer(read_only=True)

    class Meta:
        model = PowerPort
        fields = ['id', 'url', 'device', 'name', 'cable']


#
# Interfaces
#

class NestedInterfaceSerializer(WritableNestedSerializer):
    device = NestedDeviceSerializer(read_only=True)
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:interface-detail')

    class Meta:
        model = Interface
        fields = ['id', 'url', 'device', 'name', 'cable']


class InterfaceNestedCircuitSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='circuits-api:circuit-detail')

    class Meta:
        model = Circuit
        fields = ['id', 'url', 'cid']


class InterfaceCircuitTerminationSerializer(WritableNestedSerializer):
    circuit = InterfaceNestedCircuitSerializer(read_only=True)

    class Meta:
        model = CircuitTermination
        fields = [
            'id', 'circuit', 'term_side', 'port_speed', 'upstream_speed', 'xconnect_id', 'pp_info',
        ]


# Cannot import ipam.api.NestedVLANSerializer due to circular dependency
class InterfaceVLANSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:vlan-detail')

    class Meta:
        model = VLAN
        fields = ['id', 'url', 'vid', 'name', 'display_name']


class InterfaceSerializer(TaggitSerializer, ValidatedModelSerializer):
    device = NestedDeviceSerializer()
    form_factor = ChoiceField(choices=IFACE_FF_CHOICES, required=False)
    lag = NestedInterfaceSerializer(required=False, allow_null=True)
    connected_endpoint = serializers.SerializerMethodField(read_only=True)
    mode = ChoiceField(choices=IFACE_MODE_CHOICES, required=False, allow_null=True)
    untagged_vlan = InterfaceVLANSerializer(required=False, allow_null=True)
    tagged_vlans = SerializedPKRelatedField(
        queryset=VLAN.objects.all(),
        serializer=InterfaceVLANSerializer,
        required=False,
        many=True
    )
    cable = NestedCableSerializer(read_only=True)
    tags = TagListSerializerField(required=False)

    class Meta:
        model = Interface
        fields = [
            'id', 'device', 'name', 'form_factor', 'enabled', 'lag', 'mtu', 'mac_address', 'mgmt_only', 'description',
            'connected_endpoint', 'cable', 'mode', 'untagged_vlan', 'tagged_vlans', 'tags', 'count_ipaddresses',
        ]

    def validate(self, data):

        # All associated VLANs be global or assigned to the parent device's site.
        device = self.instance.device if self.instance else data.get('device')
        untagged_vlan = data.get('untagged_vlan')
        if untagged_vlan and untagged_vlan.site not in [device.site, None]:
            raise serializers.ValidationError({
                'untagged_vlan': "VLAN {} must belong to the same site as the interface's parent device, or it must be "
                                 "global.".format(untagged_vlan)
            })
        for vlan in data.get('tagged_vlans', []):
            if vlan.site not in [device.site, None]:
                raise serializers.ValidationError({
                    'tagged_vlans': "VLAN {} must belong to the same site as the interface's parent device, or it must "
                                    "be global.".format(vlan)
                })

        return super(InterfaceSerializer, self).validate(data)

    def get_connected_endpoint(self, obj):
        """
        Return the appropriate serializer for the type of connected object.
        """
        if obj.connected_endpoint is None:
            return None

        serializer = get_serializer_for_model(obj.connected_endpoint, prefix='Nested')
        context = {'request': self.context['request']}
        data = serializer(obj.connected_endpoint, context=context).data

        return data


#
# Rear ports
#

class RearPortSerializer(ValidatedModelSerializer):
    device = NestedDeviceSerializer()
    type = ChoiceField(choices=PORT_TYPE_CHOICES)
    cable = NestedCableSerializer(read_only=True)
    tags = TagListSerializerField(required=False)

    class Meta:
        model = RearPort
        fields = ['id', 'device', 'name', 'type', 'positions', 'cable', 'tags']


class NestedRearPortSerializer(WritableNestedSerializer):
    device = NestedDeviceSerializer(read_only=True)
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:rearport-detail')

    class Meta:
        model = RearPort
        fields = ['id', 'url', 'device', 'name', 'cable']


#
# Front ports
#

class FrontPortRearPortSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:rearport-detail')

    class Meta:
        model = RearPort
        fields = ['id', 'url', 'name']


class FrontPortSerializer(ValidatedModelSerializer):
    device = NestedDeviceSerializer()
    type = ChoiceField(choices=PORT_TYPE_CHOICES)
    rear_port = FrontPortRearPortSerializer()
    cable = NestedCableSerializer(read_only=True)
    tags = TagListSerializerField(required=False)

    class Meta:
        model = FrontPort
        fields = ['id', 'device', 'name', 'type', 'rear_port', 'rear_port_position', 'cable', 'tags']


class NestedFrontPortSerializer(WritableNestedSerializer):
    device = NestedDeviceSerializer(read_only=True)
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:frontport-detail')

    class Meta:
        model = FrontPort
        fields = ['id', 'url', 'device', 'name', 'cable']


#
# Device bays
#

class DeviceBaySerializer(TaggitSerializer, ValidatedModelSerializer):
    device = NestedDeviceSerializer()
    installed_device = NestedDeviceSerializer(required=False, allow_null=True)
    tags = TagListSerializerField(required=False)

    class Meta:
        model = DeviceBay
        fields = ['id', 'device', 'name', 'installed_device', 'tags']


class NestedDeviceBaySerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:rearport-detail')
    device = NestedDeviceSerializer(read_only=True)

    class Meta:
        model = DeviceBay
        fields = ['id', 'url', 'device', 'name']


#
# Inventory items
#

class InventoryItemSerializer(TaggitSerializer, ValidatedModelSerializer):
    device = NestedDeviceSerializer()
    # Provide a default value to satisfy UniqueTogetherValidator
    parent = serializers.PrimaryKeyRelatedField(queryset=InventoryItem.objects.all(), allow_null=True, default=None)
    manufacturer = NestedManufacturerSerializer(required=False, allow_null=True, default=None)
    tags = TagListSerializerField(required=False)

    class Meta:
        model = InventoryItem
        fields = [
            'id', 'device', 'parent', 'name', 'manufacturer', 'part_id', 'serial', 'asset_tag', 'discovered',
            'description', 'tags',
        ]


#
# Interface connections
#

class InterfaceConnectionSerializer(ValidatedModelSerializer):
    interface_a = serializers.SerializerMethodField()
    interface_b = NestedInterfaceSerializer(source='connected_endpoint')
    connection_status = ChoiceField(choices=CONNECTION_STATUS_CHOICES, required=False)

    class Meta:
        model = Interface
        fields = ['interface_a', 'interface_b', 'connection_status']

    def get_interface_a(self, obj):
        context = {'request': self.context['request']}
        return NestedInterfaceSerializer(instance=obj, context=context).data


#
# Virtual chassis
#

class VirtualChassisSerializer(TaggitSerializer, ValidatedModelSerializer):
    master = NestedDeviceSerializer()
    tags = TagListSerializerField(required=False)

    class Meta:
        model = VirtualChassis
        fields = ['id', 'master', 'domain', 'tags']


class NestedVirtualChassisSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:virtualchassis-detail')

    class Meta:
        model = VirtualChassis
        fields = ['id', 'url']
