from django import forms

from dcim.models import *
from extras.forms import AddRemoveTagsForm, CustomFieldModelBulkEditForm
from ipam.models import VLAN
from utilities.forms import BootstrapMixin, DynamicModelChoiceField
from wireless.constants import SSID_MAX_LENGTH

__all__ = (
    'WirelessLANBulkEditForm',
    'WirelessLinkBulkEditForm',
)


class WirelessLANBulkEditForm(BootstrapMixin, AddRemoveTagsForm, CustomFieldModelBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=PowerFeed.objects.all(),
        widget=forms.MultipleHiddenInput
    )
    vlan = DynamicModelChoiceField(
        queryset=VLAN.objects.all(),
        required=False,
    )
    ssid = forms.CharField(
        max_length=SSID_MAX_LENGTH,
        required=False
    )
    description = forms.CharField(
        required=False
    )

    class Meta:
        nullable_fields = ['vlan', 'ssid', 'description']


class WirelessLinkBulkEditForm(BootstrapMixin, AddRemoveTagsForm, CustomFieldModelBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=PowerFeed.objects.all(),
        widget=forms.MultipleHiddenInput
    )
    ssid = forms.CharField(
        max_length=SSID_MAX_LENGTH,
        required=False
    )
    description = forms.CharField(
        required=False
    )

    class Meta:
        nullable_fields = ['ssid', 'description']
