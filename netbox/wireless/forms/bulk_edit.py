from django import forms

from dcim.choices import LinkStatusChoices
from extras.forms import AddRemoveTagsForm, CustomFieldModelBulkEditForm
from ipam.models import VLAN
from utilities.forms import BootstrapMixin, DynamicModelChoiceField
from wireless.choices import *
from wireless.constants import SSID_MAX_LENGTH
from wireless.models import *

__all__ = (
    'WirelessLANBulkEditForm',
    'WirelessLANGroupBulkEditForm',
    'WirelessLinkBulkEditForm',
)


class WirelessLANGroupBulkEditForm(BootstrapMixin, AddRemoveTagsForm, CustomFieldModelBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=WirelessLANGroup.objects.all(),
        widget=forms.MultipleHiddenInput
    )
    parent = DynamicModelChoiceField(
        queryset=WirelessLANGroup.objects.all(),
        required=False
    )
    description = forms.CharField(
        max_length=200,
        required=False
    )

    class Meta:
        nullable_fields = ['parent', 'description']


class WirelessLANBulkEditForm(BootstrapMixin, AddRemoveTagsForm, CustomFieldModelBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=WirelessLAN.objects.all(),
        widget=forms.MultipleHiddenInput
    )
    group = DynamicModelChoiceField(
        queryset=WirelessLANGroup.objects.all(),
        required=False
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
    auth_type = forms.ChoiceField(
        choices=WirelessAuthTypeChoices,
        required=False
    )
    auth_cipher = forms.ChoiceField(
        choices=WirelessAuthCipherChoices,
        required=False
    )
    auth_psk = forms.CharField(
        required=False
    )

    class Meta:
        nullable_fields = ['ssid', 'group', 'vlan', 'description', 'auth_type', 'auth_cipher', 'auth_psk']


class WirelessLinkBulkEditForm(BootstrapMixin, AddRemoveTagsForm, CustomFieldModelBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=WirelessLink.objects.all(),
        widget=forms.MultipleHiddenInput
    )
    ssid = forms.CharField(
        max_length=SSID_MAX_LENGTH,
        required=False
    )
    status = forms.ChoiceField(
        choices=LinkStatusChoices,
        required=False
    )
    description = forms.CharField(
        required=False
    )
    auth_type = forms.ChoiceField(
        choices=WirelessAuthTypeChoices,
        required=False
    )
    auth_cipher = forms.ChoiceField(
        choices=WirelessAuthCipherChoices,
        required=False
    )
    auth_psk = forms.CharField(
        required=False
    )

    class Meta:
        nullable_fields = ['ssid', 'description', 'auth_type', 'auth_cipher', 'auth_psk']
