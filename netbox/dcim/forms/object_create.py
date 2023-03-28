from django import forms
from django.utils.translation import gettext as _

from dcim.models import *
from netbox.forms import NetBoxModelForm
from utilities.forms import DynamicModelChoiceField, DynamicModelMultipleChoiceField, ExpandableNameField
from . import model_forms

__all__ = (
    'ComponentCreateForm',
    'ConsolePortCreateForm',
    'ConsolePortTemplateCreateForm',
    'ConsoleServerPortCreateForm',
    'ConsoleServerPortTemplateCreateForm',
    'DeviceBayCreateForm',
    'DeviceBayTemplateCreateForm',
    'FrontPortCreateForm',
    'FrontPortTemplateCreateForm',
    'InterfaceCreateForm',
    'InterfaceTemplateCreateForm',
    'InventoryItemCreateForm',
    'InventoryItemTemplateCreateForm',
    'ModuleBayCreateForm',
    'ModuleBayTemplateCreateForm',
    'PowerOutletCreateForm',
    'PowerOutletTemplateCreateForm',
    'PowerPortCreateForm',
    'PowerPortTemplateCreateForm',
    'RearPortCreateForm',
    'RearPortTemplateCreateForm',
    'VirtualChassisCreateForm',
)


class ComponentCreateForm(forms.Form):
    """
    Subclass this form when facilitating the creation of one or more component or component template objects based on
    a name pattern.
    """
    name = ExpandableNameField()
    label = ExpandableNameField(
        required=False,
        help_text=_('Alphanumeric ranges are supported. (Must match the number of objects being created.)')
    )

    # Identify the fields which support replication (i.e. ExpandableNameFields). This is referenced by
    # ComponentCreateView when creating objects.
    replication_fields = ('name', 'label')

    def clean(self):
        super().clean()

        # Validate that all replication fields generate an equal number of values
        pattern_count = len(self.cleaned_data[self.replication_fields[0]])
        for field_name in self.replication_fields:
            value_count = len(self.cleaned_data[field_name])
            if self.cleaned_data[field_name] and value_count != pattern_count:
                raise forms.ValidationError({
                    field_name: f'The provided pattern specifies {value_count} values, but {pattern_count} are '
                                f'expected.'
                }, code='label_pattern_mismatch')


#
# Device component templates
#

class ConsolePortTemplateCreateForm(ComponentCreateForm, model_forms.ConsolePortTemplateForm):

    class Meta(model_forms.ConsolePortTemplateForm.Meta):
        exclude = ('name', 'label')


class ConsoleServerPortTemplateCreateForm(ComponentCreateForm, model_forms.ConsoleServerPortTemplateForm):

    class Meta(model_forms.ConsoleServerPortTemplateForm.Meta):
        exclude = ('name', 'label')


class PowerPortTemplateCreateForm(ComponentCreateForm, model_forms.PowerPortTemplateForm):

    class Meta(model_forms.PowerPortTemplateForm.Meta):
        exclude = ('name', 'label')


class PowerOutletTemplateCreateForm(ComponentCreateForm, model_forms.PowerOutletTemplateForm):

    class Meta(model_forms.PowerOutletTemplateForm.Meta):
        exclude = ('name', 'label')


class InterfaceTemplateCreateForm(ComponentCreateForm, model_forms.InterfaceTemplateForm):

    class Meta(model_forms.InterfaceTemplateForm.Meta):
        exclude = ('name', 'label')


class FrontPortTemplateCreateForm(ComponentCreateForm, model_forms.FrontPortTemplateForm):
    rear_port = forms.MultipleChoiceField(
        choices=[],
        label=_('Rear ports'),
        help_text=_('Select one rear port assignment for each front port being created.'),
    )

    # Override fieldsets from FrontPortTemplateForm to omit rear_port_position
    fieldsets = (
        (None, ('device_type', 'module_type', 'name', 'label', 'type', 'color', 'rear_port', 'description')),
    )

    class Meta(model_forms.FrontPortTemplateForm.Meta):
        exclude = ('name', 'label', 'rear_port', 'rear_port_position')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # TODO: This needs better validation
        if 'device_type' in self.initial or self.data.get('device_type'):
            parent = DeviceType.objects.get(
                pk=self.initial.get('device_type') or self.data.get('device_type')
            )
        elif 'module_type' in self.initial or self.data.get('module_type'):
            parent = ModuleType.objects.get(
                pk=self.initial.get('module_type') or self.data.get('module_type')
            )
        else:
            return

        # Determine which rear port positions are occupied. These will be excluded from the list of available mappings.
        occupied_port_positions = [
            (front_port.rear_port_id, front_port.rear_port_position)
            for front_port in parent.frontporttemplates.all()
        ]

        # Populate rear port choices
        choices = []
        rear_ports = parent.rearporttemplates.all()
        for rear_port in rear_ports:
            for i in range(1, rear_port.positions + 1):
                if (rear_port.pk, i) not in occupied_port_positions:
                    choices.append(
                        ('{}:{}'.format(rear_port.pk, i), '{}:{}'.format(rear_port.name, i))
                    )
        self.fields['rear_port'].choices = choices

    def get_iterative_data(self, iteration):

        # Assign rear port and position from selected set
        rear_port, position = self.cleaned_data['rear_port'][iteration].split(':')

        return {
            'rear_port': int(rear_port),
            'rear_port_position': int(position),
        }


class RearPortTemplateCreateForm(ComponentCreateForm, model_forms.RearPortTemplateForm):

    class Meta(model_forms.RearPortTemplateForm.Meta):
        exclude = ('name', 'label')


class DeviceBayTemplateCreateForm(ComponentCreateForm, model_forms.DeviceBayTemplateForm):

    class Meta(model_forms.DeviceBayTemplateForm.Meta):
        exclude = ('name', 'label')


class ModuleBayTemplateCreateForm(ComponentCreateForm, model_forms.ModuleBayTemplateForm):
    position = ExpandableNameField(
        label=_('Position'),
        required=False,
        help_text=_('Alphanumeric ranges are supported. (Must match the number of objects being created.)')
    )
    replication_fields = ('name', 'label', 'position')

    class Meta(model_forms.ModuleBayTemplateForm.Meta):
        exclude = ('name', 'label', 'position')


class InventoryItemTemplateCreateForm(ComponentCreateForm, model_forms.InventoryItemTemplateForm):

    class Meta(model_forms.InventoryItemTemplateForm.Meta):
        exclude = ('name', 'label')


#
# Device components
#

class ConsolePortCreateForm(ComponentCreateForm, model_forms.ConsolePortForm):

    class Meta(model_forms.ConsolePortForm.Meta):
        exclude = ('name', 'label')


class ConsoleServerPortCreateForm(ComponentCreateForm, model_forms.ConsoleServerPortForm):

    class Meta(model_forms.ConsoleServerPortForm.Meta):
        exclude = ('name', 'label')


class PowerPortCreateForm(ComponentCreateForm, model_forms.PowerPortForm):

    class Meta(model_forms.PowerPortForm.Meta):
        exclude = ('name', 'label')


class PowerOutletCreateForm(ComponentCreateForm, model_forms.PowerOutletForm):

    class Meta(model_forms.PowerOutletForm.Meta):
        exclude = ('name', 'label')


class InterfaceCreateForm(ComponentCreateForm, model_forms.InterfaceForm):

    class Meta(model_forms.InterfaceForm.Meta):
        exclude = ('name', 'label')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if 'module' in self.fields:
            self.fields['name'].help_text += ' The string <code>{module}</code> will be replaced with the position ' \
                                             'of the assigned module, if any'


class FrontPortCreateForm(ComponentCreateForm, model_forms.FrontPortForm):
    rear_port = forms.MultipleChoiceField(
        choices=[],
        label=_('Rear ports'),
        help_text=_('Select one rear port assignment for each front port being created.'),
    )

    # Override fieldsets from FrontPortForm to omit rear_port_position
    fieldsets = (
        (None, (
            'device', 'module', 'name', 'label', 'type', 'color', 'rear_port', 'mark_connected', 'description', 'tags',
        )),
    )

    class Meta(model_forms.FrontPortForm.Meta):
        exclude = ('name', 'label', 'rear_port', 'rear_port_position')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        device = Device.objects.get(
            pk=self.initial.get('device') or self.data.get('device')
        )

        # Determine which rear port positions are occupied. These will be excluded from the list of available
        # mappings.
        occupied_port_positions = [
            (front_port.rear_port_id, front_port.rear_port_position)
            for front_port in device.frontports.all()
        ]

        # Populate rear port choices
        choices = []
        rear_ports = RearPort.objects.filter(device=device)
        for rear_port in rear_ports:
            for i in range(1, rear_port.positions + 1):
                if (rear_port.pk, i) not in occupied_port_positions:
                    choices.append(
                        ('{}:{}'.format(rear_port.pk, i), '{}:{}'.format(rear_port.name, i))
                    )
        self.fields['rear_port'].choices = choices

    def get_iterative_data(self, iteration):

        # Assign rear port and position from selected set
        rear_port, position = self.cleaned_data['rear_port'][iteration].split(':')

        return {
            'rear_port': int(rear_port),
            'rear_port_position': int(position),
        }


class RearPortCreateForm(ComponentCreateForm, model_forms.RearPortForm):

    class Meta(model_forms.RearPortForm.Meta):
        exclude = ('name', 'label')


class DeviceBayCreateForm(ComponentCreateForm, model_forms.DeviceBayForm):

    class Meta(model_forms.DeviceBayForm.Meta):
        exclude = ('name', 'label')


class ModuleBayCreateForm(ComponentCreateForm, model_forms.ModuleBayForm):
    position = ExpandableNameField(
        label=_('Position'),
        required=False,
        help_text=_('Alphanumeric ranges are supported. (Must match the number of objects being created.)')
    )
    replication_fields = ('name', 'label', 'position')

    class Meta(model_forms.ModuleBayForm.Meta):
        exclude = ('name', 'label', 'position')


class InventoryItemCreateForm(ComponentCreateForm, model_forms.InventoryItemForm):

    class Meta(model_forms.InventoryItemForm.Meta):
        exclude = ('name', 'label')


#
# Virtual chassis
#

class VirtualChassisCreateForm(NetBoxModelForm):
    region = DynamicModelChoiceField(
        queryset=Region.objects.all(),
        required=False,
        initial_params={
            'sites': '$site'
        }
    )
    site_group = DynamicModelChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False,
        initial_params={
            'sites': '$site'
        }
    )
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        query_params={
            'region_id': '$region',
            'group_id': '$site_group',
        }
    )
    rack = DynamicModelChoiceField(
        queryset=Rack.objects.all(),
        required=False,
        null_option='None',
        query_params={
            'site_id': '$site'
        }
    )
    members = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        required=False,
        query_params={
            'site_id': '$site',
            'rack_id': '$rack',
        }
    )
    initial_position = forms.IntegerField(
        initial=1,
        required=False,
        help_text=_('Position of the first member device. Increases by one for each additional member.')
    )

    class Meta:
        model = VirtualChassis
        fields = [
            'name', 'domain', 'description', 'region', 'site_group', 'site', 'rack', 'members', 'initial_position', 'tags',
        ]

    def clean(self):
        super().clean()

        if self.cleaned_data['members'] and self.cleaned_data['initial_position'] is None:
            raise forms.ValidationError({
                'initial_position': "A position must be specified for the first VC member."
            })

    def save(self, *args, **kwargs):
        instance = super().save(*args, **kwargs)

        # Assign VC members
        if instance.pk and self.cleaned_data['members']:
            initial_position = self.cleaned_data.get('initial_position', 1)
            for i, member in enumerate(self.cleaned_data['members'], start=initial_position):
                member.virtual_chassis = instance
                member.vc_position = i
                member.save()

        return instance
