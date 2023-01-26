from django import forms

from core.choices import *
from core.models import *
from netbox.forms import NetBoxModelFilterSetForm
from utilities.forms import DynamicModelMultipleChoiceField, MultipleChoiceField

__all__ = (
    'DataFileFilterForm',
    'DataSourceFilterForm',
)


class DataSourceFilterForm(NetBoxModelFilterSetForm):
    model = DataSource
    fieldsets = (
        (None, ('q', 'filter_id')),
        ('Data Source', ('type', 'git_branch')),
        ('Authentication', ('username',)),
    )
    type = MultipleChoiceField(
        choices=DataSourceTypeChoices,
        required=False
    )
    git_branch = forms.CharField(
        max_length=100,
        required=False
    )
    username = forms.CharField(
        max_length=100,
        required=False
    )


class DataFileFilterForm(NetBoxModelFilterSetForm):
    model = DataFile
    fieldsets = (
        (None, ('q', 'filter_id')),
        ('File', ('datasource_id',)),
    )
    datasource_id = DynamicModelMultipleChoiceField(
        queryset=DataSource.objects.all(),
        required=False
    )
    type = MultipleChoiceField(
        choices=DataSourceTypeChoices,
        required=False
    )
    git_branch = forms.CharField(
        max_length=100,
        required=False
    )
    username = forms.CharField(
        max_length=100,
        required=False
    )
