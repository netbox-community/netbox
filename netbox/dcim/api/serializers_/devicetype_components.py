from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from dcim.choices import *
from dcim.constants import *
from dcim.models import (
    ConsolePortTemplate,
    ConsoleServerPortTemplate,
    DeviceBayTemplate,
    FrontPortTemplate,
    InterfaceTemplate,
    InventoryItemTemplate,
    ModuleBayTemplate,
    PortTemplateMapping,
    PowerOutletTemplate,
    PowerPortTemplate,
    RearPortTemplate,
)
from netbox.api.fields import ChoiceField, ContentTypeField
from netbox.api.gfk_fields import GFKSerializerField
from netbox.api.serializers import ChangeLogMessageSerializer, ValidatedModelSerializer
from wireless.choices import *

from .base import PortSerializer
from .devicetypes import DeviceTypeSerializer, ModuleTypeSerializer
from .manufacturers import ManufacturerSerializer
from .nested import NestedInterfaceTemplateSerializer
from .roles import InventoryItemRoleSerializer

__all__ = (
    'ConsolePortTemplateSerializer',
    'ConsoleServerPortTemplateSerializer',
    'DeviceBayTemplateSerializer',
    'FrontPortTemplateSerializer',
    'InterfaceTemplateSerializer',
    'InventoryItemTemplateSerializer',
    'ModuleBayTemplateSerializer',
    'PowerOutletTemplateSerializer',
    'PowerPortTemplateSerializer',
    'RearPortTemplateSerializer',
)


class ComponentTemplateSerializer(ChangeLogMessageSerializer, ValidatedModelSerializer):
    pass


class ConsolePortTemplateSerializer(ComponentTemplateSerializer):
    device_type = DeviceTypeSerializer(
        nested=True,
        required=False,
        allow_null=True,
        default=None
    )
    module_type = ModuleTypeSerializer(
        nested=True,
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
            'id', 'url', 'display', 'device_type', 'module_type', 'name', 'label', 'type',
            'description', 'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'description')


class ConsoleServerPortTemplateSerializer(ComponentTemplateSerializer):
    device_type = DeviceTypeSerializer(
        nested=True,
        required=False,
        allow_null=True,
        default=None
    )
    module_type = ModuleTypeSerializer(
        nested=True,
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
            'id', 'url', 'display', 'device_type', 'module_type', 'name', 'label', 'type',
            'description', 'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'description')


class PowerPortTemplateSerializer(ComponentTemplateSerializer):
    device_type = DeviceTypeSerializer(
        nested=True,
        required=False,
        allow_null=True,
        default=None
    )
    module_type = ModuleTypeSerializer(
        nested=True,
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
            'id', 'url', 'display', 'device_type', 'module_type', 'name', 'label', 'type',
            'maximum_draw', 'allocated_draw', 'description', 'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'description')


class PowerOutletTemplateSerializer(ComponentTemplateSerializer):
    device_type = DeviceTypeSerializer(
        nested=True,
        required=False,
        allow_null=True,
        default=None
    )
    module_type = ModuleTypeSerializer(
        nested=True,
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
    power_port = PowerPortTemplateSerializer(
        nested=True,
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
            'id', 'url', 'display', 'device_type', 'module_type', 'name', 'label', 'type',
            'color', 'power_port', 'feed_leg', 'description', 'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'description')


class InterfaceTemplateSerializer(ComponentTemplateSerializer):
    device_type = DeviceTypeSerializer(
        nested=True,
        required=False,
        allow_null=True,
        default=None
    )
    module_type = ModuleTypeSerializer(
        nested=True,
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
            'id', 'url', 'display', 'device_type', 'module_type', 'name', 'label', 'type', 'enabled',
            'mgmt_only', 'description', 'bridge', 'poe_mode', 'poe_type', 'rf_role', 'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'description')


class RearPortTemplateMappingSerializer(serializers.ModelSerializer):
    position = serializers.IntegerField(
        source='rear_port_position'
    )
    front_port = serializers.PrimaryKeyRelatedField(
        queryset=FrontPortTemplate.objects.all(),
    )

    class Meta:
        model = PortTemplateMapping
        fields = ('position', 'front_port', 'front_port_position')


class RearPortTemplateSerializer(ComponentTemplateSerializer, PortSerializer):
    device_type = DeviceTypeSerializer(
        required=False,
        nested=True,
        allow_null=True,
        default=None
    )
    module_type = ModuleTypeSerializer(
        nested=True,
        required=False,
        allow_null=True,
        default=None
    )
    type = ChoiceField(choices=PortTypeChoices)
    front_ports = RearPortTemplateMappingSerializer(
        source='mappings',
        many=True,
        required=False,
    )

    class Meta:
        model = RearPortTemplate
        fields = [
            'id', 'url', 'display', 'device_type', 'module_type', 'name', 'label', 'type', 'color', 'positions',
            'front_ports', 'description', 'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'description')


class FrontPortTemplateMappingSerializer(serializers.ModelSerializer):
    position = serializers.IntegerField(
        source='front_port_position'
    )
    rear_port = serializers.PrimaryKeyRelatedField(
        queryset=RearPortTemplate.objects.all(),
    )

    class Meta:
        model = PortTemplateMapping
        fields = ('position', 'rear_port', 'rear_port_position')


class FrontPortTemplateSerializer(ComponentTemplateSerializer, PortSerializer):
    device_type = DeviceTypeSerializer(
        nested=True,
        required=False,
        allow_null=True,
        default=None
    )
    module_type = ModuleTypeSerializer(
        nested=True,
        required=False,
        allow_null=True,
        default=None
    )
    type = ChoiceField(choices=PortTypeChoices)
    rear_ports = FrontPortTemplateMappingSerializer(
        source='mappings',
        many=True,
        required=False,
    )

    class Meta:
        model = FrontPortTemplate
        fields = [
            'id', 'url', 'display', 'device_type', 'module_type', 'name', 'label', 'type', 'color', 'positions',
            'rear_ports', 'description', 'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'description')


class ModuleBayTemplateSerializer(ComponentTemplateSerializer):
    device_type = DeviceTypeSerializer(
        nested=True,
        required=False,
        allow_null=True,
        default=None
    )
    module_type = ModuleTypeSerializer(
        nested=True,
        required=False,
        allow_null=True,
        default=None
    )

    class Meta:
        model = ModuleBayTemplate
        fields = [
            'id', 'url', 'display', 'device_type', 'module_type', 'name', 'label', 'position', 'description',
            'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'description')


class DeviceBayTemplateSerializer(ComponentTemplateSerializer):
    device_type = DeviceTypeSerializer(
        nested=True
    )

    class Meta:
        model = DeviceBayTemplate
        fields = [
            'id', 'url', 'display', 'device_type', 'name', 'label', 'description',
            'created', 'last_updated'
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'description')


class InventoryItemTemplateSerializer(ComponentTemplateSerializer):
    device_type = DeviceTypeSerializer(
        nested=True
    )
    parent = serializers.PrimaryKeyRelatedField(
        queryset=InventoryItemTemplate.objects.all(),
        allow_null=True,
        default=None
    )
    role = InventoryItemRoleSerializer(nested=True, required=False, allow_null=True)
    manufacturer = ManufacturerSerializer(
        nested=True,
        required=False,
        allow_null=True,
        default=None
    )
    component_type = ContentTypeField(
        queryset=ContentType.objects.filter(MODULAR_COMPONENT_TEMPLATE_MODELS),
        required=False,
        allow_null=True
    )
    component = GFKSerializerField(read_only=True)
    _depth = serializers.IntegerField(source='level', read_only=True)

    class Meta:
        model = InventoryItemTemplate
        fields = [
            'id', 'url', 'display', 'device_type', 'parent', 'name', 'label', 'role', 'manufacturer',
            'part_id', 'description', 'component_type', 'component_id', 'component', 'created', 'last_updated',
            '_depth',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'description', '_depth')
