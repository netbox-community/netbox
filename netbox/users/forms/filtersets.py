from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from netbox.forms import NetBoxModelFilterSetForm
from netbox.forms.mixins import SavedFiltersMixin
from users.models import Group, ObjectPermission, Token, User
from utilities.forms import BOOLEAN_WITH_BLANK_CHOICES, FilterForm
from utilities.forms.fields import DynamicModelMultipleChoiceField
from utilities.forms.rendering import FieldSet
from utilities.forms.widgets import DateTimePicker

__all__ = (
    'GroupFilterForm',
    'ObjectPermissionFilterForm',
    'TokenFilterForm',
    'UserFilterForm',
)


class GroupFilterForm(NetBoxModelFilterSetForm):
    model = Group
    fieldsets = (
        FieldSet('q', 'filter_id',),
    )


class UserFilterForm(NetBoxModelFilterSetForm):
    model = User
    fieldsets = (
        FieldSet('q', 'filter_id',),
        FieldSet('group_id', name=_('Group')),
        FieldSet('is_active', 'is_staff', 'is_superuser', name=_('Status')),
    )
    group_id = DynamicModelMultipleChoiceField(
        queryset=Group.objects.all(),
        required=False,
        label=_('Group')
    )
    is_active = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        ),
        label=_('Is Active'),
    )
    is_staff = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        ),
        label=_('Is Staff'),
    )
    is_superuser = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        ),
        label=_('Is Superuser'),
    )


class ObjectPermissionFilterForm(NetBoxModelFilterSetForm):
    model = ObjectPermission
    fieldsets = (
        FieldSet('q', 'filter_id',),
        FieldSet('enabled', 'group_id', 'user_id', name=_('Permission')),
        FieldSet('can_view', 'can_add', 'can_change', 'can_delete', name=_('Actions')),
    )
    enabled = forms.NullBooleanField(
        label=_('Enabled'),
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    group_id = DynamicModelMultipleChoiceField(
        queryset=Group.objects.all(),
        required=False,
        label=_('Group')
    )
    user_id = DynamicModelMultipleChoiceField(
        queryset=get_user_model().objects.all(),
        required=False,
        label=_('User')
    )
    can_view = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        ),
        label=_('Can View'),
    )
    can_add = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        ),
        label=_('Can Add'),
    )
    can_change = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        ),
        label=_('Can Change'),
    )
    can_delete = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        ),
        label=_('Can Delete'),
    )


class TokenFilterForm(SavedFiltersMixin, FilterForm):
    model = Token
    fieldsets = (
        FieldSet('q', 'filter_id',),
        FieldSet('user_id', 'write_enabled', 'expires', 'last_used', name=_('Token')),
    )
    user_id = DynamicModelMultipleChoiceField(
        queryset=get_user_model().objects.all(),
        required=False,
        label=_('User')
    )
    write_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        ),
        label=_('Write Enabled'),
    )
    expires = forms.DateTimeField(
        required=False,
        label=_('Expires'),
        widget=DateTimePicker()
    )
    last_used = forms.DateTimeField(
        required=False,
        label=_('Last Used'),
        widget=DateTimePicker()
    )
