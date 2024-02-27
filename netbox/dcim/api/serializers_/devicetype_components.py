from django.contrib.contenttypes.models import ContentType
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from dcim.choices import *
from dcim.constants import *
from dcim.models import (
    ConsolePortTemplate, ConsoleServerPortTemplate, DeviceBayTemplate, FrontPortTemplate, InterfaceTemplate,
    InventoryItemTemplate, ModuleBayTemplate, PowerOutletTemplate, PowerPortTemplate, RearPortTemplate,
)
from netbox.api.fields import ChoiceField, ContentTypeField
from netbox.api.serializers import ValidatedModelSerializer
from utilities.api import get_serializer_for_model
from wireless.choices import *
from .devicetypes import DeviceTypeSerializer, ModuleTypeSerializer
from .manufacturers import ManufacturerSerializer
from .roles import InventoryItemRoleSerializer
from ..nested_serializers import *

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


class ConsolePortTemplateSerializer(ValidatedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:consoleporttemplate-detail')
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
            'id', 'url', 'display', 'device_type', 'module_type', 'name', 'label', 'type', 'description', 'created',
            'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'description')


class ConsoleServerPortTemplateSerializer(ValidatedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:consoleserverporttemplate-detail')
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
            'id', 'url', 'display', 'device_type', 'module_type', 'name', 'label', 'type', 'description', 'created',
            'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'description')


class PowerPortTemplateSerializer(ValidatedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:powerporttemplate-detail')
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
            'id', 'url', 'display', 'device_type', 'module_type', 'name', 'label', 'type', 'maximum_draw',
            'allocated_draw', 'description', 'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'description')


class PowerOutletTemplateSerializer(ValidatedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:poweroutlettemplate-detail')
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
            'id', 'url', 'display', 'device_type', 'module_type', 'name', 'label', 'type', 'power_port', 'feed_leg',
            'description', 'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'description')


class InterfaceTemplateSerializer(ValidatedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:interfacetemplate-detail')
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
            'id', 'url', 'display', 'device_type', 'module_type', 'name', 'label', 'type', 'enabled', 'mgmt_only',
            'description', 'bridge', 'poe_mode', 'poe_type', 'rf_role', 'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'description')


class RearPortTemplateSerializer(ValidatedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:rearporttemplate-detail')
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

    class Meta:
        model = RearPortTemplate
        fields = [
            'id', 'url', 'display', 'device_type', 'module_type', 'name', 'label', 'type', 'color', 'positions',
            'description', 'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'description')


class FrontPortTemplateSerializer(ValidatedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:frontporttemplate-detail')
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
    rear_port = RearPortTemplateSerializer(nested=True)

    class Meta:
        model = FrontPortTemplate
        fields = [
            'id', 'url', 'display', 'device_type', 'module_type', 'name', 'label', 'type', 'color', 'rear_port',
            'rear_port_position', 'description', 'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'description')


class ModuleBayTemplateSerializer(ValidatedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:modulebaytemplate-detail')
    device_type = DeviceTypeSerializer(
        nested=True
    )

    class Meta:
        model = ModuleBayTemplate
        fields = [
            'id', 'url', 'display', 'device_type', 'name', 'label', 'position', 'description', 'created',
            'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'description')


class DeviceBayTemplateSerializer(ValidatedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:devicebaytemplate-detail')
    device_type = DeviceTypeSerializer(
        nested=True
    )

    class Meta:
        model = DeviceBayTemplate
        fields = ['id', 'url', 'display', 'device_type', 'name', 'label', 'description', 'created', 'last_updated']
        brief_fields = ('id', 'url', 'display', 'name', 'description')


class InventoryItemTemplateSerializer(ValidatedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:inventoryitemtemplate-detail')
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
    component = serializers.SerializerMethodField(read_only=True)
    _depth = serializers.IntegerField(source='level', read_only=True)

    class Meta:
        model = InventoryItemTemplate
        fields = [
            'id', 'url', 'display', 'device_type', 'parent', 'name', 'label', 'role', 'manufacturer', 'part_id',
            'description', 'component_type', 'component_id', 'component', 'created', 'last_updated', '_depth',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'description', '_depth')

    @extend_schema_field(serializers.JSONField(allow_null=True))
    def get_component(self, obj):
        if obj.component is None:
            return None
        serializer = get_serializer_for_model(obj.component)
        context = {'request': self.context['request']}
        return serializer(obj.component, nested=True, context=context).data
