from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from core.choices import *
from core.models import *
from netbox.forms import NetBoxModelFilterSetForm
from netbox.forms.mixins import SavedFiltersMixin
from netbox.utils import get_data_backend_choices
from utilities.forms import BOOLEAN_WITH_BLANK_CHOICES, FilterForm
from utilities.forms.fields import ContentTypeChoiceField, DynamicModelMultipleChoiceField
from utilities.forms.rendering import FieldSet
from utilities.forms.widgets import DateTimePicker

__all__ = (
    'ConfigRevisionFilterForm',
    'DataFileFilterForm',
    'DataSourceFilterForm',
    'JobFilterForm',
)


class DataSourceFilterForm(NetBoxModelFilterSetForm):
    model = DataSource
    fieldsets = (
        FieldSet('q', 'filter_id'),
        FieldSet('type', 'status', name=_('Data Source')),
    )
    type = forms.MultipleChoiceField(
        label=_('Type'),
        choices=get_data_backend_choices,
        required=False
    )
    status = forms.MultipleChoiceField(
        label=_('Status'),
        choices=DataSourceStatusChoices,
        required=False
    )
    enabled = forms.NullBooleanField(
        label=_('Enabled'),
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )


class DataFileFilterForm(NetBoxModelFilterSetForm):
    model = DataFile
    fieldsets = (
        FieldSet('q', 'filter_id'),
        FieldSet('source_id', name=_('File')),
    )
    source_id = DynamicModelMultipleChoiceField(
        queryset=DataSource.objects.all(),
        required=False,
        label=_('Data source')
    )


class JobFilterForm(SavedFiltersMixin, FilterForm):
    fieldsets = (
        FieldSet('q', 'filter_id'),
        FieldSet('object_type', 'status', name=_('Attributes')),
        FieldSet(
            'created__before', 'created__after', 'scheduled__before', 'scheduled__after', 'started__before',
            'started__after', 'completed__before', 'completed__after', 'user', name=_('Creation')
        ),
    )
    object_type = ContentTypeChoiceField(
        label=_('Object Type'),
        queryset=ObjectType.objects.with_feature('jobs'),
        required=False,
    )
    status = forms.MultipleChoiceField(
        label=_('Status'),
        choices=JobStatusChoices,
        required=False
    )
    created__after = forms.DateTimeField(
        label=_('Created after'),
        required=False,
        widget=DateTimePicker()
    )
    created__before = forms.DateTimeField(
        label=_('Created before'),
        required=False,
        widget=DateTimePicker()
    )
    scheduled__after = forms.DateTimeField(
        label=_('Scheduled after'),
        required=False,
        widget=DateTimePicker()
    )
    scheduled__before = forms.DateTimeField(
        label=_('Scheduled before'),
        required=False,
        widget=DateTimePicker()
    )
    started__after = forms.DateTimeField(
        label=_('Started after'),
        required=False,
        widget=DateTimePicker()
    )
    started__before = forms.DateTimeField(
        label=_('Started before'),
        required=False,
        widget=DateTimePicker()
    )
    completed__after = forms.DateTimeField(
        label=_('Completed after'),
        required=False,
        widget=DateTimePicker()
    )
    completed__before = forms.DateTimeField(
        label=_('Completed before'),
        required=False,
        widget=DateTimePicker()
    )
    user = DynamicModelMultipleChoiceField(
        queryset=get_user_model().objects.all(),
        required=False,
        label=_('User')
    )


class ConfigRevisionFilterForm(SavedFiltersMixin, FilterForm):
    fieldsets = (
        FieldSet('q', 'filter_id'),
    )
