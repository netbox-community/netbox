import decimal

from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext as _
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from dcim.choices import *
from dcim.constants import MACADDRESS_ASSIGNMENT_MODELS, MODULE_TOKEN
from dcim.models import Device, DeviceBay, MACAddress, Module, VirtualDeviceContext
from extras.api.serializers_.configtemplates import ConfigTemplateSerializer
from ipam.api.serializers_.ip import IPAddressSerializer
from netbox.api.fields import ChoiceField, ContentTypeField, RelatedObjectCountField
from netbox.api.gfk_fields import GFKSerializerField
from netbox.api.serializers import PrimaryModelSerializer
from tenancy.api.serializers_.tenants import TenantSerializer
from virtualization.api.serializers_.clusters import ClusterSerializer

from .devicetypes import *
from .nested import NestedDeviceBaySerializer, NestedDeviceSerializer, NestedModuleBaySerializer
from .platforms import PlatformSerializer
from .racks import RackSerializer
from .roles import DeviceRoleSerializer
from .sites import LocationSerializer, SiteSerializer
from .virtualchassis import VirtualChassisSerializer

__all__ = (
    'DeviceSerializer',
    'DeviceWithConfigContextSerializer',
    'MACAddressSerializer',
    'ModuleSerializer',
    'VirtualDeviceContextSerializer',
)


class DeviceSerializer(PrimaryModelSerializer):
    device_type = DeviceTypeSerializer(nested=True)
    role = DeviceRoleSerializer(nested=True)
    tenant = TenantSerializer(
        nested=True,
        required=False,
        allow_null=True,
        default=None
    )
    platform = PlatformSerializer(nested=True, required=False, allow_null=True)
    site = SiteSerializer(nested=True)
    location = LocationSerializer(nested=True, required=False, allow_null=True, default=None)
    rack = RackSerializer(nested=True, required=False, allow_null=True, default=None)
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
    primary_ip = IPAddressSerializer(nested=True, read_only=True, allow_null=True)
    primary_ip4 = IPAddressSerializer(nested=True, required=False, allow_null=True)
    primary_ip6 = IPAddressSerializer(nested=True, required=False, allow_null=True)
    oob_ip = IPAddressSerializer(nested=True, required=False, allow_null=True)
    parent_device = serializers.SerializerMethodField()
    cluster = ClusterSerializer(nested=True, required=False, allow_null=True)
    virtual_chassis = VirtualChassisSerializer(nested=True, required=False, allow_null=True, default=None)
    vc_position = serializers.IntegerField(allow_null=True, max_value=255, min_value=0, default=None)
    config_template = ConfigTemplateSerializer(nested=True, required=False, allow_null=True, default=None)

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
            'id', 'url', 'display_url', 'display', 'name', 'device_type', 'role', 'tenant', 'platform', 'serial',
            'asset_tag', 'site', 'location', 'rack', 'position', 'face', 'latitude', 'longitude', 'parent_device',
            'status', 'airflow', 'primary_ip', 'primary_ip4', 'primary_ip6', 'oob_ip', 'cluster', 'virtual_chassis',
            'vc_position', 'vc_priority', 'description', 'owner', 'comments', 'config_template', 'local_context_data',
            'tags', 'custom_fields', 'created', 'last_updated', 'console_port_count', 'console_server_port_count',
            'power_port_count', 'power_outlet_count', 'interface_count', 'front_port_count', 'rear_port_count',
            'device_bay_count', 'module_bay_count', 'inventory_item_count',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'description')

    @extend_schema_field(NestedDeviceSerializer(allow_null=True))
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
    config_context = serializers.SerializerMethodField(read_only=True, allow_null=True)

    class Meta(DeviceSerializer.Meta):
        fields = [
            'id', 'url', 'display_url', 'display', 'name', 'device_type', 'role', 'tenant', 'platform', 'serial',
            'asset_tag', 'site', 'location', 'rack', 'position', 'face', 'latitude', 'longitude', 'parent_device',
            'status', 'airflow', 'primary_ip', 'primary_ip4', 'primary_ip6', 'oob_ip', 'cluster', 'virtual_chassis',
            'vc_position', 'vc_priority', 'description', 'owner', 'comments', 'config_template', 'config_context',
            'local_context_data', 'tags', 'custom_fields', 'created', 'last_updated', 'console_port_count',
            'console_server_port_count', 'power_port_count', 'power_outlet_count', 'interface_count',
            'front_port_count', 'rear_port_count', 'device_bay_count', 'module_bay_count', 'inventory_item_count',
        ]

    @extend_schema_field(serializers.JSONField(allow_null=True))
    def get_config_context(self, obj):
        return obj.get_config_context()


class VirtualDeviceContextSerializer(PrimaryModelSerializer):
    device = DeviceSerializer(nested=True)
    identifier = serializers.IntegerField(allow_null=True, max_value=32767, min_value=0, required=False, default=None)
    tenant = TenantSerializer(nested=True, required=False, allow_null=True, default=None)
    primary_ip = IPAddressSerializer(nested=True, read_only=True, allow_null=True)
    primary_ip4 = IPAddressSerializer(nested=True, required=False, allow_null=True)
    primary_ip6 = IPAddressSerializer(nested=True, required=False, allow_null=True)
    status = ChoiceField(choices=VirtualDeviceContextStatusChoices)

    # Related object counts
    interface_count = RelatedObjectCountField('interfaces')

    class Meta:
        model = VirtualDeviceContext
        fields = [
            'id', 'url', 'display_url', 'display', 'name', 'device', 'identifier', 'tenant', 'primary_ip',
            'primary_ip4', 'primary_ip6', 'status', 'description', 'owner', 'comments', 'tags', 'custom_fields',
            'created', 'last_updated', 'interface_count',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'identifier', 'device', 'description')


class ModuleSerializer(PrimaryModelSerializer):
    device = DeviceSerializer(nested=True)
    module_bay = NestedModuleBaySerializer()
    module_type = ModuleTypeSerializer(nested=True)
    status = ChoiceField(choices=ModuleStatusChoices, required=False)
    replicate_components = serializers.BooleanField(
        required=False,
        default=True,
        write_only=True,
        label=_('Replicate components'),
        help_text=_('Automatically populate components associated with this module type (default: true)')
    )
    adopt_components = serializers.BooleanField(
        required=False,
        default=False,
        write_only=True,
        label=_('Adopt components'),
        help_text=_('Adopt already existing components')
    )

    class Meta:
        model = Module
        fields = [
            'id', 'url', 'display_url', 'display', 'device', 'module_bay', 'module_type', 'status', 'serial',
            'asset_tag', 'description', 'owner', 'comments', 'tags', 'custom_fields', 'created', 'last_updated',
            'replicate_components', 'adopt_components',
        ]
        brief_fields = ('id', 'url', 'display', 'device', 'module_bay', 'module_type', 'description')

    def validate(self, data):
        # When used as a nested serializer (e.g. as the `module` field on device component
        # serializers), `data` is already a resolved Module instance — skip our custom logic.
        if self.nested:
            return super().validate(data)

        # Pop write-only transient fields before ValidatedModelSerializer tries to
        # construct a Module instance for full_clean(); restore them afterwards.
        replicate_components = data.pop('replicate_components', True)
        adopt_components = data.pop('adopt_components', False)
        data = super().validate(data)

        # For updates these fields are not meaningful; omit them from validated_data so that
        # ModelSerializer.update() does not set unexpected attributes on the instance.
        if self.instance:
            return data

        # Always pass the flags to create() so it can set the correct private attributes.
        data['replicate_components'] = replicate_components
        data['adopt_components'] = adopt_components

        # Skip conflict checks when no component operations are requested.
        if not replicate_components and not adopt_components:
            return data

        device = data.get('device')
        module_type = data.get('module_type')
        module_bay = data.get('module_bay')

        if not all([device, module_type, module_bay]):
            return data

        # Build module bay tree for MODULE_TOKEN placeholder resolution (outermost to innermost)
        module_bays = []
        current_bay = module_bay
        while current_bay:
            module_bays.append(current_bay)
            current_bay = current_bay.module.module_bay if current_bay.module else None
        module_bays.reverse()

        for templates_attr, component_attr in [
            ('consoleporttemplates', 'consoleports'),
            ('consoleserverporttemplates', 'consoleserverports'),
            ('interfacetemplates', 'interfaces'),
            ('powerporttemplates', 'powerports'),
            ('poweroutlettemplates', 'poweroutlets'),
            ('rearporttemplates', 'rearports'),
            ('frontporttemplates', 'frontports'),
        ]:
            installed_components = {
                component.name: component
                for component in getattr(device, component_attr).all()
            }

            for template in getattr(module_type, templates_attr).all():
                resolved_name = template.name
                if MODULE_TOKEN in template.name:
                    if not module_bay.position:
                        raise serializers.ValidationError(
                            _("Cannot install module with placeholder values in a module bay with no position defined.")
                        )
                    if template.name.count(MODULE_TOKEN) != len(module_bays):
                        raise serializers.ValidationError(
                            _(
                                "Cannot install module with placeholder values in a module bay tree {level} in tree "
                                "but {tokens} placeholders given."
                            ).format(
                                level=len(module_bays), tokens=template.name.count(MODULE_TOKEN)
                            )
                        )
                    for bay in module_bays:
                        resolved_name = resolved_name.replace(MODULE_TOKEN, bay.position, 1)

                existing_item = installed_components.get(resolved_name)

                if adopt_components and existing_item and existing_item.module:
                    raise serializers.ValidationError(
                        _("Cannot adopt {model} {name} as it already belongs to a module").format(
                            model=template.component_model.__name__,
                            name=resolved_name
                        )
                    )

                if not adopt_components and replicate_components and resolved_name in installed_components:
                    raise serializers.ValidationError(
                        _("A {model} named {name} already exists").format(
                            model=template.component_model.__name__,
                            name=resolved_name
                        )
                    )

        return data

    def create(self, validated_data):
        replicate_components = validated_data.pop('replicate_components', True)
        adopt_components = validated_data.pop('adopt_components', False)

        # Tags are handled after save; pop them here to pass to _save_tags()
        tags = validated_data.pop('tags', None)

        # Build the instance without saving so we can set private attributes
        # that control component replication behaviour in Module.save()
        instance = self.Meta.model(**validated_data)
        if adopt_components:
            instance._adopt_components = True
        if not replicate_components:
            instance._disable_replication = True
        instance.save()

        if tags is not None:
            self._save_tags(instance, tags)

        return instance


class MACAddressSerializer(PrimaryModelSerializer):
    assigned_object_type = ContentTypeField(
        queryset=ContentType.objects.filter(MACADDRESS_ASSIGNMENT_MODELS),
        required=False,
        allow_null=True
    )
    assigned_object = GFKSerializerField(read_only=True)

    class Meta:
        model = MACAddress
        fields = [
            'id', 'url', 'display_url', 'display', 'mac_address', 'assigned_object_type', 'assigned_object_id',
            'assigned_object', 'description', 'owner', 'comments', 'tags', 'custom_fields', 'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'mac_address', 'description')
