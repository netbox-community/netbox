from rest_framework import serializers

from dcim import models
from netbox.api import WritableNestedSerializer

__all__ = [
    'NestedCableSerializer',
    'NestedConsolePortSerializer',
    'NestedConsolePortTemplateSerializer',
    'NestedConsoleServerPortSerializer',
    'NestedConsoleServerPortTemplateSerializer',
    'NestedDeviceBaySerializer',
    'NestedDeviceBayTemplateSerializer',
    'NestedDeviceRoleSerializer',
    'NestedDeviceSerializer',
    'NestedDeviceTypeSerializer',
    'NestedFrontPortSerializer',
    'NestedFrontPortTemplateSerializer',
    'NestedInterfaceSerializer',
    'NestedInterfaceTemplateSerializer',
    'NestedInventoryItemSerializer',
    'NestedManufacturerSerializer',
    'NestedPlatformSerializer',
    'NestedPowerFeedSerializer',
    'NestedPowerOutletSerializer',
    'NestedPowerOutletTemplateSerializer',
    'NestedPowerPanelSerializer',
    'NestedPowerPortSerializer',
    'NestedPowerPortTemplateSerializer',
    'NestedRackGroupSerializer',
    'NestedRackReservationSerializer',
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
    _depth = serializers.IntegerField(source='level', read_only=True)

    class Meta:
        model = models.Region
        fields = ['id', 'url', 'name', 'slug', 'site_count', '_depth']


class NestedSiteSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:site-detail')

    class Meta:
        model = models.Site
        fields = ['id', 'url', 'name', 'slug']


#
# Racks
#

class NestedRackGroupSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:rackgroup-detail')
    rack_count = serializers.IntegerField(read_only=True)
    _depth = serializers.IntegerField(source='level', read_only=True)

    class Meta:
        model = models.RackGroup
        fields = ['id', 'url', 'name', 'slug', 'rack_count', '_depth']


class NestedRackRoleSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:rackrole-detail')
    rack_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.RackRole
        fields = ['id', 'url', 'name', 'slug', 'rack_count']


class NestedRackSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:rack-detail')
    device_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.Rack
        fields = ['id', 'url', 'name', 'display_name', 'device_count']


class NestedRackReservationSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:rackreservation-detail')
    user = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.RackReservation
        fields = ['id', 'url', 'user', 'units']

    def get_user(self, obj):
        return obj.user.username


#
# Device types
#

class NestedManufacturerSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:manufacturer-detail')
    devicetype_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.Manufacturer
        fields = ['id', 'url', 'name', 'slug', 'devicetype_count']


class NestedDeviceTypeSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:devicetype-detail')
    manufacturer = NestedManufacturerSerializer(read_only=True)
    device_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.DeviceType
        fields = ['id', 'url', 'manufacturer', 'model', 'slug', 'display_name', 'device_count']


class NestedConsolePortTemplateSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:consoleporttemplate-detail')

    class Meta:
        model = models.ConsolePortTemplate
        fields = ['id', 'url', 'name']


class NestedConsoleServerPortTemplateSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:consoleserverporttemplate-detail')

    class Meta:
        model = models.ConsoleServerPortTemplate
        fields = ['id', 'url', 'name']


class NestedPowerPortTemplateSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:powerporttemplate-detail')

    class Meta:
        model = models.PowerPortTemplate
        fields = ['id', 'url', 'name']


class NestedPowerOutletTemplateSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:poweroutlettemplate-detail')

    class Meta:
        model = models.PowerOutletTemplate
        fields = ['id', 'url', 'name']


class NestedInterfaceTemplateSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:interfacetemplate-detail')

    class Meta:
        model = models.InterfaceTemplate
        fields = ['id', 'url', 'name']


class NestedRearPortTemplateSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:rearporttemplate-detail')

    class Meta:
        model = models.RearPortTemplate
        fields = ['id', 'url', 'name']


class NestedFrontPortTemplateSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:frontporttemplate-detail')

    class Meta:
        model = models.FrontPortTemplate
        fields = ['id', 'url', 'name']


class NestedDeviceBayTemplateSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:devicebaytemplate-detail')

    class Meta:
        model = models.DeviceBayTemplate
        fields = ['id', 'url', 'name']


#
# Devices
#

class NestedDeviceRoleSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:devicerole-detail')
    device_count = serializers.IntegerField(read_only=True)
    virtualmachine_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.DeviceRole
        fields = ['id', 'url', 'name', 'slug', 'device_count', 'virtualmachine_count']


class NestedPlatformSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:platform-detail')
    device_count = serializers.IntegerField(read_only=True)
    virtualmachine_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.Platform
        fields = ['id', 'url', 'name', 'slug', 'device_count', 'virtualmachine_count']


class NestedDeviceSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:device-detail')

    class Meta:
        model = models.Device
        fields = ['id', 'url', 'name', 'display_name']


class NestedConsoleServerPortSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:consoleserverport-detail')
    device = NestedDeviceSerializer(read_only=True)

    class Meta:
        model = models.ConsoleServerPort
        fields = ['id', 'url', 'device', 'name', 'cable']


class NestedConsolePortSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:consoleport-detail')
    device = NestedDeviceSerializer(read_only=True)

    class Meta:
        model = models.ConsolePort
        fields = ['id', 'url', 'device', 'name', 'cable']


class NestedPowerOutletSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:poweroutlet-detail')
    device = NestedDeviceSerializer(read_only=True)

    class Meta:
        model = models.PowerOutlet
        fields = ['id', 'url', 'device', 'name', 'cable']


class NestedPowerPortSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:powerport-detail')
    device = NestedDeviceSerializer(read_only=True)

    class Meta:
        model = models.PowerPort
        fields = ['id', 'url', 'device', 'name', 'cable']


class NestedInterfaceSerializer(WritableNestedSerializer):
    device = NestedDeviceSerializer(read_only=True)
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:interface-detail')

    class Meta:
        model = models.Interface
        fields = ['id', 'url', 'device', 'name', 'cable']


class NestedRearPortSerializer(WritableNestedSerializer):
    device = NestedDeviceSerializer(read_only=True)
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:rearport-detail')

    class Meta:
        model = models.RearPort
        fields = ['id', 'url', 'device', 'name', 'cable']


class NestedFrontPortSerializer(WritableNestedSerializer):
    device = NestedDeviceSerializer(read_only=True)
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:frontport-detail')

    class Meta:
        model = models.FrontPort
        fields = ['id', 'url', 'device', 'name', 'cable']


class NestedDeviceBaySerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:devicebay-detail')
    device = NestedDeviceSerializer(read_only=True)

    class Meta:
        model = models.DeviceBay
        fields = ['id', 'url', 'device', 'name']


class NestedInventoryItemSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:inventoryitem-detail')
    device = NestedDeviceSerializer(read_only=True)
    _depth = serializers.IntegerField(source='level', read_only=True)

    class Meta:
        model = models.InventoryItem
        fields = ['id', 'url', 'device', 'name', '_depth']


#
# Cables
#

class NestedCableSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:cable-detail')

    class Meta:
        model = models.Cable
        fields = ['id', 'url', 'label']


#
# Virtual chassis
#

class NestedVirtualChassisSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:virtualchassis-detail')
    master = NestedDeviceSerializer()
    member_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.VirtualChassis
        fields = ['id', 'name', 'url', 'master', 'member_count']


#
# Power panels/feeds
#

class NestedPowerPanelSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:powerpanel-detail')
    powerfeed_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.PowerPanel
        fields = ['id', 'url', 'name', 'powerfeed_count']


class NestedPowerFeedSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:powerfeed-detail')

    class Meta:
        model = models.PowerFeed
        fields = ['id', 'url', 'name', 'cable']
