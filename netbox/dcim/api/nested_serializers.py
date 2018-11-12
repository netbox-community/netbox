from rest_framework import serializers

from dcim.models import (
    Cable, ConsolePort, ConsoleServerPort, Device, DeviceBay, DeviceType, DeviceRole, FrontPort, FrontPortTemplate,
    Interface, Manufacturer, Platform, PowerOutlet, PowerPort, Rack, RackGroup, RackRole, RearPort, RearPortTemplate,
    Region, Site, VirtualChassis,
)
from utilities.api import WritableNestedSerializer

__all__ = [
    'NestedCableSerializer',
    'NestedConsolePortSerializer',
    'NestedConsoleServerPortSerializer',
    'NestedDeviceBaySerializer',
    'NestedDeviceRoleSerializer',
    'NestedDeviceSerializer',
    'NestedDeviceTypeSerializer',
    'NestedFrontPortSerializer',
    'NestedFrontPortTemplateSerializer',
    'NestedInterfaceSerializer',
    'NestedManufacturerSerializer',
    'NestedPlatformSerializer',
    'NestedPowerOutletSerializer',
    'NestedPowerPortSerializer',
    'NestedRackGroupSerializer',
    'NestedRackRoleSerializer',
    'NestedRackSerializer',
    'NestedRearPortSerializer',
    'NestedRearPortTemplateSerializer',
    'NestedRegionSerializer',
    'NestedSiteSerializer',
    'NestedVirtualChassisSerializer',
]


#
# Regions/sites
#

class NestedRegionSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:region-detail')

    class Meta:
        model = Region
        fields = ['id', 'url', 'name', 'slug']


class NestedSiteSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:site-detail')

    class Meta:
        model = Site
        fields = ['id', 'url', 'name', 'slug']


#
# Racks
#

class NestedRackGroupSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:rackgroup-detail')

    class Meta:
        model = RackGroup
        fields = ['id', 'url', 'name', 'slug']


class NestedRackRoleSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:rackrole-detail')

    class Meta:
        model = RackRole
        fields = ['id', 'url', 'name', 'slug']


class NestedRackSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:rack-detail')

    class Meta:
        model = Rack
        fields = ['id', 'url', 'name', 'display_name']


#
# Device types
#

class NestedManufacturerSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:manufacturer-detail')

    class Meta:
        model = Manufacturer
        fields = ['id', 'url', 'name', 'slug']


class NestedDeviceTypeSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:devicetype-detail')
    manufacturer = NestedManufacturerSerializer(read_only=True)

    class Meta:
        model = DeviceType
        fields = ['id', 'url', 'manufacturer', 'model', 'slug']


class NestedRearPortTemplateSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:rearporttemplate-detail')

    class Meta:
        model = RearPortTemplate
        fields = ['id', 'url', 'name']


class NestedFrontPortTemplateSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:frontporttemplate-detail')

    class Meta:
        model = FrontPortTemplate
        fields = ['id', 'url', 'name']


#
# Devices
#

class NestedDeviceRoleSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:devicerole-detail')

    class Meta:
        model = DeviceRole
        fields = ['id', 'url', 'name', 'slug']


class NestedPlatformSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:platform-detail')

    class Meta:
        model = Platform
        fields = ['id', 'url', 'name', 'slug']


class NestedDeviceSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:device-detail')

    class Meta:
        model = Device
        fields = ['id', 'url', 'name', 'display_name']


class NestedConsoleServerPortSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:consoleserverport-detail')
    device = NestedDeviceSerializer(read_only=True)

    class Meta:
        model = ConsoleServerPort
        fields = ['id', 'url', 'device', 'name', 'cable']


class NestedConsolePortSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:consoleport-detail')
    device = NestedDeviceSerializer(read_only=True)

    class Meta:
        model = ConsolePort
        fields = ['id', 'url', 'device', 'name', 'cable']


class NestedPowerOutletSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:poweroutlet-detail')
    device = NestedDeviceSerializer(read_only=True)

    class Meta:
        model = PowerOutlet
        fields = ['id', 'url', 'device', 'name', 'cable']


class NestedPowerPortSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:powerport-detail')
    device = NestedDeviceSerializer(read_only=True)

    class Meta:
        model = PowerPort
        fields = ['id', 'url', 'device', 'name', 'cable']


class NestedInterfaceSerializer(WritableNestedSerializer):
    device = NestedDeviceSerializer(read_only=True)
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:interface-detail')

    class Meta:
        model = Interface
        fields = ['id', 'url', 'device', 'name', 'cable']


class NestedRearPortSerializer(WritableNestedSerializer):
    device = NestedDeviceSerializer(read_only=True)
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:rearport-detail')

    class Meta:
        model = RearPort
        fields = ['id', 'url', 'device', 'name', 'cable']


class NestedFrontPortSerializer(WritableNestedSerializer):
    device = NestedDeviceSerializer(read_only=True)
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:frontport-detail')

    class Meta:
        model = FrontPort
        fields = ['id', 'url', 'device', 'name', 'cable']


class NestedDeviceBaySerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:rearport-detail')
    device = NestedDeviceSerializer(read_only=True)

    class Meta:
        model = DeviceBay
        fields = ['id', 'url', 'device', 'name']


#
# Cables
#

class NestedCableSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:cable-detail')

    class Meta:
        model = Cable
        fields = ['id', 'url', 'label']


#
# Virtual chassis
#

class NestedVirtualChassisSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:virtualchassis-detail')
    master = NestedDeviceSerializer()

    class Meta:
        model = VirtualChassis
        fields = ['id', 'url', 'master']
