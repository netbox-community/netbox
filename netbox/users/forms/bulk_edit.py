from django import forms
from django.utils.translation import gettext_lazy as _

from users.models import *
from utilities.forms import BootstrapMixin
from utilities.forms.widgets import BulkEditNullBooleanSelect

__all__ = (
    'ObjectPermissionBulkEditForm',
    'UserBulkEditForm',
)


class UserBulkEditForm(BootstrapMixin, forms.Form):
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


class ObjectPermissionBulkEditForm(BootstrapMixin, forms.Form):
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
