from django import forms
from django.utils.translation import gettext as _

from dcim.choices import LinkStatusChoices
from netbox.forms import NetBoxModelFilterSetForm
from utilities.forms import add_blank_choice, DynamicModelMultipleChoiceField, StaticSelect, TagFilterField
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


class WirelessLANFilterForm(NetBoxModelFilterSetForm):
    model = WirelessLAN
    fieldsets = (
        (None, ('q', 'tag')),
        ('Attributes', ('ssid', 'group_id',)),
        ('Authentication', ('auth_type', 'auth_cipher', 'auth_psk')),
    )
    ssid = forms.CharField(
        required=False,
        label='SSID'
    )
    group_id = DynamicModelMultipleChoiceField(
        queryset=WirelessLANGroup.objects.all(),
        required=False,
        null_option='None',
        label=_('Group')
    )
    auth_type = forms.ChoiceField(
        required=False,
        choices=add_blank_choice(WirelessAuthTypeChoices),
        widget=StaticSelect()
    )
    auth_cipher = forms.ChoiceField(
        required=False,
        choices=add_blank_choice(WirelessAuthCipherChoices),
        widget=StaticSelect()
    )
    auth_psk = forms.CharField(
        required=False
    )
    tag = TagFilterField(model)


class WirelessLinkFilterForm(NetBoxModelFilterSetForm):
    model = WirelessLink
    ssid = forms.CharField(
        required=False,
        label='SSID'
    )
    status = forms.ChoiceField(
        required=False,
        choices=add_blank_choice(LinkStatusChoices),
        widget=StaticSelect()
    )
    auth_type = forms.ChoiceField(
        required=False,
        choices=add_blank_choice(WirelessAuthTypeChoices),
        widget=StaticSelect()
    )
    auth_cipher = forms.ChoiceField(
        required=False,
        choices=add_blank_choice(WirelessAuthCipherChoices),
        widget=StaticSelect()
    )
    auth_psk = forms.CharField(
        required=False
    )
    tag = TagFilterField(model)
