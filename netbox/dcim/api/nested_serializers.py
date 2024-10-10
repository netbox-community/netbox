import warnings

from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers

from dcim import models
from netbox.api.fields import RelatedObjectCountField
from netbox.api.serializers import WritableNestedSerializer
from .serializers_.nested import (
    NestedDeviceBaySerializer, NestedDeviceSerializer, NestedInterfaceSerializer, NestedInterfaceTemplateSerializer,
    NestedLocationSerializer, NestedModuleBaySerializer, NestedRegionSerializer, NestedSiteGroupSerializer,
)

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
    'NestedInventoryItemRoleSerializer',
    'NestedInventoryItemTemplateSerializer',
    'NestedManufacturerSerializer',
    'NestedModuleBaySerializer',
    'NestedModuleBayTemplateSerializer',
    'NestedModuleSerializer',
    'NestedModuleTypeSerializer',
    'NestedPlatformSerializer',
    'NestedPowerFeedSerializer',
    'NestedPowerOutletSerializer',
    'NestedPowerOutletTemplateSerializer',
    'NestedPowerPanelSerializer',
    'NestedPowerPortSerializer',
    'NestedPowerPortTemplateSerializer',
    'NestedLocationSerializer',
    'NestedRackReservationSerializer',
    'NestedRackRoleSerializer',
    'NestedRackSerializer',
    'NestedRearPortSerializer',
    'NestedRearPortTemplateSerializer',
    'NestedRegionSerializer',
    'NestedSiteSerializer',
    'NestedSiteGroupSerializer',
    'NestedVirtualChassisSerializer',
    'NestedVirtualDeviceContextSerializer',
]

# TODO: Remove in v4.2
warnings.warn(
    "Dedicated nested serializers will be removed in NetBox v4.2. Use Serializer(nested=True) instead.",
    DeprecationWarning
)


#
# Regions/sites
#

class NestedSiteSerializer(WritableNestedSerializer):

    class Meta:
        model = models.Site
        fields = ['id', 'url', 'display_url', 'display', 'name', 'slug']


#
# Racks
#

@extend_schema_serializer(
    exclude_fields=('rack_count',),
)
class NestedRackRoleSerializer(WritableNestedSerializer):
    rack_count = RelatedObjectCountField('racks')

    class Meta:
        model = models.RackRole
        fields = ['id', 'url', 'display_url', 'display', 'name', 'slug', 'rack_count']


@extend_schema_serializer(
    exclude_fields=('device_count',),
)
class NestedRackSerializer(WritableNestedSerializer):
    device_count = RelatedObjectCountField('devices')

    class Meta:
        model = models.Rack
        fields = ['id', 'url', 'display_url', 'display', 'name', 'device_count']


class NestedRackReservationSerializer(WritableNestedSerializer):
    user = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.RackReservation
        fields = ['id', 'url', 'display_url', 'display', 'user', 'units']

    def get_user(self, obj):
        return obj.user.username


#
# Device/module types
#

@extend_schema_serializer(
    exclude_fields=('devicetype_count',),
)
class NestedManufacturerSerializer(WritableNestedSerializer):
    devicetype_count = RelatedObjectCountField('device_types')

    class Meta:
        model = models.Manufacturer
        fields = ['id', 'url', 'display_url', 'display', 'name', 'slug', 'devicetype_count']


@extend_schema_serializer(
    exclude_fields=('device_count',),
)
class NestedDeviceTypeSerializer(WritableNestedSerializer):
    manufacturer = NestedManufacturerSerializer(read_only=True)
    device_count = RelatedObjectCountField('instances')

    class Meta:
        model = models.DeviceType
        fields = ['id', 'url', 'display_url', 'display', 'manufacturer', 'model', 'slug', 'device_count']


class NestedModuleTypeSerializer(WritableNestedSerializer):
    manufacturer = NestedManufacturerSerializer(read_only=True)

    class Meta:
        model = models.ModuleType
        fields = ['id', 'url', 'display_url', 'display', 'manufacturer', 'model']


#
# Component templates
#

class NestedConsolePortTemplateSerializer(WritableNestedSerializer):

    class Meta:
        model = models.ConsolePortTemplate
        fields = ['id', 'url', 'display_url', 'display', 'name']


class NestedConsoleServerPortTemplateSerializer(WritableNestedSerializer):

    class Meta:
        model = models.ConsoleServerPortTemplate
        fields = ['id', 'url', 'display_url', 'display', 'name']


class NestedPowerPortTemplateSerializer(WritableNestedSerializer):

    class Meta:
        model = models.PowerPortTemplate
        fields = ['id', 'url', 'display_url', 'display', 'name']


class NestedPowerOutletTemplateSerializer(WritableNestedSerializer):

    class Meta:
        model = models.PowerOutletTemplate
        fields = ['id', 'url', 'display_url', 'display', 'name']


class NestedRearPortTemplateSerializer(WritableNestedSerializer):

    class Meta:
        model = models.RearPortTemplate
        fields = ['id', 'url', 'display_url', 'display', 'name']


class NestedFrontPortTemplateSerializer(WritableNestedSerializer):

    class Meta:
        model = models.FrontPortTemplate
        fields = ['id', 'url', 'display_url', 'display', 'name']


class NestedModuleBayTemplateSerializer(WritableNestedSerializer):

    class Meta:
        model = models.ModuleBayTemplate
        fields = ['id', 'url', 'display_url', 'display', 'name']


class NestedDeviceBayTemplateSerializer(WritableNestedSerializer):

    class Meta:
        model = models.DeviceBayTemplate
        fields = ['id', 'url', 'display_url', 'display', 'name']


class NestedInventoryItemTemplateSerializer(WritableNestedSerializer):
    _depth = serializers.IntegerField(source='level', read_only=True)

    class Meta:
        model = models.InventoryItemTemplate
        fields = ['id', 'url', 'display_url', 'display', 'name', '_depth']


#
# Devices
#

@extend_schema_serializer(
    exclude_fields=('device_count', 'virtualmachine_count'),
)
class NestedDeviceRoleSerializer(WritableNestedSerializer):
    device_count = RelatedObjectCountField('devices')
    virtualmachine_count = RelatedObjectCountField('virtual_machines')

    class Meta:
        model = models.DeviceRole
        fields = ['id', 'url', 'display_url', 'display', 'name', 'slug', 'device_count', 'virtualmachine_count']


@extend_schema_serializer(
    exclude_fields=('device_count', 'virtualmachine_count'),
)
class NestedPlatformSerializer(WritableNestedSerializer):
    device_count = RelatedObjectCountField('devices')
    virtualmachine_count = RelatedObjectCountField('virtual_machines')

    class Meta:
        model = models.Platform
        fields = ['id', 'url', 'display_url', 'display', 'name', 'slug', 'device_count', 'virtualmachine_count']


class ModuleNestedModuleBaySerializer(WritableNestedSerializer):

    class Meta:
        model = models.ModuleBay
        fields = ['id', 'url', 'display_url', 'display', 'name']


class NestedModuleSerializer(WritableNestedSerializer):
    device = NestedDeviceSerializer(read_only=True)
    module_bay = ModuleNestedModuleBaySerializer(read_only=True)
    module_type = NestedModuleTypeSerializer(read_only=True)

    class Meta:
        model = models.Module
        fields = ['id', 'url', 'display_url', 'display', 'device', 'module_bay', 'module_type']


class NestedConsoleServerPortSerializer(WritableNestedSerializer):
    device = NestedDeviceSerializer(read_only=True)
    _occupied = serializers.BooleanField(required=False, read_only=True)

    class Meta:
        model = models.ConsoleServerPort
        fields = ['id', 'url', 'display_url', 'display', 'device', 'name', 'cable', '_occupied']


class NestedConsolePortSerializer(WritableNestedSerializer):
    device = NestedDeviceSerializer(read_only=True)
    _occupied = serializers.BooleanField(required=False, read_only=True)

    class Meta:
        model = models.ConsolePort
        fields = ['id', 'url', 'display_url', 'display', 'device', 'name', 'cable', '_occupied']


class NestedPowerOutletSerializer(WritableNestedSerializer):
    device = NestedDeviceSerializer(read_only=True)
    _occupied = serializers.BooleanField(required=False, read_only=True)

    class Meta:
        model = models.PowerOutlet
        fields = ['id', 'url', 'display_url', 'display', 'device', 'name', 'cable', '_occupied']


class NestedPowerPortSerializer(WritableNestedSerializer):
    device = NestedDeviceSerializer(read_only=True)
    _occupied = serializers.BooleanField(required=False, read_only=True)

    class Meta:
        model = models.PowerPort
        fields = ['id', 'url', 'display_url', 'display', 'device', 'name', 'cable', '_occupied']


class NestedRearPortSerializer(WritableNestedSerializer):
    device = NestedDeviceSerializer(read_only=True)
    _occupied = serializers.BooleanField(required=False, read_only=True)

    class Meta:
        model = models.RearPort
        fields = ['id', 'url', 'display_url', 'display', 'device', 'name', 'cable', '_occupied']


class NestedFrontPortSerializer(WritableNestedSerializer):
    device = NestedDeviceSerializer(read_only=True)
    _occupied = serializers.BooleanField(required=False, read_only=True)

    class Meta:
        model = models.FrontPort
        fields = ['id', 'url', 'display_url', 'display', 'device', 'name', 'cable', '_occupied']


class NestedInventoryItemSerializer(WritableNestedSerializer):
    device = NestedDeviceSerializer(read_only=True)
    _depth = serializers.IntegerField(source='level', read_only=True)

    class Meta:
        model = models.InventoryItem
        fields = ['id', 'url', 'display_url', 'display', 'device', 'name', '_depth']


@extend_schema_serializer(
    exclude_fields=('inventoryitem_count',),
)
class NestedInventoryItemRoleSerializer(WritableNestedSerializer):
    inventoryitem_count = RelatedObjectCountField('inventory_items')

    class Meta:
        model = models.InventoryItemRole
        fields = ['id', 'url', 'display_url', 'display', 'name', 'slug', 'inventoryitem_count']


#
# Cables
#

class NestedCableSerializer(WritableNestedSerializer):

    class Meta:
        model = models.Cable
        fields = ['id', 'url', 'display_url', 'display', 'label']


#
# Virtual chassis
#

@extend_schema_serializer(
    exclude_fields=('member_count',),
)
class NestedVirtualChassisSerializer(WritableNestedSerializer):
    master = NestedDeviceSerializer()
    member_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.VirtualChassis
        fields = ['id', 'url', 'display_url', 'display', 'name', 'master', 'member_count']


#
# Power panels/feeds
#

@extend_schema_serializer(
    exclude_fields=('powerfeed_count',),
)
class NestedPowerPanelSerializer(WritableNestedSerializer):
    powerfeed_count = RelatedObjectCountField('powerfeeds')

    class Meta:
        model = models.PowerPanel
        fields = ['id', 'url', 'display_url', 'display', 'name', 'powerfeed_count']


class NestedPowerFeedSerializer(WritableNestedSerializer):
    _occupied = serializers.BooleanField(required=False, read_only=True)

    class Meta:
        model = models.PowerFeed
        fields = ['id', 'url', 'display_url', 'display', 'name', 'cable', '_occupied']


class NestedVirtualDeviceContextSerializer(WritableNestedSerializer):
    device = NestedDeviceSerializer()

    class Meta:
        model = models.VirtualDeviceContext
        fields = ['id', 'url', 'display_url', 'display', 'name', 'identifier', 'device']
