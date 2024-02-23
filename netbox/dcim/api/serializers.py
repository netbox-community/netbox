import decimal

from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from timezone_field.rest_framework import TimeZoneSerializerField

from dcim.choices import *
from dcim.constants import *
from dcim.models import *
from extras.api.nested_serializers import NestedConfigTemplateSerializer
from ipam.api.nested_serializers import (
    NestedASNSerializer, NestedIPAddressSerializer, NestedVLANSerializer, NestedVRFSerializer,
)
from ipam.models import ASN, VLAN
from netbox.api.fields import ChoiceField, ContentTypeField, SerializedPKRelatedField
from netbox.api.serializers import (
    GenericObjectSerializer, NestedGroupModelSerializer, NetBoxModelSerializer, ValidatedModelSerializer,
    WritableNestedSerializer,
)
from netbox.config import ConfigItem
from netbox.constants import NESTED_SERIALIZER_PREFIX
from tenancy.api.nested_serializers import NestedTenantSerializer
from users.api.nested_serializers import NestedUserSerializer
from utilities.api import get_serializer_for_model
from virtualization.api.nested_serializers import NestedClusterSerializer
from vpn.api.nested_serializers import NestedL2VPNTerminationSerializer
from wireless.api.nested_serializers import NestedWirelessLANSerializer, NestedWirelessLinkSerializer
from wireless.choices import *
from wireless.models import WirelessLAN
from .nested_serializers import *


class CabledObjectSerializer(serializers.ModelSerializer):
    cable = NestedCableSerializer(read_only=True, allow_null=True)
    cable_end = serializers.CharField(read_only=True)
    link_peers_type = serializers.SerializerMethodField(read_only=True)
    link_peers = serializers.SerializerMethodField(read_only=True)
    _occupied = serializers.SerializerMethodField(read_only=True)

    @extend_schema_field(OpenApiTypes.STR)
    def get_link_peers_type(self, obj):
        """
        Return the type of the peer link terminations, or None.
        """
        if not obj.cable:
            return None

        if obj.link_peers:
            return f'{obj.link_peers[0]._meta.app_label}.{obj.link_peers[0]._meta.model_name}'

        return None

    @extend_schema_field(serializers.ListField)
    def get_link_peers(self, obj):
        """
        Return the appropriate serializer for the link termination model.
        """
        if not obj.link_peers:
            return []

        # Return serialized peer termination objects
        serializer = get_serializer_for_model(obj.link_peers[0], prefix=NESTED_SERIALIZER_PREFIX)
        context = {'request': self.context['request']}
        return serializer(obj.link_peers, context=context, many=True).data

    @extend_schema_field(serializers.BooleanField)
    def get__occupied(self, obj):
        return obj._occupied


class ConnectedEndpointsSerializer(serializers.ModelSerializer):
    """
    Legacy serializer for pre-v3.3 connections
    """
    connected_endpoints_type = serializers.SerializerMethodField(read_only=True)
    connected_endpoints = serializers.SerializerMethodField(read_only=True)
    connected_endpoints_reachable = serializers.SerializerMethodField(read_only=True)

    @extend_schema_field(OpenApiTypes.STR)
    def get_connected_endpoints_type(self, obj):
        if endpoints := obj.connected_endpoints:
            return f'{endpoints[0]._meta.app_label}.{endpoints[0]._meta.model_name}'

    @extend_schema_field(serializers.ListField)
    def get_connected_endpoints(self, obj):
        """
        Return the appropriate serializer for the type of connected object.
        """
        if endpoints := obj.connected_endpoints:
            serializer = get_serializer_for_model(endpoints[0], prefix=NESTED_SERIALIZER_PREFIX)
            context = {'request': self.context['request']}
            return serializer(endpoints, many=True, context=context).data

    @extend_schema_field(serializers.BooleanField)
    def get_connected_endpoints_reachable(self, obj):
        return obj._path and obj._path.is_complete and obj._path.is_active


#
# Regions/sites
#

class RegionSerializer(NestedGroupModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:region-detail')
    parent = NestedRegionSerializer(required=False, allow_null=True, default=None)
    site_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Region
        fields = [
            'id', 'url', 'display', 'name', 'slug', 'parent', 'description', 'tags', 'custom_fields', 'created',
            'last_updated', 'site_count', '_depth',
        ]


class SiteGroupSerializer(NestedGroupModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:sitegroup-detail')
    parent = NestedSiteGroupSerializer(required=False, allow_null=True, default=None)
    site_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = SiteGroup
        fields = [
            'id', 'url', 'display', 'name', 'slug', 'parent', 'description', 'tags', 'custom_fields', 'created',
            'last_updated', 'site_count', '_depth',
        ]


class SiteSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:site-detail')
    status = ChoiceField(choices=SiteStatusChoices, required=False)
    region = NestedRegionSerializer(required=False, allow_null=True)
    group = NestedSiteGroupSerializer(required=False, allow_null=True)
    tenant = NestedTenantSerializer(required=False, allow_null=True)
    time_zone = TimeZoneSerializerField(required=False, allow_null=True)
    asns = SerializedPKRelatedField(
        queryset=ASN.objects.all(),
        serializer=NestedASNSerializer,
        required=False,
        many=True
    )

    # Related object counts
    circuit_count = serializers.IntegerField(read_only=True)
    device_count = serializers.IntegerField(read_only=True)
    prefix_count = serializers.IntegerField(read_only=True)
    rack_count = serializers.IntegerField(read_only=True)
    virtualmachine_count = serializers.IntegerField(read_only=True)
    vlan_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Site
        fields = [
            'id', 'url', 'display', 'name', 'slug', 'status', 'region', 'group', 'tenant', 'facility', 'time_zone',
            'description', 'physical_address', 'shipping_address', 'latitude', 'longitude', 'comments', 'asns', 'tags',
            'custom_fields', 'created', 'last_updated', 'circuit_count', 'device_count', 'prefix_count', 'rack_count',
            'virtualmachine_count', 'vlan_count',
        ]


#
# Racks
#

class LocationSerializer(NestedGroupModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:location-detail')
    site = NestedSiteSerializer()
    parent = NestedLocationSerializer(required=False, allow_null=True)
    status = ChoiceField(choices=LocationStatusChoices, required=False)
    tenant = NestedTenantSerializer(required=False, allow_null=True)
    rack_count = serializers.IntegerField(read_only=True)
    device_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Location
        fields = [
            'id', 'url', 'display', 'name', 'slug', 'site', 'parent', 'status', 'tenant', 'description', 'tags',
            'custom_fields', 'created', 'last_updated', 'rack_count', 'device_count', '_depth',
        ]


class RackRoleSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:rackrole-detail')
    rack_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = RackRole
        fields = [
            'id', 'url', 'display', 'name', 'slug', 'color', 'description', 'tags', 'custom_fields', 'created',
            'last_updated', 'rack_count',
        ]


class RackSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:rack-detail')
    site = NestedSiteSerializer()
    location = NestedLocationSerializer(required=False, allow_null=True, default=None)
    tenant = NestedTenantSerializer(required=False, allow_null=True)
    status = ChoiceField(choices=RackStatusChoices, required=False)
    role = NestedRackRoleSerializer(required=False, allow_null=True)
    type = ChoiceField(choices=RackTypeChoices, allow_blank=True, required=False, allow_null=True)
    facility_id = serializers.CharField(max_length=50, allow_blank=True, allow_null=True, label=_('Facility ID'),
                                        default=None)
    width = ChoiceField(choices=RackWidthChoices, required=False)
    outer_unit = ChoiceField(choices=RackDimensionUnitChoices, allow_blank=True, required=False, allow_null=True)
    weight_unit = ChoiceField(choices=WeightUnitChoices, allow_blank=True, required=False, allow_null=True)
    device_count = serializers.IntegerField(read_only=True)
    powerfeed_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Rack
        fields = [
            'id', 'url', 'display', 'name', 'facility_id', 'site', 'location', 'tenant', 'status', 'role', 'serial',
            'asset_tag', 'type', 'width', 'u_height', 'starting_unit', 'weight', 'max_weight', 'weight_unit',
            'desc_units', 'outer_width', 'outer_depth', 'outer_unit', 'mounting_depth', 'description', 'comments',
            'tags', 'custom_fields', 'created', 'last_updated', 'device_count', 'powerfeed_count',
        ]


class RackUnitSerializer(serializers.Serializer):
    """
    A rack unit is an abstraction formed by the set (rack, position, face); it does not exist as a row in the database.
    """
    id = serializers.DecimalField(
        max_digits=4,
        decimal_places=1,
        read_only=True
    )
    name = serializers.CharField(read_only=True)
    face = ChoiceField(choices=DeviceFaceChoices, read_only=True)
    device = NestedDeviceSerializer(read_only=True)
    occupied = serializers.BooleanField(read_only=True)
    display = serializers.SerializerMethodField(read_only=True)

    @extend_schema_field(OpenApiTypes.STR)
    def get_display(self, obj):
        return obj['name']


class RackReservationSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:rackreservation-detail')
    rack = NestedRackSerializer()
    user = NestedUserSerializer()
    tenant = NestedTenantSerializer(required=False, allow_null=True)

    class Meta:
        model = RackReservation
        fields = [
            'id', 'url', 'display', 'rack', 'units', 'created', 'last_updated', 'user', 'tenant', 'description',
            'comments', 'tags', 'custom_fields',
        ]


class RackElevationDetailFilterSerializer(serializers.Serializer):
    q = serializers.CharField(
        required=False,
        default=None
    )
    face = serializers.ChoiceField(
        choices=DeviceFaceChoices,
        default=DeviceFaceChoices.FACE_FRONT
    )
    render = serializers.ChoiceField(
        choices=RackElevationDetailRenderChoices,
        default=RackElevationDetailRenderChoices.RENDER_JSON
    )
    unit_width = serializers.IntegerField(
        default=ConfigItem('RACK_ELEVATION_DEFAULT_UNIT_WIDTH')
    )
    unit_height = serializers.IntegerField(
        default=ConfigItem('RACK_ELEVATION_DEFAULT_UNIT_HEIGHT')
    )
    legend_width = serializers.IntegerField(
        default=RACK_ELEVATION_DEFAULT_LEGEND_WIDTH
    )
    margin_width = serializers.IntegerField(
        default=RACK_ELEVATION_DEFAULT_MARGIN_WIDTH
    )
    exclude = serializers.IntegerField(
        required=False,
        default=None
    )
    expand_devices = serializers.BooleanField(
        required=False,
        default=True
    )
    include_images = serializers.BooleanField(
        required=False,
        default=True
    )


#
# Device/module types
#

class ManufacturerSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:manufacturer-detail')
    devicetype_count = serializers.IntegerField(read_only=True)
    inventoryitem_count = serializers.IntegerField(read_only=True)
    platform_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Manufacturer
        fields = [
            'id', 'url', 'display', 'name', 'slug', 'description', 'tags', 'custom_fields', 'created', 'last_updated',
            'devicetype_count', 'inventoryitem_count', 'platform_count',
        ]


class DeviceTypeSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:devicetype-detail')
    manufacturer = NestedManufacturerSerializer()
    default_platform = NestedPlatformSerializer(required=False, allow_null=True)
    u_height = serializers.DecimalField(
        max_digits=4,
        decimal_places=1,
        label=_('Position (U)'),
        min_value=0,
        default=1.0
    )
    subdevice_role = ChoiceField(choices=SubdeviceRoleChoices, allow_blank=True, required=False, allow_null=True)
    airflow = ChoiceField(choices=DeviceAirflowChoices, allow_blank=True, required=False, allow_null=True)
    weight_unit = ChoiceField(choices=WeightUnitChoices, allow_blank=True, required=False, allow_null=True)
    device_count = serializers.IntegerField(read_only=True)
    front_image = serializers.URLField(allow_null=True, required=False)
    rear_image = serializers.URLField(allow_null=True, required=False)

    # Counter fields
    console_port_template_count = serializers.IntegerField(read_only=True)
    console_server_port_template_count = serializers.IntegerField(read_only=True)
    power_port_template_count = serializers.IntegerField(read_only=True)
    power_outlet_template_count = serializers.IntegerField(read_only=True)
    interface_template_count = serializers.IntegerField(read_only=True)
    front_port_template_count = serializers.IntegerField(read_only=True)
    rear_port_template_count = serializers.IntegerField(read_only=True)
    device_bay_template_count = serializers.IntegerField(read_only=True)
    module_bay_template_count = serializers.IntegerField(read_only=True)
    inventory_item_template_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = DeviceType
        fields = [
            'id', 'url', 'display', 'manufacturer', 'default_platform', 'model', 'slug', 'part_number', 'u_height',
            'exclude_from_utilization', 'is_full_depth', 'subdevice_role', 'airflow', 'weight', 'weight_unit',
            'front_image', 'rear_image', 'description', 'comments', 'tags', 'custom_fields', 'created', 'last_updated',
            'device_count', 'console_port_template_count', 'console_server_port_template_count', 'power_port_template_count',
            'power_outlet_template_count', 'interface_template_count', 'front_port_template_count',
            'rear_port_template_count', 'device_bay_template_count', 'module_bay_template_count',
            'inventory_item_template_count',
        ]


class ModuleTypeSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:moduletype-detail')
    manufacturer = NestedManufacturerSerializer()
    weight_unit = ChoiceField(choices=WeightUnitChoices, allow_blank=True, required=False, allow_null=True)

    class Meta:
        model = ModuleType
        fields = [
            'id', 'url', 'display', 'manufacturer', 'model', 'part_number', 'weight', 'weight_unit', 'description',
            'comments', 'tags', 'custom_fields', 'created', 'last_updated',
        ]


#
# Component templates
#

class ConsolePortTemplateSerializer(ValidatedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:consoleporttemplate-detail')
    device_type = NestedDeviceTypeSerializer(
        required=False,
        allow_null=True,
        default=None
    )
    module_type = NestedModuleTypeSerializer(
        required=False,
        allow_null=True,
        default=None
    )
    type = ChoiceField(
        choices=ConsolePortTypeChoices,
        allow_blank=True,
        required=False
    )

    class Meta:
        model = ConsolePortTemplate
        fields = [
            'id', 'url', 'display', 'device_type', 'module_type', 'name', 'label', 'type', 'description', 'created',
            'last_updated',
        ]


class ConsoleServerPortTemplateSerializer(ValidatedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:consoleserverporttemplate-detail')
    device_type = NestedDeviceTypeSerializer(
        required=False,
        allow_null=True,
        default=None
    )
    module_type = NestedModuleTypeSerializer(
        required=False,
        allow_null=True,
        default=None
    )
    type = ChoiceField(
        choices=ConsolePortTypeChoices,
        allow_blank=True,
        required=False
    )

    class Meta:
        model = ConsoleServerPortTemplate
        fields = [
            'id', 'url', 'display', 'device_type', 'module_type', 'name', 'label', 'type', 'description', 'created',
            'last_updated',
        ]


class PowerPortTemplateSerializer(ValidatedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:powerporttemplate-detail')
    device_type = NestedDeviceTypeSerializer(
        required=False,
        allow_null=True,
        default=None
    )
    module_type = NestedModuleTypeSerializer(
        required=False,
        allow_null=True,
        default=None
    )
    type = ChoiceField(
        choices=PowerPortTypeChoices,
        allow_blank=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = PowerPortTemplate
        fields = [
            'id', 'url', 'display', 'device_type', 'module_type', 'name', 'label', 'type', 'maximum_draw',
            'allocated_draw', 'description', 'created', 'last_updated',
        ]


class PowerOutletTemplateSerializer(ValidatedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:poweroutlettemplate-detail')
    device_type = NestedDeviceTypeSerializer(
        required=False,
        allow_null=True,
        default=None
    )
    module_type = NestedModuleTypeSerializer(
        required=False,
        allow_null=True,
        default=None
    )
    type = ChoiceField(
        choices=PowerOutletTypeChoices,
        allow_blank=True,
        required=False,
        allow_null=True
    )
    power_port = NestedPowerPortTemplateSerializer(
        required=False,
        allow_null=True
    )
    feed_leg = ChoiceField(
        choices=PowerOutletFeedLegChoices,
        allow_blank=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = PowerOutletTemplate
        fields = [
            'id', 'url', 'display', 'device_type', 'module_type', 'name', 'label', 'type', 'power_port', 'feed_leg',
            'description', 'created', 'last_updated',
        ]


class InterfaceTemplateSerializer(ValidatedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:interfacetemplate-detail')
    device_type = NestedDeviceTypeSerializer(
        required=False,
        allow_null=True,
        default=None
    )
    module_type = NestedModuleTypeSerializer(
        required=False,
        allow_null=True,
        default=None
    )
    type = ChoiceField(choices=InterfaceTypeChoices)
    bridge = NestedInterfaceTemplateSerializer(
        required=False,
        allow_null=True
    )
    poe_mode = ChoiceField(
        choices=InterfacePoEModeChoices,
        required=False,
        allow_blank=True,
        allow_null=True
    )
    poe_type = ChoiceField(
        choices=InterfacePoETypeChoices,
        required=False,
        allow_blank=True,
        allow_null=True
    )
    rf_role = ChoiceField(
        choices=WirelessRoleChoices,
        required=False,
        allow_blank=True,
        allow_null=True
    )

    class Meta:
        model = InterfaceTemplate
        fields = [
            'id', 'url', 'display', 'device_type', 'module_type', 'name', 'label', 'type', 'enabled', 'mgmt_only',
            'description', 'bridge', 'poe_mode', 'poe_type', 'rf_role', 'created', 'last_updated',
        ]


class RearPortTemplateSerializer(ValidatedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:rearporttemplate-detail')
    device_type = NestedDeviceTypeSerializer(
        required=False,
        allow_null=True,
        default=None
    )
    module_type = NestedModuleTypeSerializer(
        required=False,
        allow_null=True,
        default=None
    )
    type = ChoiceField(choices=PortTypeChoices)

    class Meta:
        model = RearPortTemplate
        fields = [
            'id', 'url', 'display', 'device_type', 'module_type', 'name', 'label', 'type', 'color', 'positions',
            'description', 'created', 'last_updated',
        ]


class FrontPortTemplateSerializer(ValidatedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:frontporttemplate-detail')
    device_type = NestedDeviceTypeSerializer(
        required=False,
        allow_null=True,
        default=None
    )
    module_type = NestedModuleTypeSerializer(
        required=False,
        allow_null=True,
        default=None
    )
    type = ChoiceField(choices=PortTypeChoices)
    rear_port = NestedRearPortTemplateSerializer()

    class Meta:
        model = FrontPortTemplate
        fields = [
            'id', 'url', 'display', 'device_type', 'module_type', 'name', 'label', 'type', 'color', 'rear_port',
            'rear_port_position', 'description', 'created', 'last_updated',
        ]


class ModuleBayTemplateSerializer(ValidatedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:modulebaytemplate-detail')
    device_type = NestedDeviceTypeSerializer()

    class Meta:
        model = ModuleBayTemplate
        fields = [
            'id', 'url', 'display', 'device_type', 'name', 'label', 'position', 'description', 'created',
            'last_updated',
        ]


class DeviceBayTemplateSerializer(ValidatedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:devicebaytemplate-detail')
    device_type = NestedDeviceTypeSerializer()

    class Meta:
        model = DeviceBayTemplate
        fields = ['id', 'url', 'display', 'device_type', 'name', 'label', 'description', 'created', 'last_updated']


class InventoryItemTemplateSerializer(ValidatedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:inventoryitemtemplate-detail')
    device_type = NestedDeviceTypeSerializer()
    parent = serializers.PrimaryKeyRelatedField(
        queryset=InventoryItemTemplate.objects.all(),
        allow_null=True,
        default=None
    )
    role = NestedInventoryItemRoleSerializer(required=False, allow_null=True)
    manufacturer = NestedManufacturerSerializer(required=False, allow_null=True, default=None)
    component_type = ContentTypeField(
        queryset=ContentType.objects.filter(MODULAR_COMPONENT_TEMPLATE_MODELS),
        required=False,
        allow_null=True
    )
    component = serializers.SerializerMethodField(read_only=True)
    _depth = serializers.IntegerField(source='level', read_only=True)

    class Meta:
        model = InventoryItemTemplate
        fields = [
            'id', 'url', 'display', 'device_type', 'parent', 'name', 'label', 'role', 'manufacturer', 'part_id',
            'description', 'component_type', 'component_id', 'component', 'created', 'last_updated', '_depth',
        ]

    @extend_schema_field(serializers.JSONField(allow_null=True))
    def get_component(self, obj):
        if obj.component is None:
            return None
        serializer = get_serializer_for_model(obj.component, prefix=NESTED_SERIALIZER_PREFIX)
        context = {'request': self.context['request']}
        return serializer(obj.component, context=context).data


#
# Devices
#

class DeviceRoleSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:devicerole-detail')
    config_template = NestedConfigTemplateSerializer(required=False, allow_null=True, default=None)
    device_count = serializers.IntegerField(read_only=True)
    virtualmachine_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = DeviceRole
        fields = [
            'id', 'url', 'display', 'name', 'slug', 'color', 'vm_role', 'config_template', 'description', 'tags',
            'custom_fields', 'created', 'last_updated', 'device_count', 'virtualmachine_count',
        ]


class PlatformSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:platform-detail')
    manufacturer = NestedManufacturerSerializer(required=False, allow_null=True)
    config_template = NestedConfigTemplateSerializer(required=False, allow_null=True, default=None)
    device_count = serializers.IntegerField(read_only=True)
    virtualmachine_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Platform
        fields = [
            'id', 'url', 'display', 'name', 'slug', 'manufacturer', 'config_template', 'description', 'tags',
            'custom_fields', 'created', 'last_updated', 'device_count', 'virtualmachine_count',
        ]


class DeviceSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:device-detail')
    device_type = NestedDeviceTypeSerializer()
    role = NestedDeviceRoleSerializer()
    device_role = NestedDeviceRoleSerializer(read_only=True, help_text='Deprecated in v3.6 in favor of `role`.')
    tenant = NestedTenantSerializer(required=False, allow_null=True, default=None)
    platform = NestedPlatformSerializer(required=False, allow_null=True)
    site = NestedSiteSerializer()
    location = NestedLocationSerializer(required=False, allow_null=True, default=None)
    rack = NestedRackSerializer(required=False, allow_null=True, default=None)
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
    primary_ip = NestedIPAddressSerializer(read_only=True)
    primary_ip4 = NestedIPAddressSerializer(required=False, allow_null=True)
    primary_ip6 = NestedIPAddressSerializer(required=False, allow_null=True)
    oob_ip = NestedIPAddressSerializer(required=False, allow_null=True)
    parent_device = serializers.SerializerMethodField()
    cluster = NestedClusterSerializer(required=False, allow_null=True)
    virtual_chassis = NestedVirtualChassisSerializer(required=False, allow_null=True, default=None)
    vc_position = serializers.IntegerField(allow_null=True, max_value=255, min_value=0, default=None)
    config_template = NestedConfigTemplateSerializer(required=False, allow_null=True, default=None)

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
            'id', 'url', 'display', 'name', 'device_type', 'role', 'device_role', 'tenant', 'platform', 'serial',
            'asset_tag', 'site', 'location', 'rack', 'position', 'face', 'latitude', 'longitude', 'parent_device',
            'status', 'airflow', 'primary_ip', 'primary_ip4', 'primary_ip6', 'oob_ip', 'cluster', 'virtual_chassis',
            'vc_position', 'vc_priority', 'description', 'comments', 'config_template', 'local_context_data', 'tags',
            'custom_fields', 'created', 'last_updated', 'console_port_count', 'console_server_port_count',
            'power_port_count', 'power_outlet_count', 'interface_count', 'front_port_count', 'rear_port_count',
            'device_bay_count', 'module_bay_count', 'inventory_item_count',
        ]

    @extend_schema_field(NestedDeviceSerializer)
    def get_parent_device(self, obj):
        try:
            device_bay = obj.parent_bay
        except DeviceBay.DoesNotExist:
            return None
        context = {'request': self.context['request']}
        data = NestedDeviceSerializer(instance=device_bay.device, context=context).data
        data['device_bay'] = NestedDeviceBaySerializer(instance=device_bay, context=context).data
        return data

    def get_device_role(self, obj):
        return obj.role


class DeviceWithConfigContextSerializer(DeviceSerializer):
    config_context = serializers.SerializerMethodField(read_only=True)

    class Meta(DeviceSerializer.Meta):
        fields = [
            'id', 'url', 'display', 'name', 'device_type', 'role', 'device_role', 'tenant', 'platform', 'serial',
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
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:virtualdevicecontext-detail')
    device = NestedDeviceSerializer()
    tenant = NestedTenantSerializer(required=False, allow_null=True, default=None)
    primary_ip = NestedIPAddressSerializer(read_only=True, allow_null=True)
    primary_ip4 = NestedIPAddressSerializer(required=False, allow_null=True)
    primary_ip6 = NestedIPAddressSerializer(required=False, allow_null=True)
    status = ChoiceField(choices=VirtualDeviceContextStatusChoices)

    # Related object counts
    interface_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = VirtualDeviceContext
        fields = [
            'id', 'url', 'display', 'name', 'device', 'identifier', 'tenant', 'primary_ip', 'primary_ip4',
            'primary_ip6', 'status', 'description', 'comments', 'tags', 'custom_fields', 'created', 'last_updated',
            'interface_count',
        ]


class ModuleSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:module-detail')
    device = NestedDeviceSerializer()
    module_bay = NestedModuleBaySerializer()
    module_type = NestedModuleTypeSerializer()
    status = ChoiceField(choices=ModuleStatusChoices, required=False)

    class Meta:
        model = Module
        fields = [
            'id', 'url', 'display', 'device', 'module_bay', 'module_type', 'status', 'serial', 'asset_tag',
            'description', 'comments', 'tags', 'custom_fields', 'created', 'last_updated',
        ]


#
# Device components
#

class ConsoleServerPortSerializer(NetBoxModelSerializer, CabledObjectSerializer, ConnectedEndpointsSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:consoleserverport-detail')
    device = NestedDeviceSerializer()
    module = ComponentNestedModuleSerializer(
        required=False,
        allow_null=True
    )
    type = ChoiceField(
        choices=ConsolePortTypeChoices,
        allow_blank=True,
        required=False
    )
    speed = ChoiceField(
        choices=ConsolePortSpeedChoices,
        allow_null=True,
        required=False
    )

    class Meta:
        model = ConsoleServerPort
        fields = [
            'id', 'url', 'display', 'device', 'module', 'name', 'label', 'type', 'speed', 'description',
            'mark_connected', 'cable', 'cable_end', 'link_peers', 'link_peers_type', 'connected_endpoints',
            'connected_endpoints_type', 'connected_endpoints_reachable', 'tags', 'custom_fields', 'created',
            'last_updated', '_occupied',
        ]


class ConsolePortSerializer(NetBoxModelSerializer, CabledObjectSerializer, ConnectedEndpointsSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:consoleport-detail')
    device = NestedDeviceSerializer()
    module = ComponentNestedModuleSerializer(
        required=False,
        allow_null=True
    )
    type = ChoiceField(
        choices=ConsolePortTypeChoices,
        allow_blank=True,
        required=False
    )
    speed = ChoiceField(
        choices=ConsolePortSpeedChoices,
        allow_null=True,
        required=False
    )

    class Meta:
        model = ConsolePort
        fields = [
            'id', 'url', 'display', 'device', 'module', 'name', 'label', 'type', 'speed', 'description',
            'mark_connected', 'cable', 'cable_end', 'link_peers', 'link_peers_type', 'connected_endpoints',
            'connected_endpoints_type', 'connected_endpoints_reachable', 'tags', 'custom_fields', 'created',
            'last_updated', '_occupied',
        ]


class PowerOutletSerializer(NetBoxModelSerializer, CabledObjectSerializer, ConnectedEndpointsSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:poweroutlet-detail')
    device = NestedDeviceSerializer()
    module = ComponentNestedModuleSerializer(
        required=False,
        allow_null=True
    )
    type = ChoiceField(
        choices=PowerOutletTypeChoices,
        allow_blank=True,
        required=False,
        allow_null=True
    )
    power_port = NestedPowerPortSerializer(
        required=False,
        allow_null=True
    )
    feed_leg = ChoiceField(
        choices=PowerOutletFeedLegChoices,
        allow_blank=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = PowerOutlet
        fields = [
            'id', 'url', 'display', 'device', 'module', 'name', 'label', 'type', 'power_port', 'feed_leg',
            'description', 'mark_connected', 'cable', 'cable_end', 'link_peers', 'link_peers_type',
            'connected_endpoints', 'connected_endpoints_type', 'connected_endpoints_reachable', 'tags', 'custom_fields',
            'created', 'last_updated', '_occupied',
        ]


class PowerPortSerializer(NetBoxModelSerializer, CabledObjectSerializer, ConnectedEndpointsSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:powerport-detail')
    device = NestedDeviceSerializer()
    module = ComponentNestedModuleSerializer(
        required=False,
        allow_null=True
    )
    type = ChoiceField(
        choices=PowerPortTypeChoices,
        allow_blank=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = PowerPort
        fields = [
            'id', 'url', 'display', 'device', 'module', 'name', 'label', 'type', 'maximum_draw', 'allocated_draw',
            'description', 'mark_connected', 'cable', 'cable_end', 'link_peers', 'link_peers_type',
            'connected_endpoints', 'connected_endpoints_type', 'connected_endpoints_reachable', 'tags', 'custom_fields',
            'created', 'last_updated', '_occupied',
        ]


class InterfaceSerializer(NetBoxModelSerializer, CabledObjectSerializer, ConnectedEndpointsSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:interface-detail')
    device = NestedDeviceSerializer()
    vdcs = SerializedPKRelatedField(
        queryset=VirtualDeviceContext.objects.all(),
        serializer=NestedVirtualDeviceContextSerializer,
        required=False,
        many=True
    )
    module = ComponentNestedModuleSerializer(
        required=False,
        allow_null=True
    )
    type = ChoiceField(choices=InterfaceTypeChoices)
    parent = NestedInterfaceSerializer(required=False, allow_null=True)
    bridge = NestedInterfaceSerializer(required=False, allow_null=True)
    lag = NestedInterfaceSerializer(required=False, allow_null=True)
    mode = ChoiceField(choices=InterfaceModeChoices, required=False, allow_blank=True)
    duplex = ChoiceField(choices=InterfaceDuplexChoices, required=False, allow_blank=True, allow_null=True)
    rf_role = ChoiceField(choices=WirelessRoleChoices, required=False, allow_blank=True)
    rf_channel = ChoiceField(choices=WirelessChannelChoices, required=False, allow_blank=True)
    poe_mode = ChoiceField(choices=InterfacePoEModeChoices, required=False, allow_blank=True)
    poe_type = ChoiceField(choices=InterfacePoETypeChoices, required=False, allow_blank=True)
    untagged_vlan = NestedVLANSerializer(required=False, allow_null=True)
    tagged_vlans = SerializedPKRelatedField(
        queryset=VLAN.objects.all(),
        serializer=NestedVLANSerializer,
        required=False,
        many=True
    )
    vrf = NestedVRFSerializer(required=False, allow_null=True)
    l2vpn_termination = NestedL2VPNTerminationSerializer(read_only=True, allow_null=True)
    wireless_link = NestedWirelessLinkSerializer(read_only=True, allow_null=True)
    wireless_lans = SerializedPKRelatedField(
        queryset=WirelessLAN.objects.all(),
        serializer=NestedWirelessLANSerializer,
        required=False,
        many=True
    )
    count_ipaddresses = serializers.IntegerField(read_only=True)
    count_fhrp_groups = serializers.IntegerField(read_only=True)
    mac_address = serializers.CharField(
        required=False,
        default=None,
        allow_blank=True,
        allow_null=True
    )
    wwn = serializers.CharField(required=False, default=None, allow_blank=True, allow_null=True)

    class Meta:
        model = Interface
        fields = [
            'id', 'url', 'display', 'device', 'vdcs', 'module', 'name', 'label', 'type', 'enabled', 'parent', 'bridge',
            'lag', 'mtu', 'mac_address', 'speed', 'duplex', 'wwn', 'mgmt_only', 'description', 'mode', 'rf_role',
            'rf_channel', 'poe_mode', 'poe_type', 'rf_channel_frequency', 'rf_channel_width', 'tx_power',
            'untagged_vlan', 'tagged_vlans', 'mark_connected', 'cable', 'cable_end', 'wireless_link', 'link_peers',
            'link_peers_type', 'wireless_lans', 'vrf', 'l2vpn_termination', 'connected_endpoints',
            'connected_endpoints_type', 'connected_endpoints_reachable', 'tags', 'custom_fields', 'created',
            'last_updated', 'count_ipaddresses', 'count_fhrp_groups', '_occupied',
        ]

    def validate(self, data):

        # Validate many-to-many VLAN assignments
        device = self.instance.device if self.instance else data.get('device')
        for vlan in data.get('tagged_vlans', []):
            if vlan.site not in [device.site, None]:
                raise serializers.ValidationError({
                    'tagged_vlans': f"VLAN {vlan} must belong to the same site as the interface's parent device, or "
                                    f"it must be global."
                })

        return super().validate(data)


class RearPortSerializer(NetBoxModelSerializer, CabledObjectSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:rearport-detail')
    device = NestedDeviceSerializer()
    module = ComponentNestedModuleSerializer(
        required=False,
        allow_null=True
    )
    type = ChoiceField(choices=PortTypeChoices)

    class Meta:
        model = RearPort
        fields = [
            'id', 'url', 'display', 'device', 'module', 'name', 'label', 'type', 'color', 'positions', 'description',
            'mark_connected', 'cable', 'cable_end', 'link_peers', 'link_peers_type', 'tags', 'custom_fields', 'created',
            'last_updated', '_occupied',
        ]


class FrontPortRearPortSerializer(WritableNestedSerializer):
    """
    NestedRearPortSerializer but with parent device omitted (since front and rear ports must belong to same device)
    """
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:rearport-detail')

    class Meta:
        model = RearPort
        fields = ['id', 'url', 'display', 'name', 'label', 'description']


class FrontPortSerializer(NetBoxModelSerializer, CabledObjectSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:frontport-detail')
    device = NestedDeviceSerializer()
    module = ComponentNestedModuleSerializer(
        required=False,
        allow_null=True
    )
    type = ChoiceField(choices=PortTypeChoices)
    rear_port = FrontPortRearPortSerializer()

    class Meta:
        model = FrontPort
        fields = [
            'id', 'url', 'display', 'device', 'module', 'name', 'label', 'type', 'color', 'rear_port',
            'rear_port_position', 'description', 'mark_connected', 'cable', 'cable_end', 'link_peers',
            'link_peers_type', 'tags', 'custom_fields', 'created', 'last_updated', '_occupied',
        ]


class ModuleBaySerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:modulebay-detail')
    device = NestedDeviceSerializer()
    installed_module = ModuleBayNestedModuleSerializer(required=False, allow_null=True)

    class Meta:
        model = ModuleBay
        fields = [
            'id', 'url', 'display', 'device', 'name', 'installed_module', 'label', 'position', 'description', 'tags',
            'custom_fields', 'created', 'last_updated',
        ]


class DeviceBaySerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:devicebay-detail')
    device = NestedDeviceSerializer()
    installed_device = NestedDeviceSerializer(required=False, allow_null=True)

    class Meta:
        model = DeviceBay
        fields = [
            'id', 'url', 'display', 'device', 'name', 'label', 'description', 'installed_device', 'tags',
            'custom_fields', 'created', 'last_updated',
        ]


class InventoryItemSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:inventoryitem-detail')
    device = NestedDeviceSerializer()
    parent = serializers.PrimaryKeyRelatedField(queryset=InventoryItem.objects.all(), allow_null=True, default=None)
    role = NestedInventoryItemRoleSerializer(required=False, allow_null=True)
    manufacturer = NestedManufacturerSerializer(required=False, allow_null=True, default=None)
    component_type = ContentTypeField(
        queryset=ContentType.objects.filter(MODULAR_COMPONENT_MODELS),
        required=False,
        allow_null=True
    )
    component = serializers.SerializerMethodField(read_only=True)
    _depth = serializers.IntegerField(source='level', read_only=True)

    class Meta:
        model = InventoryItem
        fields = [
            'id', 'url', 'display', 'device', 'parent', 'name', 'label', 'role', 'manufacturer', 'part_id', 'serial',
            'asset_tag', 'discovered', 'description', 'component_type', 'component_id', 'component', 'tags',
            'custom_fields', 'created', 'last_updated', '_depth',
        ]

    @extend_schema_field(serializers.JSONField(allow_null=True))
    def get_component(self, obj):
        if obj.component is None:
            return None
        serializer = get_serializer_for_model(obj.component, prefix=NESTED_SERIALIZER_PREFIX)
        context = {'request': self.context['request']}
        return serializer(obj.component, context=context).data


#
# Device component roles
#

class InventoryItemRoleSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:inventoryitemrole-detail')
    inventoryitem_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = InventoryItemRole
        fields = [
            'id', 'url', 'display', 'name', 'slug', 'color', 'description', 'tags', 'custom_fields', 'created',
            'last_updated', 'inventoryitem_count',
        ]


#
# Cables
#

class CableSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:cable-detail')
    a_terminations = GenericObjectSerializer(many=True, required=False)
    b_terminations = GenericObjectSerializer(many=True, required=False)
    status = ChoiceField(choices=LinkStatusChoices, required=False)
    tenant = NestedTenantSerializer(required=False, allow_null=True)
    length_unit = ChoiceField(choices=CableLengthUnitChoices, allow_blank=True, required=False, allow_null=True)

    class Meta:
        model = Cable
        fields = [
            'id', 'url', 'display', 'type', 'a_terminations', 'b_terminations', 'status', 'tenant', 'label', 'color',
            'length', 'length_unit', 'description', 'comments', 'tags', 'custom_fields', 'created', 'last_updated',
        ]


class TracedCableSerializer(serializers.ModelSerializer):
    """
    Used only while tracing a cable path.
    """
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:cable-detail')

    class Meta:
        model = Cable
        fields = [
            'id', 'url', 'type', 'status', 'label', 'color', 'length', 'length_unit', 'description',
        ]


class CableTerminationSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:cabletermination-detail')
    termination_type = ContentTypeField(
        queryset=ContentType.objects.filter(CABLE_TERMINATION_MODELS)
    )
    termination = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CableTermination
        fields = [
            'id', 'url', 'display', 'cable', 'cable_end', 'termination_type', 'termination_id', 'termination',
            'created', 'last_updated',
        ]

    @extend_schema_field(serializers.JSONField(allow_null=True))
    def get_termination(self, obj):
        serializer = get_serializer_for_model(obj.termination, prefix=NESTED_SERIALIZER_PREFIX)
        context = {'request': self.context['request']}
        return serializer(obj.termination, context=context).data


class CablePathSerializer(serializers.ModelSerializer):
    path = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CablePath
        fields = ['id', 'path', 'is_active', 'is_complete', 'is_split']

    @extend_schema_field(serializers.ListField)
    def get_path(self, obj):
        ret = []
        for nodes in obj.path_objects:
            serializer = get_serializer_for_model(nodes[0], prefix=NESTED_SERIALIZER_PREFIX)
            context = {'request': self.context['request']}
            ret.append(serializer(nodes, context=context, many=True).data)
        return ret


#
# Virtual chassis
#

class VirtualChassisSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:virtualchassis-detail')
    master = NestedDeviceSerializer(required=False, allow_null=True, default=None)

    # Counter fields
    member_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = VirtualChassis
        fields = [
            'id', 'url', 'display', 'name', 'domain', 'master', 'description', 'comments', 'tags', 'custom_fields',
            'created', 'last_updated', 'member_count',
        ]


#
# Power panels
#

class PowerPanelSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:powerpanel-detail')
    site = NestedSiteSerializer()
    location = NestedLocationSerializer(
        required=False,
        allow_null=True,
        default=None
    )
    powerfeed_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = PowerPanel
        fields = [
            'id', 'url', 'display', 'site', 'location', 'name', 'description', 'comments', 'tags', 'custom_fields',
            'powerfeed_count', 'created', 'last_updated',
        ]


class PowerFeedSerializer(NetBoxModelSerializer, CabledObjectSerializer, ConnectedEndpointsSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:powerfeed-detail')
    power_panel = NestedPowerPanelSerializer()
    rack = NestedRackSerializer(
        required=False,
        allow_null=True,
        default=None
    )
    type = ChoiceField(
        choices=PowerFeedTypeChoices,
        default=lambda: PowerFeedTypeChoices.TYPE_PRIMARY,
    )
    status = ChoiceField(
        choices=PowerFeedStatusChoices,
        default=lambda: PowerFeedStatusChoices.STATUS_ACTIVE,
    )
    supply = ChoiceField(
        choices=PowerFeedSupplyChoices,
        default=lambda: PowerFeedSupplyChoices.SUPPLY_AC,
    )
    phase = ChoiceField(
        choices=PowerFeedPhaseChoices,
        default=lambda: PowerFeedPhaseChoices.PHASE_SINGLE,
    )
    tenant = NestedTenantSerializer(
        required=False,
        allow_null=True
    )

    class Meta:
        model = PowerFeed
        fields = [
            'id', 'url', 'display', 'power_panel', 'rack', 'name', 'status', 'type', 'supply', 'phase', 'voltage',
            'amperage', 'max_utilization', 'mark_connected', 'cable', 'cable_end', 'link_peers', 'link_peers_type',
            'connected_endpoints', 'connected_endpoints_type', 'connected_endpoints_reachable', 'description',
            'tenant', 'comments', 'tags', 'custom_fields', 'created', 'last_updated', '_occupied',
        ]
