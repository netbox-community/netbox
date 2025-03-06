from django import forms
from django.utils.translation import gettext_lazy as _

from dcim.choices import LinkStatusChoices
from dcim.models import Location, Region, Site, SiteGroup
from netbox.choices import *
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
        FieldSet('region_id', 'site_group_id', 'site_id', 'location_id', name=_('Scope')),
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
    region_id = DynamicModelMultipleChoiceField(
        queryset=Region.objects.all(),
        required=False,
        label=_('Region')
    )
    site_group_id = DynamicModelMultipleChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False,
        label=_('Site group')
    )
    site_id = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        null_option='None',
        query_params={
            'region_id': '$region_id',
            'site_group_id': '$site_group_id',
        },
        label=_('Site')
    )
    location_id = DynamicModelMultipleChoiceField(
        queryset=Location.objects.all(),
        required=False,
        label=_('Location')
    )
    tag = TagFilterField(model)


class WirelessLinkFilterForm(TenancyFilterForm, NetBoxModelFilterSetForm):
    model = WirelessLink
    fieldsets = (
        FieldSet('q', 'filter_id', 'tag'),
        FieldSet('ssid', 'status', 'distance', 'distance_unit', name=_('Attributes')),
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
    distance = forms.DecimalField(
        label=_('Distance'),
        required=False,
    )
    distance_unit = forms.ChoiceField(
        label=_('Distance unit'),
        choices=add_blank_choice(DistanceUnitChoices),
        required=False
    )
    tag = TagFilterField(model)
