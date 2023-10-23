from django import forms
from django.utils.translation import gettext_lazy as _

from circuits.choices import CircuitCommitRateChoices, CircuitStatusChoices
from circuits.models import *
from ipam.models import ASN
from netbox.forms import NetBoxModelBulkEditForm
from tenancy.models import Tenant
from utilities.forms import add_blank_choice
from utilities.forms.fields import ColorField, CommentField, DynamicModelChoiceField, DynamicModelMultipleChoiceField
from utilities.forms.widgets import DatePicker, NumberWithOptions

__all__ = (
    'CircuitBulkEditForm',
    'CircuitTypeBulkEditForm',
    'ProviderBulkEditForm',
    'ProviderAccountBulkEditForm',
    'ProviderNetworkBulkEditForm',
)


class ProviderBulkEditForm(NetBoxModelBulkEditForm):
    asns = DynamicModelMultipleChoiceField(
        queryset=ASN.objects.all(),
        label=_('ASNs'),
        required=False
    )
    description = forms.CharField(
        label=_('Description'),
        max_length=200,
        required=False
    )
    comments = CommentField()

    model = Provider
    fieldsets = (
        (None, ('asns', 'description')),
    )
    nullable_fields = (
        'asns', 'description', 'comments',
    )


class ProviderAccountBulkEditForm(NetBoxModelBulkEditForm):
    provider = DynamicModelChoiceField(
        label=_('Provider'),
        queryset=Provider.objects.all(),
        required=False
    )
    description = forms.CharField(
        label=_('Description'),
        max_length=200,
        required=False
    )
    comments = CommentField()

    model = ProviderAccount
    fieldsets = (
        (None, ('provider', 'description')),
    )
    nullable_fields = (
        'description', 'comments',
    )


class ProviderNetworkBulkEditForm(NetBoxModelBulkEditForm):
    provider = DynamicModelChoiceField(
        label=_('Provider'),
        queryset=Provider.objects.all(),
        required=False
    )
    service_id = forms.CharField(
        max_length=100,
        required=False,
        label=_('Service ID')
    )
    description = forms.CharField(
        label=_('Description'),
        max_length=200,
        required=False
    )
    comments = CommentField()

    model = ProviderNetwork
    fieldsets = (
        (None, ('provider', 'service_id', 'description')),
    )
    nullable_fields = (
        'service_id', 'description', 'comments',
    )


class CircuitTypeBulkEditForm(NetBoxModelBulkEditForm):
    color = ColorField(
        label=_('Color'),
        required=False
    )
    description = forms.CharField(
        label=_('Description'),
        max_length=200,
        required=False
    )

    model = CircuitType
    fieldsets = (
        (None, ('color', 'description')),
    )
    nullable_fields = ('color', 'description')


class CircuitBulkEditForm(NetBoxModelBulkEditForm):
    type = DynamicModelChoiceField(
        label=_('Type'),
        queryset=CircuitType.objects.all(),
        required=False
    )
    provider = DynamicModelChoiceField(
        label=_('Provider'),
        queryset=Provider.objects.all(),
        required=False
    )
    provider_account = DynamicModelChoiceField(
        label=_('Provider account'),
        queryset=ProviderAccount.objects.all(),
        required=False,
        query_params={
            'provider': '$provider'
        }
    )
    status = forms.ChoiceField(
        label=_('Status'),
        choices=add_blank_choice(CircuitStatusChoices),
        required=False,
        initial=''
    )
    tenant = DynamicModelChoiceField(
        label=_('Tenant'),
        queryset=Tenant.objects.all(),
        required=False
    )
    install_date = forms.DateField(
        label=_('Install date'),
        required=False,
        widget=DatePicker()
    )
    termination_date = forms.DateField(
        label=_('Termination date'),
        required=False,
        widget=DatePicker()
    )
    commit_rate = forms.IntegerField(
        required=False,
        label=_('Commit rate (Kbps)'),
        widget=NumberWithOptions(
            options=CircuitCommitRateChoices
        )
    )
    description = forms.CharField(
        label=_('Description'),
        max_length=100,
        required=False
    )
    comments = CommentField()

    model = Circuit
    fieldsets = (
        (_('Circuit'), ('provider', 'type', 'status', 'description')),
        (_('Service Parameters'), ('provider_account', 'install_date', 'termination_date', 'commit_rate')),
        (_('Tenancy'), ('tenant',)),
    )
    nullable_fields = (
        'tenant', 'commit_rate', 'description', 'comments',
    )
