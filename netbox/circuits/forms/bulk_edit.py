from django import forms
from django.utils.translation import gettext_lazy as _

from circuits.choices import CircuitCommitRateChoices, CircuitPriorityChoices, CircuitStatusChoices
from circuits.models import *
from dcim.models import Site
from ipam.models import ASN
from netbox.forms import NetBoxModelBulkEditForm
from tenancy.models import Tenant
from utilities.forms import add_blank_choice
from utilities.forms.fields import ColorField, CommentField, DynamicModelChoiceField, DynamicModelMultipleChoiceField
from utilities.forms.rendering import FieldSet, TabbedGroups
from utilities.forms.widgets import BulkEditNullBooleanSelect, DatePicker, NumberWithOptions

__all__ = (
    'CircuitBulkEditForm',
    'CircuitGroupAssignmentBulkEditForm',
    'CircuitGroupBulkEditForm',
    'CircuitTerminationBulkEditForm',
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
        FieldSet('asns', 'description'),
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
        FieldSet('provider', 'description'),
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
        FieldSet('provider', 'service_id', 'description'),
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
        FieldSet('color', 'description'),
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
        FieldSet('provider', 'type', 'status', 'description', name=_('Circuit')),
        FieldSet('provider_account', 'install_date', 'termination_date', 'commit_rate', name=_('Service Parameters')),
        FieldSet('tenant', name=_('Tenancy')),
    )
    nullable_fields = (
        'tenant', 'commit_rate', 'description', 'comments',
    )


class CircuitTerminationBulkEditForm(NetBoxModelBulkEditForm):
    description = forms.CharField(
        label=_('Description'),
        max_length=200,
        required=False
    )
    site = DynamicModelChoiceField(
        label=_('Site'),
        queryset=Site.objects.all(),
        required=False
    )
    provider_network = DynamicModelChoiceField(
        label=_('Provider Network'),
        queryset=ProviderNetwork.objects.all(),
        required=False
    )
    port_speed = forms.IntegerField(
        required=False,
        label=_('Port speed (Kbps)'),
    )
    upstream_speed = forms.IntegerField(
        required=False,
        label=_('Upstream speed (Kbps)'),
    )
    mark_connected = forms.NullBooleanField(
        label=_('Mark connected'),
        required=False,
        widget=BulkEditNullBooleanSelect
    )

    model = CircuitTermination
    fieldsets = (
        FieldSet(
            'description',
            TabbedGroups(
                FieldSet('site', name=_('Site')),
                FieldSet('provider_network', name=_('Provider Network')),
            ),
            'mark_connected', name=_('Circuit Termination')
        ),
        FieldSet('port_speed', 'upstream_speed', name=_('Termination Details')),
    )
    nullable_fields = ('description')


class CircuitGroupBulkEditForm(NetBoxModelBulkEditForm):
    description = forms.CharField(
        label=_('Description'),
        max_length=200,
        required=False
    )
    tenant = DynamicModelChoiceField(
        label=_('Tenant'),
        queryset=Tenant.objects.all(),
        required=False
    )

    model = CircuitGroup
    nullable_fields = (
        'description', 'tenant',
    )


class CircuitGroupAssignmentBulkEditForm(NetBoxModelBulkEditForm):
    circuit = DynamicModelChoiceField(
        label=_('Circuit'),
        queryset=Circuit.objects.all(),
        required=False
    )
    priority = forms.ChoiceField(
        label=_('Priority'),
        choices=add_blank_choice(CircuitPriorityChoices),
        required=False
    )

    model = CircuitGroupAssignment
    fieldsets = (
        FieldSet('circuit', 'priority'),
    )
    nullable_fields = ('priority',)
