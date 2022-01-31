from django import forms
from django.utils.translation import gettext as _

from circuits.choices import CircuitStatusChoices
from circuits.models import *
from dcim.models import Region, Site, SiteGroup
from netbox.forms import NetBoxModelFilterSetForm
from tenancy.forms import TenancyFilterForm
from utilities.forms import DynamicModelMultipleChoiceField, StaticSelectMultiple, TagFilterField

__all__ = (
    'CircuitFilterForm',
    'CircuitTypeFilterForm',
    'ProviderFilterForm',
    'ProviderNetworkFilterForm',
)


class ProviderFilterForm(NetBoxModelFilterSetForm):
    model = Provider
    fieldsets = (
        (None, ('q', 'tag')),
        ('Location', ('region_id', 'site_group_id', 'site_id')),
        ('ASN', ('asn',)),
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
        query_params={
            'region_id': '$region_id',
            'site_group_id': '$site_group_id',
        },
        label=_('Site')
    )
    asn = forms.IntegerField(
        required=False,
        label=_('ASN')
    )
    tag = TagFilterField(model)


class ProviderNetworkFilterForm(NetBoxModelFilterSetForm):
    model = ProviderNetwork
    fieldsets = (
        (None, ('q', 'tag')),
        ('Attributes', ('provider_id', 'service_id')),
    )
    provider_id = DynamicModelMultipleChoiceField(
        queryset=Provider.objects.all(),
        required=False,
        label=_('Provider')
    )
    service_id = forms.CharField(
        max_length=100,
        required=False
    )
    tag = TagFilterField(model)


class CircuitTypeFilterForm(NetBoxModelFilterSetForm):
    model = CircuitType
    tag = TagFilterField(model)


class CircuitFilterForm(TenancyFilterForm, NetBoxModelFilterSetForm):
    model = Circuit
    fieldsets = (
        (None, ('q', 'tag')),
        ('Provider', ('provider_id', 'provider_network_id')),
        ('Attributes', ('type_id', 'status', 'commit_rate')),
        ('Location', ('region_id', 'site_group_id', 'site_id')),
        ('Tenant', ('tenant_group_id', 'tenant_id')),
    )
    type_id = DynamicModelMultipleChoiceField(
        queryset=CircuitType.objects.all(),
        required=False,
        label=_('Type')
    )
    provider_id = DynamicModelMultipleChoiceField(
        queryset=Provider.objects.all(),
        required=False,
        label=_('Provider')
    )
    provider_network_id = DynamicModelMultipleChoiceField(
        queryset=ProviderNetwork.objects.all(),
        required=False,
        query_params={
            'provider_id': '$provider_id'
        },
        label=_('Provider network')
    )
    status = forms.MultipleChoiceField(
        choices=CircuitStatusChoices,
        required=False,
        widget=StaticSelectMultiple()
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
        query_params={
            'region_id': '$region_id',
            'site_group_id': '$site_group_id',
        },
        label=_('Site')
    )
    commit_rate = forms.IntegerField(
        required=False,
        min_value=0,
        label=_('Commit rate (Kbps)')
    )
    tag = TagFilterField(model)
