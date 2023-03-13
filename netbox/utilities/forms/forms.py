import csv
import json
import re
from io import StringIO

import yaml
from django import forms
from django.utils.translation import gettext as _

from utilities.choices import ImportFormatChoices
from utilities.forms.utils import parse_csv
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
            css = field.widget.attrs.get('class', '')

            if field.widget.__class__ not in exempt_widgets:
                field.widget.attrs['class'] = f'{css} form-control'

            elif isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = f'{css} form-check-input'

            elif isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = f'{css} form-select'

            if field.required and not isinstance(field.widget, forms.FileInput):
                field.widget.attrs['required'] = 'required'

            if 'placeholder' not in field.widget.attrs and field.label is not None:
                field.widget.attrs['placeholder'] = field.label

    def is_valid(self):
        is_valid = super().is_valid()

        # Apply is-invalid CSS class to fields with errors
        if not is_valid:
            for field_name in self.errors:
                # Ignore e.g. __all__
                if field := self.fields.get(field_name):
                    css = field.widget.attrs.get('class', '')
                    field.widget.attrs['class'] = f'{css} is-invalid'

        return is_valid


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
    format = forms.ChoiceField(
        choices=ImportFormatChoices,
        initial=ImportFormatChoices.AUTO,
        widget=StaticSelect()
    )

    data_field = 'data'

    def clean(self):
        super().clean()

        # Determine whether we're reading from form data or an uploaded file
        if self.cleaned_data['data'] and self.cleaned_data['data_file']:
            raise forms.ValidationError("Form data must be empty when uploading a file.")
        if 'data_file' in self.files:
            self.data_field = 'data_file'
            file = self.files.get('data_file')
            data = file.read().decode('utf-8-sig')
        else:
            data = self.cleaned_data['data']

        # Determine the data format
        if self.cleaned_data['format'] == ImportFormatChoices.AUTO:
            format = self._detect_format(data)
        else:
            format = self.cleaned_data['format']

        # Process data according to the selected format
        if format == ImportFormatChoices.CSV:
            self.cleaned_data['data'] = self._clean_csv(data)
        elif format == ImportFormatChoices.JSON:
            self.cleaned_data['data'] = self._clean_json(data)
        elif format == ImportFormatChoices.YAML:
            self.cleaned_data['data'] = self._clean_yaml(data)
        else:
            raise forms.ValidationError(f"Unknown data format: {format}")

    def _detect_format(self, data):
        """
        Attempt to automatically detect the format (CSV, JSON, or YAML) of the given data, or raise
        a ValidationError.
        """
        try:
            if data[0] in ('{', '['):
                return ImportFormatChoices.JSON
            if data.startswith('---') or data.startswith('- '):
                return ImportFormatChoices.YAML
            if ',' in data.split('\n', 1)[0]:
                return ImportFormatChoices.CSV
        except IndexError:
            pass
        raise forms.ValidationError({
            'format': _('Unable to detect data format. Please specify.')
        })

    def _clean_csv(self, data):
        """
        Clean CSV-formatted data. The first row will be treated as column headers.
        """
        stream = StringIO(data.strip())
        reader = csv.reader(stream)
        headers, records = parse_csv(reader)

        # Set CSV headers for reference by the model form
        self._csv_headers = headers

        return records

    def _clean_json(self, data):
        """
        Clean JSON-formatted data. If only a single object is defined, it will be encapsulated as a list.
        """
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
        """
        Clean YAML-formatted data. Data must be either
          a) A single document comprising a list of dictionaries (each representing an object), or
          b) Multiple documents, separated with the '---' token
        """
        records = []
        try:
            for data in yaml.load_all(data, Loader=yaml.SafeLoader):
                if type(data) == list:
                    records.extend(data)
                elif type(data) == dict:
                    records.append(data)
                else:
                    raise forms.ValidationError({
                        self.data_field: _(
                            "Invalid YAML data. Data must be in the form of multiple documents, or a single document "
                            "comprising a list of dictionaries."
                        )
                    })
        except yaml.error.YAMLError as err:
            raise forms.ValidationError({
                self.data_field: f"Invalid YAML data: {err}"
            })

        return records


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
