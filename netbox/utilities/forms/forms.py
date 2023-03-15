import re

from django import forms
from django.utils.translation import gettext as _

from .widgets import APISelect, APISelectMultiple, ClearableFileInput

__all__ = (
    'BootstrapMixin',
    'BulkEditForm',
    'BulkRenameForm',
    'ConfirmationForm',
    'CSVModelForm',
    'FilterForm',
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
            forms.FileInput,
            forms.RadioSelect,
            APISelect,
            APISelectMultiple,
            ClearableFileInput,
        ]

        for field_name, field in self.fields.items():
            css = field.widget.attrs.get('class', '')

            if field.widget.__class__ in exempt_widgets:
                continue

            elif isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = f'{css} form-check-input'

            elif isinstance(field.widget, forms.SelectMultiple):
                if 'size' not in field.widget.attrs:
                    field.widget.attrs['class'] = f'{css} netbox-static-select'

            elif isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = f'{css} netbox-static-select'

            else:
                field.widget.attrs['class'] = f'{css} form-control'

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
