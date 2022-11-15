from django import forms
from django.utils.translation import gettext as _

from circuits.choices import CircuitStatusChoices
from circuits.models import *
from dcim.models import Region, Site, SiteGroup
from ipam.models import ASN
from netbox.forms import NetBoxModelFilterSetForm
from tenancy.forms import TenancyFilterForm, ContactModelFilterForm
from utilities.forms import DatePicker, DynamicModelMultipleChoiceField, MultipleChoiceField, TagFilterField

__all__ = (
    'CircuitFilterForm',
    'CircuitTypeFilterForm',
    'ProviderFilterForm',
    'ProviderNetworkFilterForm',
)


class ProviderFilterForm(ContactModelFilterForm, NetBoxModelFilterSetForm):
    model = Provider
    fieldsets = (
        (None, ('q', 'filter_id', 'tag')),
        ('Location', ('region_id', 'site_group_id', 'site_id')),
        ('ASN', ('asn',)),
        ('Contacts', ('contact', 'contact_role', 'contact_group')),
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
        label=_('ASN (legacy)')
    )
    asn_id = DynamicModelMultipleChoiceField(
        queryset=ASN.objects.all(),
        required=False,
        label=_('ASNs')
    )
    tag = TagFilterField(model)


class ProviderNetworkFilterForm(NetBoxModelFilterSetForm):
    model = ProviderNetwork
    fieldsets = (
        (None, ('q', 'filter_id', 'tag')),
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


class CircuitFilterForm(TenancyFilterForm, ContactModelFilterForm, NetBoxModelFilterSetForm):
    model = Circuit
    fieldsets = (
        (None, ('q', 'filter_id', 'tag')),
        ('Provider', ('provider_id', 'provider_network_id')),
        ('Attributes', ('type_id', 'status', 'install_date', 'termination_date', 'commit_rate')),
        ('Location', ('region_id', 'site_group_id', 'site_id')),
        ('Tenant', ('tenant_group_id', 'tenant_id')),
        ('Contacts', ('contact', 'contact_role', 'contact_group')),
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
    status = MultipleChoiceField(
        choices=CircuitStatusChoices,
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
        query_params={
            'region_id': '$region_id',
            'site_group_id': '$site_group_id',
        },
        label=_('Site')
    )
    install_date = forms.DateField(
        required=False,
        widget=DatePicker
    )
    termination_date = forms.DateField(
        required=False,
        widget=DatePicker
    )
    commit_rate = forms.IntegerField(
        required=False,
        min_value=0,
        label=_('Commit rate (Kbps)')
    )
    tag = TagFilterField(model)
