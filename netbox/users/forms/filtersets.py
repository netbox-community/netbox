from django import forms
from django.utils.translation import gettext_lazy as _
from users.models import NetBoxGroup, NetBoxUser, ObjectPermission
from utilities.forms import BOOLEAN_WITH_BLANK_CHOICES, FilterForm, add_blank_choice

from netbox.forms import NetBoxModelFilterSetForm

__all__ = (
    'GroupFilterForm',
    'ObjectPermissionFilterForm',
    'UserFilterForm',
)


class UserFilterForm(NetBoxModelFilterSetForm):
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


class GroupFilterForm(NetBoxModelFilterSetForm):
    model = NetBoxGroup
    fieldsets = (
        (None, ('q', 'filter_id',)),
    )


class ObjectPermissionFilterForm(NetBoxModelFilterSetForm):
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
