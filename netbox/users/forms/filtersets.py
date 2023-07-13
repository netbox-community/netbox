from django import forms
from django.utils.translation import gettext_lazy as _

from circuits.choices import CircuitCommitRateChoices, CircuitStatusChoices
from circuits.models import *
from dcim.models import Region, Site, SiteGroup
from ipam.models import ASN
from netbox.forms import NetBoxModelFilterSetForm
from tenancy.forms import TenancyFilterForm, ContactModelFilterForm
from users.models import ObjectPermission, NetBoxGroup, NetBoxUser
from utilities.forms import BOOLEAN_WITH_BLANK_CHOICES, FilterForm, add_blank_choice
from utilities.forms.fields import DynamicModelMultipleChoiceField, TagFilterField
from utilities.forms.widgets import DatePicker, NumberWithOptions

__all__ = (
    'GroupFilterForm',
    'ObjectPermissionFilterForm',
    'UserFilterForm',
)


class UserFilterForm(ContactModelFilterForm, NetBoxModelFilterSetForm):
    model = NetBoxUser
    fieldsets = (
        (None, ('q', 'filter_id',)),
        (_('Security'), ('is_superuser', 'is_staff', 'is_active')),
    )
    is_superuser = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        ),
        label=_('Is Superuser'),
    )
    is_staff = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        ),
        label=_('Is Staff'),
    )
    is_active = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        ),
        label=_('Is Active'),
    )


class GroupFilterForm(ContactModelFilterForm, NetBoxModelFilterSetForm):
    model = NetBoxGroup
    fieldsets = (
        (None, ('q', 'filter_id',)),
    )


class ObjectPermissionFilterForm(ContactModelFilterForm, NetBoxModelFilterSetForm):
    model = ObjectPermission
    fieldsets = (
        (None, ('q', 'filter_id',)),
        (None, ('enabled',)),
    )
    enabled = forms.NullBooleanField(
        label=_('Enabled'),
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
