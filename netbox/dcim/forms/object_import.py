from django import forms
from django.utils.translation import gettext_lazy as _

from dcim.choices import InterfacePoEModeChoices, InterfacePoETypeChoices, InterfaceTypeChoices, PortTypeChoices
from dcim.models import *
from wireless.choices import WirelessRoleChoices

__all__ = (
    'ConsolePortTemplateImportForm',
    'ConsoleServerPortTemplateImportForm',
    'DeviceBayTemplateImportForm',
    'FrontPortTemplateImportForm',
    'InterfaceTemplateImportForm',
    'InventoryItemTemplateImportForm',
    'ModuleBayTemplateImportForm',
    'PowerOutletTemplateImportForm',
    'PowerPortTemplateImportForm',
    'RearPortTemplateImportForm',
)


#
# Component template import forms
#

class ConsolePortTemplateImportForm(forms.ModelForm):

    class Meta:
        model = ConsolePortTemplate
        fields = [
            'device_type', 'module_type', 'name', 'label', 'type', 'description',
        ]


class ConsoleServerPortTemplateImportForm(forms.ModelForm):

    class Meta:
        model = ConsoleServerPortTemplate
        fields = [
            'device_type', 'module_type', 'name', 'label', 'type', 'description',
        ]


class PowerPortTemplateImportForm(forms.ModelForm):

    class Meta:
        model = PowerPortTemplate
        fields = [
            'device_type', 'module_type', 'name', 'label', 'type', 'maximum_draw', 'allocated_draw', 'description',
        ]


class PowerOutletTemplateImportForm(forms.ModelForm):
    power_port = forms.ModelChoiceField(
        label=_('Power port'),
        queryset=PowerPortTemplate.objects.all(),
        to_field_name='name',
        required=False
    )

    class Meta:
        model = PowerOutletTemplate
        fields = [
            'device_type', 'module_type', 'name', 'label', 'type', 'power_port', 'feed_leg', 'description',
        ]

    def clean_device_type(self):
        if device_type := self.cleaned_data['device_type']:
            power_port = self.fields['power_port']
            power_port.queryset = power_port.queryset.filter(device_type=device_type)

        return device_type

    def clean_module_type(self):
        if module_type := self.cleaned_data['module_type']:
            power_port = self.fields['power_port']
            power_port.queryset = power_port.queryset.filter(module_type=module_type)

        return module_type


class InterfaceTemplateImportForm(forms.ModelForm):
    type = forms.ChoiceField(
        label=_('Type'),
        choices=InterfaceTypeChoices.CHOICES
    )
    poe_mode = forms.ChoiceField(
        choices=InterfacePoEModeChoices,
        required=False,
        label=_('PoE mode')
    )
    poe_type = forms.ChoiceField(
        choices=InterfacePoETypeChoices,
        required=False,
        label=_('PoE type')
    )
    rf_role = forms.ChoiceField(
        choices=WirelessRoleChoices,
        required=False,
        label=_('Wireless role')
    )

    class Meta:
        model = InterfaceTemplate
        fields = [
            'device_type', 'module_type', 'name', 'label', 'type', 'enabled', 'mgmt_only', 'description', 'poe_mode',
            'poe_type', 'rf_role'
        ]


class FrontPortTemplateImportForm(forms.ModelForm):
    type = forms.ChoiceField(
        label=_('Type'),
        choices=PortTypeChoices.CHOICES
    )
    rear_port = forms.ModelChoiceField(
        label=_('Rear port'),
        queryset=RearPortTemplate.objects.all(),
        to_field_name='name'
    )

    def clean_device_type(self):
        if device_type := self.cleaned_data['device_type']:
            rear_port = self.fields['rear_port']
            rear_port.queryset = rear_port.queryset.filter(device_type=device_type)

        return device_type

    def clean_module_type(self):
        if module_type := self.cleaned_data['module_type']:
            rear_port = self.fields['rear_port']
            rear_port.queryset = rear_port.queryset.filter(module_type=module_type)

        return module_type

    class Meta:
        model = FrontPortTemplate
        fields = [
            'device_type', 'module_type', 'name', 'type', 'color', 'rear_port', 'rear_port_position', 'label',
            'description',
        ]


class RearPortTemplateImportForm(forms.ModelForm):
    type = forms.ChoiceField(
        label=_('Type'),
        choices=PortTypeChoices.CHOICES
    )

    class Meta:
        model = RearPortTemplate
        fields = [
            'device_type', 'module_type', 'name', 'type', 'color', 'positions', 'label', 'description',
        ]


class ModuleBayTemplateImportForm(forms.ModelForm):

    class Meta:
        model = ModuleBayTemplate
        fields = [
            'device_type', 'name', 'label', 'position', 'description',
        ]


class DeviceBayTemplateImportForm(forms.ModelForm):

    class Meta:
        model = DeviceBayTemplate
        fields = [
            'device_type', 'name', 'label', 'description',
        ]


class InventoryItemTemplateImportForm(forms.ModelForm):
    parent = forms.ModelChoiceField(
        label=_('Parent'),
        queryset=InventoryItemTemplate.objects.all(),
        required=False
    )
    role = forms.ModelChoiceField(
        label=_('Role'),
        queryset=InventoryItemRole.objects.all(),
        to_field_name='name',
        required=False
    )
    manufacturer = forms.ModelChoiceField(
        label=_('Manufacturer'),
        queryset=Manufacturer.objects.all(),
        to_field_name='name',
        required=False
    )

    class Meta:
        model = InventoryItemTemplate
        fields = [
            'device_type', 'parent', 'name', 'label', 'role', 'manufacturer', 'part_id', 'description',
        ]

    def clean_device_type(self):
        if device_type := self.cleaned_data['device_type']:
            parent = self.fields['parent']
            parent.queryset = parent.queryset.filter(device_type=device_type)

        return device_type

    def clean_module_type(self):
        if module_type := self.cleaned_data['module_type']:
            parent = self.fields['parent']
            parent.queryset = parent.queryset.filter(module_type=module_type)

        return module_type
