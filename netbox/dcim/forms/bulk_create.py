from django import forms

from dcim.models import *
from django.utils.translation import gettext as _
from extras.forms import CustomFieldsMixin
from extras.models import Tag
from utilities.forms import BootstrapMixin, DynamicModelMultipleChoiceField, ExpandableNameField, form_from_model
from .object_create import ComponentCreateForm

__all__ = (
    'ConsolePortBulkCreateForm',
    'ConsoleServerPortBulkCreateForm',
    'DeviceBayBulkCreateForm',
    # 'FrontPortBulkCreateForm',
    'InterfaceBulkCreateForm',
    'InventoryItemBulkCreateForm',
    'ModuleBayBulkCreateForm',
    'PowerOutletBulkCreateForm',
    'PowerPortBulkCreateForm',
    'RearPortBulkCreateForm',
)


#
# Device components
#

class DeviceBulkAddComponentForm(BootstrapMixin, CustomFieldsMixin, ComponentCreateForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=Device.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
    description = forms.CharField(
        max_length=100,
        required=False
    )
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )
    replication_fields = ('name', 'label')


class ConsolePortBulkCreateForm(
    form_from_model(ConsolePort, ['type', 'speed', 'mark_connected']),
    DeviceBulkAddComponentForm
):
    model = ConsolePort
    field_order = ('name', 'label', 'type', 'mark_connected', 'description', 'tags')


class ConsoleServerPortBulkCreateForm(
    form_from_model(ConsoleServerPort, ['type', 'speed', 'mark_connected']),
    DeviceBulkAddComponentForm
):
    model = ConsoleServerPort
    field_order = ('name', 'label', 'type', 'speed', 'description', 'tags')


class PowerPortBulkCreateForm(
    form_from_model(PowerPort, ['type', 'maximum_draw', 'allocated_draw', 'mark_connected']),
    DeviceBulkAddComponentForm
):
    model = PowerPort
    field_order = ('name', 'label', 'type', 'maximum_draw', 'allocated_draw', 'description', 'tags')


class PowerOutletBulkCreateForm(
    form_from_model(PowerOutlet, ['type', 'feed_leg', 'mark_connected']),
    DeviceBulkAddComponentForm
):
    model = PowerOutlet
    field_order = ('name', 'label', 'type', 'feed_leg', 'description', 'tags')


class InterfaceBulkCreateForm(
    form_from_model(Interface, [
        'type', 'enabled', 'speed', 'duplex', 'mtu', 'mgmt_only', 'mark_connected', 'poe_mode', 'poe_type',
    ]),
    DeviceBulkAddComponentForm
):
    model = Interface
    field_order = (
        'name', 'label', 'type', 'enabled', 'speed', 'duplex', 'mtu', 'mgmt_only', 'poe_mode',
        'poe_type', 'mark_connected', 'description', 'tags',
    )


# class FrontPortBulkCreateForm(
#     form_from_model(FrontPort, ['label', 'type', 'description', 'tags']),
#     DeviceBulkAddComponentForm
# ):
#     pass


class RearPortBulkCreateForm(
    form_from_model(RearPort, ['type', 'color', 'positions', 'mark_connected']),
    DeviceBulkAddComponentForm
):
    model = RearPort
    field_order = ('name', 'label', 'type', 'positions', 'mark_connected', 'description', 'tags')


class ModuleBayBulkCreateForm(DeviceBulkAddComponentForm):
    model = ModuleBay
    field_order = ('name', 'label', 'position', 'description', 'tags')
    replication_fields = ('name', 'label', 'position')
    position = ExpandableNameField(
        label=_('Position'),
        required=False,
        help_text=_('Alphanumeric ranges are supported. (Must match the number of names being created.)')
    )


class DeviceBayBulkCreateForm(DeviceBulkAddComponentForm):
    model = DeviceBay
    field_order = ('name', 'label', 'description', 'tags')


class InventoryItemBulkCreateForm(
    form_from_model(InventoryItem, ['role', 'manufacturer', 'part_id', 'serial', 'asset_tag', 'discovered']),
    DeviceBulkAddComponentForm
):
    model = InventoryItem
    field_order = (
        'name', 'label', 'role', 'manufacturer', 'part_id', 'serial', 'asset_tag', 'discovered',
        'description', 'tags',
    )
