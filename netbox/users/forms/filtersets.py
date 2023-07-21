from django import forms
from extras.forms.mixins import SavedFiltersMixin
from utilities.forms import FilterForm
from users.models import Token
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _

from netbox.forms import NetBoxModelFilterSetForm
from users.models import NetBoxGroup, NetBoxUser, ObjectPermission
from utilities.forms import BOOLEAN_WITH_BLANK_CHOICES
from utilities.forms.fields import DynamicModelMultipleChoiceField

__all__ = (
    'GroupFilterForm',
    'ObjectPermissionFilterForm',
    'TokenFilterForm',
    'UserFilterForm',
)


class TokenFilterForm(SavedFiltersMixin, FilterForm):
    model = Token


class GroupFilterForm(NetBoxModelFilterSetForm):
    model = NetBoxGroup
    fieldsets = (
        (None, ('q', 'filter_id',)),
    )


class UserFilterForm(NetBoxModelFilterSetForm):
    model = NetBoxUser
    fieldsets = (
        (None, ('q', 'filter_id',)),
        (_('Group'), ('group_id',)),
        (_('Status'), ('is_active', 'is_staff', 'is_superuser')),
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
        (None, ('q', 'filter_id',)),
        (_('Permission'), ('enabled', 'group_id', 'user_id')),
        (_('Actions'), ('can_view', 'can_add', 'can_change', 'can_delete')),
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
