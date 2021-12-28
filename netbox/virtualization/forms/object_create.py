from django import forms

from utilities.forms import BootstrapMixin, ExpandableNameField

__all__ = (
    'VMInterfaceCreateForm',
)


class VMInterfaceCreateForm(BootstrapMixin, forms.Form):
    name_pattern = ExpandableNameField(
        label='Name'
    )
