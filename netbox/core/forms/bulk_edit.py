from django import forms
from django.utils.translation import gettext as _

from core.choices import DataSourceTypeChoices
from core.models import *
from netbox.forms import NetBoxModelBulkEditForm
from utilities.forms import (
    add_blank_choice, BulkEditNullBooleanSelect, StaticSelect,
)

__all__ = (
    'DataSourceBulkEditForm',
)


class DataSourceBulkEditForm(NetBoxModelBulkEditForm):
    type = forms.ChoiceField(
        choices=add_blank_choice(DataSourceTypeChoices),
        required=False,
        initial='',
        widget=StaticSelect()
    )
    enabled = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect(),
        label=_('Enforce unique space')
    )
    description = forms.CharField(
        max_length=200,
        required=False
    )
    git_branch = forms.CharField(
        max_length=100,
        required=False
    )
    ignore_rules = forms.CharField(
        required=False,
        widget=forms.Textarea()
    )
    username = forms.CharField(
        max_length=100,
        required=False
    )
    password = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.PasswordInput()
    )

    model = DataSource
    fieldsets = (
        (None, ('type', 'enabled', 'description', 'git_branch', 'ignore_rules')),
        ('Authentication', ('username', 'password')),
    )
    nullable_fields = (
        'description', 'description', 'git_branch', 'ignore_rules', 'username', 'password',
    )
