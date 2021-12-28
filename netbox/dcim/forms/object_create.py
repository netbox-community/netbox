from django import forms

from dcim.models import *
from extras.forms import CustomFieldModelForm
from extras.models import Tag
from utilities.forms import (
    BootstrapMixin, DynamicModelChoiceField, DynamicModelMultipleChoiceField, ExpandableNameField,
)

__all__ = (
    'DeviceComponentCreateForm',
    'DeviceTypeComponentCreateForm',
    'FrontPortCreateForm',
    'FrontPortTemplateCreateForm',
    'VirtualChassisCreateForm',
)


class ComponentCreateForm(BootstrapMixin, forms.Form):
    """
    Subclass this form when facilitating the creation of one or more device component or component templates based on
    a name pattern.
    """
    name_pattern = ExpandableNameField(
        label='Name'
    )
    label_pattern = ExpandableNameField(
        label='Label',
        required=False,
        help_text='Alphanumeric ranges are supported. (Must match the number of names being created.)'
    )

    def clean(self):
        super().clean()

        # Validate that the number of components being created from both the name_pattern and label_pattern are equal
        if self.cleaned_data['label_pattern']:
            name_pattern_count = len(self.cleaned_data['name_pattern'])
            label_pattern_count = len(self.cleaned_data['label_pattern'])
            if name_pattern_count != label_pattern_count:
                raise forms.ValidationError({
                    'label_pattern': f'The provided name pattern will create {name_pattern_count} components, however '
                                     f'{label_pattern_count} labels will be generated. These counts must match.'
                }, code='label_pattern_mismatch')


class DeviceTypeComponentCreateForm(ComponentCreateForm):
    device_type = DynamicModelChoiceField(
        queryset=DeviceType.objects.all(),
    )
    field_order = ('device_type', 'name_pattern', 'label_pattern')


class DeviceComponentCreateForm(ComponentCreateForm):
    device = DynamicModelChoiceField(
        queryset=Device.objects.all()
    )
    field_order = ('device', 'name_pattern', 'label_pattern')


class FrontPortTemplateCreateForm(DeviceTypeComponentCreateForm):
    rear_port_set = forms.MultipleChoiceField(
        choices=[],
        label='Rear ports',
        help_text='Select one rear port assignment for each front port being created.',
    )
    field_order = (
        'device_type', 'name_pattern', 'label_pattern', 'rear_port_set',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        device_type = DeviceType.objects.get(
            pk=self.initial.get('device_type') or self.data.get('device_type')
        )

        # Determine which rear port positions are occupied. These will be excluded from the list of available mappings.
        occupied_port_positions = [
            (front_port.rear_port_id, front_port.rear_port_position)
            for front_port in device_type.frontporttemplates.all()
        ]

        # Populate rear port choices
        choices = []
        rear_ports = RearPortTemplate.objects.filter(device_type=device_type)
        for rear_port in rear_ports:
            for i in range(1, rear_port.positions + 1):
                if (rear_port.pk, i) not in occupied_port_positions:
                    choices.append(
                        ('{}:{}'.format(rear_port.pk, i), '{}:{}'.format(rear_port.name, i))
                    )
        self.fields['rear_port_set'].choices = choices

    def get_iterative_data(self, iteration):

        # Assign rear port and position from selected set
        rear_port, position = self.cleaned_data['rear_port_set'][iteration].split(':')

        return {
            'rear_port': int(rear_port),
            'rear_port_position': int(position),
        }


class FrontPortCreateForm(DeviceComponentCreateForm):
    rear_port_set = forms.MultipleChoiceField(
        choices=[],
        label='Rear ports',
        help_text='Select one rear port assignment for each front port being created.',
    )
    field_order = (
        'device', 'name_pattern', 'label_pattern', 'rear_port_set',
    )

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
        self.fields['rear_port_set'].choices = choices

    def get_iterative_data(self, iteration):

        # Assign rear port and position from selected set
        rear_port, position = self.cleaned_data['rear_port_set'][iteration].split(':')

        return {
            'rear_port': int(rear_port),
            'rear_port_position': int(position),
        }


class VirtualChassisCreateForm(CustomFieldModelForm):
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
        help_text='Position of the first member device. Increases by one for each additional member.'
    )
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = VirtualChassis
        fields = [
            'name', 'domain', 'region', 'site_group', 'site', 'rack', 'members', 'initial_position', 'tags',
        ]

    def clean(self):
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
