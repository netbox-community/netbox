from django import forms

from dcim.choices import LinkStatusChoices
from extras.forms import AddRemoveTagsForm, CustomFieldModelBulkEditForm
from ipam.models import VLAN
from utilities.forms import add_blank_choice, DynamicModelChoiceField
from wireless.choices import *
from wireless.constants import SSID_MAX_LENGTH
from wireless.models import *

__all__ = (
    'WirelessLANBulkEditForm',
    'WirelessLANGroupBulkEditForm',
    'WirelessLinkBulkEditForm',
)


class WirelessLANGroupBulkEditForm(AddRemoveTagsForm, CustomFieldModelBulkEditForm):
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


class WirelessLANBulkEditForm(AddRemoveTagsForm, CustomFieldModelBulkEditForm):
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
        label='VLAN'
    )
    ssid = forms.CharField(
        max_length=SSID_MAX_LENGTH,
        required=False,
        label='SSID'
    )
    description = forms.CharField(
        required=False
    )
    auth_type = forms.ChoiceField(
        choices=add_blank_choice(WirelessAuthTypeChoices),
        required=False
    )
    auth_cipher = forms.ChoiceField(
        choices=add_blank_choice(WirelessAuthCipherChoices),
        required=False
    )
    auth_psk = forms.CharField(
        required=False,
        label='Pre-shared key'
    )

    class Meta:
        nullable_fields = ['ssid', 'group', 'vlan', 'description', 'auth_type', 'auth_cipher', 'auth_psk']


class WirelessLinkBulkEditForm(AddRemoveTagsForm, CustomFieldModelBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=WirelessLink.objects.all(),
        widget=forms.MultipleHiddenInput
    )
    ssid = forms.CharField(
        max_length=SSID_MAX_LENGTH,
        required=False,
        label='SSID'
    )
    status = forms.ChoiceField(
        choices=add_blank_choice(LinkStatusChoices),
        required=False
    )
    description = forms.CharField(
        required=False
    )
    auth_type = forms.ChoiceField(
        choices=add_blank_choice(WirelessAuthTypeChoices),
        required=False
    )
    auth_cipher = forms.ChoiceField(
        choices=add_blank_choice(WirelessAuthCipherChoices),
        required=False
    )
    auth_psk = forms.CharField(
        required=False,
        label='Pre-shared key'
    )

    class Meta:
        nullable_fields = ['ssid', 'description', 'auth_type', 'auth_cipher', 'auth_psk']
