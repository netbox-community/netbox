from django import forms

from dcim.models import *
from extras.forms import AddRemoveTagsForm, CustomFieldModelBulkEditForm
from ipam.models import VLAN
from utilities.forms import BootstrapMixin, DynamicModelChoiceField

__all__ = (
    'SSIDBulkEditForm',
)


class SSIDBulkEditForm(BootstrapMixin, AddRemoveTagsForm, CustomFieldModelBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=PowerFeed.objects.all(),
        widget=forms.MultipleHiddenInput
    )
    vlan = DynamicModelChoiceField(
        queryset=VLAN.objects.all(),
        required=False,
    )
    description = forms.CharField(
        required=False
    )

    class Meta:
        nullable_fields = [
            'vlan', 'description',
        ]
