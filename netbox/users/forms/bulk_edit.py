from django import forms
from django.contrib.postgres.forms import SimpleArrayField
from django.utils.translation import gettext_lazy as _

from ipam.formfields import IPNetworkFormField
from ipam.validators import prefix_validator
from users.models import *
from utilities.forms import BulkEditForm
from utilities.forms.widgets import BulkEditNullBooleanSelect, DateTimePicker

__all__ = (
    'ObjectPermissionBulkEditForm',
    'UserBulkEditForm',
    'TokenBulkEditForm',
)


class UserBulkEditForm(forms.Form):
    pk = forms.ModelMultipleChoiceField(
        queryset=NetBoxUser.objects.all(),
        widget=forms.MultipleHiddenInput
    )
    first_name = forms.CharField(
        label=_('First name'),
        max_length=150,
        required=False
    )
    last_name = forms.CharField(
        label=_('Last name'),
        max_length=150,
        required=False
    )
    is_active = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect,
        label=_('Active')
    )
    is_staff = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect,
        label=_('Staff status')
    )
    is_superuser = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect,
        label=_('Superuser status')
    )

    model = NetBoxUser
    fieldsets = (
        (None, ('first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser')),
    )
    nullable_fields = ('first_name', 'last_name')


class ObjectPermissionBulkEditForm(forms.Form):
    pk = forms.ModelMultipleChoiceField(
        queryset=ObjectPermission.objects.all(),
        widget=forms.MultipleHiddenInput
    )
    description = forms.CharField(
        label=_('Description'),
        max_length=200,
        required=False
    )
    enabled = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect,
        label=_('Enabled')
    )

    model = ObjectPermission
    fieldsets = (
        (None, ('enabled', 'description')),
    )
    nullable_fields = ('description',)


class TokenBulkEditForm(BulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=Token.objects.all(),
        widget=forms.MultipleHiddenInput
    )
    write_enabled = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect,
        label=_('Write enabled')
    )
    description = forms.CharField(
        max_length=200,
        required=False,
        label=_('Description')
    )
    expires = forms.DateTimeField(
        required=False,
        widget=DateTimePicker(),
        label=_('Expires')
    )
    allowed_ips = SimpleArrayField(
        base_field=IPNetworkFormField(validators=[prefix_validator]),
        required=False,
        label=_('Allowed IPs')
    )

    model = Token
    fieldsets = (
        (None, ('write_enabled', 'description', 'expires', 'allowed_ips')),
    )
    nullable_fields = (
        'expires', 'description', 'allowed_ips',
    )
