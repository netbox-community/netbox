from django import forms
from django.utils.translation import gettext as _

from circuits.choices import CircuitCommitRateChoices, CircuitStatusChoices
from circuits.models import *
from dcim.models import Region, Site, SiteGroup
from ipam.models import ASN
from netbox.forms import NetBoxModelFilterSetForm
from tenancy.forms import TenancyFilterForm, ContactModelFilterForm
from users.models import NetBoxUser
from utilities.forms.fields import DynamicModelMultipleChoiceField, TagFilterField
from utilities.forms.widgets import DatePicker, NumberWithOptions

__all__ = (
    'UserFilterForm',
)


class UserFilterForm(ContactModelFilterForm, NetBoxModelFilterSetForm):
    model = NetBoxUser
    fieldsets = (
        (None, ('q', 'filter_id',)),
        ('Name', ('username', 'first_name', 'last_name')),
        ('Security', ('is_superuser', 'is_staff', 'is_active')),
    )
    username = forms.CharField(
        required=False
    )
    first_name = forms.CharField(
        required=False
    )
    last_name = forms.CharField(
        required=False
    )
    is_superuser = forms.BooleanField(
        required=False,
        label='Is Superuser',
    )
    is_staff = forms.BooleanField(
        required=False,
        label='Is Staff',
    )
    is_active = forms.BooleanField(
        required=False,
        label='Is Active',
    )
