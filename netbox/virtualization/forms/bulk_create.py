from django import forms

from utilities.forms import BootstrapMixin, ExpandableNameField, form_from_model
from virtualization.models import VMInterface, VirtualMachine

__all__ = (
    'VMInterfaceBulkCreateForm',
)


class VirtualMachineBulkAddComponentForm(BootstrapMixin, forms.Form):
    pk = forms.ModelMultipleChoiceField(
        queryset=VirtualMachine.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
    name_pattern = ExpandableNameField(
        label='Name'
    )

    def clean_tags(self):
        # Because we're feeding TagField data (on the bulk edit form) to another TagField (on the model form), we
        # must first convert the list of tags to a string.
        return ','.join(self.cleaned_data.get('tags'))


class VMInterfaceBulkCreateForm(
    form_from_model(VMInterface, ['enabled', 'mtu', 'description', 'tags']),
    VirtualMachineBulkAddComponentForm
):
    pass
