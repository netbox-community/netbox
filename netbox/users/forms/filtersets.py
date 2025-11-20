from django import forms
from django.utils.translation import gettext_lazy as _

from netbox.forms import NetBoxModelFilterSetForm
from netbox.forms.mixins import SavedFiltersMixin
from users.choices import TokenVersionChoices
from users.models import Group, ObjectPermission, Owner, OwnerGroup, Token, User
from utilities.forms import BOOLEAN_WITH_BLANK_CHOICES, FilterForm
from utilities.forms.fields import DynamicModelMultipleChoiceField
from utilities.forms.rendering import FieldSet
from utilities.forms.utils import add_blank_choice
from utilities.forms.widgets import DateTimePicker

__all__ = (
    'GroupFilterForm',
    'ObjectPermissionFilterForm',
    'OwnerFilterForm',
    'OwnerGroupFilterForm',
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
        FieldSet('is_active', 'is_superuser', name=_('Status')),
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
        queryset=User.objects.all(),
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
        FieldSet('version', 'user_id', 'enabled', 'write_enabled', 'expires', 'last_used', name=_('Token')),
    )
    version = forms.ChoiceField(
        choices=add_blank_choice(TokenVersionChoices),
        required=False,
    )
    user_id = DynamicModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        label=_('User')
    )
    enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        ),
        label=_('Enabled'),
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


class OwnerGroupFilterForm(NetBoxModelFilterSetForm):
    model = OwnerGroup
    fieldsets = (
        FieldSet('q', 'filter_id',),
    )


class OwnerFilterForm(NetBoxModelFilterSetForm):
    model = Owner
    fieldsets = (
        FieldSet('q', 'filter_id',),
        FieldSet('group_id', name=_('Group')),
        FieldSet('user_group_id', 'user_id', name=_('Membership')),
    )
    group_id = DynamicModelMultipleChoiceField(
        queryset=OwnerGroup.objects.all(),
        required=False,
        label=_('Group')
    )
    user_group_id = DynamicModelMultipleChoiceField(
        queryset=Group.objects.all(),
        required=False,
        label=_('Groups')
    )
    user_id = DynamicModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        label=_('Users')
    )
