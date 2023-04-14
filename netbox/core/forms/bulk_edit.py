from django import forms
from django.utils.translation import gettext as _

from core.choices import DataSourceTypeChoices
from core.models import *
from netbox.forms import NetBoxModelBulkEditForm
from utilities.forms import add_blank_choice
from utilities.forms.fields import CommentField
from utilities.forms.widgets import BulkEditNullBooleanSelect

__all__ = (
    'DataSourceBulkEditForm',
)


class DataSourceBulkEditForm(NetBoxModelBulkEditForm):
    type = forms.ChoiceField(
        choices=add_blank_choice(DataSourceTypeChoices),
        required=False,
        initial=''
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
    comments = CommentField(
        label=_('Comments')
    )
    parameters = forms.JSONField(
        required=False
    )
    ignore_rules = forms.CharField(
        required=False,
        widget=forms.Textarea()
    )

    model = DataSource
    fieldsets = (
        (None, ('type', 'enabled', 'description', 'comments', 'parameters', 'ignore_rules')),
    )
    nullable_fields = (
        'description', 'description', 'parameters', 'comments', 'parameters', 'ignore_rules',
    )
