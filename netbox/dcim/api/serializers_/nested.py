from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers

from netbox.api.serializers import WritableNestedSerializer
from dcim import models

__all__ = (
    'NestedDeviceBaySerializer',
    'NestedDeviceSerializer',
    'NestedInterfaceSerializer',
    'NestedInterfaceTemplateSerializer',
    'NestedLocationSerializer',
    'NestedModuleBaySerializer',
    'NestedRegionSerializer',
    'NestedSiteGroupSerializer',
)


@extend_schema_serializer(
    exclude_fields=('site_count',),
)
class NestedRegionSerializer(WritableNestedSerializer):
    site_count = serializers.IntegerField(read_only=True)
    _depth = serializers.IntegerField(source='level', read_only=True)

    class Meta:
        model = models.Region
        fields = ['id', 'url', 'display_url', 'display', 'name', 'slug', 'site_count', '_depth']


@extend_schema_serializer(
    exclude_fields=('site_count',),
)
class NestedSiteGroupSerializer(WritableNestedSerializer):
    site_count = serializers.IntegerField(read_only=True)
    _depth = serializers.IntegerField(source='level', read_only=True)

    class Meta:
        model = models.SiteGroup
        fields = ['id', 'url', 'display_url', 'display', 'name', 'slug', 'site_count', '_depth']


@extend_schema_serializer(
    exclude_fields=('rack_count',),
)
class NestedLocationSerializer(WritableNestedSerializer):
    rack_count = serializers.IntegerField(read_only=True)
    _depth = serializers.IntegerField(source='level', read_only=True)

    class Meta:
        model = models.Location
        fields = ['id', 'url', 'display_url', 'display', 'name', 'slug', 'rack_count', '_depth']


class NestedDeviceSerializer(WritableNestedSerializer):

    class Meta:
        model = models.Device
        fields = ['id', 'url', 'display_url', 'display', 'name']


class NestedInterfaceSerializer(WritableNestedSerializer):
    device = NestedDeviceSerializer(read_only=True)
    _occupied = serializers.BooleanField(required=False, read_only=True)

    class Meta:
        model = models.Interface
        fields = ['id', 'url', 'display_url', 'display', 'device', 'name', 'cable', '_occupied']


class NestedInterfaceTemplateSerializer(WritableNestedSerializer):

    class Meta:
        model = models.InterfaceTemplate
        fields = ['id', 'url', 'display_url', 'display', 'name']


class NestedDeviceBaySerializer(WritableNestedSerializer):
    device = NestedDeviceSerializer(read_only=True)

    class Meta:
        model = models.DeviceBay
        fields = ['id', 'url', 'display_url', 'display', 'device', 'name']


class ModuleBayNestedModuleSerializer(WritableNestedSerializer):

    class Meta:
        model = models.Module
        fields = ['id', 'url', 'display_url', 'display', 'serial']


class NestedModuleBaySerializer(WritableNestedSerializer):

    class Meta:
        model = models.ModuleBay
        fields = ['id', 'url', 'display_url', 'display', 'name']
