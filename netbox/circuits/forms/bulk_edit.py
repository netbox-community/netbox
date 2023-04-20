from django import forms
from django.utils.translation import gettext as _

from circuits.choices import CircuitCommitRateChoices, CircuitStatusChoices
from circuits.models import *
from ipam.models import ASN
from netbox.forms import NetBoxModelBulkEditForm
from tenancy.models import Tenant
from utilities.forms import add_blank_choice
from utilities.forms.fields import CommentField, DynamicModelChoiceField, DynamicModelMultipleChoiceField
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
        max_length=200,
        required=False
    )
    comments = CommentField(
        label=_('Comments')
    )

    model = Provider
    fieldsets = (
        (None, ('asns', 'description')),
    )
    nullable_fields = (
        'asns', 'description', 'comments',
    )


class ProviderAccountBulkEditForm(NetBoxModelBulkEditForm):
    provider = DynamicModelChoiceField(
        queryset=Provider.objects.all(),
        required=False
    )
    description = forms.CharField(
        max_length=200,
        required=False
    )
    comments = CommentField(
        label=_('Comments')
    )

    model = ProviderAccount
    fieldsets = (
        (None, ('provider', 'description')),
    )
    nullable_fields = (
        'description', 'comments',
    )


class ProviderNetworkBulkEditForm(NetBoxModelBulkEditForm):
    provider = DynamicModelChoiceField(
        queryset=Provider.objects.all(),
        required=False
    )
    service_id = forms.CharField(
        max_length=100,
        required=False,
        label=_('Service ID')
    )
    description = forms.CharField(
        max_length=200,
        required=False
    )
    comments = CommentField(
        label=_('Comments')
    )

    model = ProviderNetwork
    fieldsets = (
        (None, ('provider', 'service_id', 'description')),
    )
    nullable_fields = (
        'service_id', 'description', 'comments',
    )


class CircuitTypeBulkEditForm(NetBoxModelBulkEditForm):
    description = forms.CharField(
        max_length=200,
        required=False
    )

    model = CircuitType
    fieldsets = (
        (None, ('description',)),
    )
    nullable_fields = ('description',)


class CircuitBulkEditForm(NetBoxModelBulkEditForm):
    type = DynamicModelChoiceField(
        queryset=CircuitType.objects.all(),
        required=False
    )
    provider = DynamicModelChoiceField(
        queryset=Provider.objects.all(),
        required=False
    )
    provider_account = DynamicModelChoiceField(
        queryset=ProviderAccount.objects.all(),
        required=False,
        query_params={
            'provider': '$provider'
        }
    )
    status = forms.ChoiceField(
        choices=add_blank_choice(CircuitStatusChoices),
        required=False,
        initial=''
    )
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False
    )
    install_date = forms.DateField(
        required=False,
        widget=DatePicker()
    )
    termination_date = forms.DateField(
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
        max_length=100,
        required=False
    )
    comments = CommentField(
        label=_('Comments')
    )

    model = Circuit
    fieldsets = (
        ('Circuit', ('provider', 'type', 'status', 'description')),
        ('Service Parameters', ('provider_account', 'install_date', 'termination_date', 'commit_rate')),
        ('Tenancy', ('tenant',)),
    )
    nullable_fields = (
        'tenant', 'commit_rate', 'description', 'comments',
    )
