import json
import re

import yaml
from django import forms

from .widgets import APISelect, APISelectMultiple, StaticSelect2


__all__ = (
    'BootstrapMixin',
    'BulkEditForm',
    'BulkRenameForm',
    'ConfirmationForm',
    'CSVModelForm',
    'ImportForm',
    'ReturnURLForm',
    'TableConfigForm',
)


class BootstrapMixin(forms.BaseForm):
    """
    Add the base Bootstrap CSS classes to form elements.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        exempt_widgets = [
            forms.CheckboxInput,
            forms.ClearableFileInput,
            forms.FileInput,
            forms.RadioSelect,
            APISelect,
            APISelectMultiple,
            StaticSelect2,
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


class BulkEditForm(forms.Form):
    """
    Base form for editing multiple objects in bulk
    """
    def __init__(self, model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model
        self.nullable_fields = []

        # Copy any nullable fields defined in Meta
        if hasattr(self.Meta, 'nullable_fields'):
            self.nullable_fields = self.Meta.nullable_fields


class BulkRenameForm(forms.Form):
    """
    An extendable form to be used for renaming objects in bulk.
    """
    find = forms.CharField()
    replace = forms.CharField()
    use_regex = forms.BooleanField(
        required=False,
        initial=True,
        label='Use regular expressions'
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
    def __init__(self, *args, headers=None, **kwargs):
        super().__init__(*args, **kwargs)

        # Modify the model form to accommodate any customized to_field_name properties
        if headers:
            for field, to_field in headers.items():
                if to_field is not None:
                    self.fields[field].to_field_name = to_field


class ImportForm(BootstrapMixin, forms.Form):
    """
    Generic form for creating an object from JSON/YAML data
    """
    data = forms.CharField(
        widget=forms.Textarea,
        help_text="Enter object data in JSON or YAML format. Note: Only a single object/document is supported."
    )
    format = forms.ChoiceField(
        choices=(
            ('json', 'JSON'),
            ('yaml', 'YAML')
        ),
        initial='yaml'
    )

    def clean(self):
        super().clean()

        data = self.cleaned_data['data']
        format = self.cleaned_data['format']

        # Process JSON/YAML data
        if format == 'json':
            try:
                self.cleaned_data['data'] = json.loads(data)
                # Check for multiple JSON objects
                if type(self.cleaned_data['data']) is not dict:
                    raise forms.ValidationError({
                        'data': "Import is limited to one object at a time."
                    })
            except json.decoder.JSONDecodeError as err:
                raise forms.ValidationError({
                    'data': "Invalid JSON data: {}".format(err)
                })
        else:
            # Check for multiple YAML documents
            if '\n---' in data:
                raise forms.ValidationError({
                    'data': "Import is limited to one object at a time."
                })
            try:
                self.cleaned_data['data'] = yaml.load(data, Loader=yaml.SafeLoader)
            except yaml.error.YAMLError as err:
                raise forms.ValidationError({
                    'data': "Invalid YAML data: {}".format(err)
                })


class TableConfigForm(BootstrapMixin, forms.Form):
    """
    Form for configuring user's table preferences.
    """
    columns = forms.MultipleChoiceField(
        choices=[],
        required=False,
        widget=forms.SelectMultiple(
            attrs={'size': 10}
        ),
        help_text="Use the buttons below to arrange columns in the desired order, then select all columns to display."
    )

    def __init__(self, table, *args, **kwargs):
        self.table = table

        super().__init__(*args, **kwargs)

        # Initialize columns field based on table attributes
        self.fields['columns'].choices = table.configurable_columns
        self.fields['columns'].initial = table.visible_columns

    @property
    def table_name(self):
        return self.table.__class__.__name__
