import csv
import json
import re
from io import StringIO

import yaml
from django import forms
from django.utils.translation import gettext as _

from utilities.forms.utils import parse_csv
from .choices import ImportFormatChoices
from .widgets import APISelect, APISelectMultiple, ClearableFileInput, StaticSelect

__all__ = (
    'BootstrapMixin',
    'BulkEditForm',
    'BulkRenameForm',
    'ConfirmationForm',
    'CSVModelForm',
    'FilterForm',
    'ImportForm',
    'ReturnURLForm',
    'TableConfigForm',
)


#
# Mixins
#

class BootstrapMixin:
    """
    Add the base Bootstrap CSS classes to form elements.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        exempt_widgets = [
            forms.CheckboxInput,
            forms.FileInput,
            forms.RadioSelect,
            forms.Select,
            APISelect,
            APISelectMultiple,
            ClearableFileInput,
            StaticSelect,
        ]

        for field_name, field in self.fields.items():

            if field.widget.__class__ not in exempt_widgets:
                css = field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = ' '.join([css, 'form-control']).strip()

            if field.required and not isinstance(field.widget, forms.FileInput):
                field.widget.attrs['required'] = 'required'

            if 'placeholder' not in field.widget.attrs and field.label is not None:
                field.widget.attrs['placeholder'] = field.label

            if field.widget.__class__ == forms.CheckboxInput:
                css = field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = ' '.join((css, 'form-check-input')).strip()

            if field.widget.__class__ == forms.Select:
                css = field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = ' '.join((css, 'form-select')).strip()


#
# Form classes
#

class ReturnURLForm(forms.Form):
    """
    Provides a hidden return URL field to control where the user is directed after the form is submitted.
    """
    return_url = forms.CharField(required=False, widget=forms.HiddenInput())


class ConfirmationForm(BootstrapMixin, ReturnURLForm):
    """
    A generic confirmation form. The form is not valid unless the confirm field is checked.
    """
    confirm = forms.BooleanField(required=True, widget=forms.HiddenInput(), initial=True)


class BulkEditForm(BootstrapMixin, forms.Form):
    """
    Provides bulk edit support for objects.
    """
    nullable_fields = ()


class BulkRenameForm(BootstrapMixin, forms.Form):
    """
    An extendable form to be used for renaming objects in bulk.
    """
    find = forms.CharField()
    replace = forms.CharField(
        required=False
    )
    use_regex = forms.BooleanField(
        required=False,
        initial=True,
        label=_('Use regular expressions')
    )

    def clean(self):
        super().clean()

        # Validate regular expression in "find" field
        if self.cleaned_data['use_regex']:
            try:
                re.compile(self.cleaned_data['find'])
            except re.error:
                raise forms.ValidationError({
                    'find': "Invalid regular expression"
                })


class CSVModelForm(forms.ModelForm):
    """
    ModelForm used for the import of objects in CSV format.
    """
    def __init__(self, *args, headers=None, fields=None, **kwargs):
        headers = headers or {}
        fields = fields or []
        super().__init__(*args, **kwargs)

        # Modify the model form to accommodate any customized to_field_name properties
        for field, to_field in headers.items():
            if to_field is not None:
                self.fields[field].to_field_name = to_field

        # Omit any fields not specified (e.g. because the form is being used to
        # updated rather than create objects)
        if fields:
            for field in list(self.fields.keys()):
                if field not in fields:
                    del self.fields[field]


class ImportForm(BootstrapMixin, forms.Form):
    data = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'font-monospace'}),
        help_text=_("Enter object data in CSV, JSON or YAML format.")
    )
    data_file = forms.FileField(
        label="Data file",
        required=False
    )
    # TODO: Enable auto-detection of format
    format = forms.ChoiceField(
        choices=ImportFormatChoices,
        initial=ImportFormatChoices.CSV,
        widget=StaticSelect()
    )

    data_field = 'data'

    def clean(self):
        super().clean()
        format = self.cleaned_data['format']

        # Determine whether we're reading from form data or an uploaded file
        if self.cleaned_data['data'] and self.cleaned_data['data_file']:
            raise forms.ValidationError("Form data must be empty when uploading a file.")
        if 'data_file' in self.files:
            self.data_field = 'data_file'
            file = self.files.get('data_file')
            data = file.read().decode('utf-8')
        else:
            data = self.cleaned_data['data']

        # Process data according to the selected format
        if format == ImportFormatChoices.CSV:
            self.cleaned_data['data'] = self._clean_csv(data)
        elif format == ImportFormatChoices.JSON:
            self.cleaned_data['data'] = self._clean_json(data)
        elif format == ImportFormatChoices.YAML:
            self.cleaned_data['data'] = self._clean_yaml(data)

    def _clean_csv(self, data):
        stream = StringIO(data.strip())
        reader = csv.reader(stream)
        headers, records = parse_csv(reader)

        # Set CSV headers for reference by the model form
        self._csv_headers = headers

        return records

    def _clean_json(self, data):
        try:
            data = json.loads(data)
            # Accommodate for users entering single objects
            if type(data) is not list:
                data = [data]
            return data
        except json.decoder.JSONDecodeError as err:
            raise forms.ValidationError({
                self.data_field: f"Invalid JSON data: {err}"
            })

    def _clean_yaml(self, data):
        try:
            return yaml.load_all(data, Loader=yaml.SafeLoader)
        except yaml.error.YAMLError as err:
            raise forms.ValidationError({
                self.data_field: f"Invalid YAML data: {err}"
            })


class FilterForm(BootstrapMixin, forms.Form):
    """
    Base Form class for FilterSet forms.
    """
    q = forms.CharField(
        required=False,
        label=_('Search')
    )


class TableConfigForm(BootstrapMixin, forms.Form):
    """
    Form for configuring user's table preferences.
    """
    available_columns = forms.MultipleChoiceField(
        choices=[],
        required=False,
        widget=forms.SelectMultiple(
            attrs={'size': 10, 'class': 'form-select'}
        ),
        label=_('Available Columns')
    )
    columns = forms.MultipleChoiceField(
        choices=[],
        required=False,
        widget=forms.SelectMultiple(
            attrs={'size': 10, 'class': 'form-select'}
        ),
        label=_('Selected Columns')
    )

    def __init__(self, table, *args, **kwargs):
        self.table = table

        super().__init__(*args, **kwargs)

        # Initialize columns field based on table attributes
        self.fields['available_columns'].choices = table.available_columns
        self.fields['columns'].choices = table.selected_columns

    @property
    def table_name(self):
        return self.table.__class__.__name__
