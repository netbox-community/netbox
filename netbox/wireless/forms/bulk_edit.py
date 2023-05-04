from django import forms
from django.utils.translation import gettext as _

from dcim.choices import LinkStatusChoices
from ipam.models import VLAN
from netbox.forms import NetBoxModelBulkEditForm
from tenancy.models import Tenant
from utilities.forms import add_blank_choice
from utilities.forms.fields import CommentField, DynamicModelChoiceField
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
    status = forms.ChoiceField(
        choices=add_blank_choice(WirelessLANStatusChoices),
        required=False
    )
    group = DynamicModelChoiceField(
        queryset=WirelessLANGroup.objects.all(),
        required=False
    )
    vlan = DynamicModelChoiceField(
        queryset=VLAN.objects.all(),
        required=False,
        label=_('VLAN')
    )
    ssid = forms.CharField(
        max_length=SSID_MAX_LENGTH,
        required=False,
        label=_('SSID')
    )
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
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
        label=_('Pre-shared key')
    )
    description = forms.CharField(
        max_length=200,
        required=False
    )
    comments = CommentField(
        label='Comments'
    )

    model = WirelessLAN
    fieldsets = (
        (None, ('group', 'ssid', 'status', 'vlan', 'tenant', 'description')),
        ('Authentication', ('auth_type', 'auth_cipher', 'auth_psk')),
    )
    nullable_fields = (
        'ssid', 'group', 'vlan', 'tenant', 'description', 'auth_type', 'auth_cipher', 'auth_psk', 'comments',
    )


class WirelessLinkBulkEditForm(NetBoxModelBulkEditForm):
    ssid = forms.CharField(
        max_length=SSID_MAX_LENGTH,
        required=False,
        label=_('SSID')
    )
    status = forms.ChoiceField(
        choices=add_blank_choice(LinkStatusChoices),
        required=False
    )
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
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
        label=_('Pre-shared key')
    )
    description = forms.CharField(
        max_length=200,
        required=False
    )
    comments = CommentField(
        label='Comments'
    )

    model = WirelessLink
    fieldsets = (
        (None, ('ssid', 'status', 'tenant', 'description')),
        ('Authentication', ('auth_type', 'auth_cipher', 'auth_psk'))
    )
    nullable_fields = (
        'ssid', 'tenant', 'description', 'auth_type', 'auth_cipher', 'auth_psk', 'comments',
    )
