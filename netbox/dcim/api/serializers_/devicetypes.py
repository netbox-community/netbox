from django.utils.translation import gettext as _
from rest_framework import serializers

from dcim.choices import *
from dcim.models import DeviceType, ModuleType
from netbox.api.fields import ChoiceField, RelatedObjectCountField
from netbox.api.serializers import NetBoxModelSerializer
from .manufacturers import ManufacturerSerializer
from .platforms import PlatformSerializer

__all__ = (
    'DeviceTypeSerializer',
    'ModuleTypeSerializer',
)


class DeviceTypeSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:devicetype-detail')
    manufacturer = ManufacturerSerializer(nested=True)
    default_platform = PlatformSerializer(nested=True, required=False, allow_null=True)
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
    front_image = serializers.ImageField(required=False, allow_null=True)
    rear_image = serializers.ImageField(required=False, allow_null=True)

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

    # Related object counts
    device_count = RelatedObjectCountField('instances')

    class Meta:
        model = DeviceType
        fields = [
            'id', 'url', 'display', 'manufacturer', 'default_platform', 'model', 'slug', 'part_number', 'u_height',
            'exclude_from_utilization', 'is_full_depth', 'subdevice_role', 'airflow', 'weight', 'weight_unit',
            'front_image', 'rear_image', 'description', 'comments', 'tags', 'custom_fields', 'created', 'last_updated',
            'device_count', 'console_port_template_count', 'console_server_port_template_count',
            'power_port_template_count', 'power_outlet_template_count', 'interface_template_count',
            'front_port_template_count', 'rear_port_template_count', 'device_bay_template_count',
            'module_bay_template_count', 'inventory_item_template_count',
        ]
        brief_fields = ('id', 'url', 'display', 'manufacturer', 'model', 'slug', 'description', 'device_count')


class ModuleTypeSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:moduletype-detail')
    manufacturer = ManufacturerSerializer(nested=True)
    weight_unit = ChoiceField(choices=WeightUnitChoices, allow_blank=True, required=False, allow_null=True)

    class Meta:
        model = ModuleType
        fields = [
            'id', 'url', 'display', 'manufacturer', 'model', 'part_number', 'weight', 'weight_unit', 'description',
            'comments', 'tags', 'custom_fields', 'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'manufacturer', 'model', 'description')
