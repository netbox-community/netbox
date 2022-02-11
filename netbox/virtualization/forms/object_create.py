from django import forms

from dcim.choices import InterfaceModeChoices
from dcim.forms.common import InterfaceCommonForm
from extras.forms import CustomFieldsMixin
from extras.models import Tag
from ipam.models import VLAN
from utilities.forms import (
    add_blank_choice, BootstrapMixin, DynamicModelChoiceField, DynamicModelMultipleChoiceField, ExpandableNameField,
    StaticSelect,
)
from virtualization.models import VMInterface, VirtualMachine

__all__ = (
    'VMInterfaceCreateForm',
)


class VMInterfaceCreateForm(BootstrapMixin, CustomFieldsMixin, InterfaceCommonForm):
    model = VMInterface
    virtual_machine = DynamicModelChoiceField(
        queryset=VirtualMachine.objects.all()
    )
    name_pattern = ExpandableNameField(
        label='Name'
    )
    enabled = forms.BooleanField(
        required=False,
        initial=True
    )
    parent = DynamicModelChoiceField(
        queryset=VMInterface.objects.all(),
        required=False,
        query_params={
            'virtual_machine_id': '$virtual_machine',
        }
    )
    bridge = DynamicModelChoiceField(
        queryset=VMInterface.objects.all(),
        required=False,
        query_params={
            'virtual_machine_id': '$virtual_machine',
        }
    )
    mac_address = forms.CharField(
        required=False,
        label='MAC Address'
    )
    description = forms.CharField(
        max_length=200,
        required=False
    )
    mode = forms.ChoiceField(
        choices=add_blank_choice(InterfaceModeChoices),
        required=False,
        widget=StaticSelect(),
    )
    untagged_vlan = DynamicModelChoiceField(
        queryset=VLAN.objects.all(),
        required=False
    )
    tagged_vlans = DynamicModelMultipleChoiceField(
        queryset=VLAN.objects.all(),
        required=False
    )
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )
    field_order = (
        'virtual_machine', 'name_pattern', 'enabled', 'parent', 'bridge', 'mtu', 'mac_address', 'description', 'mode',
        'untagged_vlan', 'tagged_vlans', 'tags'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        vm_id = self.initial.get('virtual_machine') or self.data.get('virtual_machine')

        # Limit VLAN choices by virtual machine
        self.fields['untagged_vlan'].widget.add_query_param('available_on_virtualmachine', vm_id)
        self.fields['tagged_vlans'].widget.add_query_param('available_on_virtualmachine', vm_id)
