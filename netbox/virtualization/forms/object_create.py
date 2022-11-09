from utilities.forms import ExpandableNameField
from .model_forms import VMInterfaceForm

__all__ = (
    'VMInterfaceCreateForm',
)


class VMInterfaceCreateForm(VMInterfaceForm):
    name = ExpandableNameField()
    replication_fields = ('name',)

    class Meta(VMInterfaceForm.Meta):
        exclude = ('name',)
