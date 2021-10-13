from django import forms
from django.utils.translation import gettext as _

from extras.forms import CustomFieldModelFilterForm
from utilities.forms import BootstrapMixin, TagFilterField
from wireless.models import *

__all__ = (
    'WirelessLANFilterForm',
    'WirelessLinkFilterForm',
)


class WirelessLANFilterForm(BootstrapMixin, CustomFieldModelFilterForm):
    model = WirelessLAN
    field_groups = [
        ['q', 'tag'],
    ]
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': _('All Fields')}),
        label=_('Search')
    )
    ssid = forms.CharField(
        required=False,
        label='SSID'
    )
    tag = TagFilterField(model)


class WirelessLinkFilterForm(BootstrapMixin, CustomFieldModelFilterForm):
    model = WirelessLink
    field_groups = [
        ['q', 'tag'],
    ]
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': _('All Fields')}),
        label=_('Search')
    )
    ssid = forms.CharField(
        required=False,
        label='SSID'
    )
    tag = TagFilterField(model)
