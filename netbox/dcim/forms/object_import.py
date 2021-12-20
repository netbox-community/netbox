from django import forms

from dcim.choices import InterfaceTypeChoices, PortTypeChoices
from dcim.models import *
from utilities.forms import BootstrapMixin

__all__ = (
    'ConsolePortTemplateImportForm',
    'ConsoleServerPortTemplateImportForm',
    'DeviceBayTemplateImportForm',
    'DeviceTypeImportForm',
    'FrontPortTemplateImportForm',
    'InterfaceTemplateImportForm',
    'ModuleBayTemplateImportForm',
    'ModuleTypeImportForm',
    'PowerOutletTemplateImportForm',
    'PowerPortTemplateImportForm',
    'RearPortTemplateImportForm',
)


class DeviceTypeImportForm(BootstrapMixin, forms.ModelForm):
    manufacturer = forms.ModelChoiceField(
        queryset=Manufacturer.objects.all(),
        to_field_name='name'
    )

    class Meta:
        model = DeviceType
        fields = [
            'manufacturer', 'model', 'slug', 'part_number', 'u_height', 'is_full_depth', 'subdevice_role', 'airflow',
            'comments',
        ]


class ModuleTypeImportForm(BootstrapMixin, forms.ModelForm):
    manufacturer = forms.ModelChoiceField(
        queryset=Manufacturer.objects.all(),
        to_field_name='name'
    )

    class Meta:
        model = ModuleType
        fields = ['manufacturer', 'model', 'part_number', 'comments']


#
# Component template import forms
#

class ComponentTemplateImportForm(BootstrapMixin, forms.ModelForm):

    def clean_device_type(self):
        # Limit fields referencing other components to the parent DeviceType
        if data := self.cleaned_data['device_type']:
            for field_name, field in self.fields.items():
                if isinstance(field, forms.ModelChoiceField) and field_name not in ['device_type', 'module_type']:
                    field.queryset = field.queryset.filter(device_type=data)

        return data

    def clean_module_type(self):
        # Limit fields referencing other components to the parent ModuleType
        if data := self.cleaned_data['module_type']:
            for field_name, field in self.fields.items():
                if isinstance(field, forms.ModelChoiceField) and field_name not in ['device_type', 'module_type']:
                    field.queryset = field.queryset.filter(module_type=data)

        return data


class ConsolePortTemplateImportForm(ComponentTemplateImportForm):

    class Meta:
        model = ConsolePortTemplate
        fields = [
            'device_type', 'module_type', 'name', 'label', 'type', 'description',
        ]


class ConsoleServerPortTemplateImportForm(ComponentTemplateImportForm):

    class Meta:
        model = ConsoleServerPortTemplate
        fields = [
            'device_type', 'module_type', 'name', 'label', 'type', 'description',
        ]


class PowerPortTemplateImportForm(ComponentTemplateImportForm):

    class Meta:
        model = PowerPortTemplate
        fields = [
            'device_type', 'module_type', 'name', 'label', 'type', 'maximum_draw', 'allocated_draw', 'description',
        ]


class PowerOutletTemplateImportForm(ComponentTemplateImportForm):
    power_port = forms.ModelChoiceField(
        queryset=PowerPortTemplate.objects.all(),
        to_field_name='name',
        required=False
    )

    class Meta:
        model = PowerOutletTemplate
        fields = [
            'device_type', 'module_type', 'name', 'label', 'type', 'power_port', 'feed_leg', 'description',
        ]


class InterfaceTemplateImportForm(ComponentTemplateImportForm):
    type = forms.ChoiceField(
        choices=InterfaceTypeChoices.CHOICES
    )

    class Meta:
        model = InterfaceTemplate
        fields = [
            'device_type', 'module_type', 'name', 'label', 'type', 'mgmt_only', 'description',
        ]


class FrontPortTemplateImportForm(ComponentTemplateImportForm):
    type = forms.ChoiceField(
        choices=PortTypeChoices.CHOICES
    )
    rear_port = forms.ModelChoiceField(
        queryset=RearPortTemplate.objects.all(),
        to_field_name='name'
    )

    class Meta:
        model = FrontPortTemplate
        fields = [
            'device_type', 'module_type', 'name', 'type', 'rear_port', 'rear_port_position', 'label', 'description',
        ]


class RearPortTemplateImportForm(ComponentTemplateImportForm):
    type = forms.ChoiceField(
        choices=PortTypeChoices.CHOICES
    )

    class Meta:
        model = RearPortTemplate
        fields = [
            'device_type', 'module_type', 'name', 'type', 'positions', 'label', 'description',
        ]


class ModuleBayTemplateImportForm(ComponentTemplateImportForm):

    class Meta:
        model = ModuleBayTemplate
        fields = [
            'device_type', 'name', 'label', 'position', 'description',
        ]


class DeviceBayTemplateImportForm(ComponentTemplateImportForm):

    class Meta:
        model = DeviceBayTemplate
        fields = [
            'device_type', 'name', 'label', 'description',
        ]
