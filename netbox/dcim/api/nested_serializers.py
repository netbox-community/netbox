from rest_framework import serializers

from dcim.constants import CONNECTION_STATUS_CHOICES
from dcim.models import (
    Cable, ConsolePort, ConsoleServerPort, Device, DeviceBay, DeviceType, DeviceRole, FrontPort, FrontPortTemplate,
    Interface, Manufacturer, Platform, PowerFeed, PowerOutlet, PowerPanel, PowerPort, PowerPortTemplate, Rack,
    RackGroup, RackRole, RearPort, RearPortTemplate, Region, Site, VirtualChassis,
)
from utilities.api import ChoiceField, WritableNestedSerializer

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
    'NestedPowerFeedSerializer',
    'NestedPowerOutletSerializer',
    'NestedPowerPanelSerializer',
    'NestedPowerPortSerializer',
    'NestedPowerPortTemplateSerializer',
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
    site_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Region
        fields = ['id', 'url', 'name', 'slug', 'site_count']


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
    rack_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = RackGroup
        fields = ['id', 'url', 'name', 'slug', 'rack_count']


class NestedRackRoleSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:rackrole-detail')
    rack_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = RackRole
        fields = ['id', 'url', 'name', 'slug', 'rack_count']


class NestedRackSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:rack-detail')
    device_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Rack
        fields = ['id', 'url', 'name', 'display_name', 'device_count']


#
# Device types
#

class NestedManufacturerSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:manufacturer-detail')
    devicetype_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Manufacturer
        fields = ['id', 'url', 'name', 'slug', 'devicetype_count']


class NestedDeviceTypeSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:devicetype-detail')
    manufacturer = NestedManufacturerSerializer(read_only=True)
    device_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = DeviceType
        fields = ['id', 'url', 'manufacturer', 'model', 'slug', 'display_name', 'device_count']


class NestedPowerPortTemplateSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:powerporttemplate-detail')

    class Meta:
        model = PowerPortTemplate
        fields = ['id', 'url', 'name']


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
    device_count = serializers.IntegerField(read_only=True)
    virtualmachine_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = DeviceRole
        fields = ['id', 'url', 'name', 'slug', 'device_count', 'virtualmachine_count']


class NestedPlatformSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:platform-detail')
    device_count = serializers.IntegerField(read_only=True)
    virtualmachine_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Platform
        fields = ['id', 'url', 'name', 'slug', 'device_count', 'virtualmachine_count']


class NestedDeviceSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:device-detail')

    class Meta:
        model = Device
        fields = ['id', 'url', 'name', 'display_name']


class NestedConsoleServerPortSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:consoleserverport-detail')
    device = NestedDeviceSerializer(read_only=True)
    connection_status = ChoiceField(choices=CONNECTION_STATUS_CHOICES, read_only=True)

    class Meta:
        model = ConsoleServerPort
        fields = ['id', 'url', 'device', 'name', 'cable', 'connection_status']


class NestedConsolePortSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:consoleport-detail')
    device = NestedDeviceSerializer(read_only=True)
    connection_status = ChoiceField(choices=CONNECTION_STATUS_CHOICES, read_only=True)

    class Meta:
        model = ConsolePort
        fields = ['id', 'url', 'device', 'name', 'cable', 'connection_status']


class NestedPowerOutletSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:poweroutlet-detail')
    device = NestedDeviceSerializer(read_only=True)
    connection_status = ChoiceField(choices=CONNECTION_STATUS_CHOICES, read_only=True)

    class Meta:
        model = PowerOutlet
        fields = ['id', 'url', 'device', 'name', 'cable', 'connection_status']


class NestedPowerPortSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:powerport-detail')
    device = NestedDeviceSerializer(read_only=True)
    connection_status = ChoiceField(choices=CONNECTION_STATUS_CHOICES, read_only=True)

    class Meta:
        model = PowerPort
        fields = ['id', 'url', 'device', 'name', 'cable', 'connection_status']


class NestedInterfaceSerializer(WritableNestedSerializer):
    device = NestedDeviceSerializer(read_only=True)
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:interface-detail')
    connection_status = ChoiceField(choices=CONNECTION_STATUS_CHOICES, read_only=True)

    class Meta:
        model = Interface
        fields = ['id', 'url', 'device', 'name', 'cable', 'connection_status']


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
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:devicebay-detail')
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
    member_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = VirtualChassis
        fields = ['id', 'url', 'master', 'member_count']


#
# Power panels/feeds
#

class NestedPowerPanelSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:powerpanel-detail')
    powerfeed_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = PowerPanel
        fields = ['id', 'url', 'name', 'powerfeed_count']


class NestedPowerFeedSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:powerfeed-detail')

    class Meta:
        model = PowerFeed
        fields = ['id', 'url', 'name']
