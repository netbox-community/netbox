from django.utils.translation import gettext_lazy as _
from utilities.forms.fields import ExpandableNameField
from .model_forms import VMInterfaceForm

__all__ = (
    'VMInterfaceCreateForm',
)


class VMInterfaceCreateForm(VMInterfaceForm):
    name = ExpandableNameField(
        label=_('Name'),
    )
    replication_fields = ('name',)

    class Meta(VMInterfaceForm.Meta):
        exclude = ('name',)
