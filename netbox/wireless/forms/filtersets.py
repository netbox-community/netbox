from django import forms
from django.utils.translation import gettext_lazy as _

from dcim.choices import LinkStatusChoices
from netbox.forms import NetBoxModelFilterSetForm
from tenancy.forms import TenancyFilterForm
from utilities.forms import add_blank_choice
from utilities.forms.fields import DynamicModelMultipleChoiceField, TagFilterField
from utilities.forms.rendering import FieldSet
from wireless.choices import *
from wireless.models import *

__all__ = (
    'WirelessLANFilterForm',
    'WirelessLANGroupFilterForm',
    'WirelessLinkFilterForm',
)


class WirelessLANGroupFilterForm(NetBoxModelFilterSetForm):
    model = WirelessLANGroup
    parent_id = DynamicModelMultipleChoiceField(
        queryset=WirelessLANGroup.objects.all(),
        required=False,
        label=_('Parent group')
    )
    tag = TagFilterField(model)


class WirelessLANFilterForm(TenancyFilterForm, NetBoxModelFilterSetForm):
    model = WirelessLAN
    fieldsets = (
        FieldSet('q', 'filter_id', 'tag'),
        FieldSet('ssid', 'group_id', 'status', name=_('Attributes')),
        FieldSet('tenant_group_id', 'tenant_id', name=_('Tenant')),
        FieldSet('auth_type', 'auth_cipher', 'auth_psk', name=_('Authentication')),
    )
    ssid = forms.CharField(
        required=False,
        label=_('SSID')
    )
    group_id = DynamicModelMultipleChoiceField(
        queryset=WirelessLANGroup.objects.all(),
        required=False,
        null_option='None',
        label=_('Group')
    )
    status = forms.ChoiceField(
        label=_('Status'),
        required=False,
        choices=add_blank_choice(WirelessLANStatusChoices)
    )
    auth_type = forms.ChoiceField(
        label=_('Authentication type'),
        required=False,
        choices=add_blank_choice(WirelessAuthTypeChoices)
    )
    auth_cipher = forms.ChoiceField(
        label=_('Authentication cipher'),
        required=False,
        choices=add_blank_choice(WirelessAuthCipherChoices)
    )
    auth_psk = forms.CharField(
        label=_('Pre-shared key'),
        required=False
    )
    tag = TagFilterField(model)


class WirelessLinkFilterForm(TenancyFilterForm, NetBoxModelFilterSetForm):
    model = WirelessLink
    fieldsets = (
        FieldSet('q', 'filter_id', 'tag'),
        FieldSet('ssid', 'status', name=_('Attributes')),
        FieldSet('tenant_group_id', 'tenant_id', name=_('Tenant')),
        FieldSet('auth_type', 'auth_cipher', 'auth_psk', name=_('Authentication')),
    )
    ssid = forms.CharField(
        required=False,
        label=_('SSID')
    )
    status = forms.ChoiceField(
        label=_('Status'),
        required=False,
        choices=add_blank_choice(LinkStatusChoices)
    )
    auth_type = forms.ChoiceField(
        label=_('Authentication type'),
        required=False,
        choices=add_blank_choice(WirelessAuthTypeChoices)
    )
    auth_cipher = forms.ChoiceField(
        label=_('Authentication cipher'),
        required=False,
        choices=add_blank_choice(WirelessAuthCipherChoices)
    )
    auth_psk = forms.CharField(
        label=_('Pre-shared key'),
        required=False
    )
    tag = TagFilterField(model)
