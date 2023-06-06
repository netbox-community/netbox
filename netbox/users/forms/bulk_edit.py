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
    'GroupBulkEditForm',
    'ObjectPermissionBulkEditForm',
    'UserBulkEditForm',
)


class UserBulkEditForm(NetBoxModelBulkEditForm):
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


class GroupBulkEditForm(NetBoxModelBulkEditForm):
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


class ObjectPermissionBulkEditForm(NetBoxModelBulkEditForm):
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
