import re

from django import forms
from django.utils.translation import gettext as _

__all__ = (
    'BulkEditForm',
    'BulkRenameForm',
    'ConfirmationForm',
    'CSVModelForm',
    'FilterForm',
    'TableConfigForm',
)


class ConfirmationForm(forms.Form):
    """
    A generic confirmation form. The form is not valid unless the `confirm` field is checked.
    """
    return_url = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )
    confirm = forms.BooleanField(
        required=True,
        widget=forms.HiddenInput(),
        initial=True
    )


class BulkEditForm(forms.Form):
    """
    Provides bulk edit support for objects.
    """
    nullable_fields = ()


class BulkRenameForm(forms.Form):
    """
    An extendable form to be used for renaming objects in bulk.
    """
    find = forms.CharField(
        strip=False
    )
    replace = forms.CharField(
        strip=False,
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
    id = forms.IntegerField(
        label=_('ID'),
        required=False,
        help_text=_('Numeric ID of an existing object to update (if not creating a new object)')
    )

    def __init__(self, *args, headers=None, **kwargs):
        self.headers = headers or {}
        super().__init__(*args, **kwargs)

        # Modify the model form to accommodate any customized to_field_name properties
        for field, to_field in self.headers.items():
            if to_field is not None:
                self.fields[field].to_field_name = to_field

    def clean(self):
        # Flag any invalid CSV headers
        for header in self.headers:
            if header not in self.fields:
                raise forms.ValidationError(
                    _("Unrecognized header: {name}").format(name=header)
                )

        return super().clean()


class FilterForm(forms.Form):
    """
    Base Form class for FilterSet forms.
    """
    q = forms.CharField(
        required=False,
        label=_('Search')
    )


class TableConfigForm(forms.Form):
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
