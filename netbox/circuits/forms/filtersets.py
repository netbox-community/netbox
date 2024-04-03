from django import forms
from django.utils.translation import gettext as _

from circuits.choices import CircuitCommitRateChoices, CircuitStatusChoices
from circuits.models import *
from dcim.models import Region, Site, SiteGroup
from ipam.models import ASN
from netbox.forms import NetBoxModelFilterSetForm
from tenancy.forms import TenancyFilterForm, ContactModelFilterForm
from utilities.forms.fields import ColorField, DynamicModelMultipleChoiceField, TagFilterField
from utilities.forms.widgets import DatePicker, NumberWithOptions

__all__ = (
    'CircuitFilterForm',
    'CircuitTypeFilterForm',
    'ProviderFilterForm',
    'ProviderAccountFilterForm',
    'ProviderNetworkFilterForm',
)


class ProviderFilterForm(ContactModelFilterForm, NetBoxModelFilterSetForm):
    model = Provider
    fieldsets = (
        (None, ('q', 'filter_id', 'tag')),
        (_('Location'), ('region_id', 'site_group_id', 'site_id')),
        (_('ASN'), ('asn_id',)),
        (_('Contacts'), ('contact', 'contact_role', 'contact_group')),
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
    asn_id = DynamicModelMultipleChoiceField(
        queryset=ASN.objects.all(),
        required=False,
        label=_('ASNs')
    )
    tag = TagFilterField(model)


class ProviderAccountFilterForm(NetBoxModelFilterSetForm):
    model = ProviderAccount
    fieldsets = (
        (None, ('q', 'filter_id', 'tag')),
        (_('Attributes'), ('provider_id', 'account')),
    )
    provider_id = DynamicModelMultipleChoiceField(
        queryset=Provider.objects.all(),
        required=False,
        label=_('Provider')
    )
    account = forms.CharField(
        label=_('Account'),
        required=False
    )
    tag = TagFilterField(model)


class ProviderNetworkFilterForm(NetBoxModelFilterSetForm):
    model = ProviderNetwork
    fieldsets = (
        (None, ('q', 'filter_id', 'tag')),
        (_('Attributes'), ('provider_id', 'service_id')),
    )
    provider_id = DynamicModelMultipleChoiceField(
        queryset=Provider.objects.all(),
        required=False,
        label=_('Provider')
    )
    service_id = forms.CharField(
        label=_('Service ID'),
        max_length=100,
        required=False
    )
    tag = TagFilterField(model)


class CircuitTypeFilterForm(NetBoxModelFilterSetForm):
    model = CircuitType
    fieldsets = (
        (None, ('q', 'filter_id', 'tag')),
        (_('Attributes'), ('color',)),
    )
    tag = TagFilterField(model)

    color = ColorField(
        label=_('Color'),
        required=False
    )


class CircuitFilterForm(TenancyFilterForm, ContactModelFilterForm, NetBoxModelFilterSetForm):
    model = Circuit
    fieldsets = (
        (None, ('q', 'filter_id', 'tag')),
        (_('Provider'), ('provider_id', 'provider_account_id', 'provider_network_id')),
        (_('Attributes'), ('type_id', 'status', 'install_date', 'termination_date', 'commit_rate')),
        (_('Location'), ('region_id', 'site_group_id', 'site_id')),
        (_('Tenant'), ('tenant_group_id', 'tenant_id')),
        (_('Contacts'), ('contact', 'contact_role', 'contact_group')),
    )
    selector_fields = ('filter_id', 'q', 'region_id', 'site_group_id', 'site_id', 'provider_id', 'provider_network_id')
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
    provider_account_id = DynamicModelMultipleChoiceField(
        queryset=ProviderAccount.objects.all(),
        required=False,
        query_params={
            'provider_id': '$provider_id'
        },
        label=_('Provider account')
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
        label=_('Status'),
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
        label=_('Install date'),
        required=False,
        widget=DatePicker
    )
    termination_date = forms.DateField(
        label=_('Termination date'),
        required=False,
        widget=DatePicker
    )
    commit_rate = forms.IntegerField(
        required=False,
        min_value=0,
        label=_('Commit rate (Kbps)'),
        widget=NumberWithOptions(
            options=CircuitCommitRateChoices
        )
    )
    tag = TagFilterField(model)
