from django import forms
from django.utils.translation import gettext as _

from circuits.choices import CircuitCommitRateChoices, CircuitPriorityChoices, CircuitStatusChoices, CircuitTerminationSideChoices
from circuits.models import *
from dcim.models import Location, Region, Site, SiteGroup
from ipam.models import ASN
from netbox.choices import DistanceUnitChoices
from netbox.forms import NetBoxModelFilterSetForm
from tenancy.forms import TenancyFilterForm, ContactModelFilterForm
from utilities.forms import add_blank_choice
from utilities.forms.fields import ColorField, DynamicModelMultipleChoiceField, TagFilterField
from utilities.forms.rendering import FieldSet
from utilities.forms.widgets import DatePicker, NumberWithOptions

__all__ = (
    'CircuitFilterForm',
    'CircuitGroupAssignmentFilterForm',
    'CircuitGroupFilterForm',
    'CircuitTerminationFilterForm',
    'CircuitTypeFilterForm',
    'ProviderFilterForm',
    'ProviderAccountFilterForm',
    'ProviderNetworkFilterForm',
)


class ProviderFilterForm(ContactModelFilterForm, NetBoxModelFilterSetForm):
    model = Provider
    fieldsets = (
        FieldSet('q', 'filter_id', 'tag'),
        FieldSet('region_id', 'site_group_id', 'site_id', name=_('Location')),
        FieldSet('asn_id', name=_('ASN')),
        FieldSet('contact', 'contact_role', 'contact_group', name=_('Contacts')),
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
        FieldSet('q', 'filter_id', 'tag'),
        FieldSet('provider_id', 'account', name=_('Attributes')),
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
        FieldSet('q', 'filter_id', 'tag'),
        FieldSet('provider_id', 'service_id', name=_('Attributes')),
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
        FieldSet('q', 'filter_id', 'tag'),
        FieldSet('color', name=_('Attributes')),
    )
    tag = TagFilterField(model)

    color = ColorField(
        label=_('Color'),
        required=False
    )


class CircuitFilterForm(TenancyFilterForm, ContactModelFilterForm, NetBoxModelFilterSetForm):
    model = Circuit
    fieldsets = (
        FieldSet('q', 'filter_id', 'tag'),
        FieldSet('provider_id', 'provider_account_id', 'provider_network_id', name=_('Provider')),
        FieldSet('type_id', 'status', 'install_date', 'termination_date', 'commit_rate', 'distance', 'distance_unit', name=_('Attributes')),
        FieldSet('region_id', 'site_group_id', 'site_id', name=_('Location')),
        FieldSet('tenant_group_id', 'tenant_id', name=_('Tenant')),
        FieldSet('contact', 'contact_role', 'contact_group', name=_('Contacts')),
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


class CircuitTerminationFilterForm(NetBoxModelFilterSetForm):
    model = CircuitTermination
    fieldsets = (
        FieldSet('q', 'filter_id', 'tag'),
        FieldSet('circuit_id', 'term_side', name=_('Circuit')),
        FieldSet('provider_id', name=_('Provider')),
        FieldSet('region_id', 'site_group_id', 'site_id', 'location_id', name=_('Termination')),
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
        label=_('Site')
    )
    location_id = DynamicModelMultipleChoiceField(
        queryset=Location.objects.all(),
        required=False,
        label=_('Location')
    )
    circuit_id = DynamicModelMultipleChoiceField(
        queryset=Circuit.objects.all(),
        required=False,
        label=_('Circuit')
    )
    term_side = forms.MultipleChoiceField(
        label=_('Term Side'),
        choices=CircuitTerminationSideChoices,
        required=False
    )
    provider_network_id = DynamicModelMultipleChoiceField(
        queryset=ProviderNetwork.objects.all(),
        required=False,
        query_params={
            'provider_id': '$provider_id'
        },
        label=_('Provider network')
    )
    provider_id = DynamicModelMultipleChoiceField(
        queryset=Provider.objects.all(),
        required=False,
        label=_('Provider')
    )
    tag = TagFilterField(model)


class CircuitGroupFilterForm(TenancyFilterForm, NetBoxModelFilterSetForm):
    model = CircuitGroup
    fieldsets = (
        FieldSet('q', 'filter_id', 'tag'),
        FieldSet('tenant_group_id', 'tenant_id', name=_('Tenant')),
    )
    tag = TagFilterField(model)


class CircuitGroupAssignmentFilterForm(NetBoxModelFilterSetForm):
    model = CircuitGroupAssignment
    fieldsets = (
        FieldSet('q', 'filter_id', 'tag'),
        FieldSet('provider_id', 'circuit_id', 'group_id', 'priority', name=_('Assignment')),
    )
    provider_id = DynamicModelMultipleChoiceField(
        queryset=Provider.objects.all(),
        required=False,
        label=_('Provider')
    )
    circuit_id = DynamicModelMultipleChoiceField(
        queryset=Circuit.objects.all(),
        required=False,
        label=_('Circuit')
    )
    group_id = DynamicModelMultipleChoiceField(
        queryset=CircuitGroup.objects.all(),
        required=False,
        label=_('Group')
    )
    priority = forms.MultipleChoiceField(
        label=_('Priority'),
        choices=CircuitPriorityChoices,
        required=False
    )
    tag = TagFilterField(model)
