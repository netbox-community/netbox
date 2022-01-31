from django import forms

from circuits.choices import CircuitStatusChoices
from circuits.models import *
from netbox.forms import NetBoxModelBulkEditForm
from tenancy.models import Tenant
from utilities.forms import add_blank_choice, CommentField, DynamicModelChoiceField, SmallTextarea, StaticSelect

__all__ = (
    'CircuitBulkEditForm',
    'CircuitTypeBulkEditForm',
    'ProviderBulkEditForm',
    'ProviderNetworkBulkEditForm',
)


class ProviderBulkEditForm(NetBoxModelBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=Provider.objects.all(),
        widget=forms.MultipleHiddenInput
    )
    asn = forms.IntegerField(
        required=False,
        label='ASN'
    )
    account = forms.CharField(
        max_length=30,
        required=False,
        label='Account number'
    )
    portal_url = forms.URLField(
        required=False,
        label='Portal'
    )
    noc_contact = forms.CharField(
        required=False,
        widget=SmallTextarea,
        label='NOC contact'
    )
    admin_contact = forms.CharField(
        required=False,
        widget=SmallTextarea,
        label='Admin contact'
    )
    comments = CommentField(
        widget=SmallTextarea,
        label='Comments'
    )

    nullable_fields = (
        'asn', 'account', 'portal_url', 'noc_contact', 'admin_contact', 'comments',
    )


class ProviderNetworkBulkEditForm(NetBoxModelBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=ProviderNetwork.objects.all(),
        widget=forms.MultipleHiddenInput
    )
    provider = DynamicModelChoiceField(
        queryset=Provider.objects.all(),
        required=False
    )
    service_id = forms.CharField(
        max_length=100,
        required=False
    )
    description = forms.CharField(
        max_length=200,
        required=False
    )
    comments = CommentField(
        widget=SmallTextarea,
        label='Comments'
    )

    nullable_fields = (
        'service_id', 'description', 'comments',
    )


class CircuitTypeBulkEditForm(NetBoxModelBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=CircuitType.objects.all(),
        widget=forms.MultipleHiddenInput
    )
    description = forms.CharField(
        max_length=200,
        required=False
    )

    nullable_fields = ('description',)


class CircuitBulkEditForm(NetBoxModelBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=Circuit.objects.all(),
        widget=forms.MultipleHiddenInput
    )
    type = DynamicModelChoiceField(
        queryset=CircuitType.objects.all(),
        required=False
    )
    provider = DynamicModelChoiceField(
        queryset=Provider.objects.all(),
        required=False
    )
    status = forms.ChoiceField(
        choices=add_blank_choice(CircuitStatusChoices),
        required=False,
        initial='',
        widget=StaticSelect()
    )
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False
    )
    commit_rate = forms.IntegerField(
        required=False,
        label='Commit rate (Kbps)'
    )
    description = forms.CharField(
        max_length=100,
        required=False
    )
    comments = CommentField(
        widget=SmallTextarea,
        label='Comments'
    )

    nullable_fields = (
        'tenant', 'commit_rate', 'description', 'comments',
    )
