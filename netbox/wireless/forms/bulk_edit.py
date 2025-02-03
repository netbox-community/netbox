from django import forms
from django.utils.translation import gettext_lazy as _

from dcim.choices import LinkStatusChoices
from dcim.forms.mixins import ScopedBulkEditForm
from ipam.models import VLAN
from netbox.choices import *
from netbox.forms import NetBoxModelBulkEditForm
from tenancy.models import Tenant
from utilities.forms import add_blank_choice
from utilities.forms.fields import CommentField, DynamicModelChoiceField
from utilities.forms.rendering import FieldSet
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
        label=_('Parent'),
        queryset=WirelessLANGroup.objects.all(),
        required=False
    )
    description = forms.CharField(
        label=_('Description'),
        max_length=200,
        required=False
    )

    model = WirelessLANGroup
    fieldsets = (
        FieldSet('parent', 'description'),
    )
    nullable_fields = ('parent', 'description')


class WirelessLANBulkEditForm(ScopedBulkEditForm, NetBoxModelBulkEditForm):
    status = forms.ChoiceField(
        label=_('Status'),
        choices=add_blank_choice(WirelessLANStatusChoices),
        required=False
    )
    group = DynamicModelChoiceField(
        label=_('Group'),
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
        label=_('Tenant'),
        queryset=Tenant.objects.all(),
        required=False
    )
    auth_type = forms.ChoiceField(
        label=_('Authentication type'),
        choices=add_blank_choice(WirelessAuthTypeChoices),
        required=False
    )
    auth_cipher = forms.ChoiceField(
        label=_('Authentication cipher'),
        choices=add_blank_choice(WirelessAuthCipherChoices),
        required=False
    )
    auth_psk = forms.CharField(
        required=False,
        label=_('Pre-shared key')
    )
    description = forms.CharField(
        label=_('Description'),
        max_length=200,
        required=False
    )
    comments = CommentField()

    model = WirelessLAN
    fieldsets = (
        FieldSet('group', 'ssid', 'status', 'vlan', 'tenant', 'description'),
        FieldSet('scope_type', 'scope', name=_('Scope')),
        FieldSet('auth_type', 'auth_cipher', 'auth_psk', name=_('Authentication')),
    )
    nullable_fields = (
        'ssid', 'group', 'vlan', 'tenant', 'description', 'auth_type', 'auth_cipher', 'auth_psk', 'scope', 'comments',
    )


class WirelessLinkBulkEditForm(NetBoxModelBulkEditForm):
    ssid = forms.CharField(
        max_length=SSID_MAX_LENGTH,
        required=False,
        label=_('SSID')
    )
    status = forms.ChoiceField(
        label=_('Status'),
        choices=add_blank_choice(LinkStatusChoices),
        required=False
    )
    tenant = DynamicModelChoiceField(
        label=_('Tenant'),
        queryset=Tenant.objects.all(),
        required=False
    )
    auth_type = forms.ChoiceField(
        label=_('Authentication type'),
        choices=add_blank_choice(WirelessAuthTypeChoices),
        required=False
    )
    auth_cipher = forms.ChoiceField(
        label=_('Authentication cipher'),
        choices=add_blank_choice(WirelessAuthCipherChoices),
        required=False
    )
    auth_psk = forms.CharField(
        required=False,
        label=_('Pre-shared key')
    )
    distance = forms.DecimalField(
        label=_('Distance'),
        min_value=0,
        required=False
    )
    distance_unit = forms.ChoiceField(
        label=_('Distance unit'),
        choices=add_blank_choice(DistanceUnitChoices),
        required=False,
        initial=''
    )
    description = forms.CharField(
        label=_('Description'),
        max_length=200,
        required=False
    )
    comments = CommentField()

    model = WirelessLink
    fieldsets = (
        FieldSet('ssid', 'status', 'tenant', 'description'),
        FieldSet('auth_type', 'auth_cipher', 'auth_psk', name=_('Authentication')),
        FieldSet('distance', 'distance_unit', name=_('Attributes')),
    )
    nullable_fields = (
        'ssid', 'tenant', 'description', 'auth_type', 'auth_cipher', 'auth_psk', 'distance', 'comments',
    )
