from django import forms

from dcim.choices import LinkStatusChoices
from ipam.models import VLAN
from netbox.forms import NetBoxModelBulkEditForm
from utilities.forms import add_blank_choice, DynamicModelChoiceField
from wireless.choices import *
from wireless.constants import SSID_MAX_LENGTH
from wireless.models import *

__all__ = (
    'WirelessLANBulkEditForm',
    'WirelessLANGroupBulkEditForm',
    'WirelessLinkBulkEditForm',
)


class WirelessLANGroupBulkEditForm(NetBoxModelBulkEditForm):
    parent = DynamicModelChoiceField(
        queryset=WirelessLANGroup.objects.all(),
        required=False
    )
    description = forms.CharField(
        max_length=200,
        required=False
    )

    model = WirelessLANGroup
    fieldsets = (
        (None, ('parent', 'description')),
    )
    nullable_fields = ('parent', 'description')


class WirelessLANBulkEditForm(NetBoxModelBulkEditForm):
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

    model = WirelessLAN
    fieldsets = (
        (None, ('group', 'vlan', 'ssid', 'description')),
        ('Authentication', ('auth_type', 'auth_cipher', 'auth_psk')),
    )
    nullable_fields = (
        'ssid', 'group', 'vlan', 'description', 'auth_type', 'auth_cipher', 'auth_psk',
    )


class WirelessLinkBulkEditForm(NetBoxModelBulkEditForm):
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

    model = WirelessLink
    fieldsets = (
        (None, ('ssid', 'status', 'description')),
        ('Authentication', ('auth_type', 'auth_cipher', 'auth_psk'))
    )
    nullable_fields = (
        'ssid', 'description', 'auth_type', 'auth_cipher', 'auth_psk',
    )
