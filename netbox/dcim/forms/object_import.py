from django import forms
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from dcim.choices import InterfacePoEModeChoices, InterfacePoETypeChoices, InterfaceTypeChoices, PortTypeChoices
from dcim.models import *
from wireless.choices import WirelessRoleChoices

__all__ = (
    'ConsolePortTemplateImportForm',
    'ConsoleServerPortTemplateImportForm',
    'CoolingIntakeTemplateImportForm',
    'CoolingOutflowTemplateImportForm',
    'DeviceBayTemplateImportForm',
    'FrontPortTemplateImportForm',
    'InterfaceTemplateImportForm',
    'InventoryItemTemplateImportForm',
    'ModuleBayTemplateImportForm',
    'PortTemplateMappingImportForm',
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


class CoolingIntakeTemplateImportForm(forms.ModelForm):

    class Meta:
        model = CoolingIntakeTemplate
        fields = [
            'device_type', 'module_type', 'name', 'label', 'type', 'diameter', 'diameter_unit',
            'max_flow', 'max_flow_unit', 'description',
        ]


class CoolingOutflowTemplateImportForm(forms.ModelForm):
    cooling_intake = forms.ModelChoiceField(
        label=_('Cooling intake'),
        queryset=CoolingIntakeTemplate.objects.all(),
        to_field_name='name',
        required=False
    )

    class Meta:
        model = CoolingOutflowTemplate
        fields = [
            'device_type', 'module_type', 'name', 'label', 'type', 'diameter', 'diameter_unit',
            'cooling_intake', 'description',
        ]

    def clean_device_type(self):
        if device_type := self.cleaned_data['device_type']:
            cooling_intake = self.fields['cooling_intake']
            cooling_intake.queryset = cooling_intake.queryset.filter(device_type=device_type)

        return device_type

    def clean_module_type(self):
        if module_type := self.cleaned_data['module_type']:
            cooling_intake = self.fields['cooling_intake']
            cooling_intake.queryset = cooling_intake.queryset.filter(module_type=module_type)

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
            'device_type', 'module_type', 'name', 'label', 'type', 'channels', 'channel_id', 'enabled', 'mgmt_only',
            'description', 'poe_mode', 'poe_type', 'rf_role'
        ]


class FrontPortTemplateImportForm(forms.ModelForm):
    type = forms.ChoiceField(
        label=_('Type'),
        choices=PortTypeChoices.CHOICES
    )

    class Meta:
        model = FrontPortTemplate
        fields = [
            'device_type', 'module_type', 'name', 'type', 'color', 'positions', 'label', 'description',
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


class PortTemplateMappingImportForm(forms.ModelForm):
    front_port = forms.ModelChoiceField(
        label=_('Front port'),
        queryset=FrontPortTemplate.objects.all(),
        to_field_name='name',
    )
    rear_port = forms.ModelChoiceField(
        label=_('Rear port'),
        queryset=RearPortTemplate.objects.all(),
        to_field_name='name',
    )

    class Meta:
        model = PortTemplateMapping
        fields = [
            'device_type', 'module_type', 'front_port', 'front_port_position', 'rear_port', 'rear_port_position',
        ]

    def clean_device_type(self):
        if device_type := self.cleaned_data['device_type']:
            front_port = self.fields['front_port']
            rear_port = self.fields['rear_port']
            front_port.queryset = front_port.queryset.filter(device_type=device_type)
            rear_port.queryset = rear_port.queryset.filter(device_type=device_type)
        return device_type

    def clean_module_type(self):
        if module_type := self.cleaned_data['module_type']:
            front_port = self.fields['front_port']
            rear_port = self.fields['rear_port']
            front_port.queryset = front_port.queryset.filter(module_type=module_type)
            rear_port.queryset = rear_port.queryset.filter(module_type=module_type)
        return module_type


class ModuleBayTemplateImportForm(forms.ModelForm):
    module_bay_types = forms.ModelMultipleChoiceField(
        label=_('Module bay types'),
        queryset=ModuleBayType.objects.all(),
        to_field_name='name',
        required=False,
    )

    class Meta:
        model = ModuleBayTemplate
        # module_bay_types must stay last: clean_device_type/clean_module_type narrow its queryset by
        # manufacturer before it is itself cleaned, and Django cleans fields in this order.
        fields = [
            'device_type', 'module_type', 'name', 'label', 'position', 'enabled', 'description',
            'module_bay_types',
        ]

    def clean_enabled(self):
        # A dict-bound BooleanField resolves a missing key to False, not the model's own
        # default=True -- match ModuleBayImportForm's equivalent CSV-import behavior.
        if 'enabled' not in self.data:
            return True
        return self.cleaned_data['enabled']

    def _scope_module_bay_types(self, manufacturer):
        module_bay_types = self.fields['module_bay_types']
        module_bay_types.queryset = module_bay_types.queryset.filter(
            Q(manufacturer__isnull=True) | Q(manufacturer=manufacturer)
        )

    def clean_device_type(self):
        if device_type := self.cleaned_data['device_type']:
            self._scope_module_bay_types(device_type.manufacturer)

        return device_type

    def clean_module_type(self):
        if module_type := self.cleaned_data['module_type']:
            self._scope_module_bay_types(module_type.manufacturer)

        return module_type

    def clean_module_bay_types(self):
        """
        Collapse to one match per name, preferring a manufacturer-specific match over a global
        one. ModuleBayType's unique constraint is on (manufacturer, name), not name alone, so a
        name can legitimately collide between a global type and one scoped to this template's
        own manufacturer (narrowed by clean_device_type/clean_module_type above); the field's
        default name-based lookup resolves both matches into cleaned_data rather than picking
        one, since it has no way to know which is meant.
        """
        module_bay_types = self.cleaned_data['module_bay_types']

        by_name = {}
        for module_bay_type in module_bay_types:
            existing = by_name.get(module_bay_type.name)
            if existing is None or module_bay_type.manufacturer_id is not None:
                by_name[module_bay_type.name] = module_bay_type

        return list(by_name.values())


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
