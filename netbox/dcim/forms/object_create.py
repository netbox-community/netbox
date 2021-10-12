from django import forms

from dcim.choices import *
from dcim.constants import *
from dcim.models import *
from extras.forms import CustomFieldModelForm, CustomFieldsMixin
from extras.models import Tag
from ipam.models import VLAN
from utilities.forms import (
    add_blank_choice, BootstrapMixin, ColorField, DynamicModelChoiceField, DynamicModelMultipleChoiceField,
    ExpandableNameField, StaticSelect,
)
from .common import InterfaceCommonForm

__all__ = (
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
    'PowerOutletCreateForm',
    'PowerOutletTemplateCreateForm',
    'PowerPortCreateForm',
    'PowerPortTemplateCreateForm',
    'RearPortCreateForm',
    'RearPortTemplateCreateForm',
    'VirtualChassisCreateForm',
)


class ComponentForm(forms.Form):
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


class VirtualChassisCreateForm(BootstrapMixin, CustomFieldModelForm):
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

    def save(self, *args, **kwargs):
        instance = super().save(*args, **kwargs)

        # Assign VC members
        if instance.pk:
            initial_position = self.cleaned_data.get('initial_position') or 1
            for i, member in enumerate(self.cleaned_data['members'], start=initial_position):
                member.virtual_chassis = instance
                member.vc_position = i
                member.save()

        return instance


#
# Component templates
#

class ComponentTemplateCreateForm(BootstrapMixin, ComponentForm):
    """
    Base form for the creation of device component templates (subclassed from ComponentTemplateModel).
    """
    manufacturer = DynamicModelChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False,
        initial_params={
            'device_types': 'device_type'
        }
    )
    device_type = DynamicModelChoiceField(
        queryset=DeviceType.objects.all(),
        query_params={
            'manufacturer_id': '$manufacturer'
        }
    )
    description = forms.CharField(
        required=False
    )


class ConsolePortTemplateCreateForm(ComponentTemplateCreateForm):
    type = forms.ChoiceField(
        choices=add_blank_choice(ConsolePortTypeChoices),
        widget=StaticSelect()
    )
    field_order = ('manufacturer', 'device_type', 'name_pattern', 'label_pattern', 'type', 'description')


class ConsoleServerPortTemplateCreateForm(ComponentTemplateCreateForm):
    type = forms.ChoiceField(
        choices=add_blank_choice(ConsolePortTypeChoices),
        widget=StaticSelect()
    )
    field_order = ('manufacturer', 'device_type', 'name_pattern', 'label_pattern', 'type', 'description')


class PowerPortTemplateCreateForm(ComponentTemplateCreateForm):
    type = forms.ChoiceField(
        choices=add_blank_choice(PowerPortTypeChoices),
        required=False
    )
    maximum_draw = forms.IntegerField(
        min_value=1,
        required=False,
        help_text="Maximum power draw (watts)"
    )
    allocated_draw = forms.IntegerField(
        min_value=1,
        required=False,
        help_text="Allocated power draw (watts)"
    )
    field_order = (
        'manufacturer', 'device_type', 'name_pattern', 'label_pattern', 'type', 'maximum_draw', 'allocated_draw',
        'description',
    )


class PowerOutletTemplateCreateForm(ComponentTemplateCreateForm):
    type = forms.ChoiceField(
        choices=add_blank_choice(PowerOutletTypeChoices),
        required=False
    )
    power_port = forms.ModelChoiceField(
        queryset=PowerPortTemplate.objects.all(),
        required=False
    )
    feed_leg = forms.ChoiceField(
        choices=add_blank_choice(PowerOutletFeedLegChoices),
        required=False,
        widget=StaticSelect()
    )
    field_order = (
        'manufacturer', 'device_type', 'name_pattern', 'label_pattern', 'type', 'power_port', 'feed_leg',
        'description',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Limit power_port choices to current DeviceType
        device_type = DeviceType.objects.get(
            pk=self.initial.get('device_type') or self.data.get('device_type')
        )
        self.fields['power_port'].queryset = PowerPortTemplate.objects.filter(
            device_type=device_type
        )


class InterfaceTemplateCreateForm(ComponentTemplateCreateForm):
    type = forms.ChoiceField(
        choices=InterfaceTypeChoices,
        widget=StaticSelect()
    )
    mgmt_only = forms.BooleanField(
        required=False,
        label='Management only'
    )
    field_order = ('manufacturer', 'device_type', 'name_pattern', 'label_pattern', 'type', 'mgmt_only', 'description')


class FrontPortTemplateCreateForm(ComponentTemplateCreateForm):
    type = forms.ChoiceField(
        choices=PortTypeChoices,
        widget=StaticSelect()
    )
    color = ColorField(
        required=False
    )
    rear_port_set = forms.MultipleChoiceField(
        choices=[],
        label='Rear ports',
        help_text='Select one rear port assignment for each front port being created.',
    )
    field_order = (
        'manufacturer', 'device_type', 'name_pattern', 'label_pattern', 'type', 'color', 'rear_port_set', 'description',
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

    def clean(self):
        super().clean()

        # Validate that the number of ports being created equals the number of selected (rear port, position) tuples
        front_port_count = len(self.cleaned_data['name_pattern'])
        rear_port_count = len(self.cleaned_data['rear_port_set'])
        if front_port_count != rear_port_count:
            raise forms.ValidationError({
                'rear_port_set': 'The provided name pattern will create {} ports, however {} rear port assignments '
                                 'were selected. These counts must match.'.format(front_port_count, rear_port_count)
            })

    def get_iterative_data(self, iteration):

        # Assign rear port and position from selected set
        rear_port, position = self.cleaned_data['rear_port_set'][iteration].split(':')

        return {
            'rear_port': int(rear_port),
            'rear_port_position': int(position),
        }


class RearPortTemplateCreateForm(ComponentTemplateCreateForm):
    type = forms.ChoiceField(
        choices=PortTypeChoices,
        widget=StaticSelect(),
    )
    color = ColorField(
        required=False
    )
    positions = forms.IntegerField(
        min_value=REARPORT_POSITIONS_MIN,
        max_value=REARPORT_POSITIONS_MAX,
        initial=1,
        help_text='The number of front ports which may be mapped to each rear port'
    )
    field_order = (
        'manufacturer', 'device_type', 'name_pattern', 'label_pattern', 'type', 'color', 'positions', 'description',
    )


class DeviceBayTemplateCreateForm(ComponentTemplateCreateForm):
    field_order = ('manufacturer', 'device_type', 'name_pattern', 'label_pattern', 'description')


#
# Device components
#

class ComponentCreateForm(BootstrapMixin, CustomFieldsMixin, ComponentForm):
    """
    Base form for the creation of device components (models subclassed from ComponentModel).
    """
    device = DynamicModelChoiceField(
        queryset=Device.objects.all()
    )
    description = forms.CharField(
        max_length=200,
        required=False
    )
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )


class ConsolePortCreateForm(ComponentCreateForm):
    model = ConsolePort
    type = forms.ChoiceField(
        choices=add_blank_choice(ConsolePortTypeChoices),
        required=False,
        widget=StaticSelect()
    )
    speed = forms.ChoiceField(
        choices=add_blank_choice(ConsolePortSpeedChoices),
        required=False,
        widget=StaticSelect()
    )
    field_order = ('device', 'name_pattern', 'label_pattern', 'type', 'speed', 'mark_connected', 'description', 'tags')


class ConsoleServerPortCreateForm(ComponentCreateForm):
    model = ConsoleServerPort
    type = forms.ChoiceField(
        choices=add_blank_choice(ConsolePortTypeChoices),
        required=False,
        widget=StaticSelect()
    )
    speed = forms.ChoiceField(
        choices=add_blank_choice(ConsolePortSpeedChoices),
        required=False,
        widget=StaticSelect()
    )
    field_order = ('device', 'name_pattern', 'label_pattern', 'type', 'speed', 'mark_connected', 'description', 'tags')


class PowerPortCreateForm(ComponentCreateForm):
    model = PowerPort
    type = forms.ChoiceField(
        choices=add_blank_choice(PowerPortTypeChoices),
        required=False,
        widget=StaticSelect()
    )
    maximum_draw = forms.IntegerField(
        min_value=1,
        required=False,
        help_text="Maximum draw in watts"
    )
    allocated_draw = forms.IntegerField(
        min_value=1,
        required=False,
        help_text="Allocated draw in watts"
    )
    field_order = (
        'device', 'name_pattern', 'label_pattern', 'type', 'maximum_draw', 'allocated_draw', 'mark_connected',
        'description', 'tags',
    )


class PowerOutletCreateForm(ComponentCreateForm):
    model = PowerOutlet
    type = forms.ChoiceField(
        choices=add_blank_choice(PowerOutletTypeChoices),
        required=False,
        widget=StaticSelect()
    )
    power_port = forms.ModelChoiceField(
        queryset=PowerPort.objects.all(),
        required=False
    )
    feed_leg = forms.ChoiceField(
        choices=add_blank_choice(PowerOutletFeedLegChoices),
        required=False
    )
    field_order = (
        'device', 'name_pattern', 'label_pattern', 'type', 'power_port', 'feed_leg', 'mark_connected', 'description',
        'tags',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Limit power_port queryset to PowerPorts which belong to the parent Device
        device = Device.objects.get(
            pk=self.initial.get('device') or self.data.get('device')
        )
        self.fields['power_port'].queryset = PowerPort.objects.filter(device=device)


class InterfaceCreateForm(ComponentCreateForm, InterfaceCommonForm):
    model = Interface
    type = forms.ChoiceField(
        choices=InterfaceTypeChoices,
        widget=StaticSelect(),
    )
    enabled = forms.BooleanField(
        required=False,
        initial=True
    )
    parent = DynamicModelChoiceField(
        queryset=Interface.objects.all(),
        required=False,
        query_params={
            'device_id': '$device',
        }
    )
    lag = DynamicModelChoiceField(
        queryset=Interface.objects.all(),
        required=False,
        query_params={
            'device_id': '$device',
            'type': 'lag',
        }
    )
    mac_address = forms.CharField(
        required=False,
        label='MAC Address'
    )
    mgmt_only = forms.BooleanField(
        required=False,
        label='Management only',
        help_text='This interface is used only for out-of-band management'
    )
    mode = forms.ChoiceField(
        choices=add_blank_choice(InterfaceModeChoices),
        required=False,
        widget=StaticSelect()
    )
    rf_channel = forms.ChoiceField(
        choices=add_blank_choice(WirelessChannelChoices),
        required=False,
        widget=StaticSelect(),
        label='Wireless channel'
    )
    rf_channel_width = forms.ChoiceField(
        choices=add_blank_choice(WirelessChannelWidthChoices),
        required=False,
        widget=StaticSelect(),
        label='Channel width'
    )
    untagged_vlan = DynamicModelChoiceField(
        queryset=VLAN.objects.all(),
        required=False
    )
    tagged_vlans = DynamicModelMultipleChoiceField(
        queryset=VLAN.objects.all(),
        required=False
    )
    field_order = (
        'device', 'name_pattern', 'label_pattern', 'type', 'enabled', 'parent', 'lag', 'mtu', 'mac_address',
        'description', 'mgmt_only', 'mark_connected', 'rf_channel', 'rf_channel_width', 'mode' 'untagged_vlan',
        'tagged_vlans', 'tags'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Limit VLAN choices by device
        device_id = self.initial.get('device') or self.data.get('device')
        self.fields['untagged_vlan'].widget.add_query_param('available_on_device', device_id)
        self.fields['tagged_vlans'].widget.add_query_param('available_on_device', device_id)


class FrontPortCreateForm(ComponentCreateForm):
    model = FrontPort
    type = forms.ChoiceField(
        choices=PortTypeChoices,
        widget=StaticSelect(),
    )
    color = ColorField(
        required=False
    )
    rear_port_set = forms.MultipleChoiceField(
        choices=[],
        label='Rear ports',
        help_text='Select one rear port assignment for each front port being created.',
    )
    field_order = (
        'device', 'name_pattern', 'label_pattern', 'type', 'color', 'rear_port_set', 'mark_connected', 'description',
        'tags',
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

    def clean(self):
        super().clean()

        # Validate that the number of ports being created equals the number of selected (rear port, position) tuples
        front_port_count = len(self.cleaned_data['name_pattern'])
        rear_port_count = len(self.cleaned_data['rear_port_set'])
        if front_port_count != rear_port_count:
            raise forms.ValidationError({
                'rear_port_set': 'The provided name pattern will create {} ports, however {} rear port assignments '
                                 'were selected. These counts must match.'.format(front_port_count, rear_port_count)
            })

    def get_iterative_data(self, iteration):

        # Assign rear port and position from selected set
        rear_port, position = self.cleaned_data['rear_port_set'][iteration].split(':')

        return {
            'rear_port': int(rear_port),
            'rear_port_position': int(position),
        }


class RearPortCreateForm(ComponentCreateForm):
    model = RearPort
    type = forms.ChoiceField(
        choices=PortTypeChoices,
        widget=StaticSelect(),
    )
    color = ColorField(
        required=False
    )
    positions = forms.IntegerField(
        min_value=REARPORT_POSITIONS_MIN,
        max_value=REARPORT_POSITIONS_MAX,
        initial=1,
        help_text='The number of front ports which may be mapped to each rear port'
    )
    field_order = (
        'device', 'name_pattern', 'label_pattern', 'type', 'color', 'positions', 'mark_connected', 'description',
        'tags',
    )


class DeviceBayCreateForm(ComponentCreateForm):
    model = DeviceBay
    field_order = ('device', 'name_pattern', 'label_pattern', 'description', 'tags')


class InventoryItemCreateForm(ComponentCreateForm):
    model = InventoryItem
    manufacturer = DynamicModelChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False
    )
    parent = DynamicModelChoiceField(
        queryset=InventoryItem.objects.all(),
        required=False,
        query_params={
            'device_id': '$device'
        }
    )
    part_id = forms.CharField(
        max_length=50,
        required=False,
        label='Part ID'
    )
    serial = forms.CharField(
        max_length=50,
        required=False,
    )
    asset_tag = forms.CharField(
        max_length=50,
        required=False,
    )
    field_order = (
        'device', 'parent', 'name_pattern', 'label_pattern', 'manufacturer', 'part_id', 'serial', 'asset_tag',
        'description', 'tags',
    )
