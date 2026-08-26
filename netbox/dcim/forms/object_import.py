from django import forms
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
    parent = forms.ModelChoiceField(
        label=_('Parent'),
        queryset=InterfaceTemplate.objects.all(),
        to_field_name='name',
        required=False
    )
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
            'device_type', 'module_type', 'name', 'label', 'type', 'channels', 'channel_id', 'parent', 'enabled',
            'mgmt_only', 'description', 'poe_mode', 'poe_type', 'rf_role',
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
        fields = [
            'device_type', 'module_type', 'name', 'label', 'position', 'enabled', 'description',
            'module_bay_types',
        ]

    def clean(self):
        """
        Resolve each referenced bay type name against the parent type's own manufacturer, plus
        bay types having no manufacturer (global), preferring a manufacturer-specific match
        over a global one. ModuleBayType's unique constraint is on (manufacturer, name), not
        name alone, so a name can legitimately match both, and the field's name-based lookup
        resolves every match into cleaned_data rather than picking one.

        This runs in clean() rather than in clean_module_bay_types() so that it does not depend
        on the parent having been cleaned first, which would make it sensitive to the order of
        Meta.fields.
        """
        super().clean()

        module_bay_types = self.cleaned_data.get('module_bay_types')
        if not module_bay_types:
            return

        # If neither parent resolved, leave the field alone: ModularComponentTemplateModel.clean()
        # rejects a parentless template in _post_clean(), and reporting unresolvable names on top
        # of that would just be noise.
        parent = self.cleaned_data.get('device_type') or self.cleaned_data.get('module_type')
        if parent is None:
            return

        by_name = {}
        for module_bay_type in module_bay_types:
            if module_bay_type.manufacturer_id not in (None, parent.manufacturer_id):
                continue
            existing = by_name.get(module_bay_type.name)
            if existing is None or module_bay_type.manufacturer_id is not None:
                by_name[module_bay_type.name] = module_bay_type

        # A name matching only some other manufacturer's bay type is rejected rather than
        # resolved to it.
        for module_bay_type in module_bay_types:
            if module_bay_type.name not in by_name:
                raise forms.ValidationError({
                    'module_bay_types': forms.ValidationError(
                        self.fields['module_bay_types'].error_messages['invalid_choice'],
                        code='invalid_choice',
                        params={'value': module_bay_type.name},
                    )
                })

        self.cleaned_data['module_bay_types'] = list(by_name.values())


class DeviceBayTemplateImportForm(forms.ModelForm):

    class Meta:
        model = DeviceBayTemplate
        fields = [
            'device_type', 'name', 'label', 'enabled', 'description',
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
