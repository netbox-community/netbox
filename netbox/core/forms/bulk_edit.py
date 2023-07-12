from django import forms
from django.utils.translation import gettext_lazy as _

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
        label=_('Type'),
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
        label=_('Description'),
        max_length=200,
        required=False
    )
    comments = CommentField(
        label=_('Comments')
    )
    parameters = forms.JSONField(
        label=_('Parameters'),
        required=False
    )
    ignore_rules = forms.CharField(
        label=_('Ignore rules'),
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
