from django import forms
from django.utils.translation import gettext_lazy as _

from core.models import *
from core.utils import get_data_backend_choices
from netbox.forms import NetBoxModelBulkEditForm
from utilities.forms.fields import CommentField
from utilities.forms.widgets import BulkEditNullBooleanSelect

__all__ = (
    'DataSourceBulkEditForm',
)


class DataSourceBulkEditForm(NetBoxModelBulkEditForm):
    type = forms.ChoiceField(
        label=_('Type'),
        # TODO: Field value should be empty on init (needs add_blank_choice())
        choices=get_data_backend_choices,
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
    comments = CommentField()
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
