from django import forms
from django.utils.translation import gettext as _

from core.choices import *
from core.models import *
from netbox.forms import NetBoxModelFilterSetForm
from utilities.forms import BOOLEAN_WITH_BLANK_CHOICES, DynamicModelMultipleChoiceField

__all__ = (
    'DataFileFilterForm',
    'DataSourceFilterForm',
)


class DataSourceFilterForm(NetBoxModelFilterSetForm):
    model = DataSource
    fieldsets = (
        (None, ('q', 'filter_id')),
        ('Data Source', ('type', 'status')),
    )
    type = forms.MultipleChoiceField(
        choices=DataSourceTypeChoices,
        required=False
    )
    status = forms.MultipleChoiceField(
        choices=DataSourceStatusChoices,
        required=False
    )
    enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )


class DataFileFilterForm(NetBoxModelFilterSetForm):
    model = DataFile
    fieldsets = (
        (None, ('q', 'filter_id')),
        ('File', ('source_id',)),
    )
    source_id = DynamicModelMultipleChoiceField(
        queryset=DataSource.objects.all(),
        required=False,
        label=_('Data source')
    )
