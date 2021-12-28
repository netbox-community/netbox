from django import forms

from utilities.forms import BootstrapMixin, DynamicModelChoiceField, ExpandableNameField
from .models import VirtualMachine

__all__ = (
    'VMInterfaceCreateForm',
)


class VMInterfaceCreateForm(BootstrapMixin, forms.Form):
    virtual_machine = DynamicModelChoiceField(
        queryset=VirtualMachine.objects.all()
    )
    name_pattern = ExpandableNameField(
        label='Name'
    )
